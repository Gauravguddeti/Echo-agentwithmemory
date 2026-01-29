import re

class CommandNormalizer:
    def __init__(self):
        # 1. Fillers to strip (keep it safe)
        self.fillers = [
            r"\bcan you\b", r"\bplease\b", r"\bpls\b", r"\bplz\b", 
            r"\bbrev\b", r"\bbro\b", r"\bbruh\b", r"\bmy G\b", 
            r"\byo\b", r"\bumm\b", r"\buh\b", r"\bjust\b", 
            r"\bhey\b", r"\bhi\b", r"\bokay\b", r"\bok\b"
        ]
        
        # 2. Semantic expansions (Intent Mapping)
        self.semantics = {
            r"i need maths": "open calculator",
            r"i need to calculate": "open calculator",
            r"do some math": "open calculator",
            r"lets meet": "open zoom",
            r"got a meeting": "open zoom",
            r"open calc\b": "open calculator", # Expansion
            r"open calci\b": "open calculator",
            r"open pdf": "open pdf file", # Clarification
            r"open doc": "open document",
        }

    def normalize(self, text: str) -> str:
        """
        Canonicalizes user input for cleaner intent detection.
        1. Strip fillers.
        2. Apply semantic maps.
        3. Whitespace cleanup.
        """
        clean_text = text.lower()
        
        # 1. Strip fillers
        for pattern in self.fillers:
            clean_text = re.sub(pattern, "", clean_text)
            
        # 2. Semantic Mapping
        # Check explicit phrase mappings first
        for pattern, replacement in self.semantics.items():
            if re.search(pattern, clean_text):
                clean_text = re.sub(pattern, replacement, clean_text)
                
        # 3. Cleanup
        clean_text = clean_text.strip()
        clean_text = re.sub(r"\s+", " ", clean_text)
        
        return clean_text

normalizer = CommandNormalizer()

def get_normalizer():
    return normalizer
