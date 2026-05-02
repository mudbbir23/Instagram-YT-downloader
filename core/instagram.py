import os
import instaloader
import asyncio
from typing import Dict, Any, List
from core.downloader import BaseDownloader
from utils.logger import logger
from utils.file_manager import FileManager
from services.auth_manager import InstagramAuthManager
from services.retry_handler import with_retry
from services.rate_limiter import ig_limiter

class InstagramDownloader(BaseDownloader):
    def __init__(self, file_manager: FileManager):
        self.fm = file_manager
        self.L = instaloader.Instaloader(
            download_pictures=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )
        self.auth = InstagramAuthManager(self.L)
        # Attempt loading existing session if any
        self.auth.login()

    @with_retry(max_retries=3, base_delay=5.0)
    def download_post(self, shortcode: str, username: str) -> Dict[str, Any]:
        """Download a specific post by shortcode."""
        ig_limiter.wait()
        
        if self.fm.is_downloaded("instagram", shortcode):
            logger.info(f"[Instagram] Post {shortcode} already downloaded. Skipping.")
            return {"status": "skipped", "id": shortcode}

        target_dir = self.fm.get_user_dir("instagram", username)
        
        try:
            post = instaloader.Post.from_shortcode(self.L.context, shortcode)
            if post.is_video:
                logger.info(f"[Instagram] Downloading video {shortcode} from {username}")
                # We dynamically change the target directory
                self.L.dirname_pattern = target_dir
                self.L.download_post(post, target=username)
                self.fm.mark_downloaded("instagram", shortcode)
                return {"status": "success", "id": shortcode}
            else:
                logger.info(f"[Instagram] Post {shortcode} is not a video. Skipping.")
                return {"status": "skipped", "reason": "not a video"}
        except Exception as e:
            logger.error(f"[Instagram] Failed to download {shortcode}: {e}")
            raise

    def download_profile(self, username: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Download the latest N videos from a profile."""
        ig_limiter.wait()
        logger.info(f"[Instagram] Fetching profile {username}...")
        
        results = []
        try:
            profile = instaloader.Profile.from_username(self.L.context, username)
            count = 0
            for post in profile.get_posts():
                if count >= limit:
                    break
                if post.is_video:
                    res = self.download_post(post.shortcode, username)
                    results.append(res)
                    count += 1
            return results
        except Exception as e:
            logger.error(f"[Instagram] Failed to fetch profile {username}: {e}")
            raise

    def download(self, url: str, **kwargs) -> Dict[str, Any]:
        """Determine if it's a profile or a single post."""
        # Very basic regex or splitting for URL routing
        if "instagram.com/p/" in url or "instagram.com/reel/" in url:
            # It's a post
            parts = url.strip('/').split('/')
            shortcode = parts[-1]
            return self.download_post(shortcode, "direct_links")
        else:
            # Assume it's a profile
            parts = [p for p in url.strip('/').split('/') if p]
            username = parts[-1]
            limit = kwargs.get("limit", 10)
            return {"status": "batch", "results": self.download_profile(username, limit)}

    async def async_download(self, url: str, **kwargs) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self.download(url, **kwargs))
