import os
import json
import shutil
from typing import Dict, Any

from utils.logger import logger

class FileManager:
    def __init__(self, base_dir: str = "downloads"):
        self.base_dir = base_dir
        self.instagram_dir = os.path.join(self.base_dir, "instagram")
        self.youtube_dir = os.path.join(self.base_dir, "youtube")
        self._ensure_dirs()
        self.history_file = os.path.join(self.base_dir, "history.json")
        self._load_history()

    def _ensure_dirs(self):
        os.makedirs(self.instagram_dir, exist_ok=True)
        os.makedirs(self.youtube_dir, exist_ok=True)

    def _load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load history: {e}")
                self.history = {"instagram": [], "youtube": []}
        else:
            self.history = {"instagram": [], "youtube": []}

    def _save_history(self):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=4)

    def is_downloaded(self, platform: str, media_id: str) -> bool:
        """Check if media ID is already in the download history."""
        return media_id in self.history.get(platform, [])

    def mark_downloaded(self, platform: str, media_id: str):
        """Mark a media ID as downloaded to prevent duplicates."""
        if platform not in self.history:
            self.history[platform] = []
        if media_id not in self.history[platform]:
            self.history[platform].append(media_id)
            self._save_history()

    def get_user_dir(self, platform: str, username: str) -> str:
        """Get or create the specific directory for a user/channel."""
        target_dir = os.path.join(self.base_dir, platform, username)
        os.makedirs(target_dir, exist_ok=True)
        return target_dir
