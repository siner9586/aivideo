"""Runnable OpenCV mock backend for CPU-only demos."""
from __future__ import annotations
import math, textwrap
from uuid import uuid4
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont
from app.backends.base import VideoBackend
from app.config import settings
from app.models.schemas import TextToVideoRequest, ImageToVideoRequest, VideoGenerationResult
from app.utils.video_utils import ratio_to_size

FONT = ImageFont.load_default()

def _put_text(frame: np.ndarray, lines: list[str]) -> np.ndarray:
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)); d=ImageDraw.Draw(img)
    y=24
    for line in lines:
        d.text((24,y), line[:110], fill=(255,255,255), font=FONT); y += 22
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def _transform(img: np.ndarray, i: int, total: int, motion: str) -> np.ndarray:
    h,w = img.shape[:2]; t = i/max(total-1,1)
    zoom = 1.0
    dx=dy=0
    if motion in {'slow_push_in','zoom_in','close_up'}: zoom = 1+0.10*t
    if motion in {'pull_back','zoom_out'}: zoom = 1.10-0.10*t
    if motion in {'pan_left'}: dx = int(-35*t)
    if motion in {'pan_right'}: dx = int(35*t)
    if motion in {'tilt_up'}: dy = int(-28*t)
    if motion in {'tilt_down'}: dy = int(28*t)
    M = cv2.getRotationMatrix2D((w/2,h/2), 0, zoom); M[:,2] += (dx,dy)
    return cv2.warpAffine(img, M, (w,h), borderMode=cv2.BORDER_REFLECT)

class MockVideoBackend(VideoBackend):
    name='mock'
    def _write(self, frames: list[np.ndarray], path: str, fps: int) -> None:
        h,w = frames[0].shape[:2]
        writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w,h))
        for f in frames: writer.write(f)
        writer.release()
    def generate_text(self, request: TextToVideoRequest) -> VideoGenerationResult:
        w,h = ratio_to_size(request.aspect_ratio, request.resolution); fps=request.fps; total=int((request.num_frames or request.duration*fps))
        out = settings.output_dir / f"{uuid4().hex}.mp4"; motion=request.camera_motion or 'slow_push_in'
        frames=[]
        for i in range(total):
            t=i/max(total-1,1); x=np.linspace(0,1,w); y=np.linspace(0,1,h)[:,None]
            b=(80+70*x+30*math.sin(t*math.pi)).astype(np.uint8); g=(60+80*y).astype(np.uint8); r=(90+80*(1-x)+40*t).astype(np.uint8)
            frame=np.dstack([np.tile(b,(h,1)),np.tile(g,(1,w)),np.tile(r,(h,1))])
            frame=_transform(frame,i,total,motion)
            lines=['AI Video Studio Demo', f'shot: 1 | camera: {motion}', *textwrap.wrap(request.prompt, 46)[:4]]
            frames.append(_put_text(frame, lines))
        self._write(frames, str(out), fps)
        return VideoGenerationResult(task_id=out.stem, output_path=str(out), preview_url=f'/api/assets/{out.stem}/video', metadata={'backend':'mock','fps':fps,'frames':total}, logs=['mock text-to-video completed'])
    def generate_image(self, request: ImageToVideoRequest) -> VideoGenerationResult:
        w,h=ratio_to_size(request.aspect_ratio, request.resolution); fps=request.fps; total=int(request.duration*fps)
        img=cv2.imread(request.image_path)
        if img is None: raise ValueError('invalid image_path')
        img=cv2.resize(img,(w,h)); out=settings.output_dir / f"{uuid4().hex}.mp4"; frames=[]
        for i in range(total):
            frame=_transform(img,i,total,request.motion_type)
            frames.append(_put_text(frame,['AI Video Studio Demo',f'image-to-video | camera: {request.motion_type}',*textwrap.wrap(request.prompt,48)[:3]]))
        self._write(frames,str(out),fps)
        return VideoGenerationResult(task_id=out.stem, output_path=str(out), preview_url=f'/api/assets/{out.stem}/video', metadata={'backend':'mock-i2v'}, logs=['mock image-to-video completed'])
