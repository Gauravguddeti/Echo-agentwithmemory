import re
from typing import List
from .schema import Chunk, ChunkType, StructuredIntent

class SemanticParser:
    def __init__(self):
        # Cache patterns
        self.fillers = r"^(can you|can ya|could you|please|just|kindly|hey|yo|bro|brev|mate|sir|ok|okay|so|now|then|well|uh|um|take a|do a|make a)"
        
        self.actions = {
            "open": ["open", "launch", "start", "run", "access"],
            "search": ["search", "find", "look up", "google", "bing", "ask"],
            "write": ["write", "type", "jot", "note", "add", "fill", "log"],
            "navigate": ["go to", "navigate to", "visit", "browse to", "take me to", "open url"],
            "click": ["click", "press", "hit", "select"]
        }
        
        # Inverted index for fast lookup
        self.action_map = {}
        for safe_key, variants in self.actions.items():
            for v in variants:
                self.action_map[v] = safe_key

        self.objects = {
            "notepad": ["notepad", "note", "notes", "text editor", "untitled"],
            "calculator": ["calculator", "calc"],
            "google": ["google"],
            "youtube": ["youtube", "yt", "tube"],
            "browser": ["browser", "chrome", "edge", "brave", "firefox", "internet"]
        }
        
        self.prepositions = ["in", "on", "into", "to", "for", "with", "at", "using"]

    def _tokenize(self, text: str) -> List[str]:
        # Simple whitespace tokenizer preserving strict sequence for now
        # Ideally we process phrases.
        return text.split()

    def chunk_text(self, text: str) -> List[Chunk]:
        """
        Transforms raw text into semantic chunks.
        """
        clean_text = text.lower().strip()
        chunks = []
        
        # 1. Strip Fillers (Repeatedly from start)
        while True:
            match = re.match(self.fillers, clean_text, re.IGNORECASE)
            if match:
                chunks.append(Chunk(text=match.group(0), type=ChunkType.FILLER))
                clean_text = clean_text[len(match.group(0)):].strip()
            else:
                break
                
        # 2. Identify Primary Action
        # We look for the longest matching action phrase at the start
        # "take me to" vs "take"
        action_found = None
        best_len = 0
        
        for variant in self.action_map.keys():
            if clean_text.startswith(variant):
                if len(variant) > best_len:
                    action_found = variant
                    best_len = len(variant)
        
        if action_found:
            chunks.append(Chunk(text=action_found, type=ChunkType.ACTION))
            clean_text = clean_text[len(action_found):].strip()
        else:
            # Maybe the action is implied? Or user didn't start with action.
            # "notepad open" (unlikely in English but possible)
            pass

        # 3. Parse remaining as Object/Target/Prep
        # This is where it gets tricky. "google mr beast" -> Object: Google, Target: Mr beast?
        # "open notepad" -> Object: Notepad.
        
        # Naive approach: Scan tokens.
        # Ideally we assume: [Action] [Object] [Prep] [Target] OR [Action] [Target] [Prep] [Object]
        
        # Let's just consume the rest and classify known objects.
        
        remaining = clean_text
        
        # Check for prepositions splitting the sentence
        # "write hello in notepad" -> [write] "hello" [in] "notepad"
        
        split_prep = None
        split_idx = -1
        
        for prep in self.prepositions:
            # Check " in " padding
            pattern = f" {prep} "
            if pattern in " " + remaining + " ":
                split_prep = prep
                # Find index
                idx = (" " + remaining + " ").index(pattern)
                # Adjust for padding
                split_idx = idx
                break
        
        if split_prep:
            part1 = remaining[:split_idx].strip()
            part2 = remaining[split_idx+len(split_prep):].strip() # +2 for spaces? No our logic is rough
            # Use split logic properly
            parts = remaining.split(f" {split_prep} ", 1)
            
            if parts[0]:
                chunks.append(Chunk(text=parts[0], type=ChunkType.TARGET)) # Assume target first? "write X"
            
            chunks.append(Chunk(text=split_prep, type=ChunkType.PREPOSITION))
            
            if len(parts) > 1:
                # Classify part 2
                is_obj = False
                for obj_key, variants in self.objects.items():
                    if parts[1] in variants:
                         chunks.append(Chunk(text=parts[1], type=ChunkType.OBJECT))
                         is_obj = True
                         break
                if not is_obj:
                     chunks.append(Chunk(text=parts[1], type=ChunkType.TARGET))
        else:
            # No preposition. "open notepad", "search google"
            # Check if remaining matches an object
            is_obj = False
            for obj_key, variants in self.objects.items():
                if remaining == obj_key or remaining in variants:
                        chunks.append(Chunk(text=remaining, type=ChunkType.OBJECT))
                        is_obj = True
                        break
            
            if not is_obj and remaining:
                 chunks.append(Chunk(text=remaining, type=ChunkType.TARGET))

        return chunks

    def split_compound_intent(self, text: str) -> List[str]:
        # Simple heuristic split by "and", "then"
        # Avoid splitting parameters? e.g. "write A and B"
        # For now, strict keyword split is risky but requested.
        # "open youtube and search X" -> "open youtube", "search X"
        
        # Normalize
        clean = text.lower()
        
        # Protected split?
        # Let's split by " and " (padding important)
        segments = []
        
        # Splitters
        for splitter in [" and ", " then ", " also "]:
             if splitter in clean:
                  # Naive split
                  # "write mom and dad" -> "write mom", "dad" (bad)
                  # "open notepad and write boolean" -> YES
                  # Rule: Split only if right side has a verb?
                  
                  # Let's rely on the prompt's examples: "open youtube and write..."
                  # We will return the naive split for Phase 10 validation.
                  # The Decider/Semantic parser will fail to find an action in "dad" and treat it likely as invalid/chat.
                  return clean.split(splitter)

        return [text]

    def infer_goal(self, chunks: List[Chunk], original_text: str) -> StructuredIntent:
        """
        Maps chunks to a StructuredIntent.
        """
        action = None
        obj = None
        target = None
        
        for c in chunks:
            if c.type == ChunkType.ACTION:
                action = self.action_map.get(c.text, c.text) # Map "jot" -> "write"
            elif c.type == ChunkType.OBJECT:
                # Map concrete object name e.g. "calc" -> "calculator"
                found = False
                for key, variants in self.objects.items():
                    if c.text in variants:
                        obj = key
                        found = True
                        break
                if not found:
                    obj = c.text
            elif c.type == ChunkType.TARGET:
                # Accumulate target?
                if target:
                    target += " " + c.text
                else:
                    target = c.text

        # 0. Greetings / Chat (Conversation First)
        # If text is JUST fillers/greetings, return chat.
        # "yo", "hi", "what up", "thanks"
        clean = original_text.lower().strip()
        greetings = ["yo", "hi", "hello", "hey", "sup", "what's up", "whats up", "thanks", "thx", "cool", "damn", "lol", "lmao", "wow", "ok", "bet", "great"]
        if clean in greetings or (len(chunks) == 1 and chunks[0].type == ChunkType.FILLER):
             return StructuredIntent(goal="chat", target="", confidence=1.0, original_text=original_text, style="casual")

        # Rules Engine
        
        # 1. Desktop Write
        if action == "write":
            if obj in ["notepad", "text editor"]:
                 return StructuredIntent(goal="desktop_write", target="notepad", params={"text": target}, confidence=0.9, original_text=original_text)
            
            # Generic Write (e.g. "Write X to it")
            # If we have a target message, and maybe an object that wasn't matched (stored in chunks?)
            # Simplified: If action is write, and we have SOME target text.
            if target:
                 # Check if the "target" contains the app name or pronoun at the end?
                 # Naive: If "it" is in chunks?
                 # Let's trust the Resolver.
                 # If explicit "note" logic didn't hit.
                 return StructuredIntent(goal="desktop_write", target="it", params={"text": target}, confidence=0.7, original_text=original_text)

        # 2. Browser Search
        if action == "search":
            if obj == "youtube":
                return StructuredIntent(goal="browser_search", target="youtube", params={"query": target or obj}, confidence=0.95, original_text=original_text)
            if obj == "google" or not obj:
                # "search X" -> obj=None, target=X -> Google
                return StructuredIntent(goal="browser_search", target="google", params={"query": target or obj}, confidence=0.9, original_text=original_text)

        # 3. Browser Nav
        if action == "navigate":
            return StructuredIntent(goal="browser_nav", target="browser", params={"url": target}, confidence=0.95, original_text=original_text)

        # 4. Open App
        if action == "open":
            if obj:
                 return StructuredIntent(goal="open_app", target=obj, confidence=0.9, original_text=original_text)
            if target:
                 return StructuredIntent(goal="open_app", target=target, confidence=0.8, original_text=original_text)

        # 5. Filesystem (Create Folder)
        # "create a folder", "make directory"
        if "folder" in original_text or "directory" in original_text:
             if "create" in original_text or "make" in original_text or "new" in original_text:
                 # Infer params
                 name = None
                 path = None # Default CWD
                 
                 # Preposition splitting "folder named X in Y"
                 # Semantic chunker handles this roughly, but target might be "X in Y"
                 
                 clean_target = target
                 
                 # Check for explicit path preposition
                 for prep in [" in ", " at ", " on "]:
                      if prep in original_text: # Check original text to find path arg
                           # This is tricky without advanced parsing.
                           # Simple heuristic: Split clean_target if it has prep?
                           if clean_target and prep in clean_target:
                                parts = clean_target.split(prep)
                                clean_target = parts[0].strip() # Name
                                path = parts[1].strip() # Path
                                break
                 
                 if clean_target:
                      # Canonicalize Name
                      for filler in ["named", "called", "label", "titled", "me a", "a new", "a"]:
                           clean_target = clean_target.replace(filler, "").strip()
                      
                      # Final check: Is it too long? Sentence detection?
                      if len(clean_target.split()) > 4:
                           # Too long, likely a sentence.
                           name = None
                      else:
                           name = clean_target if clean_target else None

                 return StructuredIntent(goal="filesystem", target="create_folder", params={"name": name, "path": path}, confidence=0.85, original_text=original_text)

        # 5b. Filesystem (Delete)
        if "delete" in original_text or "remove" in original_text:
             # "delete test folder"
             clean_target = target
             if clean_target:
                  for filler in ["folder", "file", "directory", "the", "that", "this"]:
                       clean_target = clean_target.replace(filler, "").strip()
             
             name = clean_target if clean_target else target # Fallback
             return StructuredIntent(goal="filesystem", target="delete_item", params={"name": name}, confidence=0.85, original_text=original_text)

        # 5c. Filesystem (Create File)
        # "create a file", "make a file"
        if "file" in original_text:
             if "create" in original_text or "make" in original_text or "new" in original_text:
                 # Infer params
                 name = None
                 path = None
                 if target:
                      clean_target = target
                      for filler in ["named", "called", "label", "titled", "me a", "a new", "a"]:
                           clean_target = clean_target.replace(filler, "").strip()
                      # Preposition split for file? "file named X in Y"
                      # Reuse logic? For now simple.
                      name = clean_target
                 return StructuredIntent(goal="filesystem", target="create_file", params={"name": name}, confidence=0.85, original_text=original_text)

        # 6. Fallback / Click
        if action == "click":
             return StructuredIntent(goal="browser_click", target=target, confidence=0.3, original_text=original_text)

        # 7. Implicit "Take a note"
        # Expanded for "taking notes" and "note what I said"
        if "take" in original_text.lower() and ("note" in original_text.lower() or "notes" in original_text.lower()) or "jot" in original_text.lower() or ("note" in original_text.lower() and ("that" in original_text.lower() or "this" in original_text.lower())):
             
             clean = original_text.replace("take a note", "").replace("start taking notes", "").replace("jot down", "").replace("note that", "").replace("note this", "").strip()
             
             # Check for "what i said" / "what i told"
             if "what i said" in original_text or "what i told" in original_text:
                  return StructuredIntent(goal="desktop_write", target="notepad", params={"text": "__LAST_USER_MESSAGE__"}, confidence=0.9, original_text=original_text)
                  
             if not clean:
                  # If empty after stripping, maybe it's just "take a note" -> Open Notepad
                  return StructuredIntent(goal="desktop_write", target="notepad", params={"text": ""}, confidence=0.85, original_text=original_text)

             return StructuredIntent(goal="desktop_write", target="notepad", params={"text": clean}, confidence=0.85, original_text=original_text)

        return StructuredIntent(goal="unknown", target="", confidence=0.0, original_text=original_text)

semantic_parser = SemanticParser()
