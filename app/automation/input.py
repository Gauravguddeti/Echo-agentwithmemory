import subprocess
import os
import time
import tempfile

import ctypes
from typing import Optional

class InputManager:
    def get_foreground_window_title(self) -> str:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value

    def copy_to_clipboard(self, text: str):
        # ... (keep existing)
        try:
            ps_text = text.replace("'", "''")
            cmd = f"powershell -command \"Set-Clipboard -Value '{ps_text}'\""
            subprocess.run(cmd, shell=True, check=True)
        except Exception as e:
            print(f"Clipboard Error: {e}")

    def send_keys(self, keys: str):
        # ... (keep existing)
        script = f"""
Set wshShell = WScript.CreateObject("WScript.Shell")
wshShell.SendKeys "{keys}"
"""
        self._run_vbs(script)

    def focus_app(self, title: str):
        # ... (keep existing)
        script = f"""
Set wshShell = WScript.CreateObject("WScript.Shell")
wshShell.AppActivate "{title}"
"""
        self._run_vbs(script)

    def _run_vbs(self, content: str):
        fd, path = tempfile.mkstemp(suffix=".vbs")
        try:
            with os.fdopen(fd, 'w') as tmp:
                tmp.write(content)
            subprocess.run(f"cscript //nologo {path}", shell=True)
        finally:
            if os.path.exists(path):
                os.remove(path)

    def write_text(self, text: str, mode="paste"):
        if mode == "paste":
            self.copy_to_clipboard(text)
            time.sleep(0.3) 
            self.send_keys("^v")
        else:
            self.send_keys(text)

    def write_text_safely(self, text: str, target_title_keyword: str) -> str:
        """
        Writes text only if the target window is focused. 
        Checks focus every chunk.
        """
        active = self.get_foreground_window_title()
        if target_title_keyword.lower() not in active.lower():
            return f"Error: Focused window '{active}' does not match '{target_title_keyword}'."
            
        # Write 
        self.write_text(text, mode="paste")
        
        # Verify after
        active_after = self.get_foreground_window_title()
        if target_title_keyword.lower() not in active_after.lower():
             return f"Warning: Focus lost during writing! Focus moved to '{active_after}'."
             
        return "Success: Text written safely."

input_manager = InputManager()

def get_input_manager():
    return input_manager
