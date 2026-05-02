import re
from datetime import datetime

def sanitize_filename(title: str) -> str:
    """Remove illegal characters from a string so it can be used as a filename."""
    # Keep only alphanumerics, hyphens, and spaces
    safe_title = re.sub(r'[^\w\-\. ]', '_', title)
    # Collapse multiple spaces or underscores
    safe_title = re.sub(r'[_ ]+', '_', safe_title).strip('_')
    return safe_title[:100]  # Max 100 chars

def generate_filename(title: str, quality: str = "", ext: str = "mp4") -> str:
    """Generate a consistent filename format: title_date_quality.ext"""
    safe_title = sanitize_filename(title)
    date_str = datetime.now().strftime("%Y%m%d")
    
    parts = [safe_title, date_str]
    if quality:
        parts.append(quality)
        
    return f"{'_'.join(parts)}.{ext}"

def format_size(bytes_size: int) -> str:
    """Format bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"
