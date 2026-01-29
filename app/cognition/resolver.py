from .schema import StructuredIntent
from .context import SessionContext

class IntentResolver:
    def __init__(self):
        self.pronouns = ["it", "this", "that", "him", "her", "them"]

    def resolve(self, intent: StructuredIntent, context: SessionContext) -> StructuredIntent:
        """
        Resolves pronouns in the intent's target or params using context.
        """
        resolved_intent = intent # Mutable or Copy? Let's treat as mutable for now.
        
        # Check params for pronouns
        # e.g. Browser Search Query
        if "query" in intent.params:
            q = intent.params["query"].lower().split()
            new_q = []
            replaced = False
            for word in q:
                if word in self.pronouns:
                    # Resolve!
                    if context.active_entities:
                        new_q.append(context.active_entities[0]) # Use most recent
                        replaced = True
                    else:
                        new_q.append(word) # Keep if no context
                else:
                    new_q.append(word)
            
            if replaced:
                intent.params["query"] = " ".join(new_q)
                intent.confidence += 0.1 # Boost confidence
                print(f"[Resolver] Resolved query: {intent.params['query']}")

        # e.g. Browser Nav URL/Target
        # "take me to it" -> goal=browser_nav, target="it" (or url="it")
        if "url" in intent.params:
            url_target = intent.params["url"]
            if url_target in self.pronouns:
                 if context.active_entities:
                      entity = context.active_entities[0]
                      intent.params["url"] = entity
                      print(f"[Resolver] Resolved URL target: {entity}")

        # Filesystem Context (New Safety)
        if intent.goal == "filesystem":
             # "delete it", "remove that folder"
             # Check if target or name param is a pronoun
             target_name = intent.params.get("name")
             if target_name in self.pronouns or intent.target in self.pronouns:
                  # Look for recent PATHS in entities
                  # We assume active_entities might hold paths if we tracked FS actions
                  # Context currently tracks generic entities.
                  # Logic: If entity looks like a path or was used in recent FS action? 
                  # For now: Swap with last entity, Decider checks existence.
                  if context.active_entities:
                       candidate = context.active_entities[0]
                       if target_name in self.pronouns:
                            intent.params["name"] = candidate
                       if intent.target in self.pronouns:
                            intent.target = candidate
                       print(f"[Resolver] Resolved FS target: {candidate}")

        # Generic App/Write Resolution
        # "Write to it", "Open it"
        # If target is pronoun and NOT handled above
        if intent.goal in ["desktop_write", "open_app"]:
             if intent.target in self.pronouns:
                  if context.active_entities:
                       # Prefer entities that look like Apps?
                       # Or just use most recent.
                       candidate = context.active_entities[0]
                       intent.target = candidate
                       print(f"[Resolver] Resolved App target: {candidate}")

        # Referencing Resolution (Phase 11)
        # "note what i said"
        if intent.params.get("text") == "__LAST_USER_MESSAGE__":
             # Get last user query from context
             last_msg = context.last_user_query
             if last_msg:
                  intent.params["text"] = last_msg
                  print(f"[Resolver] Resolved Last Message: {last_msg}")
             else:
                  intent.params["text"] = "" # Empty fallback

        return intent
