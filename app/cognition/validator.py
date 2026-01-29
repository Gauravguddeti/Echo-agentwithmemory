from app.cognition.planner import CognitivePlan, PlanStep
import re
import os

class PlanValidator:
    def validate(self, plan: CognitivePlan) -> CognitivePlan:
        """
        Validates the plan against safety and sanity rules.
        If validation fails, modifies the plan to ask for clarification.
        """
        if plan.ask_user:
            return plan

        for step in plan.steps:
            if not self._validate_step(step):
                # Invalidate plan
                plan.ask_user = True
                plan.clarification_question = f"I found an issue with the step: {step.description}. Can you clarify?"
                plan.steps = [] # clear execution
                return plan
        
        return plan

    def _validate_step(self, step: PlanStep) -> bool:
        if step.tool == "create_file" or step.tool == "write_file":
            path = step.params.get("path") or step.params.get("target_file")
            if not path: return False
            
            # 1. Filename Quality Check
            filename = os.path.basename(path)
            if len(filename) > 50: # Rule: No sentences as filenames
                return False
            
            if re.search(r'[<>"/\\|?*]', filename):
                # Invalid Windows filename characters found
                return False

        if step.tool == "delete_file":
            path = step.params.get("path")
            if path in ["C:\\", "D:\\", "/"]:
                return False # Safety
                
        return True

validator = PlanValidator()
