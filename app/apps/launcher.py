import os

def launch_app(path: str) -> str:
    """
    Safely launches an application using os.startfile.
    """
    try:
        # 1. Check direct path
        if os.path.exists(path):
            os.startfile(path)
            return f"Launched: {os.path.basename(path)}"
            
        # 2. Check system path (e.g. 'notepad', 'calc')
        import shutil
        import subprocess
        
        system_path = shutil.which(path)
        if system_path:
             subprocess.Popen(system_path)
             return f"Launched System App: {os.path.basename(system_path)}"
             
        # 3. Fallback: Try launching as command (e.g. 'notepad')
        # This covers aliases that might not show in which()
        try:
            subprocess.Popen(path, shell=True)
            return f"Launched Command: {path}"
        except:
             return f"Error: App path not found: {path}"

    except Exception as e:
        return f"Launch Error: {e}"
