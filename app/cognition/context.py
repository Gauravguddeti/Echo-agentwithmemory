from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field

@dataclass
class SessionContext:
    session_id: str
    last_user_query: str = ""
    last_ai_response: str = ""
    active_entities: List[str] = field(default_factory=list) # ["shroud", "notepad"]
    last_intent: Optional[str] = None # "browser_search"
    memories: str = ""  # Long-term memory context
    screen: Optional[Dict[str, Any]] = None  # Screen perception data
    reasoning: str = "" # NLU Reasoning
    suggested_tool: Optional[str] = None # Reasoner suggestion

class ContextManager:
    def __init__(self):
        self._sessions: Dict[str, SessionContext] = {}

    def get_context(self, session_id: str) -> SessionContext:
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionContext(session_id=session_id)
        return self._sessions[session_id]

    def update(self, session_id: str, query: str = None, entities: List[str] = None, intent: str = None):
        ctx = self.get_context(session_id)
        if query:
            ctx.last_user_query = query
        if entities:
            # Add new entities to the front (most recent)
            # Filter duplicates to keep history clean
            for e in entities:
                if e in ctx.active_entities:
                    ctx.active_entities.remove(e)
                ctx.active_entities.insert(0, e)
            # Keep size manageable
            ctx.active_entities = ctx.active_entities[:5]
        if intent:
            ctx.last_intent = intent

# Singleton
context_manager = ContextManager()
