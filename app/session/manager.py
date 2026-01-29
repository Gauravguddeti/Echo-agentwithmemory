from app.session.models import SessionMode, SessionState

# In-memory storage for session modes
# Key: session_id, Value: SessionState
_sessions = {}

class SessionManager:
    def get_state(self, session_id: str) -> SessionState:
        if session_id not in _sessions:
            _sessions[session_id] = SessionState()
        return _sessions[session_id]

    def set_mode(self, session_id: str, mode: SessionMode):
        state = self.get_state(session_id)
        state.mode = mode
        _sessions[session_id] = state
        print(f"Session {session_id} mode set to {mode}")

    def clear_history(self, session_id: str):
        # Delegate to utils.prune_history logic or just clear simple map?
        # The main history is in utils.get_session_history using Langchain ChatMessageHistory logic.
        # We need a way to invoke clear on that store.
        from app.utils import store 
        # store is {session_id: ChatMessageHistory}
        if session_id in store:
            store[session_id].clear()
            print(f"History cleared for {session_id}")
            return True
        return False

session_manager = SessionManager()

def get_session_manager():
    return session_manager
