"""
UI Element Finder - Phase 15
Find UI elements by name, type, or OCR text
"""
import pyautogui
from typing import Optional, List, Tuple, Dict
from dataclasses import dataclass

try:
    from pywinauto import Desktop
    from pywinauto.findwindows import ElementNotFoundError
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False
    print("[UIFinder] pywinauto not available, using OCR fallback only")


@dataclass
class UIElement:
    name: str
    x: int
    y: int
    width: int
    height: int
    element_type: str
    confidence: float = 1.0
    
    @property
    def center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)


class UIFinder:
    def __init__(self):
        self.desktop = Desktop(backend="uia") if PYWINAUTO_AVAILABLE else None
        self.ocr_enabled = True
    
    def find_by_name(self, name: str, window_title: Optional[str] = None) -> List[UIElement]:
        """Find UI elements by name/text using Windows UI Automation"""
        elements = []
        
        if PYWINAUTO_AVAILABLE and self.desktop:
            try:
                # Get windows
                windows = self.desktop.windows()
                
                for win in windows:
                    # Filter by window title if specified
                    if window_title and window_title.lower() not in win.window_text().lower():
                        continue
                    
                    try:
                        # Search for elements containing the name
                        found = win.descendants(title_re=f".*{name}.*")
                        for elem in found[:5]:  # Limit results
                            rect = elem.rectangle()
                            elements.append(UIElement(
                                name=elem.window_text(),
                                x=rect.left,
                                y=rect.top,
                                width=rect.width(),
                                height=rect.height(),
                                element_type=elem.element_info.control_type
                            ))
                    except:
                        continue
            except Exception as e:
                print(f"[UIFinder] Windows search failed: {e}")
        
        # OCR Fallback
        if not elements and self.ocr_enabled:
            elements = self._find_by_ocr(name)
        
        return elements
    
    def _find_by_ocr(self, text: str) -> List[UIElement]:
        """Find text on screen using OCR"""
        elements = []
        try:
            # Use pyautogui's locateOnScreen if we have an image
            # For text, we need to take a screenshot and OCR it
            # This is a placeholder - full OCR requires pytesseract
            locations = list(pyautogui.locateAllOnScreen(text))
            for loc in locations[:5]:
                elements.append(UIElement(
                    name=text,
                    x=loc.left,
                    y=loc.top,
                    width=loc.width,
                    height=loc.height,
                    element_type="ocr_text",
                    confidence=0.8
                ))
        except Exception as e:
            # OCR/image matching failed
            pass
        
        return elements
    
    def find_button(self, name: str) -> Optional[UIElement]:
        """Find a button by name"""
        elements = self.find_by_name(name)
        buttons = [e for e in elements if "Button" in e.element_type or "button" in e.name.lower()]
        return buttons[0] if buttons else (elements[0] if elements else None)
    
    def find_text_field(self, name: str = "") -> Optional[UIElement]:
        """Find an input/text field"""
        if PYWINAUTO_AVAILABLE and self.desktop:
            try:
                for win in self.desktop.windows():
                    try:
                        # Look for Edit controls
                        edits = win.descendants(control_type="Edit")
                        for edit in edits:
                            if not name or name.lower() in edit.window_text().lower():
                                rect = edit.rectangle()
                                return UIElement(
                                    name=edit.window_text() or "Text Field",
                                    x=rect.left,
                                    y=rect.top,
                                    width=rect.width(),
                                    height=rect.height(),
                                    element_type="Edit"
                                )
                    except:
                        continue
            except Exception as e:
                print(f"[UIFinder] Text field search failed: {e}")
        
        return None
    
    def get_active_window(self) -> Optional[str]:
        """Get the title of the active window"""
        if PYWINAUTO_AVAILABLE and self.desktop:
            try:
                from pywinauto import Desktop
                active = Desktop(backend="uia").get_active()
                return active.window_text() if active else None
            except:
                pass
        return None
    
    def focus_window(self, title_query: str) -> bool:
        """Focus a window by title"""
        if PYWINAUTO_AVAILABLE and self.desktop:
            try:
                # Find window by title
                windows = self.desktop.windows()
                for win in windows:
                    if title_query.lower() in win.window_text().lower():
                        if win.is_minimized():
                            win.restore()
                        win.set_focus()
                        return True
            except Exception as e:
                print(f"[UIFinder] Focus failed: {e}")
        return False


# Singleton
ui_finder = UIFinder()

def get_ui_finder() -> UIFinder:
    return ui_finder
