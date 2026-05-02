import time
import asyncio
import random
from utils.logger import logger

class RateLimiter:
    def __init__(self, default_delay: float = 5.0, jitter: float = 2.0):
        """
        Rate limiter to prevent API bans.
        Uses a base delay with random jitter.
        """
        self.default_delay = default_delay
        self.jitter = jitter
        self.last_call_time = 0.0

    def _get_delay(self) -> float:
        """Calculate required delay with jitter."""
        elapsed = time.time() - self.last_call_time
        target_delay = self.default_delay + random.uniform(0, self.jitter)
        if elapsed < target_delay:
            return target_delay - elapsed
        return 0.0

    def wait(self):
        """Synchronous wait."""
        delay = self._get_delay()
        if delay > 0:
            logger.debug(f"[RateLimit] Throttling for {delay:.2f}s")
            time.sleep(delay)
        self.last_call_time = time.time()

    async def async_wait(self):
        """Asynchronous wait."""
        delay = self._get_delay()
        if delay > 0:
            logger.debug(f"[RateLimit] Throttling for {delay:.2f}s")
            await asyncio.sleep(delay)
        self.last_call_time = time.time()

# Global instances per platform
ig_limiter = RateLimiter(default_delay=6.0, jitter=3.0)
yt_limiter = RateLimiter(default_delay=1.0, jitter=0.5)
