import os
import json
import re
from typing import Dict, List

PROFILE_DIR = "memory"
WINDOW_SIZE = 10

class UserProfiler:
    def __init__(self):
        self._ensure_dir(PROFILE_DIR)

    def _ensure_dir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def _get_profile_path(self, user_id):
        user_dir = os.path.join(PROFILE_DIR, user_id)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        return os.path.join(user_dir, "profile.json")

    def update(self, user_id: str, message: str):
        """
        Updates the user's profile statistics based on the new message.
        """
        path = self._get_profile_path(user_id)
        
        # Load existing profile
        if os.path.exists(path):
            with open(path, "r") as f:
                profile = json.load(f)
        else:
            profile = {
                "message_lengths": [],
                "emoji_counts": []
            }
            
        # Calculate stats for this message
        length = len(message.split())
        emoji_count = len(re.findall(r'[^\w\s,.]', message)) # Very rough emoji/symbol check
        
        # Update rolling windows
        profile["message_lengths"].append(length)
        profile["emoji_counts"].append(emoji_count)
        
        # Trim to window size
        if len(profile["message_lengths"]) > WINDOW_SIZE:
            profile["message_lengths"] = profile["message_lengths"][-WINDOW_SIZE:]
            profile["emoji_counts"] = profile["emoji_counts"][-WINDOW_SIZE:]
            
        # Save profile
        with open(path, "w") as f:
            json.dump(profile, f, indent=2)

    def get_style_instructions(self, user_id: str) -> str:
        """
        Returns a system prompt instruction based on user stats.
        """
        path = self._get_profile_path(user_id)
        if not os.path.exists(path):
            return "" # Default style
            
        with open(path, "r") as f:
            profile = json.load(f)
            
        lengths = profile.get("message_lengths", [])
        emojis = profile.get("emoji_counts", [])
        
        if not lengths:
            return ""
            
        avg_len = sum(lengths) / len(lengths)
        avg_emojis = sum(emojis) / len(emojis)
        
        instructions = []
        
        # Verbosity Adaptation
        if avg_len < 6:
            instructions.append("Be extremely concise and direct. Avoid fluff.")
        elif avg_len < 15:
            instructions.append("Be concise.")
        elif avg_len > 40:
            instructions.append("Be detailed and comprehensive.")
            
        # Tone Adaptation (Emoji mirroring)
        if avg_emojis > 0.5:
            instructions.append("Use emojis occasionally to match the user's tone.")
            
        if not instructions:
            return ""
            
        return "STYLE ADAPTATION: " + " ".join(instructions)

# Singleton
profiler = UserProfiler()

def get_profiler():
    return profiler
