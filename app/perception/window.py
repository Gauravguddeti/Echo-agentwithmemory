import ctypes
from ctypes import wintypes
import psutil

# Windows API
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def get_active_window_info():
    """
    Returns text and pid of the active window.
    """
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return {"title": "Unknown", "app": "Unknown"}
        
    length = user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buff, length + 1)
    title = buff.value
    
    # Get PID
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    
    try:
        process = psutil.Process(pid.value)
        app_name = process.name()
    except:
        app_name = "Unknown"
        
    return {
        "title": title,
        "app": app_name,
        "ui_type": _infer_ui_type(app_name, title)
    }

def _infer_ui_type(app, title):
    app = app.lower()
    title = title.lower()
    if "chrome" in app or "edge" in app or "firefox" in app:
        return "browser"
    if "code" in app or "pycharm" in app:
        return "editor"
    if "cmd" in app or "powershell" in app or "terminal" in app:
        return "terminal"
    return "application"
