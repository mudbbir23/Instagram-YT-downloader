from fastapi import FastAPI, Request, BackgroundTasks, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import uuid
import os

from utils.file_manager import FileManager
from core.youtube import YouTubeDownloader
from core.instagram import InstagramDownloader
from core.tiktok import TikTokDownloader
from core.thumbnail import ThumbnailDownloader
from core.viral_engine import ViralEngine
from services.queue_manager import queue_manager

app = FastAPI(title="Instagram & YouTube Downloader API")

# Ensure templates directory exists
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(templates_dir, exist_ok=True)
templates = Jinja2Templates(directory=templates_dir)

fm = FileManager()
yt_downloader = YouTubeDownloader(fm)
ig_downloader = InstagramDownloader(fm)
tk_downloader = TikTokDownloader(fm)
th_downloader = ThumbnailDownloader(fm)

@app.on_event("startup")
async def startup_event():
    queue_manager.start()

@app.on_event("shutdown")
async def shutdown_event():
    await queue_manager.stop()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/api/download/youtube")
async def api_download_youtube(url: str = Form(...), audio_only: bool = Form(False)):
    task_id = str(uuid.uuid4())
    
    async def _yt_task():
        return await yt_downloader.async_download(url, audio_only=audio_only)
        
    await queue_manager.add_task(task_id, "youtube", url, _yt_task)
    return {"status": "queued", "task_id": task_id}

@app.post("/api/download/tiktok")
async def api_download_tiktok(url: str = Form(...)):
    task_id = str(uuid.uuid4())
    
    async def _tk_task():
        return await tk_downloader.async_download(url)
        
    await queue_manager.add_task(task_id, "tiktok", url, _tk_task)
    return {"status": "queued", "task_id": task_id}

@app.post("/api/download/thumbnail")
async def api_download_thumbnail(url: str = Form(...)):
    task_id = str(uuid.uuid4())

    async def _thumb_task():
        return await th_downloader.async_download(url)

    await queue_manager.add_task(task_id, "thumbnail", url, _thumb_task)
    return {"status": "queued", "task_id": task_id}

@app.post("/api/download/instagram")
async def api_download_instagram(url: str = Form(...), limit: int = Form(10)):
    task_id = str(uuid.uuid4())
    
    async def _ig_task():
        return await ig_downloader.async_download(url, limit=limit)
        
    await queue_manager.add_task(task_id, "instagram", url, _ig_task)
    return {"status": "queued", "task_id": task_id}

@app.post("/api/download/viral")
async def api_download_viral(username: str = Form(...), limit: int = Form(5), analyze: int = Form(50)):
    task_id = str(uuid.uuid4())
    
    # Extract raw username from input (handles URLs and @mentions)
    clean_username = username.strip().strip('/')
    if 'instagram.com' in clean_username:
        clean_username = [p for p in clean_username.split('/') if p][-1]
    if clean_username.startswith('@'):
        clean_username = clean_username[1:]
        
    async def _viral_task():
        ve = ViralEngine(ig_downloader.L)
        viral_posts = ve.get_top_viral_posts(clean_username, limit=limit, analyze_last=analyze)
        results = []
        for vp in viral_posts:
            # Running sync in a thread executor or directly here since it's in a queue worker
            res = ig_downloader.download_post(vp['shortcode'], clean_username)
            results.append(res)
        return {"status": "batch", "results": results}
        
    await queue_manager.add_task(task_id, "viral", clean_username, _viral_task)
    return {"status": "queued", "task_id": task_id}

@app.get("/api/status")
async def api_status():
    return queue_manager.get_all_statuses()

@app.get("/api/status/{task_id}")
async def api_status_id(task_id: str):
    return queue_manager.get_status(task_id)
