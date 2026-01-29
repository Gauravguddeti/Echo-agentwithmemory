from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum

class ChunkType(Enum):
    FILLER = "filler"       # "can you", "please", "bro"
    ACTION = "action"       # "open", "search", "write"
    OBJECT = "object"       # "calculator", "notepad", "google"
    TARGET = "target"       # "hello world", "mr beast"
    PREPOSITION = "prep"    # "in", "on", "to", "for"
    UNKNOWN = "unknown"

@dataclass
class Chunk:
    text: str
    type: ChunkType
    confidence: float = 1.0

@dataclass
class StructuredIntent:
    goal: str               # "open_app", "browser_search", "browser_nav", "desktop_write", "chat", "filesystem", "unknown"
    target: str             # "notepad", "google", "https://..."
    params: Dict[str, str] = field(default_factory=dict) # {"text": "hello"}
    confidence: float = 0.0
    original_text: str = ""
    style: str = "neutral"  # "casual", "formal"
