from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
import json
from app.dependencies import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

class FSIntentType(Enum):
    SEARCH = "search_file"
    OPEN_FILE = "open_file"
    OPEN_FOLDER = "open_folder"
    CREATE_FOLDER = "create_folder"
    MOVE = "move_file_or_folder"
    NONE = "none"

class FSSlots(BaseModel):
    intent: str = Field(description="One of: search_file, open_file, open_folder, create_folder, move_file_or_folder, none")
    target_name: Optional[str] = Field(None, description="The name of the file or folder to act on")
    destination: Optional[str] = Field(None, description="The destination path/folder for move operations")
    location_hint: Optional[str] = Field(None, description="Location context like 'in D', 'from Documents', 'in projects folder'")
    context_needed: Optional[str] = Field(None, description="If generic like 'open it', what does 'it' refer to?")

SYSTEM_PROMPT = """You are a Filesystem Intent Classifier.
Analyze the user's request and map it to a filesystem action.

Actions:
- search_file: "Find budget.pdf", "Where is the notes file?"
- open_file: "Open budget.pdf", "Read the report"
- open_folder: "Open the downloads folder", "Go to Documents"
- create_folder: "Make a new folder called Work", "Create directory Test"
- move_file_or_folder: "Move file.txt to Backup", "Put this in the Work folder"
- none: "Hello", "Calculate 2+2", "Who are you?"

Output valid JSON with the following keys:
- "intent": (required, string) The action name.
- "target_name": (optional, string) File/folder name.
- "destination": (optional, string) Target for moves.
- "location_hint": (optional, string) Where to look (e.g. "in D drive", "documents").
- "context_needed": (optional, string) Clarity request.
"""

class FilesystemIntentController:
    def __init__(self):
        self.llm = get_llm()

    def classify(self, message: str) -> FSSlots:
        """
        Uses LLM to classify intent and extract slots.
        """
        # 1. Fast heuristic check to avoid LLM for obvious non-FS queries?
        # Maybe "open", "find", "move", "create", "folder", "file" check.
        keywords = ["open", "find", "search", "move", "create", "make folder", "where is"]
        if not any(k in message.lower() for k in keywords):
             return FSSlots(intent="none")

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=message)
        ]
        
        try:
            # We want structured output. 
            # If model supports with_structured_output, great. 
            # Otherwise JSON mode.
            # Using JSON mode for compatibility.
            messages[0].content += "\nRespond with valid JSON conforming to FSSlots schema."
            
            response = self.llm.invoke(messages)
            content = response.content.strip()
            
            with open("fs_debug.log", "a") as f:
                f.write(f"Input: {message}\nOutput: {content}\n")
            
            # Sanitization
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            data = json.loads(content)
            return FSSlots(**data)
            
        except Exception as e:
            with open("fs_debug.log", "a") as f:
                f.write(f"Error: {e}\n")
            print(f"FS Intent Error: {e}")
            return FSSlots(intent="none")

fs_controller = FilesystemIntentController()

def get_fs_controller():
    return fs_controller
