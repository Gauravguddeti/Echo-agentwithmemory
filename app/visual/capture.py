"""
Screen Capture Module - Phase 16
Captures screenshots for visual memory.
"""
import pyautogui
import os
import time
import uuid
from typing import Optional, Tuple

VISUAL_MEMORY_DIR = "memory/visual"

class ScreenCapture:
    def __init__(self):
        self._ensure_dir(VISUAL_MEMORY_DIR)
        
    def _ensure_dir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
            
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None, save: bool = True) -> dict:
        """
        Captures the screen or a region.
        
        Args:
            region: Tuple (left, top, width, height) or None for full screen
            save: Whether to save to disk immediately
            
        Returns:
            dict with 'path', 'timestamp', 'size'
        """
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"capture_{timestamp}_{unique_id}.png"
            path = os.path.join(VISUAL_MEMORY_DIR, filename)
            
            # Capture
            if region:
                img = pyautogui.screenshot(region=region)
            else:
                img = pyautogui.screenshot()
                
            if save:
                img.save(path)
                return {
                    "status": "success",
                    "path": path,
                    "filename": filename,
                    "timestamp": timestamp,
                    "size": img.size,
                    "image": img # In-memory object
                }
            else:
                return {
                    "status": "success",
                    "image": img,
                    "size": img.size
                }
                
        except Exception as e:
            print(f"[ScreenCapture] Failed: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def capture_element(self, x: int, y: int, width: int, height: int, name: Optional[str] = None) -> dict:
        """Capture a specific UI element region"""
        result = self.capture_screen(region=(x, y, width, height))
        if result["status"] == "success" and name:
            # Rename if name provided (sanitized)
            safe_name = "".join([c for c in name if c.isalnum() or c in (' ', '_')]).strip().replace(' ', '_')
            new_filename = f"element_{safe_name}_{result['timestamp']}.png"
            new_path = os.path.join(VISUAL_MEMORY_DIR, new_filename)
            
            os.rename(result["path"], new_path)
            result["path"] = new_path
            result["filename"] = new_filename
            
        return result

# Singleton
screen_capture = ScreenCapture()

def get_screen_capture():
    return screen_capture
