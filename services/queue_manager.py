import asyncio
from typing import Dict, Any, Callable
from utils.logger import logger

class DownloadTask:
    def __init__(self, task_id: str, platform: str, url: str, coro: Callable):
        self.task_id = task_id
        self.platform = platform
        self.url = url
        self.coro = coro
        self.status = "pending" # pending, running, completed, failed
        self.result = None

class QueueManager:
    def __init__(self, max_concurrent: int = 3):
        self.queue = asyncio.Queue()
        self.tasks: Dict[str, DownloadTask] = {}
        self.max_concurrent = max_concurrent
        self.workers = []
        self._is_running = False

    async def add_task(self, task_id: str, platform: str, url: str, coro: Callable):
        task = DownloadTask(task_id, platform, url, coro)
        self.tasks[task_id] = task
        await self.queue.put(task)
        logger.info(f"[Queue] Added task {task_id} for {url}")
        return task_id

    def get_status(self, task_id: str) -> Dict[str, Any]:
        task = self.tasks.get(task_id)
        if not task:
            return {"error": "Task not found"}
        return {
            "task_id": task.task_id,
            "platform": task.platform,
            "url": task.url,
            "status": task.status,
            "result": task.result
        }

    def get_all_statuses(self) -> Dict[str, Any]:
        return {tid: self.get_status(tid) for tid in self.tasks}

    async def _worker(self):
        while self._is_running:
            try:
                task: DownloadTask = await self.queue.get()
                task.status = "running"
                logger.info(f"[Queue] Starting task {task.task_id}")
                
                try:
                    # Execute the coroutine
                    res = await task.coro()
                    task.status = "completed"
                    task.result = res
                    logger.info(f"[Queue] Completed task {task.task_id}")
                except Exception as e:
                    task.status = "failed"
                    task.result = str(e)
                    logger.error(f"[Queue] Failed task {task.task_id}: {e}")
                finally:
                    self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[Queue] Worker error: {e}")

    def start(self):
        if not self._is_running:
            self._is_running = True
            for _ in range(self.max_concurrent):
                worker = asyncio.create_task(self._worker())
                self.workers.append(worker)
            logger.info(f"[Queue] Started {self.max_concurrent} workers.")

    async def stop(self):
        self._is_running = False
        for worker in self.workers:
            worker.cancel()
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers = []
        logger.info("[Queue] Stopped workers.")

# Global instance for the FastAPI app
queue_manager = QueueManager()
