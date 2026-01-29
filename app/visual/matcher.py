import pyautogui
import os
import numpy as np
from typing import Optional, Tuple, Dict

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("[ImageMatcher] OpenCV not available. Using exact pixel matching (slower, brittle).")

# Settings
CONFIDENCE_THRESHOLD = 0.8

class ImageMatcher:
    def __init__(self):
        self.ready = True

    def find_image_on_screen(self, image_path: str, min_confidence: float = 0.8) -> Optional[Dict]:
        """
        Locates an image on the screen.
        Returns dict with center coordinates if found.
        """
        if not os.path.exists(image_path):
            return None
            
        try:
            # Use pyautogui locate
            location = None
            
            if OPENCV_AVAILABLE:
                # With confidence
                location = pyautogui.locateOnScreen(image_path, confidence=min_confidence)
            else:
                # Exact match fallback
                location = pyautogui.locateOnScreen(image_path)
            
            if location:
                return {
                    "found": True,
                    "left": location.left,
                    "top": location.top,
                    "width": location.width,
                    "height": location.height,
                    "center": (location.left + location.width//2, location.top + location.height//2)
                }
        except Exception as e:
            print(f"[ImageMatcher] Search failed: {e}")
            # Fallback for "confidence argument requires opencv" if opencv load fails
            # Try exact match
            try:
                location = pyautogui.locateOnScreen(image_path)
                if location:
                     return {
                        "found": True,
                        "left": location.left,
                        "top": location.top,
                        "width": location.width,
                        "height": location.height,
                        "center": (location.left + location.width//2, location.top + location.height//2)
                    }
            except:
                pass

        return None

# Singleton
matcher = ImageMatcher()

def get_image_matcher():
    return matcher
