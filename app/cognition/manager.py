from .context import context_manager
from .interpreter import interpreter
from .planner import planner, CognitivePlan
from .validator import validator
from app.memory_client import get_memories
import asyncio

# User ID constant (single user mode)
USER_ID = "default_user"

class CognitiveEngine:
    def __init__(self):
        pass

    async def process(self, session_id: str, message: str, llm) -> CognitivePlan:
        # 1. Interpret / Reason (Phase 17: LLM-First NLU)
        from app.cognition.reasoner import get_reasoner
        reasoner = get_reasoner()
        
        # Use Reasoner for high-level understanding
        intent_data = await reasoner.reason(message)
        print(f"[Cognition] Reasoning: Intent={intent_data.intent_type}, Tool={intent_data.suggested_tool}, Conf={intent_data.confidence}")
        
        # 2. Get Context
        ctx = context_manager.get_context(session_id)
        
        # 3. Memory Recall (Phase 11 Integration)
        # Fetch relevant memories and inject into planning context
        memory_context = ""
        try:
            memory_context = get_memories(message, USER_ID)
            if memory_context:
                print(f"[Cognition] Memory Recall: Found relevant memories")
                # Add memory to context dict for planner
                ctx.memories = memory_context
            else:
                ctx.memories = ""
        except Exception as e:
            print(f"[Cognition] Memory Recall Failed: {e}")
            ctx.memories = ""
            
        # Add reasoned intent to context for planner
        ctx.reasoning = intent_data.reasoning
        ctx.suggested_tool = intent_data.suggested_tool
        
        # 4. Planning Loop (Perception)
        # Attempt 1
        plan = await planner.plan(message, ctx)
        print(f"[Cognition] Plan Pass 1: Intent={plan.intent}, Steps={len(plan.steps)}")
        
        # Check for Perception Request
        if plan.steps and plan.steps[0].tool == "screen_perception":
             print("[Cognition] Perception Requested. Analyzing Screen...")
             from app.perception.ocr import perception
             try:
                 screen_data = await perception.analyze()
                 print(f"[Cognition] Perception Result: {screen_data['active_app']} ({len(screen_data['visible_text'])} lines)")
                 
                 # Augment Context
                 ctx.screen = screen_data
                 
                 # Re-Plan
                 plan = await planner.plan(message, ctx)
                 print(f"[Cognition] Plan Pass 2 (Post-Perception): Intent={plan.intent}")
                 
             except Exception as e:
                 print(f"[Cognition] Perception Failed: {e}")
        
        # 5. Validate
        valid_plan = validator.validate(plan)
        if valid_plan.ask_user:
             print(f"[Cognition] Validation Triggered Clarification: {valid_plan.clarification_question}")
        
        # 6. Update Context for future reference (Phase 3 - Context Awareness)
        # Extract entities from message and plan for pronoun resolution
        entities = []
        if plan.steps:
            for step in plan.steps:
                if step.params.get("path"):
                    entities.append(step.params["path"])
                if step.params.get("name"):
                    entities.append(step.params["name"])
        
        context_manager.update(
            session_id,
            query=message,
            entities=entities if entities else None,
            intent=plan.intent
        )
             
        return valid_plan

engine = CognitiveEngine()
