# Ultimate Downloader Platform

A production-ready, scalable media extractor for YouTube and Instagram built with Python. 
Features a fast CLI engine using `Typer` and a scalable background-processing Web UI using `FastAPI`.

## 🚀 Features

- **Instagram Bulk Engine:** Download Posts, Reels, IGTV, and full Profiles.
- **Viral Intelligence Mode:** Scrapes profile metrics, calculates Engagement Rate (ER), and extracts only the top viral videos!
- **YouTube Engine:** Wraps `yt-dlp` to merge highest quality streams, supports full playlists, channels, and audio-only extraction.
- **Smart Queue System:** Run multiple downloads concurrently in the background without blocking the UI.
- **Resilience:** Built-in Exponential Backoff Retries and Adaptive Rate Limiting to prevent IP bans.

## 📦 Setup & Installation

1. **Clone & Environment**
   ```bash
   git clone <your-repo>
   cd Instagram-YT-downloader
   python -m venv .venv
   source .venv/Scripts/activate  # On Windows
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Optional Instagram Auth**
   If you want to download from private profiles or avoid restrictive rate limits:
   - Login on a browser and extract cookies, OR
   - The CLI uses `instaloader`. The system looks for `session-username` defined in `config.yaml`.
   - Modify `services/auth_manager.py` if you wish to pass plaintext credentials (not recommended for production).

## 💻 Usage

### 1. CLI Interface
The CLI is beautifully formatted using `Rich`.

```bash
# YouTube Download
python main.py youtube "https://youtube.com/watch?v=..."
python main.py youtube "https://youtube.com/watch?v=..." --audio

# Instagram Standard Download
python main.py instagram "https://instagram.com/p/..."
python main.py instagram "username" --limit 20

# Instagram Viral Mode
python main.py viral "username" --limit 5 --analyze 50
```

### 2. Web UI (FastAPI)
The SaaS-ready Web UI allows managing downloads asynchronously.

```bash
python web_app.py
```
- Open `http://127.0.0.1:8000` in your browser.
- Use the modern Glassmorphism UI to queue YouTube links, Instagram links, or engage the Viral Engine.

## 🏗️ Architecture

```
/core         -> Downloader implementations (yt-dlp wrapper, instaloader wrapper, viral scoring).
/services     -> Resiliency layers (Queueing, Rate Limits, Exponential Backoff, Auth).
/utils        -> Formatting, IO ops, Loggers.
/interfaces   -> The presentation layer (CLI, Web API).
```

## 🚀 SaaS Scaling Roadmap

To transition this from a local tool to a production SaaS:
1. **Database:** Replace the JSON history file in `FileManager` with PostgreSQL.
2. **Queue:** Replace FastAPI `asyncio.Queue` with Celery or BullMQ + Redis.
3. **Storage:** Modify `FileManager` to upload downloaded files directly to AWS S3 / Cloudflare R2 instead of local disk.
4. **Proxies:** Integrate rotating residential proxies into `instaloader` and `yt-dlp` arguments to handle high traffic and avoid 429 errors.
5. **Auth:** Integrate Clerk or Supabase for user authentication.

## ⚠️ Security Considerations

- Never commit the `session` file or `.env` to GitHub.
- If accepting URLs from public users, sanitize and validate the URL structure to prevent SSRF (Server-Side Request Forgery). The current script does not deeply sanitize inputs assuming trusted CLI usage.
