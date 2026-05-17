from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.skills.prompt_parser import parse_prompt
router=APIRouter(prefix='/api')
class ParseIn(BaseModel): prompt: str
@router.post('/parse')
def parse(body: ParseIn):
    try: return parse_prompt(body.prompt)
    except Exception as exc: raise HTTPException(400, str(exc))
