"""
Visual Element Memory - Phase 16 (Lightweight)
Stores paths to visual UI elements. Matches using template matching.
"""
import os
import json
from typing import List, Optional, Dict
from app.visual.matcher import get_image_matcher

ELEMENTS_FILE = "memory/visual/elements.json"

class ElementMemory:
    def __init__(self):
        self._ensure_dir("memory/visual")
        self.elements = self._load_elements()
        self.matcher = get_image_matcher()

    def _ensure_dir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def _load_elements(self) -> List[dict]:
        if os.path.exists(ELEMENTS_FILE):
            try:
                with open(ELEMENTS_FILE, "r") as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_elements(self):
        with open(ELEMENTS_FILE, "w") as f:
            json.dump(self.elements, f, indent=2)

    def remember_element(self, name: str, image_path: str, region: tuple) -> bool:
        """
        Stores a new UI element path.
        """
        element = {
            "name": name,
            "image_path": image_path,
            "region": region,
            "type": "template" 
        }
        
        # Check if name exists, update if so
        existing = next((e for e in self.elements if e["name"] == name), None)
        if existing:
            self.elements.remove(existing)
            
        self.elements.append(element)
        self._save_elements()
        print(f"[ElementMemory] Remembered element: '{name}'")
        return True

    def find_match(self, query: str, threshold: float = 0.8) -> Optional[Dict]:
        """
        Finds a matching element by name (exact/partial) or scans screen for known templates.
        
        Args:
            query: Name of the element to look for (e.g., "play button")
        """
        # 1. Name Match (Lookup)
        # We look for a stored element whose name matches the query
        candidate = next((e for e in self.elements if query.lower() in e["name"].lower()), None)
        
        if candidate:
            print(f"[ElementMemory] Found stored template for '{query}': {candidate['name']}")
            # 2. Visual Scan (Screen Confirmation)
            # Check if this element is currently on screen
            match_result = self.matcher.find_image_on_screen(candidate["image_path"], min_confidence=threshold)
            
            if match_result:
                print(f"[ElementMemory] Visual match confirmed on screen at {match_result['center']}")
                return {
                    "name": candidate["name"],
                    "center": match_result["center"],
                    "found_on_screen": True
                }
            else:
                print(f"[ElementMemory] Template found in memory but NOT on screen.")
                return {
                    "name": candidate["name"],
                    "center": None,
                    "found_on_screen": False,
                    "message": "Element known but not visible right now."
                }
                
        return None

# Singleton
element_memory = ElementMemory()

def get_element_memory():
    return element_memory
