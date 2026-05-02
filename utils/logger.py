import os
import logging
from rich.logging import RichHandler
from rich.console import Console

# Shared console for Typer/Rich
console = Console()

def setup_logger(name: str = "Downloader", log_file: str = "app.log"):
    """Setup a rich logger with file backup."""
    # Create logs dir
    os.makedirs("logs", exist_ok=True)
    
    log_path = os.path.join("logs", log_file)

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(console=console, rich_tracebacks=True),
            logging.FileHandler(log_path, encoding='utf-8')
        ]
    )
    
    return logging.getLogger(name)

logger = setup_logger()
