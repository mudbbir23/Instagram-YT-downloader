from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseDownloader(ABC):
    """Abstract base class for downloaders."""
    
    @abstractmethod
    def download(self, url: str, **kwargs) -> Dict[str, Any]:
        """Download media from the given URL."""
        pass

    @abstractmethod
    async def async_download(self, url: str, **kwargs) -> Dict[str, Any]:
        """Asynchronously download media from the given URL."""
        pass
