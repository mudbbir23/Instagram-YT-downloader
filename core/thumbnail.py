import re
import os
import asyncio
import urllib.request
from typing import Dict, Any
from utils.logger import logger
from utils.file_manager import FileManager


# YouTube thumbnail quality levels, highest first
THUMB_QUALITIES = [
    ("maxresdefault", "HD 1280x720"),
    ("sddefault",     "SD 640x480"),
    ("hqdefault",     "HQ 480x360"),
    ("mqdefault",     "MQ 320x180"),
    ("default",       "Default 120x90"),
]


def _extract_video_id(url: str) -> str:
    """Extract the 11-char video ID from any YouTube URL format."""
    patterns = [
        r"(?:v=|youtu\.be/|/embed/|/shorts/)([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract a YouTube video ID from: {url}")


class ThumbnailDownloader:
    def __init__(self, file_manager: FileManager):
        self.fm = file_manager

    def download(self, url: str, **kwargs) -> Dict[str, Any]:
        video_id = _extract_video_id(url)

        target_dir = self.fm.get_user_dir("thumbnails", "youtube")
        os.makedirs(target_dir, exist_ok=True)

        downloaded_quality = None
        saved_path = None

        for quality_key, quality_label in THUMB_QUALITIES:
            thumb_url = f"https://img.youtube.com/vi/{video_id}/{quality_key}.jpg"
            save_path = os.path.join(target_dir, f"{video_id}_{quality_key}.jpg")

            try:
                logger.info(f"[Thumbnail] Trying quality '{quality_label}' for {video_id}")
                req = urllib.request.Request(
                    thumb_url,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = response.read()
                    # YouTube returns a tiny 120×90 placeholder for missing qualities
                    if len(data) < 2000:
                        logger.info(f"[Thumbnail] '{quality_label}' not available (placeholder), trying next…")
                        continue
                    with open(save_path, "wb") as f:
                        f.write(data)
                downloaded_quality = quality_label
                saved_path = save_path
                break
            except Exception as e:
                logger.warning(f"[Thumbnail] Failed fetching '{quality_key}': {e}")
                continue

        if not saved_path:
            raise RuntimeError(f"No thumbnail could be downloaded for video: {video_id}")

        logger.info(f"[Thumbnail] Saved {downloaded_quality} thumbnail → {saved_path}")
        return {
            "status": "success",
            "video_id": video_id,
            "quality": downloaded_quality,
            "file": saved_path,
        }

    async def async_download(self, url: str, **kwargs) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.download, url)
