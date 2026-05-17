from fastapi import APIRouter, UploadFile, File, HTTPException
from app.skills.asset_manager import get_asset_manager

router = APIRouter(prefix='/api', tags=['assets'])

@router.post('/upload')
async def upload(file: UploadFile = File(...)):
    data = await file.read()
    try:
        rec = get_asset_manager().save_upload_bytes(file.filename or 'upload.bin', data)
        return {'path': rec.path, 'asset': rec}
    except ValueError as exc:
        raise HTTPException(400, str(exc))

@router.post('/assets/upload')
async def upload_asset(file: UploadFile = File(...), project_id: str | None = None, shot_id: str | None = None):
    data = await file.read()
    try:
        return get_asset_manager().save_upload_bytes(file.filename or 'upload.bin', data, project_id, shot_id)
    except ValueError as exc:
        raise HTTPException(400, str(exc))

@router.get('/assets')
def assets():
    return get_asset_manager().list_assets()

@router.get('/assets/{asset_id}')
def asset(asset_id: str):
    item = get_asset_manager().get_asset(asset_id)
    if not item:
        raise HTTPException(404, 'asset not found')
    return item

@router.delete('/assets/{asset_id}')
def delete_asset(asset_id: str):
    return {'deleted': get_asset_manager().delete_asset(asset_id)}

@router.post('/projects/{project_id}/assets/{asset_id}')
def bind_project(project_id: str, asset_id: str):
    try:
        return get_asset_manager().bind_to_project(project_id, asset_id)
    except KeyError as exc:
        raise HTTPException(404, str(exc))

@router.post('/projects/{project_id}/shots/{shot_id}/assets/{asset_id}')
def bind_shot(project_id: str, shot_id: str, asset_id: str):
    try:
        return get_asset_manager().bind_to_shot(project_id, shot_id, asset_id)
    except KeyError as exc:
        raise HTTPException(404, str(exc))
