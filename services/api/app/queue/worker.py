"""Background worker for lightweight queue execution."""
from __future__ import annotations
import threading, time
from app.models.schemas import TextToVideoRequest
from app.queue.job_queue import JobQueue, get_job_queue
from app.skills.text_to_video import generate_text_to_video

class QueueWorker:
    def __init__(self, queue: JobQueue | None = None, poll_interval: float = 0.25) -> None:
        self.queue = queue or get_job_queue(); self.poll_interval = poll_interval
        self._stop = threading.Event(); self._thread: threading.Thread | None = None
    def start(self) -> None:
        if self._thread and self._thread.is_alive(): return
        self._thread = threading.Thread(target=self.run, daemon=True); self._thread.start()
    def stop(self) -> None: self._stop.set()
    def run_once(self) -> bool:
        if self.queue.pending.empty(): return False
        task_id = self.queue.pending.get(); task = self.queue.get_task(task_id)
        if not task or task.status == 'cancelled': return True
        try:
            self.queue.store.update_task(task_id, status='running', progress=0.1)
            req = TextToVideoRequest(prompt=task.input_prompt, backend=task.backend, duration=float(task.metadata.get('duration', 4)), fps=int(task.metadata.get('fps', 12)), aspect_ratio=task.metadata.get('aspect_ratio','16:9'), resolution=task.metadata.get('resolution','480p'), camera_motion=task.metadata.get('camera_motion','slow_push_in'))
            result = generate_text_to_video(req)
            self.queue.store.update_task(task_id, status='completed', progress=1.0, output_video_path=result.output_path, metadata={**task.metadata, 'result': result.model_dump()})
            if task.project_id and task.shot_id:
                try:
                    from app.projects.project_manager import get_project_manager
                    get_project_manager().update_shot(task.project_id, task.shot_id, {'status':'completed','output_video_path':result.output_path})
                except Exception:
                    pass
        except Exception as exc:
            self.queue.store.update_task(task_id, status='failed', progress=0.0, error_message=str(exc))
        return True
    def run(self) -> None:
        while not self._stop.is_set():
            if not self.run_once(): time.sleep(self.poll_interval)

_worker: QueueWorker | None = None

def start_default_worker() -> QueueWorker:
    global _worker
    if _worker is None:
        _worker = QueueWorker(); _worker.start()
    return _worker
