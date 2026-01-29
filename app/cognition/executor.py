from app.cognition.planner import CognitivePlan
from app.filesystem.actions import get_fs_actions
from app.memory_client import add_memory
from app.tasks.manager import get_task_manager
import os

class PlanExecutor:
    def __init__(self):
        self.fs = get_fs_actions()
        self.task_manager = get_task_manager()
        print("[Executor] v2.0 - Loaded (Memory Fixes Applied)")

    async def execute(self, plan: CognitivePlan, session_id: str, user_id: str = "default_user") -> str:
        """
        Executes the plan.
        Returns a summary string of results.
        Only writes memory if execution was successful.
        """
        # Task Management (Phase 9)
        task = None
        if plan.steps:
            try:
                task = self.task_manager.create_task(plan.intent)
            except Exception as e:
                print(f"[Executor] Task creation failed: {e}")
        
        results = []
        success = True

        for step in plan.steps:
            print(f"[Executor] Step: {step.tool} | Params: {step.params}")
            try:
                res = None
                if step.tool == "create_file" or step.tool == "write_file":
                    path = step.params.get("path") or step.params.get("target_file")
                    content = step.params.get("content", "")
                    res = self.fs.write_file(path, content)
                
                elif step.tool == "delete_file" or step.tool == "delete_folder":
                    path = step.params.get("path")
                    res = self.fs.execute("delete", path)
                
                elif step.tool == "create_folder":
                    path = step.params.get("path")
                    res = self.fs.execute("create_folder", path)
                
                elif step.tool == "list_dir":
                    path = step.params.get("path")
                    if os.path.exists(path):
                        items = os.listdir(path)
                        res = f"Contents of {path}: {', '.join(items[:10])}"
                    else:
                        res = "Path not found."

                elif step.tool == "launch_app_search":
                    app_name = step.params.get("app_name", "")
                    if app_name:
                        from app.automation.search_launcher import get_search_launcher
                        launcher = get_search_launcher()
                        # Check if trusted or needs confirmation
                        if launcher.is_trusted(app_name):
                            result = launcher.search_and_launch(app_name, confirmed=True)
                            res = result["message"]
                        else:
                            # Return confirmation request - will be handled by chat router
                            res = f"NEEDS_CONFIRM:launch_app:{app_name}"
                    else:
                        res = "No app name provided."

                elif step.tool == "click_element":
                    target = step.params.get("target", "")
                    if target:
                        from app.automation.ui_finder import get_ui_finder
                        from app.automation.actions import get_screen_actions
                        from app.visual.element_memory import get_element_memory
                        
                        finder = get_ui_finder()
                        actions = get_screen_actions()
                        memory = get_element_memory()
                        
                        # 1. Try Visual Memory Match (Phase 16)
                        visual_match = memory.find_match(target)
                        if visual_match and visual_match["found_on_screen"]:
                             cx, cy = visual_match["center"]
                             result = actions.click(cx, cy, confirmed=True)
                             res = f"Clicked remembered element '{visual_match['name']}' at ({cx},{cy})"
                        
                        # 2. Try UI Finder (Properties/OCR)
                        else:
                            element = finder.find_button(target)
                            if element:
                                result = actions.click(element.center[0], element.center[1], confirmed=True)
                                res = result.message
                            else:
                                res = f"Could not find element: {target}"
                    else:
                        res = "No target specified for click."

                elif step.tool == "type_into":
                    text = step.params.get("text", "")
                    focus_val = step.params.get("target_app") or step.params.get("focus") 
                    
                    if text:
                        from app.automation.actions import get_screen_actions
                        from app.automation.ui_finder import get_ui_finder
                        
                        actions = get_screen_actions()
                        finder = get_ui_finder()
                        
                        # Smart Launch Logic (Phase 17)
                        if focus_val:
                            # Try to focus first
                            focused = finder.focus_window(focus_val)
                            if not focused:
                                # App not found/open. Request Launch.
                                res = f"NEEDS_CONFIRM:launch_app:{focus_val}"
                                # Stop here to let chat.py handle the launch prompt
                                return res

                        result = actions.type_text(text, confirmed=True, focus=focus_val)
                        res = result.message
                    else:
                        res = "No text specified to type."

                elif step.tool == "scroll_screen":
                    direction = step.params.get("direction", "down")
                    amount = step.params.get("amount", 3)
                    from app.automation.actions import get_screen_actions
                    actions = get_screen_actions()
                    result = actions.scroll(direction, amount, confirmed=True)
                    res = result.message

                elif step.tool == "press_keys":
                    keys_str = step.params.get("keys", "")
                    focus_val = step.params.get("focus", None)
                    if keys_str:
                        from app.automation.actions import get_screen_actions
                        actions = get_screen_actions()
                        keys = keys_str.replace("+", " ").split()
                        
                        # Phase 17: Safer hotkeys
                        result = actions.hotkey(*keys, confirmed=True, focus=focus_val)
                        res = result.message
                    else:
                        res = "No keys specified."

                elif step.tool == "remember_ui_element":
                    name = step.params.get("name", "unknown_element")
                    from app.visual.capture import get_screen_capture
                    from app.visual.element_memory import get_element_memory
                    
                    capture = get_screen_capture()
                    memory = get_element_memory()
                    
                    # Capture full screen for now (or active window if we had bounds)
                    # Ideally, we'd interactively ask user to select region, but automating full screen is safer start.
                    scan = capture.capture_screen(save=True)
                    
                    if scan["status"] == "success":
                        # Store in element memory
                        # Region is full screen (0,0,width,height)
                        w, h = scan["size"]
                        region = (0, 0, w, h)
                        
                        success = memory.remember_element(name, scan["path"], region)
                        if success:
                            res = f"Visual memory saved: '{name}'"
                        else:
                            res = "Failed to embed visual memory."
                    else:
                        res = f"Screen capture failed: {scan.get('message')}"

                elif step.tool == "chat":
                    res = step.params.get("message") or step.params.get("response") or "OK."

                elif step.tool == "memory_save":
                    res = "Saving memory to long-term storage."

                if res:
                    results.append(res)
                # But for file ops, we want confirmation.
                # If tool is chat, just res.
                # If file op, "Created X".
                
                if step.tool != "chat":
                     # Replace the raw append with formatted if needed, or rely on tool output
                     # The tool output usually says "Created folder..."
                     # But results.append above appended just 'res'.
                     # Let's override the list logic.
                     pass
                     
                if res and "Error" in res:
                    success = False
                    break # Stop execution on failure? Strict discipline says yes?
            
            except Exception as e:
                results.append(f"Step '{step.description}' Failed: {e}")
                success = False
                break

        final_summary = "\n".join(results)

        # Memory Discipline
        if success and plan.memory_candidates:
             # Create a structured message for the memory system
             facts = "\n".join(plan.memory_candidates)
             mem_res = add_memory([{"role": "user", "content": f"System Note: Extracted facts: {facts}"}], user_id)
             
             # Check if we actually saved something
             if mem_res and mem_res.get("results"):
                 count = len(mem_res["results"])
                 results.append(f"🧠 I've committed {count} new memories to long-term storage.")
             else:
                 # If extraction returned empty but candidates existed, it might be due to importance filtering or previously existing facts
                 # But let's check if we just fixed the extraction fragility
                 pass
        
        # Task Completion (Phase 9)
        if success and task:
            try:
                self.task_manager.complete_active_task()
            except Exception as e:
                print(f"[Executor] Task completion failed: {e}")
        
        return final_summary

executor = PlanExecutor()
