from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.queue.job_queue import get_job_queue
from app.queue.worker import start_default_worker

router = APIRouter(prefix='/api/queue', tags=['queue'])
start_default_worker()

class QueueSubmitRequest(BaseModel):
    project_id: str | None = None
    shot_id: str | None = None
    backend: str = 'mock'
    input_prompt: str = ''
    input_assets: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

@router.post('/submit')
def submit(req: QueueSubmitRequest):
    if not req.input_prompt.strip():
        raise HTTPException(400, 'input_prompt is required')
    return get_job_queue().submit_task(req.project_id, req.shot_id, req.backend, req.input_prompt, req.input_assets, req.metadata)

@router.get('/tasks')
def tasks():
    return get_job_queue().list_tasks()

@router.get('/tasks/{task_id}')
def task(task_id: str):
    item = get_job_queue().get_task(task_id)
    if not item:
        raise HTTPException(404, 'task not found')
    return item

@router.post('/tasks/{task_id}/cancel')
def cancel(task_id: str):
    try:
        return get_job_queue().cancel_task(task_id)
    except KeyError:
        raise HTTPException(404, 'task not found')

@router.post('/tasks/{task_id}/retry')
def retry(task_id: str):
    try:
        return get_job_queue().retry_task(task_id)
    except KeyError:
        raise HTTPException(404, 'task not found')
