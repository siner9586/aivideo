from fastapi import APIRouter, HTTPException
from app.database import save_task, load_task
from app.models.schemas import TextToVideoRequest, ImageToVideoRequest, PostProcessSettings
from app.skills.text_to_video import generate_text_to_video
from app.skills.image_to_video import generate_image_to_video
from app.skills.post_processing import enhance_video
from app.skills.preference_scoring import save_human_feedback
router=APIRouter(prefix='/api')
@router.post('/generate/text-to-video')
def text_to_video(req: TextToVideoRequest):
    try:
        result=generate_text_to_video(req); save_task(result.task_id, result.model_dump()); return {'task_id':result.task_id,'status':result.status, 'result':result}
    except Exception as exc: raise HTTPException(400, str(exc))
@router.post('/generate/image-to-video')
def image_to_video(req: ImageToVideoRequest):
    try:
        result=generate_image_to_video(req); save_task(result.task_id, result.model_dump()); return {'task_id':result.task_id,'status':result.status,'result':result}
    except Exception as exc: raise HTTPException(400, str(exc))
@router.get('/tasks/{task_id}')
def task(task_id: str):
    item=load_task(task_id)
    if not item: raise HTTPException(404, 'task not found')
    return item
@router.post('/postprocess/{task_id}')
def postprocess(task_id: str, settings: PostProcessSettings):
    item=load_task(task_id)
    if not item: raise HTTPException(404, 'task not found')
    out=item['output_path'].replace('.mp4','_enhanced.mp4')
    res=enhance_video(item['output_path'], out, settings); item['postprocess']=res.model_dump(); save_task(task_id,item); return res
@router.post('/feedback/{task_id}')
def feedback(task_id: str, payload: dict): return {'path': save_human_feedback(task_id, payload)}
