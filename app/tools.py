from duckduckgo_search import DDGS
import math

def calculate(expression: str) -> str:
    """
    Evaluates a math expression safely (limited scope).
    """
    allowed_names = {"math": math, "abs": abs, "round": round, "min": min, "max": max}
    try:
        # Very meaningful security risk if unrestricted. 
        # For this phase, we assume input is filtered by Controller to contain mostly numbers/operators.
        # Use a restricted namespace.
        result = eval(expression, {"__builtins__": None}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Error: {e}"

def search_web(query: str, max_results=2) -> str:
    """
    Searches DuckDuckGo and returns summaries.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            if not results:
                return "No results found."
            
            summary = []
            for r in results:
                summary.append(f"- {r['title']}: {r['body']}")
            return "\n".join(summary)
    except Exception as e:
        return f"Search Error: {e}"
