from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.skills.prompt_templates import list_templates, get_template, apply_template

router = APIRouter(prefix='/api/templates', tags=['templates'])

class ApplyTemplateRequest(BaseModel):
    template_id: str
    idea: str = ''
    extra: str = ''

@router.get('')
def templates(category: str | None = None):
    return list_templates(category)

@router.get('/{template_id}')
def template(template_id: str):
    try:
        return get_template(template_id)
    except KeyError:
        raise HTTPException(404, 'template not found')

@router.post('/apply')
def apply(req: ApplyTemplateRequest):
    try:
        return apply_template(req.template_id, req.idea, req.extra)
    except KeyError:
        raise HTTPException(404, 'template not found')
