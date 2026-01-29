from enum import Enum
import re

class ReasoningType(Enum):
    DIRECT = "DIRECT"
    COMPLEX = "COMPLEX"
    NEEDS_INFO = "NEEDS_INFO"

class ReasoningController:
    def __init__(self):
        pass

    def classify_intent(self, query: str) -> ReasoningType:
        """
        Classifies the user query logic.
        """
        text = query.strip()
        words = text.split()
        
        # 1. Clarification needed? (Very short ambiguous queries)
        if len(words) < 3 and "?" in text:
            # E.g. "Why?", "Who?", "And then?"
            return ReasoningType.NEEDS_INFO
            
        # 2. Multi-step / Complex reasoning?
        # Keywords suggesting complexity
        complex_keywords = [
            "compare", "difference", "plan", "steps", 
            "analyze", "evaluate", "why", "how", 
            "explain", "pros and cons"
        ]
        
        # Conjunctions might imply multi-part (but be careful of simple "and")
        # Regex for "first... then..." or numbered lists?
        
        text_lower = text.lower()
        if any(kw in text_lower for kw in complex_keywords):
            return ReasoningType.COMPLEX
            
        # Check for explicit multi-step indicators
        if " and " in text_lower and " then " in text_lower:
             return ReasoningType.COMPLEX
             
        # 3. Default to Direct
        return ReasoningType.DIRECT

    def check_consistency(self, response: str, memory_context: str) -> bool:
        """
        Lightweight consistency check.
        Returns False if potential contradiction found.
        """
        # Placeholder for deeper logic. 
        # For now, rely on Phase 5 Safety Monitor which hedges.
        # Phase A goal is mostly "Control", so we don't block response yet unless blatant.
        return True

reasoning_controller = ReasoningController()

def get_reasoning_controller():
    return reasoning_controller
