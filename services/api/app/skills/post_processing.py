"""Video post-production operations with ffmpeg/OpenCV fallback."""
from __future__ import annotations
import shutil, zipfile
from pathlib import Path
import cv2
from app.models.schemas import PostProcessSettings, PostProcessResult
from app.utils.ffmpeg_utils import has_ffmpeg, run_ffmpeg

ASPECT_SIZE={'16:9':(1280,720),'9:16':(720,1280),'1:1':(720,720),'5:2':(1280,512)}

def resize_video(input_path, output_path, width, height):
    """Resize a video."""
    if has_ffmpeg(): run_ffmpeg(['-i',input_path,'-vf',f'scale={width}:{height}',output_path]); return output_path
    cap=cv2.VideoCapture(input_path); fps=cap.get(cv2.CAP_PROP_FPS) or 12; writer=cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width,height))
    while True:
        ok, f=cap.read()
        if not ok: break
        writer.write(cv2.resize(f,(width,height)))
    cap.release(); writer.release(); return output_path

def change_fps(input_path, output_path, fps):
    """Change output fps."""
    if has_ffmpeg(): run_ffmpeg(['-i',input_path,'-r',str(fps),output_path]); return output_path
    cap=cv2.VideoCapture(input_path); w=int(cap.get(3)); h=int(cap.get(4)); writer=cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w,h))
    while True:
        ok,f=cap.read()
        if not ok: break
        writer.write(f)
    cap.release(); writer.release(); return output_path

def add_subtitle(input_path, output_path, text, position='bottom'):
    """Add plain subtitle text."""
    cap=cv2.VideoCapture(input_path); fps=cap.get(cv2.CAP_PROP_FPS) or 12; w=int(cap.get(3)); h=int(cap.get(4)); writer=cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w,h))
    y=h-40 if position=='bottom' else 40
    while True:
        ok,f=cap.read()
        if not ok: break
        cv2.putText(f, text[:70], (30,y), cv2.FONT_HERSHEY_SIMPLEX, .7, (255,255,255), 2, cv2.LINE_AA); writer.write(f)
    cap.release(); writer.release(); return output_path

def compose_multi_shot_video(shot_paths, output_path, transitions=None):
    """Concatenate multiple videos."""
    first=cv2.VideoCapture(shot_paths[0]); fps=first.get(cv2.CAP_PROP_FPS) or 12; w=int(first.get(3)); h=int(first.get(4)); first.release()
    writer=cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w,h))
    for p in shot_paths:
        cap=cv2.VideoCapture(p)
        while True:
            ok,f=cap.read()
            if not ok: break
            writer.write(cv2.resize(f,(w,h)))
        cap.release()
    writer.release(); return output_path

def enhance_video(input_path, output_path, settings) -> PostProcessResult:
    """Apply selected post-process settings."""
    s=settings if isinstance(settings,PostProcessSettings) else PostProcessSettings(**settings); tmp=input_path; logs=[]
    if s.aspect_ratio and not (s.width and s.height): s.width,s.height=ASPECT_SIZE.get(s.aspect_ratio,(1280,720))
    if s.width and s.height: resize_video(tmp, output_path, s.width, s.height); tmp=output_path; logs.append('resized')
    if s.fps: change_fps(tmp, output_path, s.fps); logs.append('fps changed')
    if s.subtitle: add_subtitle(tmp, output_path, s.subtitle); logs.append('subtitle added')
    if not logs: shutil.copyfile(input_path, output_path); logs.append('copied without changes')
    return PostProcessResult(output_path=output_path, settings=s, logs=logs)

def export_project_package(task_id) -> str:
    """Export task metadata and outputs as zip."""
    out=Path('data/outputs')/f'{task_id}_package.zip'
    with zipfile.ZipFile(out,'w') as z:
        for p in Path('data/outputs').glob(f'{task_id}*'): z.write(p, p.name)
    return str(out)
