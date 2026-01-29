from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.dependencies import get_llm

class PlanStep(BaseModel):
    tool: str = Field(description="Tool to use (e.g., 'create_file', 'delete_file', 'memory_save', 'ask_user')")
    params: Dict[str, Any] = Field(description="Parameters for the tool")
    description: str = Field(description="Human readable description of step")

class CognitivePlan(BaseModel):
    intent: str = Field(description="Classified intent (filesystem, memory, chat, unknown)")
    confidence: float
    ask_user: bool = Field(description="True if clarification is needed")
    clarification_question: Optional[str] = Field(default=None, description="Question to ask if ask_user is True")
    steps: List[PlanStep] = Field(description="List of execution steps")
    memory_candidates: List[str] = Field(description="Facts directly extracted from text worth remembering (e.g. 'User likes blue')")

class CognitivePlanner:
    def __init__(self):
        self.llm = get_llm()
        self.parser = PydanticOutputParser(pydantic_object=CognitivePlan)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the Cognitive Planner for an OS Assistant.
Your goal: Generate a safe, deterministic execution plan.

RULES:
1. **Follow the suggested_tool**:
   - If `context` contains `suggested_tool` (e.g. from Reasoner), YOU MUST USE IT.
   - Do not hallucinate a different tool if a suggestion is present.
   - Example: If suggested_tool="type_into", use `type_into` tool.

2. **Filenames**:
   - Default to `.txt` if extension missing.
   - Stop extraction at conjunctions ("and", "with", ",").
   - NEVER use a full sentence as a filename.
   - Example Input: "Create a file called hello world with content..." 
   - Example Param: `path="D:\\hello_world.txt"` (FULL PATH), `content="..."`

2. **Paths**:
   - D drive maps to "D:\\".
   - `create_file` params MUST have `path` as the FULL ABSOLUTE PATH (directory + filename).
   - Do NOT separate directory and filename.

3. **Ambiguity**:
   - If unsure about filename or path, set `ask_user=True`.

   - Extract facts into `memory_candidates`.

5. **Tool Discipline**:
   - Available Tools: `create_file`, `delete_file`, `create_folder`, `list_dir`, `write_file`, `memory_search`, `chat`, `screen_perception`, `launch_app_search`, `click_element`, `type_into`, `scroll_screen`, `press_keys`, `remember_ui_element`.
   - `create_file` params: `path` (string, full path), `content` (string).
   - `chat` params: `message` (string).
   - `screen_perception` params: {{}}.
   - `launch_app_search` params: `app_name` (string). Use for "open X", "launch X", "start X" requests.

6. **App Launching Rules**:
   - For "open notepad", "launch spotify", "start calculator" etc, use `launch_app_search`.
   - The app_name should be what a user would type in Windows Search.

7. **Screen Action Rules**:
   - Available: `click_element`, `type_into`, `scroll_screen`, `press_keys`
   - `click_element` params: `target` (description of what to click, e.g. "Start button", "Submit").
   - `type_into` params: `text` (what to type), `target_app` (optional, name of window to focus e.g. "Notepad").
   - `scroll_screen` params: `direction` ("up" or "down"), `amount` (optional, default 3).
   - `press_keys` params: `keys` (e.g. "ctrl+c", "alt+tab", "enter"), `focus` (optional window title to focus first, e.g. "Notepad").

8. **Visual Memory Rules** (Phase 16):
   - Available: `remember_ui_element`
   - Params: `name` (what to call this element/screen).
   - Use when user says "remember this screen", "save this as X", "remember the play button".

9. **Perception Rules**:
   - If user refers to visual context ("this", "that", "here", "screen") or asks "what is open?", use `screen_perception`.
   - If perception is needed, the plan must ONLY contain the `screen_perception` step. Do not guess actions.
   - **CRITICAL**: If `context` already contains `screen` data, DO NOT request `screen_perception` again. Use the data to answer via `chat` intent.

Return JSON strictly matching the schema.
"""),
            ("human", "Context: {context}\n\nTask: {text}\n\n{format_instructions}")
        ])

    async def plan(self, text: str, context: Optional[object] = None) -> CognitivePlan:
        # Check for suggested_tool in context and prepend it to text for visibility
        if hasattr(context, "suggested_tool") and context.suggested_tool:
             text = f"[SUGGESTED TOOL: {context.suggested_tool}] {text}"

        chain = self.prompt | self.llm | self.parser
        try:
            return await chain.ainvoke({
                "text": text,
                "context": str(context),
                "format_instructions": self.parser.get_format_instructions()
            })
        except Exception as e:
            print(f"[Planner] Error: {e}")
            with open("debug_planner_error.log", "w") as f:
                import traceback
                traceback.print_exc(file=f)
            # Fallback to chat
            return CognitivePlan(
                intent="chat",
                confidence=0.5,
                ask_user=False,
                clarification_question=None,
                steps=[],
                memory_candidates=[]
            )

planner = CognitivePlanner()
