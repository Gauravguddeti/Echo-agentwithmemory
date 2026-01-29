import os
import asyncio
from PIL import ImageGrab
import tempfile
from app.perception.window import get_active_window_info

# Try importing winsdk
try:
    from winsdk.windows.media.ocr import OcrEngine
    from winsdk.windows.graphics.imaging import BitmapDecoder
    from winsdk.windows.storage import StorageFile
    WINSDK_AVAILABLE = True
except ImportError:
    WINSDK_AVAILABLE = False
    print("[Perception] winsdk not installed. OCR disabled.")

class ScreenPerception:
    def __init__(self):
        self.ocr_engine = None
        if WINSDK_AVAILABLE:
            try:
                # Robust init: Find available language
                langs = OcrEngine.available_recognizer_languages
                if langs:
                    self.ocr_engine = OcrEngine.try_create_from_language(langs[0])
                    print(f"[Perception] OCR Engine Ready ({langs[0].display_name})")
                else:
                    print("[Perception] No OCR Languages found.")
            except Exception as e:
                print(f"[Perception] OCR Init Failed: {e}")
                self.ocr_engine = None

    async def analyze(self):
        """
        Captures screen and returns structured context.
        """
        # 1. Window Info
        win_info = get_active_window_info()
        
        # 2. Screenshot
        img = ImageGrab.grab()
        
        # 3. OCR
        visible_text = []
        if self.ocr_engine:
            visible_text = await self._run_ocr(img)
            
        return {
            "active_app": win_info["app"],
            "window_title": win_info["title"],
            "ui_type": win_info["ui_type"],
            "visible_text": visible_text,
            "confidence": 0.9 if visible_text else 0.5
        }

    async def _run_ocr(self, pil_img):
        temp_path = os.path.join(tempfile.gettempdir(), "echo_screen_ocr.png")
        try:
            pil_img.save(temp_path)
            
            # Load into WinRT
            file = await StorageFile.get_file_from_path_async(temp_path)
            stream = await file.open_async(0) # Read
            decoder = await BitmapDecoder.create_async(stream)
            bitmap = await decoder.get_software_bitmap_async()
            
            # Recognize
            result = await self.ocr_engine.recognize_async(bitmap)
            
            lines = []
            for line in result.lines:
                lines.append(line.text)
                
            return lines
            
        except Exception as e:
            print(f"[Perception] OCR Error: {e}")
            return []
        finally:
            if os.path.exists(temp_path):
                try: os.remove(temp_path)
                except: pass

perception = ScreenPerception()
