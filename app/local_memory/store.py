import os
import json
import uuid
import time
import re
from typing import List, Dict, Optional
from pydantic import BaseModel
from app.local_memory.extractor import extract_and_score
# Import Classifier
from app.local_memory.classifier import get_classifier

# --- Configuration ---
MEMORY_DIR = "memory"
THRESHOLD = 0.1 # Very Permissive

# --- Models ---
class MemoryEntry(BaseModel):
    memory_id: str
    user_id: str
    project_id: str = "default" # General
    type: str # fact, preference, behavior, summary, person, event
    title: Optional[str] = None # Short label
    content: str
    confidence: float
    created_at: str
    last_accessed: str
    tags: List[str]
    # embedding field removed

    def to_dict(self):
        return self.model_dump()

# --- Helper ---
def tokenize(text: str) -> set:
    """Simple tokenizer: lowercase and remove non-alphanumeric."""
    text = text.lower()
    import re
    tokens = re.findall(r'\b\w+\b', text)
    return set(tokens)

# --- Store Class ---
class LocalMemoryStore:
    def __init__(self):
        self._ensure_dir(MEMORY_DIR)
        # Initialize classifier
        self.classifier = get_classifier()

    def _ensure_dir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def _get_user_dir(self, user_id):
        path = os.path.join(MEMORY_DIR, user_id)
        self._ensure_dir(path)
        return path

    def add(self, text: str, user_id: str):
        """
        1. Extract facts from text.
        2. Score importance using DL Model.
        3. Check for conflicts.
        4. Save if important.
        """
        facts = extract_and_score(text)
        
        results = []
        for fact in facts:
            content = fact["content"]
            
            # Phase 2: Use DL Classifier for Importance
            dl_score = self.classifier.predict_importance(content)
            print(f"Memory: '{content}' | DL Importance: {dl_score:.4f}")
            
            # Gating Logic: 
            # We require DL score > THRESHOLD to store.
            # We can also mix with LLM confidence if needed, but Phase 2 goal is "Replace heuristic confidence".
            
            if dl_score >= THRESHOLD:
                # Check for conflicts
                conflict = self._check_conflict(content, user_id)
                
                tags = fact.get("tags", [])
                
                if conflict:
                    print(f"Conflict detected for '{content}' with existing '{conflict.content}'")
                    tags.append("potential_conflict")
                
                # Update confidence to be the DL score for future ranking
                fact["confidence"] = dl_score
                
                entry = self._create_entry(fact, user_id, tags)
                self._save_entry(entry)
                results.append(entry)
            else:
                print(f"Memory discarded due to low importance: '{content}' ({dl_score:.4f})")
                
        return {"results": results}

    def _check_conflict(self, content: str, user_id: str) -> Optional[MemoryEntry]:
        """
        Heuristic check: If new memory has high keyword overlap with existing one,
        it might be an update or conflict.
        Returns the conflicting entry if found.
        """
        tokens = tokenize(content)
        user_dir = self._get_user_dir(user_id)
        files = [f for f in os.listdir(user_dir) if f.endswith(".json")]
        
        best_match = None
        max_overlap = 0.0
        
        for file in files:
            try:
                with open(os.path.join(user_dir, file), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    entry = MemoryEntry(**data)
                    
                    entry_tokens = tokenize(entry.content)
                    if not entry_tokens: continue
                    
                    # Jaccard overlap
                    intersection = tokens.intersection(entry_tokens)
                    union = tokens.union(entry_tokens)
                    score = len(intersection) / len(union) if union else 0
                    
                    if score > 0.6: # Configurable threshold for "Same Topic"
                        if score > max_overlap:
                            max_overlap = score
                            best_match = entry
            except:
                continue
                
        return best_match

    def _create_entry(self, fact: dict, user_id: str, tags: list) -> MemoryEntry:
        content = fact["content"]
        now = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        
        return MemoryEntry(
            memory_id=str(uuid.uuid4()),
            user_id=user_id,
            project_id="default",
            type=fact.get("type", "fact"),
            title=fact.get("title", "Memory"),
            content=content,
            confidence=fact.get("confidence", 1.0),
            created_at=now,
            last_accessed=now,
            tags=tags
        )

    def _save_entry(self, entry: MemoryEntry):
        user_dir = self._get_user_dir(entry.user_id)
        file_path = os.path.join(user_dir, f"{entry.memory_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(entry.to_dict(), f, indent=2)
        print(f"Saved memory {entry.memory_id} to {file_path}")

    def search(self, query: str, user_id: str, limit: int = 5):
        """
        Keyword-based search with Decay and Confidence scoring.
        Formula: Score = (Jaccard * W1) + (Recency * W2) + (Confidence * W3)
        """
        user_dir = self._get_user_dir(user_id)
        files = [f for f in os.listdir(user_dir) if f.endswith(".json")]
        
        if not files:
            return []
            
        query_tokens = tokenize(query)
        if not query_tokens:
            return []
        
        results = []
        now_ts = time.time()
        
        # Weights
        W1_REL = 0.5
        W2_REC = 0.3
        W3_CONF = 0.2
        DECAY_RATE = 0.01 # Hourly decay rate
        
        for file in files:
            try:
                with open(os.path.join(user_dir, file), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    entry = MemoryEntry(**data)
                    
                    # 1. Relevance (Jaccard)
                    content_tokens = tokenize(entry.content)
                    # Include tags in token set for better recall
                    for tag in entry.tags:
                        content_tokens.update(tokenize(tag))
                        
                    intersection = query_tokens.intersection(content_tokens)
                    union = query_tokens.union(content_tokens)
                    
                    # Don't skip on zero intersection - let DL reranker handle semantic matches
                    # Just give a low jaccard score
                    jaccard = len(intersection) / len(union) if union else 0
                    
                    # 2. Recency (Time Decay)
                    try:
                        # Parse ISO format. Simple fallback if robust parsing needed.
                        # Assuming 'created_at' is generated by time.strftime("%Y-%m-%dT%H:%M:%S%z")
                        # We need a robust parser.
                        # For now, let's assume we can parse or fallback to file mtime.
                        # Actually, let's use file mtime for simplicity in this phase if parsing fails,
                        # or just improve creation to store timestamp float.
                        # Let's try parsing.
                        import datetime
                        try:
                            created_dt = datetime.datetime.strptime(entry.created_at, "%Y-%m-%dT%H:%M:%S%z")
                            created_ts = created_dt.timestamp()
                        except:
                            # Fallback pattern if timezone parsing fails (Windows sometimes weird with %z)
                            # Or just use current time if fail (penalty).
                             created_ts = now_ts - 86400 # Treat as 1 day old if fail
                        
                        hours_old = (now_ts - created_ts) / 3600
                        if hours_old < 0: hours_old = 0
                        
                        recency_score = 1 / (1 + DECAY_RATE * hours_old)
                    except:
                        recency_score = 0.5 # Neutral fallback
                        
                    # 3. Confidence
                    confidence_score = entry.confidence
                    
                    # Final Score
                    final_score = (jaccard * W1_REL) + (recency_score * W2_REC) + (confidence_score * W3_CONF)
                    
                    results.append((final_score, entry))
            except Exception as e:
                print(f"Error reading memory file {file}: {e}")
                
        # Phase 3: Reranking
        # Sort results by heuristic score DESC before slicing! (Fix for bug)
        results.sort(key=lambda x: x[0], reverse=True)
        
        # 1. Fetch top N candidates (heuristic)
        # Increase limit to ensuring semantic matches (which might have low Jaccard) get reranked
        heuristic_limit = max(limit * 10, 50) 
        candidates = results[:heuristic_limit]
        
        if not candidates:
            return []
            
        # 2. Extract contents for reranking
        candidate_texts = [entry.content for _, entry in candidates]
        
        # 3. Rerank
        print(f"Reranking {len(candidates)} memories for query: '{query}'")
        reranked_scores = self.classifier.rerank(query, candidate_texts)
        
        # 4. Map back to entries
        # rerank returns [(score, text), ...]
        # We need to map text back to entry. 
        # Limitation: duplicate texts? Assuming content is unique enough or we just match first.
        # Better: Pass entries to rerank? Or just map by index if rerank preserves order? 
        # CrossEncoder.predict preserves order of input pairs.
        
        # Let's do it manually using predict() on the entries directly to keep entry ref
        final_results = []
        for i, (h_score, entry) in enumerate(candidates):
            # Calculate DL Relevance Score
            dl_score = self.classifier.predict(query, entry.content)
            
            # Weighted Final Score? Or Pure DL?
            # Goal is "Recall Quality", DL is usually much better than Jaccard.
            # Let's trust DL score heavily, maybe keep recency boost?
            # Mixed: 80% DL, 20% Recency?
            # For now, let's use Pure DL Score as the primary sort key.
            
            final_results.append((dl_score, entry))
            
        # Sort by DL Score
        final_results.sort(key=lambda x: x[0], reverse=True)
        
        top_k = final_results[:limit]
        
        output = []
        for score, entry in top_k:
            output.append({
                "memory": entry.content,
                "score": float(score), # Convert numpy float
                "id": entry.memory_id,
                "created_at": entry.created_at,
                "tags": entry.tags
            })
            
        return output

    def get_all_memories(self, user_id: str) -> List[dict]:
        """
        Retrieves all memories for a user.
        """
        user_dir = self._get_user_dir(user_id)
        files = [f for f in os.listdir(user_dir) if f.endswith(".json")]
        
        memories = []
        for file in files:
            try:
                with open(os.path.join(user_dir, file), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    memories.append(data)
            except:
                continue
                
        # Sort by creation desc
        memories.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return memories

    def delete_memory(self, memory_id: str, user_id: str) -> bool:
        """
        Deletes a specific memory by ID.
        """
        user_dir = self._get_user_dir(user_id)
        file_path = os.path.join(user_dir, f"{memory_id}.json")
        
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Deleted memory: {memory_id}")
                return True
            except Exception as e:
                print(f"Error deleting memory: {e}")
                return False
        return False

    def delete_all(self, user_id: str) -> int:
        """Wipes all memories for a user."""
        user_dir = self._get_user_dir(user_id)
        files = [f for f in os.listdir(user_dir) if f.endswith(".json")]
        count = 0
        for f in files:
            try:
                os.remove(os.path.join(user_dir, f))
                count += 1
            except: pass
        print(f"Deleted {count} memories for {user_id}")
        return count

    def delete_batch(self, memory_ids: List[str], user_id: str) -> int:
        count = 0
        for mid in memory_ids:
            if self.delete_memory(mid, user_id):
                count += 1
        return count
