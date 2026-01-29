"""
Cognitive Reasoner - Phase 17
Uses LLM to understand natural language and map it to tools/plans.
Updates the previous specialized 'semantic.py' router with a general reasoning engine.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.dependencies import get_llm

class CognitiveIntent(BaseModel):
    intent_type: str = Field(description="Primary intent: 'automation', 'filesystem', 'memory', 'chat', 'weather', 'search'")
    confidence: float = Field(description="Confidence score 0.0-1.0")
    parameters: Dict[str, Any] = Field(description="Extracted parameters for the action")
    reasoning: str = Field(description="Brief explanation of why this intent was chosen")
    suggested_tool: Optional[str] = Field(description="Name of the tool that best fits this request (e.g. 'click_element', 'launch_app_search', 'create_file')")

class CognitiveReasoner:
    def __init__(self):
        self.llm = get_llm()
        self.parser = PydanticOutputParser(pydantic_object=CognitiveIntent)
        
        # Comprehensive system prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the Cognitive Engine of the Echo AI OS Assistant.
Your job is to understand user requests and map them to specific system actions.

ANALYSIS RULES:
1. **Automation**: Requests to interact with the screen, mouse, keyboard, or apps.
   - "open notepad" -> tool: `launch_app_search`, params: {{"app_name": "notepad"}}
   - "type hello" -> tool: `type_into`, params: {{"text": "hello"}}
   - "type code into vscode" -> tool: `type_into`, params: {{"text": "code", "target_app": "vscode"}}
   - "type hello in notepad" -> tool: `type_into`, params: {{"text": "hello", "target_app": "notepad"}}
   - "click the start button" -> tool: `click_element`, params: {{"target": "start button"}}
   - "scroll down" -> tool: `scroll_screen`, params: {{"direction": "down"}}
   - "close window" -> tool: `press_keys`, params: {{"keys": "alt+f4"}}
   - "close notepad" -> tool: `press_keys`, params: {{"keys": "alt+f4", "focus": "Notepad"}}

2. **Filesystem**: Requests to manage files/folders.
   - "create folder foo" -> tool: `create_folder`, params: {{"path": "D:\\foo"}} (Default to D: if unspecified)
   - "make a file test.txt" -> tool: `create_file`

3. **Memory**: Requests to remember or recall info.
   - "remember I like pizza" -> intent: `memory`
   - "what is my name?" -> intent: `memory`
   
4. **Visual Learning**: 
   - "remember this screen as main_menu" -> tool: `remember_ui_element`

RESPONSE FORMAT:
Return a JSON object conforming to the schema. 
- If uncertain, set confidence < 0.5.
- `parameters` must match the tool's expected arguments.

CONTEXT:
User's Operating System: Windows
Current Workspace: D:\\projects\\aiassisstantwithmemory
"""),
            ("human", "User Request: {text}\n\n{format_instructions}")
        ])

    async def reason(self, text: str) -> CognitiveIntent:
        """
        Analyzes the text to determine intent and standard parameters.
        """
        chain = self.prompt | self.llm | self.parser
        try:
            return await chain.ainvoke({
                "text": text,
                "format_instructions": self.parser.get_format_instructions()
            })
        except Exception as e:
            print(f"[Reasoner] Error: {e}")
            # Fallback
            return CognitiveIntent(
                intent_type="chat",
                confidence=0.0,
                parameters={},
                reasoning=f"Error parsing intent: {str(e)}",
                suggested_tool=None
            )

# Singleton
reasoner = CognitiveReasoner()

def get_reasoner():
    return reasoner
