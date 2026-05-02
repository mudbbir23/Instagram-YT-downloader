import time
import asyncio
from functools import wraps
from utils.logger import logger

def with_retry(max_retries: int = 3, base_delay: float = 2.0, exception_types: tuple = (Exception,)):
    """
    Decorator for exponential backoff retries.
    Works for both synchronous and asynchronous functions.
    """
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                retries = 0
                while retries < max_retries:
                    try:
                        return await func(*args, **kwargs)
                    except exception_types as e:
                        retries += 1
                        if retries == max_retries:
                            logger.error(f"[Retry] Max retries reached for {func.__name__}. Error: {e}")
                            raise
                        delay = base_delay * (2 ** (retries - 1))
                        logger.warning(f"[Retry] Error in {func.__name__}: {e}. Retrying in {delay}s ({retries}/{max_retries})")
                        await asyncio.sleep(delay)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                retries = 0
                while retries < max_retries:
                    try:
                        return func(*args, **kwargs)
                    except exception_types as e:
                        retries += 1
                        if retries == max_retries:
                            logger.error(f"[Retry] Max retries reached for {func.__name__}. Error: {e}")
                            raise
                        delay = base_delay * (2 ** (retries - 1))
                        logger.warning(f"[Retry] Error in {func.__name__}: {e}. Retrying in {delay}s ({retries}/{max_retries})")
                        time.sleep(delay)
            return sync_wrapper
    return decorator
