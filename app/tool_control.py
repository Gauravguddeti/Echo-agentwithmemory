import re
from app.tools import calculate, search_web

class ToolController:
    def __init__(self):
        pass

    def get_tool_result(self, query: str) -> str:
        """
        Determines if a tool should be used, executes it, and returns the result string.
        Returns None if no tool is eligible.
        """
        query_lower = query.lower()
        
        # 1. Calculator Check
        # Rule: Must contain digits AND operators
        if re.search(r'\d', query) and re.search(r'[+\-*/]', query):
            # Extract expression heuristics?
            # Simple check: If it looks like a math problem "What is 2 + 2"
            # Cleanup: Remove "What is", "?", etc. logic could be complex.
            # Simplified: Use regex to extract math part?
            # Or just pass the whole thing if we are careful?
            # Better: Only if high density of math chars.
            
            # Let's try extracting the expression roughly
            expression = re.sub(r'[a-zA-Z?]', '', query).strip()
            if len(expression) > 2: # "2+2" is 3 chars
                print(f"Tool Triggered: Calculator ('{expression}')")
                return f"Calculator Result: {calculate(expression)}"

        # 2. Web Search Check
        # Rule: Explicit intent like "news", "weather", "latest", "price"
        search_triggers = ["news", "weather", "latest", "current price", "stock", "who is"]
        # "Who is" is broad, but let's include it for testing "Who is president..."
        # Maybe limit "Who is" to meaningful entities?
        
        if any(trigger in query_lower for trigger in search_triggers):
            # Exclude personal "Who is" like "Who is my brother?" -> Memory handles that.
            if "my " not in query_lower:
                print(f"Tool Triggered: Web Search ('{query}')")
                # Search tools often fail on broad queries, but let's try.
                return f"Web Search Result:\n{search_web(query)}"
                
        return None

tool_controller = ToolController()

def get_tool_controller():
    return tool_controller
