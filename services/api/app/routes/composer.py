from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.skills.video_composer import compose_project_video, export_project_zip

router = APIRouter(prefix='/api/composer', tags=['composer'])

@router.post('/{project_id}/compose')
def compose(project_id: str, settings: dict | None = None):
    try:
        return compose_project_video(project_id, settings or {})
    except KeyError:
        raise HTTPException(404, 'project not found')

@router.post('/{project_id}/export')
def export(project_id: str):
    try:
        path = export_project_zip(project_id)
        return FileResponse(path, media_type='application/zip', filename=f'{project_id}.zip')
    except KeyError:
        raise HTTPException(404, 'project not found')
