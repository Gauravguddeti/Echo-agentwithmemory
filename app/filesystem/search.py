import os
from typing import List
from app.filesystem.config import get_allowed_roots

class ScopedSearcher:
    def __init__(self):
        pass

    def search(self, name: str, location_hint: str = None) -> List[str]:
        """
        Searches for 'name' in ALLOWED_ROOTS.
        If location_hint is provided, tries to filter roots or subfolders.
        Returns matched absolute paths.
        Limit: Depth=3, Max results=5.
        """
        roots = get_allowed_roots()
        matches = []
        max_results = 5
        
        # Filter roots by hint?
        # Simple heuristic: If hint contains "D", prioritize roots starting with D:
        active_roots = roots
        if location_hint:
            hint_lower = location_hint.lower()
            # If hint is "D drive" or "D:", filter roots
            filtered = [r for r in roots if r.lower().startswith(hint_lower[0] + ":")]
            if filtered:
                active_roots = filtered
            
            # TODO: Handle folder hints like "in docs" -> look for folder named "docs" inside roots?
            # For now, let's just search all active roots.

        print(f"Searching for '{name}' in {active_roots} (Hint: {location_hint})")

        for search_root in active_roots:
            # Depth limited walk logic
            root_depth = search_root.count(os.sep)
            
            for root, dirs, files in os.walk(search_root):
                # Check depth
                current_depth = root.count(os.sep)
                if current_depth - root_depth > 3:
                     # Skip subdirectories from here
                     del dirs[:]
                     continue
                
                # Check files (and folders if target is folder?)
                # Searcher usually looks for files or folder names matching target_name.
                
                # Check fuzzy match? Or strict? 
                # Requirement: "Matching allowed root name" ... "Resolve specific hints"
                
                for f in files:
                    if name.lower() in f.lower():
                        full_path = os.path.join(root, f)
                        matches.append(full_path)
                        if len(matches) >= max_results:
                            return matches
                            
                for d in dirs:
                     if name.lower() in d.lower():
                        full_path = os.path.join(root, d)
                        matches.append(full_path)
                        if len(matches) >= max_results:
                            return matches

        return matches

scoped_searcher = ScopedSearcher()

def get_searcher():
    return scoped_searcher
