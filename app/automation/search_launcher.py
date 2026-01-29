"""
Windows Search Launcher - Phase 14
Opens apps via Windows Search (Win key + type + Enter)
"""
import pyautogui
import time
from typing import Optional

# Safety settings
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.1  # Small pause between actions

class SearchLauncher:
    def __init__(self):
        self.last_search = None
        self.trusted_apps = set()  # Apps that don't need confirmation
    
    def search_and_launch(self, app_name: str, confirmed: bool = False) -> dict:
        """
        Opens an app via Windows Search.
        
        Args:
            app_name: Name of app to search for
            confirmed: If True, executes immediately. If False, returns confirmation request.
            
        Returns:
            dict with status and message
        """
        self.last_search = app_name
        
        # Check if already trusted
        if app_name.lower() in self.trusted_apps:
            confirmed = True
        
        if not confirmed:
            return {
                "status": "needs_confirmation",
                "message": f"Launch '{app_name}' via Windows Search?",
                "action": "launch_app_search",
                "params": {"app_name": app_name}
            }
        
        try:
            # Press Windows key
            pyautogui.press('win')
            time.sleep(0.5)  # Wait for Start menu
            
            # Type app name
            pyautogui.typewrite(app_name, interval=0.05)
            time.sleep(0.8)  # Wait for search results
            
            # Press Enter to launch
            pyautogui.press('enter')
            time.sleep(0.3)
            
            return {
                "status": "success",
                "message": f"Launched '{app_name}' via Windows Search.",
                "should_trust": True  # Ask if should remember
            }
            
        except Exception as e:
            # Press Escape to close any open menus
            pyautogui.press('escape')
            return {
                "status": "error",
                "message": f"Failed to launch '{app_name}': {str(e)}"
            }
    
    def add_trusted(self, app_name: str):
        """Add app to trusted list (no confirmation needed)"""
        self.trusted_apps.add(app_name.lower())
        
    def remove_trusted(self, app_name: str):
        """Remove app from trusted list"""
        self.trusted_apps.discard(app_name.lower())
        
    def is_trusted(self, app_name: str) -> bool:
        return app_name.lower() in self.trusted_apps


# Singleton
search_launcher = SearchLauncher()

def get_search_launcher() -> SearchLauncher:
    return search_launcher
