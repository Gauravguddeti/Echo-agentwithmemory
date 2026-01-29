import os
import shutil
from typing import Optional

class FilesystemActions:
    def __init__(self):
        pass

    def execute(self, action: str, target_path: str, destination: Optional[str] = None) -> str:
        """
        Executes the filesystem action safely.
        """
        try:
            if not os.path.exists(target_path) and action != "create_folder":
                return f"Error: Path not found: {target_path}"

            if action == "open_file":
                # Windows only
                os.startfile(target_path)
                return f"Opened file: {target_path}"
                
            elif action == "open_folder":
                os.startfile(target_path)
                return f"Opened folder: {target_path}"
                
            elif action == "create_folder":
                if os.path.exists(target_path):
                    return f"Folder already exists: {target_path}"
                os.makedirs(target_path)
                return f"Created folder: {target_path}"
                
            elif action == "move_file_or_folder":
                if not destination:
                    return "Error: No destination specified for move."
                shutil.move(target_path, destination)
                shutil.move(target_path, destination)
                return f"Moved {target_path} to {destination}"

            elif action == "rename":
                if not destination:
                    return "Error: No new name specified for rename."
                # Rename logic (handles file or folder)
                # destination should probably be the full path?
                # The chat logic provided just the new name in some cases, or full path?
                # The test provided "renamed_success.txt" (relative).
                # shutil.move or os.rename usually expects full path if not in CWD.
                # But target_path is full. If destination is just name, we should join dirs.
                
                parent = os.path.dirname(target_path)
                final_dest = destination
                if os.path.sep not in destination: # If just a filename
                    final_dest = os.path.join(parent, destination)
                
                os.rename(target_path, final_dest)
                return f"Renamed to {os.path.basename(final_dest)}"
                
            elif action == "delete":
                if os.path.isfile(target_path):
                    os.remove(target_path)
                    return f"Deleted file: {target_path}"
                elif os.path.isdir(target_path):
                    shutil.rmtree(target_path)
                    return f"Deleted folder: {target_path}"
                    
            elif action == "create_file":
                # Create file with optional content
                # For this simple action wrapper, we might need 'content' arg.
                # But execute signature is (action, target, dest).
                # We should update execute signature OR add specific methods.
                pass
                
            return f"Action '{action}' not implemented yet."
            
        except Exception as e:
            return f"Execution Error: {e}"

    def write_file(self, path: str, content: str) -> str:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Wrote to {path}"
        except Exception as e:
            return f"Error writing file: {e}"

fs_actions = FilesystemActions()

def get_fs_actions():
    return fs_actions
