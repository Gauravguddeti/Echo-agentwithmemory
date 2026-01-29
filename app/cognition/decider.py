from .schema import StructuredIntent

class ActionPlan:
    def __init__(self, action_type, func, params, reason):
        self.action_type = action_type
        self.func = func
        self.params = params
        self.reason = reason

class IntentDecider:
    def decide(self, intent: StructuredIntent) -> ActionPlan:
        """
        Converts a StructuredIntent into an executable ActionPlan.
        """
        # 1. Browser Search
        if intent.goal == "browser_search":
            import webbrowser
            from urllib.parse import quote_plus
            
            query = intent.params.get("query", intent.target)
            engine = intent.target if intent.target in ["google", "youtube"] else "google"
            
            url = f"https://www.google.com/search?q={quote_plus(query)}"
            if engine == "youtube":
                url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
                
            return ActionPlan(
                action_type="browser_search",
                func=webbrowser.open_new_tab,
                params={"url": url},
                reason=f"User wants to search {engine} for '{query}'."
            )

        # 2. Browser Nav
        if intent.goal == "browser_nav":
            # Check if target is a valid URL, if not -> fallback to search?
            # "take me to Shroud" -> "Shroud" is not a URL.
            # Cognitive Leap: If target is not a URL, Search it.
            target = intent.params.get("url", intent.target)
            
            if "." not in target and "http" not in target:
                 # It's an entity, not a URL.
                 # RE-DECIDE: Convert to Search
                 # Recursion or manual switch?
                 intent.goal = "browser_search"
                 intent.params["query"] = target
                 intent.target = "google"
                 return self.decide(intent)

            import webbrowser
            if not target.startswith("http"):
                target = "https://" + target
                
            return ActionPlan(
                action_type="browser_nav",
                func=webbrowser.open_new_tab,
                params={"url": target},
                reason=f"User wants to navigate to {target}."
            )

        # 3. Desktop Write
        if intent.goal == "desktop_write":
             from app.automation.input import get_input_manager
             from app.apps.launcher import launch_app
             import asyncio
             
             async def execute_write(app, text):
                 launch_app(app)
                 inp = get_input_manager()
                 
                 # Wait logic (simplified for decider, really should be in Flow)
                 # Reusing the robust wait loop logic from chat.py is ideal, 
                 # but for now we put it here or return a Coroutine.
                 # Let's return the Plan, and the Caller (Chat) runs it? 
                 # Or we return a function wrapper.
                 
                 # NOTE: The Decider returns a 'func'. 
                 # We can bind the complex logic here.
                 
                 target_keywords = [app.lower(), "untitled"]
                 for i in range(10):
                     await asyncio.sleep(0.5)
                     focus = inp.get_foreground_window_title()
                     if any(k in focus.lower() for k in target_keywords):
                         return inp.write_text_safely(text, focus)
                     if "notepad" in app.lower():
                         inp.focus_app("Untitled")
                 
                 return "Timeout waiting for app."

             return ActionPlan(
                 action_type="desktop_write",
                 func=execute_write,
                 params={"app": intent.target, "text": intent.params.get("text", "")},
                 reason=f"User wants to write to {intent.target}."
             )
        
        # 4. Open App
        if intent.goal == "open_app":
            from app.apps.launcher import launch_app
            return ActionPlan(
                action_type="open_app",
                func=launch_app,
                params={"path": intent.target},
                reason=f"User wants to launch {intent.target}."
            )

        # 5. Filesystem
        if intent.goal == "filesystem":
             if intent.target == "create_folder":
                  # Check params
                  name = intent.params.get("name")
                  if not name:
                       # Missing info! Return None so Chat handles it (Clarification)
                       return None
                  
                  # If name exists, return execution plan
                  import os
                  def create_folder(name, path=None):
                       target_path = path if path else os.getcwd()
                       full_path = os.path.join(target_path, name)
                       try:
                           os.makedirs(full_path, exist_ok=True)
                           return f"Created folder: {full_path}"
                       except Exception as e:
                           return f"Error creating folder: {e}"
                  
                  return ActionPlan(
                      action_type="create_folder",
                      func=create_folder,
                      params={"name": name, "path": intent.params.get("path")},
                      reason=f"Creating user folder '{name}'."
                  )

             if intent.target == "delete_item":
                  name = intent.params.get("name")
                  if not name:
                       return None
                  
                  import os
                  # Check existence
                  target_path = os.path.abspath(name) # Relative to CWD
                  if not os.path.exists(target_path):
                       # Try generic path search? Or just fail safely?
                       # Return None -> Chat asks user "Can't find it".
                       return None
                  
                  def delete_item(name, path=None):
                       t_path = path if path else os.path.abspath(name)
                       try:
                           if os.path.isdir(t_path):
                                os.rmdir(t_path) # Safe rmdir (empty only?) Use rmtree if needed but risky.
                                # Let's stick to safe rmdir for now or shutil?
                                # User prompt said "Destructive Action Safety".
                                # Maybe just rmdir.
                                return f"Deleted folder: {t_path}"
                           else:
                                os.remove(t_path)
                                return f"Deleted file: {t_path}"
                       except Exception as e:
                           return f"Error deleting: {e}"

                  return ActionPlan(
                      action_type="delete_item",
                      func=delete_item,
                      params={"name": name},
                      reason=f"Deleting user item '{name}'."
                  )

             if intent.target == "create_file":
                  name = intent.params.get("name")
                  if not name: return None
                  
                  import os
                  def create_file_action(name, path=None):
                       t_path = path if path else os.getcwd()
                       full = os.path.join(t_path, name)
                       try:
                            # Check if exists? Overwrite?
                            # Create empty
                            with open(full, 'w') as f:
                                 pass
                            return f"Created file: {full}"
                       except Exception as e:
                            return f"Error creating file: {e}"
                  
                  return ActionPlan(
                       action_type="create_file",
                       func=create_file_action,
                       params={"name": name},
                       reason=f"Creating file '{name}'."
                  )

        return None
