from app.memory_client import add_memory
import re

class LearningController:
    def __init__(self):
        pass

    def detect_feedback_intent(self, message: str) -> str:
        """
        Classifies message as 'NEGATIVE', 'POSITIVE', or 'NEUTRAL'.
        """
        msg_lower = message.lower().strip()
        
        # Negative patterns
        neg_patterns = [
            r"^no\b", r"^wrong\b", r"that'?s wrong", r"incorrect", 
            r"not true", r"stop", r"actually,"
        ]
        if any(re.search(p, msg_lower) for p in neg_patterns):
            return "NEGATIVE"
            
        # Positive patterns (Reinforcement)
        pos_patterns = [
            r"^yes\b", r"^correct", r"exactly", r"that'?s right", 
            r"good job", r"perfect"
        ]
        if any(re.search(p, msg_lower) for p in pos_patterns):
            return "POSITIVE"
            
        return "NEUTRAL"

    def process_feedback(self, user_id: str, message: str, last_ai_message: str) -> dict:
        """
        Reacts to feedback. 
        Returns a dict with 'action' and 'tags' if meaningful feedback detected.
        """
        intent = self.detect_feedback_intent(message)
        
        if intent == "NEGATIVE":
            print(f"Negative feedback detected from user {user_id}")
            # Identify this as a correction.
            # We return instructions to the caller (chat.py) to tag this memory specially.
            return {
                "action": "correction",
                "tags": ["correction", "high_importance"]
            }

        elif intent == "POSITIVE":
            return {
                "action": "reinforcement",
                "tags": ["positive_feedback"]
            }
            
        return None

learning_controller = LearningController()

def get_learning_controller():
    return learning_controller
