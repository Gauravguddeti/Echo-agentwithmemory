from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import BaseMessage
import time

# Global dictionary to store chat histories: {session_id: InMemoryChatMessageHistory}
store = {}

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

def prune_history(history: InMemoryChatMessageHistory, max_messages: int = 20):
    """
    Keep only the last `max_messages` in the history.
    This is a simple sliding window implementation.
    """
    if len(history.messages) > max_messages:
        # Keep system prompt if it was part of history (usually injected separately, but good to know)
        # For now, we assume simple truncation of oldest messages.
        # Since this is InMemoryChatMessageHistory, we can modify .messages directly or use clear/add.
        # But slicing is safer.
        history.messages = history.messages[-max_messages:]
