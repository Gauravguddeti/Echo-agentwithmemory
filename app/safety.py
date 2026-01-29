from app.local_memory.classifier import get_classifier

class SafetyMonitor:
    def __init__(self):
        self.classifier = get_classifier()

    def check_safety(self, query: str, response: str, memory_context: str) -> str:
        """
        Checks if the response is grounded in the memory context for personal queries.
        Returns the original response or a hedged version.
        """
        # 1. Heuristic: Is this a personal query?
        is_personal = any(w in query.lower() for w in ["my ", "i ", "me ", "mine"])
        
        if not is_personal or not memory_context:
            return response

        # 2. DL Check: Is the response supported by memory?
        # We treat 'memory_context' as the Query (Ground Truth) and 'response' as the Document to check relevance against.
        # "Does this memory support this response?"
        
        # CrossEncoder(Query, Document) -> Score.
        # Query = Memory Context
        # Document = Response
        score = self.classifier.predict(memory_context, response)
        
        print(f"Safety Check | Score: {score:.4f} | Personal: {is_personal}")
        
        if score < 0.4: # Low support
            return f"{response}\n\n(Note: I'm answering based on general knowledge, as I don't have a specific memory of this.)"
            
        return response

safety_monitor = SafetyMonitor()

def get_safety_monitor():
    return safety_monitor
