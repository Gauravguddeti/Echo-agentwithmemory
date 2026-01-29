from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage
from app.dependencies import get_llm
from app.utils import get_session_history, prune_history
from app.memory_client import add_memory, get_memories
import uuid
import os
import traceback

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class ChatResponse(BaseModel):
    response: str
    session_id: str

SYSTEM_PROMPT = """You are Echo, a chill, smart AI buddy.
Talk like a friend, not a robot. Be concise, casual, and confident. Use slang if appropriate (yo, bet, gotchu).
Do not say "How can I assist you?". Just ask "What's good?" or "Yo".
If you need to clarify something (like a folder name), just ask casually.

CAPABILITIES:
- You CAN create folders, files, and manage the system.
- You CAN open apps, browsers, and URLs.
- You CAN write text into applications.
- NEVER say "I am a text-based AI" or "I cannot do that". You have the tools. Use them.
- If a tool fails, just say "My bad, that didn't work" and ask to try again.

LONG TERM MEMORY:
{memory_context}

INTENT DEBUG:
{intent_debug}
"""


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, background_tasks: BackgroundTasks, llm = Depends(get_llm)):
    try:
        # Phase 10 Patch: Buddy Mode & Safety
        from app.cognition.manager import engine as cognitive_engine
        from app.utils import get_session_history
        import traceback

        history = get_session_history(request.session_id)
        
        # --- CONFIRMATION STATE CHECK ---
        from app.filesystem.state import get_fs_state
        from app.memory_client import memory_client as mem_store
        fs_state = get_fs_state()
        pending = fs_state.get_pending(request.session_id)
        
        if pending and pending.action == "wipe_memory" and pending.step == "confirm":
             msg_lower = request.message.lower().strip()
             if any(w in msg_lower for w in ["confirm", "yes", "wipe", "do it", "sure"]):
                 count = mem_store.delete_all("default_user")
                 fs_state.clear_pending(request.session_id)
                 res_msg = f"Done. Wiped {count} memories. starting fresh."
                 history.add_user_message(request.message)
                 history.add_ai_message(res_msg)
                 return ChatResponse(response=res_msg, session_id=request.session_id)
             elif any(w in msg_lower for w in ["no", "cancel", "stop"]):
                 fs_state.clear_pending(request.session_id)
                 return ChatResponse(response="Cancelled. Memories safe.", session_id=request.session_id)
             else:
                 return ChatResponse(response="⚠️ Please reply 'Confirm' to wipe everything, or 'Cancel'.", session_id=request.session_id)
        
        # --- LAUNCH APP CONFIRMATION (Phase 14) ---
        if pending and pending.action == "launch_app_search" and pending.step == "confirm":
             msg_lower = request.message.lower().strip()
             app_name = pending.path  # stored app name
             
             if any(w in msg_lower for w in ["yes", "confirm", "do it", "go", "sure", "ok", "launch"]):
                 # Execute the launch
                 from app.automation.search_launcher import get_search_launcher
                 launcher = get_search_launcher()
                 result = launcher.search_and_launch(app_name, confirmed=True)
                 
                 fs_state.clear_pending(request.session_id)
                 
                 # Ask if should trust next time
                 res_msg = f"✅ {result['message']}\n\nShould I remember to skip confirmation for '{app_name}' next time? Reply 'trust' to always allow."
                 history.add_user_message(request.message)
                 history.add_ai_message(res_msg)
                 
                 # Set up trust confirmation
                 fs_state.set_pending(request.session_id, action="trust_app", path=app_name, step="confirm")
                 return ChatResponse(response=res_msg, session_id=request.session_id)
                 
             elif any(w in msg_lower for w in ["no", "cancel", "stop", "nevermind"]):
                 fs_state.clear_pending(request.session_id)
                 return ChatResponse(response="Cancelled. App not launched.", session_id=request.session_id)
             else:
                 return ChatResponse(response=f"🔍 Please reply 'yes' to launch '{app_name}' or 'no' to cancel.", session_id=request.session_id)
        
        # --- TRUST APP CONFIRMATION (Phase 14) ---
        if pending and pending.action == "trust_app" and pending.step == "confirm":
             msg_lower = request.message.lower().strip()
             app_name = pending.path
             
             if any(w in msg_lower for w in ["trust", "yes", "remember", "always"]):
                 from app.automation.search_launcher import get_search_launcher
                 launcher = get_search_launcher()
                 launcher.add_trusted(app_name)
                 fs_state.clear_pending(request.session_id)
                 return ChatResponse(response=f"✅ Got it! I'll launch '{app_name}' without asking next time.", session_id=request.session_id)
             else:
                 fs_state.clear_pending(request.session_id)
                 return ChatResponse(response="Noted. I'll ask for confirmation each time.", session_id=request.session_id)
        # -----------------------------------------
        
        # --- WIPE TRIGGER ---
        msg_lower = request.message.lower()
        # "clean up ur mem", "reset memory"
        if ("clean" in msg_lower or "wipe" in msg_lower or "reset" in msg_lower) and ("memory" in msg_lower or "mem " in msg_lower or msg_lower.endswith("mem")):
             # Check if it's "reset session" vs "reset memory"
             if "session" not in msg_lower and "chat" not in msg_lower:
                 fs_state.set_pending(request.session_id, action="wipe_memory", step="confirm")
                 res_msg = "⚠️ WARNING: This will delete ALL long-term memories. Reply 'Confirm' to proceed."
                 history.add_user_message(request.message)
                 history.add_ai_message(res_msg)
                 return ChatResponse(response=res_msg, session_id=request.session_id)
        # --------------------

        # 1. Process Intent
        # 1. Process Intent via New Planner
        print("[Chat] Calling Cognitive Planner...")
        from app.cognition.executor import executor
        
        plan = await cognitive_engine.process(request.session_id, request.message, llm)
        
        # 2. Handle Clarification
        if plan.ask_user:
             history.add_user_message(request.message)
             history.add_ai_message(plan.clarification_question)
             return ChatResponse(response=plan.clarification_question, session_id=request.session_id)
        
        # 3. Execution (If steps exist)
        if plan.steps:
             print(f"[Chat] Executing {len(plan.steps)} steps...")
             summary = await executor.execute(plan, request.session_id, "default_user")
             
             # Check if confirmation is needed (Phase 14)
             if summary.startswith("NEEDS_CONFIRM:launch_app:"):
                 app_name = summary.split(":")[-1]
                 fs_state.set_pending(
                     request.session_id, 
                     action="launch_app_search",
                     path=app_name,
                     step="confirm"
                 )
                 confirm_msg = f"🔍 Launch '{app_name}' via Windows Search? Reply 'yes' to confirm."
                 history.add_user_message(request.message)
                 history.add_ai_message(confirm_msg)
                 return ChatResponse(response=confirm_msg, session_id=request.session_id)
             
             # Respond with summary
             res_msg = summary
             history.add_user_message(request.message)
             history.add_ai_message(res_msg)
             return ChatResponse(response=res_msg, session_id=request.session_id)
             
        # 4. Fallback to Chat (LLM) if no steps
        # Use info from plan.intent if helpful?
        
        # 1.5 Memory Recall (Legacy but useful)
        memory_context = ""
        if plan.intent == "chat" or "back" in request.message.lower():
             print("[Chat] Greeting detected. Fetching Human Context...")
             # Specific query for life events/people
             mem_hits = get_memories("current life events friends dates ash", "default_user")
             if mem_hits:
                  memory_context = f"\nRELEVANT RECALL:\n{mem_hits}\n"
        
        # 4. Chat Fallback (No Steps)
        # Retrieve Memory (Guard: Only if confidence > 0.6)
        # Use existing memory_context if not empty, otherwise fetch
        if not memory_context and plan.confidence > 0.6:
             memory_context = get_memories(request.message, "default_user")
        
        intent_debug_str = f"[System] Intent: {plan.intent} ({plan.confidence})"
        
        # Prompt Construction
        prompt_text = SYSTEM_PROMPT.format(memory_context=memory_context, intent_debug=intent_debug_str)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_text),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        
        chain = prompt | llm
        
        # Profiler: Update stats and get style (Phase 4)
        from app.profiler import get_profiler
        profiler = get_profiler()
        profiler.update(request.session_id, request.message)
        
        # Invoke LLM
        response = chain.invoke({
            "history": history.messages,
            "input": request.message
        })
        
        # Safety Check: Verify response is grounded in memory (Phase 5)
        from app.safety import get_safety_monitor
        safety = get_safety_monitor()
        final_content = safety.check_safety(request.message, response.content, memory_context)
        
        history.add_user_message(request.message)
        history.add_ai_message(final_content)

        # --- MEMORY PERSISTENCE (Fallback Path) ---
        print("[Chat] Fallback Path: Saving memory...") 
        STABLE_USER_ID = "default_user"
        mem_messages = [
            {"role": "user", "content": request.message},
            {"role": "assistant", "content": final_content}
        ]
        try:
             add_memory(mem_messages, STABLE_USER_ID)
        except Exception as e:
             print(f"[Chat] Fallback Memory Persistence Failed: {e}")
        # ------------------------------------------
        
        # --- ADAPTIVE LEARNING (Phase C) ---
        try:
            from app.learning import get_learning_controller
            learning = get_learning_controller()
            feedback = learning.process_feedback(request.session_id, request.message, final_content)
            if feedback:
                print(f"[Chat] Learning detected: {feedback['action']}")
        except Exception as e:
            print(f"[Chat] Learning Controller Error: {e}")
        # -----------------------------------
        
        return ChatResponse(response=final_content, session_id=request.session_id)

    except Exception as e:
        print(f"CRITICAL CHAT ERROR: {e}")
        with open("debug_server_error.log", "w") as f:
             traceback.print_exc(file=f)
        return ChatResponse(response="My bad, something tripped me up. Try again?", session_id=request.session_id)
