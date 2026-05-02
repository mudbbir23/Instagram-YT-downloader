import yt_dlp
import asyncio
from typing import Dict, Any
from core.downloader import BaseDownloader
from utils.logger import logger
from utils.file_manager import FileManager
from utils.formatter import generate_filename
from services.retry_handler import with_retry
from services.rate_limiter import yt_limiter

class YouTubeDownloader(BaseDownloader):
    def __init__(self, file_manager: FileManager):
        self.fm = file_manager

    def _get_opts(self, output_template: str, audio_only: bool) -> Dict[str, Any]:
        opts = {
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
        }
        if audio_only:
            opts['format'] = 'bestaudio/best'
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            opts['merge_output_format'] = 'mp4'
            
        return opts

    @with_retry(max_retries=3, base_delay=2.0)
    def download(self, url: str, audio_only: bool = False, **kwargs) -> Dict[str, Any]:
        yt_limiter.wait()
        
        # We need to extract info first to get the title and channel
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise Exception("Failed to extract video info")
            except Exception as e:
                logger.error(f"[YouTube] Info extraction failed: {e}")
                raise

        channel = info.get('uploader', 'unknown_channel')
        title = info.get('title', 'video')
        video_id = info.get('id', '')
        
        if self.fm.is_downloaded("youtube", video_id):
            logger.info(f"[YouTube] Video {video_id} already downloaded. Skipping.")
            return {"status": "skipped", "id": video_id}

        target_dir = self.fm.get_user_dir("youtube", channel)
        ext = "mp3" if audio_only else "mp4"
        filename = generate_filename(title, ext=ext)
        output_template = f"{target_dir}/{filename}"

        opts = self._get_opts(output_template, audio_only)
        
        logger.info(f"[YouTube] Downloading: {title} ({channel})")
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
            
        self.fm.mark_downloaded("youtube", video_id)
        logger.info(f"[YouTube] Download complete: {filename}")
        
        return {
            "status": "success",
            "id": video_id,
            "title": title,
            "file": output_template
        }

    async def async_download(self, url: str, audio_only: bool = False, **kwargs) -> Dict[str, Any]:
        """Run the sync download in a thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.download, url, audio_only)
