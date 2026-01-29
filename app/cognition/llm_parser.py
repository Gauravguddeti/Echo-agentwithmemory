from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from .schema import StructuredIntent
import json

class LLMIntentParser:
    def __init__(self):
        self.parser = JsonOutputParser()
        
        self.system_prompt = """You are an Intent Extraction Engine.
Analyze the user's request and map it to a Structured Intent.
Your output must be JSON.

AVAILABLE GOALS:
- open_app: Launch applications. Target=App Name.
- browser_search: Search the web. Target=Engine (google/youtube). Params={query: ...}
- browser_nav: Go to a URL. Target=browser. Params={url: ...}
- desktop_write: Write text. Target=App Name (notepad). Params={text: ...}
- filesystem: Manage files/folders. Target=Action (create_folder, create_file, delete_item). Params={name: ..., path: ...}
- chat: General conversation, greetings, questions about capabilities.
- unknown: Cannot determine.

EXAMPLES:
User: "Make a folder named Work in D drive"
Output: {"goal": "filesystem", "target": "create_folder", "params": {"name": "Work", "path": "D:\\"}}

User: "Search youtube for tutorials"
Output: {"goal": "browser_search", "target": "youtube", "params": {"query": "tutorials"}}

User: "Write hello world in notepad"
Output: {"goal": "desktop_write", "target": "notepad", "params": {"text": "hello world"}}

User: "Brev creates a file called 123"
Output: {"goal": "filesystem", "target": "create_file", "params": {"name": "123"}}

User: "Yo what's up"
Output: {"goal": "chat", "target": ""}

RULES:
- Extract parameters cleanly. Remove fillers like "named", "called", "me a".
- Map "text document" to "create_file".
- Return ONLY JSON.
"""

    async def parse(self, text: str, llm) -> StructuredIntent:
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", "{input}")
            ])
            
            chain = prompt | llm | self.parser
            
            # Run LLM
            # Note: Depending on LLM wrapper, invoke might be sync or async. 
            # Assuming LangChain invoke is synchronous but we can treat as such or use ainvoke.
            # Local vars
            result = chain.invoke({"input": text})
            
            # Map simplified JSON to Schema
            return StructuredIntent(
                goal=result.get("goal", "unknown"),
                target=result.get("target", ""),
                params=result.get("params", {}),
                confidence=0.95, # High confidence if LLM parsed it
                original_text=text,
                style="casual"
            )
        except Exception as e:
            print(f"[LLM Parser] Error: {e}")
            return StructuredIntent(goal="unknown", target="", confidence=0.0, original_text=text)

llm_parser = LLMIntentParser()
