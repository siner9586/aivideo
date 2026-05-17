from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import settings
router=APIRouter(prefix='/api')
@router.post('/upload')
async def upload(file: UploadFile = File(...)):
    ext=Path(file.filename or '').suffix.lower()
    if ext not in {'.png','.jpg','.jpeg','.webp'}: raise HTTPException(400,'unsupported image format')
    out=settings.upload_dir / f'{uuid4().hex}{ext}'
    data=await file.read()
    if len(data) > settings.max_upload_mb*1024*1024: raise HTTPException(400,'file too large')
    out.write_bytes(data); return {'path':str(out)}
