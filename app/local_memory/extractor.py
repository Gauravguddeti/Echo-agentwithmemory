import re
import json
from langchain_core.messages import SystemMessage, HumanMessage
from app.dependencies import get_llm

SYSTEM_PROMPT = """You are a Memory Extractor.
Target: Extract atomic facts, user preferences, or behavioral patterns from the conversation.
Output Format: JSON list of objects.
Schema: [{"content": "...", "title": "Short Label", "confidence": 0.0 to 1.0, "type": "fact|preference|behavior|person|event", "tags": [...]}]

Rules:
1. EXTRACT EVERYTHING. If a name is mentioned ("I'm X", "Call me Y"), EXTRACT IT.
2. If an event is mentioned ("Date", "Meeting"), EXTRACT IT.
3. If a preference is implied ("Casual", "Formal"), EXTRACT IT.
4. BE AGGRESSIVE. Better to remember too much than nothing.
5. High confidence (1.0) for self-identification ("I am Gaurav").
"""

def extract_and_score(text: str):
    """
    Extracts facts from text using the LLM.
    Returns a list of dicts.
    """
    llm = get_llm()
    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Analyze this interaction and extract memories:\n\n{text}")
        ])
        
        content = response.content.strip()
        
        # Robust JSON Extraction
        match = re.search(r'(\[.*\]|\{.*\})', content, re.DOTALL)
        if match:
            content = match.group(0)
        else:
            # Fallback: if no brackets found, try to use the whole string if it looks like json
            pass
            
        try:
            data = json.loads(content)
            # Success Log
            with open("logs/extractor_debug.log", "a") as f:
                 f.write(f"Raw: {content}\nParsed: {data}\n")
            if isinstance(data, list):
                return data
            return []
        except json.JSONDecodeError:
            print(f"Failed to parse memory extraction JSON: {content}")
            return []
            
    except Exception as e:
        with open("logs/extractor_debug.log", "a") as f:
             f.write(f"Extraction Failed: {e}\n")
        print(f"Memory extraction failed: {e}")
        return []
