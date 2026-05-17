from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.projects.project_manager import get_project_manager

router = APIRouter(prefix='/api/projects', tags=['projects'])

@router.post('')
def create_project(payload: dict):
    return get_project_manager().create_project(payload)

@router.get('')
def list_projects():
    return get_project_manager().list_projects()

@router.get('/{project_id}')
def get_project(project_id: str):
    item = get_project_manager().get_project(project_id)
    if not item:
        raise HTTPException(404, 'project not found')
    return item

@router.put('/{project_id}')
def update_project(project_id: str, payload: dict):
    try:
        return get_project_manager().update_project(project_id, payload)
    except KeyError:
        raise HTTPException(404, 'project not found')

@router.delete('/{project_id}')
def delete_project(project_id: str):
    return {'deleted': get_project_manager().delete_project(project_id)}

@router.post('/{project_id}/shots')
def add_shot(project_id: str, payload: dict):
    try:
        return get_project_manager().add_shot(project_id, payload)
    except KeyError:
        raise HTTPException(404, 'project not found')

@router.put('/{project_id}/shots/{shot_id}')
def update_shot(project_id: str, shot_id: str, payload: dict):
    try:
        return get_project_manager().update_shot(project_id, shot_id, payload)
    except KeyError as exc:
        raise HTTPException(404, str(exc))

@router.delete('/{project_id}/shots/{shot_id}')
def delete_shot(project_id: str, shot_id: str):
    try:
        return {'deleted': get_project_manager().delete_shot(project_id, shot_id)}
    except KeyError as exc:
        raise HTTPException(404, str(exc))

@router.post('/{project_id}/save')
def save_project(project_id: str):
    item = get_project_manager().get_project(project_id)
    if not item:
        raise HTTPException(404, 'project not found')
    return get_project_manager().save_project(item)

@router.post('/{project_id}/export')
def export_project(project_id: str):
    try:
        path = get_project_manager().export_project(project_id)
        return FileResponse(path, media_type='application/zip', filename=f'{project_id}.zip')
    except KeyError:
        raise HTTPException(404, 'project not found')
