"""In-memory queue plus JSONL persistence."""
from __future__ import annotations
from queue import Queue
from uuid import uuid4
from app.queue.task_store import GenerationTask, TaskStore

class JobQueue:
    def __init__(self, store: TaskStore | None = None) -> None:
        self.store = store or TaskStore()
        self.pending: Queue[str] = Queue()
    def submit_task(self, project_id: str | None, shot_id: str | None, backend: str, input_prompt: str, input_assets: list[str] | None = None, metadata: dict | None = None) -> GenerationTask:
        task = GenerationTask(task_id=uuid4().hex, project_id=project_id, shot_id=shot_id, backend=backend or 'mock', input_prompt=input_prompt, input_assets=input_assets or [], metadata=metadata or {})
        self.store.save_task(task); self.pending.put(task.task_id); return task
    def list_tasks(self) -> list[GenerationTask]: return self.store.list_tasks()
    def get_task(self, task_id: str) -> GenerationTask | None: return self.store.get_task(task_id)
    def cancel_task(self, task_id: str) -> GenerationTask:
        task = self.store.get_task(task_id)
        if not task: raise KeyError('task not found')
        if task.status in {'completed','failed'}: return task
        return self.store.update_task(task_id, status='cancelled', progress=0.0)
    def retry_task(self, task_id: str) -> GenerationTask:
        task = self.store.get_task(task_id)
        if not task: raise KeyError('task not found')
        task.status='pending'; task.progress=0.0; task.error_message=None; task.output_video_path=None
        self.store.save_task(task); self.pending.put(task.task_id); return task

_default_queue: JobQueue | None = None

def get_job_queue() -> JobQueue:
    global _default_queue
    if _default_queue is None: _default_queue = JobQueue()
    return _default_queue
