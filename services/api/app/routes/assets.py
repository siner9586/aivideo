from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.config import settings
router=APIRouter(prefix='/api')
@router.get('/assets/{task_id}/video')
def video(task_id: str):
    matches=list(Path(settings.output_dir).glob(f'{task_id}.mp4'))+list(Path(settings.output_dir).glob(f'{task_id}*.mp4'))
    if not matches: raise HTTPException(404,'video not found')
    return FileResponse(matches[0], media_type='video/mp4', filename=matches[0].name)
