from fastapi import APIRouter
from pydantic import BaseModel
from app.skills.prompt_parser import parse_prompt
from app.skills.storyboard_planner import plan_storyboard
router=APIRouter(prefix='/api')
class StoryIn(BaseModel): prompt: str; num_shots: int|None=None
@router.post('/storyboard')
def storyboard(body: StoryIn):
    return plan_storyboard(parse_prompt(body.prompt), body.num_shots)
