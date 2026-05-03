import yt_dlp
import asyncio
from typing import Dict, Any
from core.downloader import BaseDownloader
from utils.logger import logger
from utils.file_manager import FileManager
from utils.formatter import generate_filename
from services.retry_handler import with_retry
from services.rate_limiter import yt_limiter  # Reusing rate limiter or we can create a new one, but yt_limiter works fine.

class TikTokDownloader(BaseDownloader):
    def __init__(self, file_manager: FileManager):
        self.fm = file_manager

    def _get_opts(self, output_template: str) -> Dict[str, Any]:
        opts = {
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            # TikTok specific opts to try and get best video
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4'
        }
        return opts

    @with_retry(max_retries=3, base_delay=2.0)
    def download(self, url: str, **kwargs) -> Dict[str, Any]:
        yt_limiter.wait()
        
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise Exception("Failed to extract video info")
            except Exception as e:
                logger.error(f"[TikTok] Info extraction failed: {e}")
                raise

        uploader = info.get('uploader', 'unknown_user')
        title = info.get('title', 'tiktok_video')
        video_id = info.get('id', '')
        
        if self.fm.is_downloaded("tiktok", video_id):
            logger.info(f"[TikTok] Video {video_id} already downloaded. Skipping.")
            return {"status": "skipped", "id": video_id}

        target_dir = self.fm.get_user_dir("tiktok", uploader)
        filename = generate_filename(title, ext="mp4")
        output_template = f"{target_dir}/{filename}"

        opts = self._get_opts(output_template)
        
        logger.info(f"[TikTok] Downloading: {title} ({uploader})")
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
            
        self.fm.mark_downloaded("tiktok", video_id)
        logger.info(f"[TikTok] Download complete: {filename}")
        
        return {
            "status": "success",
            "id": video_id,
            "title": title,
            "file": output_template
        }

    async def async_download(self, url: str, **kwargs) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.download, url)
