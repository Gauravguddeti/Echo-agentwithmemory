"""
Screen Actions - Phase 15
Low-level UI automation: click, type, scroll, drag, hotkeys
"""
import pyautogui
import time
from typing import Optional, Tuple, List
from dataclasses import dataclass

# Safety settings
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.1  # Small pause between actions

@dataclass
class ActionResult:
    success: bool
    message: str
    needs_confirmation: bool = False


class ScreenActions:
    def __init__(self):
        self.last_action = None
        self.trusted_actions = set()  # Actions that don't need confirmation
    
    # --- CLICK ---
    def click(self, x: int, y: int, button: str = "left", confirmed: bool = False) -> ActionResult:
        """Click at screen coordinates"""
        action_key = f"click:{x},{y}"
        
        if not confirmed and action_key not in self.trusted_actions:
            return ActionResult(
                success=False,
                message=f"Click at ({x}, {y})? Reply 'yes' to confirm.",
                needs_confirmation=True
            )
        
        try:
            pyautogui.click(x, y, button=button)
            self.last_action = action_key
            return ActionResult(success=True, message=f"Clicked at ({x}, {y})")
        except Exception as e:
            return ActionResult(success=False, message=f"Click failed: {e}")
    
    # --- TYPE ---
    def type_text(self, text: str, interval: float = 0.05, confirmed: bool = False, focus: str = None) -> ActionResult:
        """Type text into focused element, optionally focusing a window first"""
        if not confirmed and "type" not in self.trusted_actions:
            preview = text[:30] + "..." if len(text) > 30 else text
            return ActionResult(
                success=False,
                message=f"Type '{preview}'? Reply 'yes' to confirm.",
                needs_confirmation=True
            )
        
        try:
            # Safer: Focus window first if requested
            if focus:
                from app.automation.ui_finder import get_ui_finder
                finder = get_ui_finder()
                # Try to focus, but proceed even if not found (user might have it open manually)
                # Ideally we check return val, but for now we just try.
                finder.focus_window(focus)
                time.sleep(0.5) # Wait longer for focus switch

            pyautogui.typewrite(text, interval=interval)
            return ActionResult(success=True, message=f"Typed: {text[:30]}..." + (f" into '{focus}'" if focus else ""))
        except Exception as e:
            # Try with unicode support
            try:
                import pyperclip
                pyperclip.copy(text)
                pyautogui.hotkey('ctrl', 'v')
                return ActionResult(success=True, message=f"Pasted: {text[:30]}..." + (f" into '{focus}'" if focus else ""))
            except:
                return ActionResult(success=False, message=f"Type failed: {e}")
    
    # --- SCROLL ---
    def scroll(self, direction: str = "down", amount: int = 3, confirmed: bool = False) -> ActionResult:
        """Scroll up or down"""
        if not confirmed and "scroll" not in self.trusted_actions:
            return ActionResult(
                success=False,
                message=f"Scroll {direction}? Reply 'yes' to confirm.",
                needs_confirmation=True
            )
        
        try:
            clicks = amount if direction == "up" else -amount
            pyautogui.scroll(clicks)
            return ActionResult(success=True, message=f"Scrolled {direction}")
        except Exception as e:
            return ActionResult(success=False, message=f"Scroll failed: {e}")
    
    # --- HOTKEY ---
    def hotkey(self, *keys, confirmed: bool = False, focus: str = None) -> ActionResult:
        """Press keyboard shortcut, optionally focusing a window first"""
        key_str = "+".join(keys)
        
        if not confirmed and f"hotkey:{key_str}" not in self.trusted_actions:
            return ActionResult(
                success=False,
                message=f"Press {key_str}? Reply 'yes' to confirm.",
                needs_confirmation=True
            )
        
        try:
            # Safer: Focus window first if requested
            if focus:
                from app.automation.ui_finder import get_ui_finder
                finder = get_ui_finder()
                finder.focus_window(focus)
                time.sleep(0.3) # Wait for focus
            
            pyautogui.hotkey(*keys)
            return ActionResult(success=True, message=f"Pressed {key_str}" + (f" in '{focus}'" if focus else ""))
        except Exception as e:
            return ActionResult(success=False, message=f"Hotkey failed: {e}")
    
    # --- DRAG ---
    def drag(self, x1: int, y1: int, x2: int, y2: int, duration: float = 0.5, confirmed: bool = False) -> ActionResult:
        """Drag from point A to point B"""
        if not confirmed and "drag" not in self.trusted_actions:
            return ActionResult(
                success=False,
                message=f"Drag from ({x1},{y1}) to ({x2},{y2})? Reply 'yes' to confirm.",
                needs_confirmation=True
            )
        
        try:
            pyautogui.moveTo(x1, y1)
            pyautogui.drag(x2 - x1, y2 - y1, duration=duration)
            return ActionResult(success=True, message=f"Dragged from ({x1},{y1}) to ({x2},{y2})")
        except Exception as e:
            return ActionResult(success=False, message=f"Drag failed: {e}")
    
    # --- MOVE ---
    def move_to(self, x: int, y: int) -> ActionResult:
        """Move mouse to position (no confirmation needed)"""
        try:
            pyautogui.moveTo(x, y)
            return ActionResult(success=True, message=f"Moved to ({x}, {y})")
        except Exception as e:
            return ActionResult(success=False, message=f"Move failed: {e}")
    
    # --- SCREENSHOT ---
    def screenshot(self, region: Optional[Tuple[int, int, int, int]] = None) -> Tuple[bool, any]:
        """Take a screenshot, optionally of a region"""
        try:
            img = pyautogui.screenshot(region=region)
            return True, img
        except Exception as e:
            return False, str(e)
    
    # --- TRUST MANAGEMENT ---
    def add_trusted(self, action_type: str):
        """Add action type to trusted (no confirmation)"""
        self.trusted_actions.add(action_type)
    
    def remove_trusted(self, action_type: str):
        """Remove action type from trusted"""
        self.trusted_actions.discard(action_type)


# Singleton
screen_actions = ScreenActions()

def get_screen_actions() -> ScreenActions:
    return screen_actions
