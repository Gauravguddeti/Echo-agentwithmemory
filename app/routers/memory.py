from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.local_memory.store import LocalMemoryStore

router = APIRouter()
store = LocalMemoryStore()

# Helper to get user_id (Single user mode)
USER_ID = "default_user"

@router.get("/memories")
async def list_memories():
    return store.get_all_memories(USER_ID)

@router.delete("/memories/{memory_id}")
async def delete_memory(memory_id: str):
    success = store.delete_memory(memory_id, USER_ID)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"status": "deleted", "id": memory_id}

@router.delete("/memories/query")
async def delete_memory_by_query(q: str = Query(..., min_length=1)):
    """
    Semantic deletion: "forget zoom" -> Search -> Delete top match.
    """
    # 1. Search semantic matches
    results = store.search(q, USER_ID, limit=1)
    
    if not results:
         return {"status": "not_found", "message": f"No memory found for '{q}'"}
    
    top_match = results[0]
    # Threshold check? If score is too low, don't delete blindly.
    if top_match["score"] < 0.4:
        return {"status": "ambiguous", "message": f"I'm not sure which memory you mean by '{q}'."}
        
    # 2. Delete
    mem_id = top_match["id"]
    content = top_match["memory"]
    store.delete_memory(mem_id, USER_ID)
    
    return {"status": "deleted", "id": mem_id, "content": content}

from pydantic import BaseModel
class BatchDeleteRequest(BaseModel):
    ids: List[str]

@router.post("/memories/batch-delete")
async def batch_delete_memories(req: BatchDeleteRequest):
    count = store.delete_batch(req.ids, USER_ID)
    return {"status": "ok", "deleted_count": count}

@router.delete("/memories")
async def delete_all_memories():
    count = store.delete_all(USER_ID)
    return {"status": "ok", "deleted_count": count, "message": "All memories wiped."}
