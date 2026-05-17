from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.skills.quality_evaluator import evaluate_video, evaluate_project, compare_candidates

router = APIRouter(prefix='/api/quality', tags=['quality'])

class EvaluateRequest(BaseModel):
    video_path: str
    prompt_spec: dict = Field(default_factory=dict)

@router.post('/evaluate')
def evaluate(req: EvaluateRequest):
    return evaluate_video(req.video_path, req.prompt_spec)

@router.post('/project/{project_id}')
def project(project_id: str):
    try:
        return evaluate_project(project_id)
    except KeyError:
        raise HTTPException(404, 'project not found')

@router.post('/compare')
def compare(payload: dict):
    return compare_candidates(payload.get('candidate_paths', []))
