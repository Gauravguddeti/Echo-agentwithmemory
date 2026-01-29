from pydantic import BaseModel, Field
from typing import Optional

class AppSlots(BaseModel):
    intent: str # "open_app" or "none"
    app_name: Optional[str] = None

class AppIntentController:
    def __init__(self):
        pass

    def classify(self, message: str) -> AppSlots:
        """
        Simple keyword heuristic + Registry Lookup to detecting App Intent.
        Avoiding full LLM overhead if possible, or use hybrid.
        """
        with open("app_debug.log", "a") as f:
            f.write(f"Classifying: {message}\n")
            
        msg_lower = message.lower()
        
        # Keyword triggers
        triggers = ["open", "launch", "start", "run"]
        if not any(t in msg_lower for t in triggers):
             return AppSlots(intent="none")
             
        # Extract potential name
        # "Open Calculator" -> "Calculator"
        # "Run VS Code" -> "VS Code"
        
        for t in triggers:
            if t in msg_lower:
                # Naive cleanup: "Open [REST]"
                # This logic is fragile without LLM.
                # But let's try strict prefix cleanup.
                
                # Check if it looks like an app in registry?
                # We can use the registry to validate?
                
                # Let's extract the "Target" string roughly
                # split by trigger, take right side.
                try:
                    # Use msg_lower to split by lowercase trigger
                    target = msg_lower.split(t, 1)[1].strip()
                    # Remove trailing punctuation
                    if target.endswith(".") or target.endswith("?"):
                        target = target[:-1]
                        
                    # Validate against registry before returning!
                    from app.apps.registry import get_app_registry
                    registry = get_app_registry()
                    
                    if registry.resolve(target):
                        result = AppSlots(intent="open_app", app_name=target)
                        with open("app_debug.log", "a") as f:
                            f.write(f"Result (Strict): {result}\n")
                        return result
                    else:
                        # Extracted "calc brev" but not found.
                        # Do NOT return. Let fallback scanner try to find "calc" inside "calc brev".
                        pass
                        
                except Exception as e:
                    pass
        
        # Fallback: Check if any known app name is explicitly mentioned in the message?
        # This requires access to the registry.
        from app.apps.registry import get_app_registry
        registry = get_app_registry()
        
        # We look for explicit known keys. 
        # Sort by length desc to match "visual studio code" before "code".
        known_apps = sorted(registry.apps.keys(), key=len, reverse=True)
        
        for app in known_apps:
            # Simple token check or substring?
            # Substring can be dangerous ("calc" in "calculate").
            # Let's try token based or boundary based.
            # For now, simple presence if it's a multi-word app, or exact word match if single word.
            
            if app in msg_lower:
                # Validation: is it a standalone word?
                import re
                if re.search(r"\b" + re.escape(app) + r"\b", msg_lower):
                     return AppSlots(intent="open_app", app_name=app)

        return AppSlots(intent="none")

app_controller = AppIntentController()

def get_app_controller():
    return app_controller
