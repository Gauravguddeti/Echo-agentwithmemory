# from mem0 import MemoryClient
# from app.config import settings
from app.local_memory.store import LocalMemoryStore

# Initialize Memory Client
# We use LocalMemoryStore for privacy and open-source compatibility
# memory_client = MemoryClient(api_key=settings.mem0_api_key)
memory_client = LocalMemoryStore()

def add_memory(messages: list, user_id: str):
    """
    Adds messages to Local memory.
    This function is intended to be run in a background task.
    """
    try:
        # For local store, we just need the text conversation to extract facts from.
        # Construct a single text blob representing the interaction.
        interaction_text = ""
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            interaction_text += f"{role}: {content}\n"
            
        print(f"Adding memory for user {user_id}...")
        result = memory_client.add(interaction_text, user_id=user_id)
        print(f"Memory added successfully: {result}")
    except Exception as e:
        print(f"Error adding memory: {e}")

def get_memories(query: str, user_id: str) -> str:
    """
    Retrieves relevant memories for a given query and user.
    Returns a formatted string of memories.
    """
    try:
        print(f"Searching memories for user {user_id} with query: {query}")
        
        # Use local search
        results = memory_client.search(query, user_id=user_id, limit=5)
        
        memories = []
        # Local store returns list of dicts with 'memory' key
        for item in results:
            mem_text = item.get("memory")
            if mem_text:
                memories.append(f"- {mem_text}")
        
        if not memories:
            return ""
            
        return "\n".join(memories)
    except Exception as e:
        print(f"Error retrieving memories: {e}")
        return ""
