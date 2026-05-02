import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from utils.file_manager import FileManager
from utils.logger import logger
from core.youtube import YouTubeDownloader
from core.instagram import InstagramDownloader
from core.viral_engine import ViralEngine

app = typer.Typer(help="CLI for Instagram & YouTube Downloader")
console = Console()
fm = FileManager()

@app.command()
def youtube(url: str, audio: bool = typer.Option(False, "--audio", "-a", help="Extract audio only")):
    """Download a YouTube video or playlist."""
    ydl = YouTubeDownloader(fm)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Downloading YouTube media...", total=None)
        try:
            result = ydl.download(url, audio_only=audio)
            progress.update(task, completed=100)
            if result.get("status") == "success":
                console.print(f"[green]✔ Downloaded:[/green] {result.get('title')}")
                console.print(f"[green]✔ Saved to:[/green] {result.get('file')}")
            elif result.get("status") == "skipped":
                console.print(f"[yellow]⚠ Skipped:[/yellow] Already downloaded ({result.get('id')})")
        except Exception as e:
            console.print(f"[red]✖ Error:[/red] {e}")

@app.command()
def instagram(
    url_or_username: str = typer.Argument(..., help="Instagram URL or username"),
    limit: int = typer.Option(10, "--limit", "-l", help="Number of posts to download if username is provided")
):
    """Download an Instagram post or latest profile posts."""
    ig = InstagramDownloader(fm)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[magenta]Downloading Instagram media...", total=None)
        try:
            result = ig.download(url_or_username, limit=limit)
            progress.update(task, completed=100)
            
            if result.get("status") == "batch":
                success_count = sum(1 for r in result["results"] if r.get("status") == "success")
                skipped_count = sum(1 for r in result["results"] if r.get("status") == "skipped")
                console.print(f"[green]✔ Batch completed.[/green] Downloaded: {success_count}, Skipped: {skipped_count}")
            else:
                if result.get("status") == "success":
                    console.print(f"[green]✔ Downloaded ID:[/green] {result.get('id')}")
                elif result.get("status") == "skipped":
                    console.print(f"[yellow]⚠ Skipped:[/yellow] {result.get('reason', 'Already downloaded')}")
        except Exception as e:
            console.print(f"[red]✖ Error:[/red] {e}")

@app.command()
def viral(
    username: str,
    limit: int = typer.Option(5, "--limit", "-l", help="Number of top viral posts to download"),
    analyze: int = typer.Option(50, "--analyze", "-a", help="Number of recent posts to analyze")
):
    """Analyze a profile and download its most viral videos."""
    ig = InstagramDownloader(fm)
    ve = ViralEngine(ig.L)
    
    console.print(f"[cyan]Analyzing profile: @{username}...[/cyan]")
    
    try:
        viral_posts = ve.get_top_viral_posts(username, limit=limit, analyze_last=analyze)
        
        if not viral_posts:
            console.print("[yellow]No video posts found or account is private without session.[/yellow]")
            return
            
        console.print(f"[green]Found {len(viral_posts)} top viral posts. Starting download...[/green]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[magenta]Downloading viral posts...", total=len(viral_posts))
            
            for vp in viral_posts:
                shortcode = vp['shortcode']
                er = vp['engagement_rate']
                progress.update(task, description=f"Downloading {shortcode} (ER: {er:.4f})")
                
                res = ig.download_post(shortcode, username)
                if res.get("status") == "success":
                    logger.info(f"Downloaded viral post {shortcode}")
                
                progress.advance(task)
                
        console.print("[green]✔ Viral downloads completed.[/green]")
        
    except Exception as e:
        console.print(f"[red]✖ Error:[/red] {e}")

if __name__ == "__main__":
    app()
