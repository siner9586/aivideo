from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.skills.video_composer import compose_project_video, export_project_zip, export_upload_ready_video

router = APIRouter(prefix='/api/composer', tags=['composer'])


class UploadReadyExportRequest(BaseModel):
    input_path: str = Field(..., description='Path of a composed MP4 on the backend filesystem.')
    output_path: str | None = Field(None, description='Optional output path. Defaults to *_upload_ready.mp4 next to input.')
    platform: str = Field('hongguo', description='hongguo, douyin, kuaishou, or generic_vertical.')


@router.post('/{project_id}/compose')
def compose(project_id: str, settings: dict | None = None):
    try:
        return compose_project_video(project_id, settings or {})
    except KeyError:
        raise HTTPException(404, 'project not found')


@router.post('/export-upload-ready')
def export_upload_ready(body: UploadReadyExportRequest):
    try:
        return export_upload_ready_video(body.input_path, body.output_path, body.platform)
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc))


@router.post('/{project_id}/export')
@router.get('/{project_id}/export')
def export(project_id: str):
    try:
        path = export_project_zip(project_id)
        return FileResponse(path, media_type='application/zip', filename=f'{project_id}.zip')
    except KeyError:
        raise HTTPException(404, 'project not found')
