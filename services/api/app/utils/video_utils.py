"""Video utility functions."""
from __future__ import annotations
import cv2

def ratio_to_size(aspect_ratio: str, resolution: str) -> tuple[int,int]:
    h = {'480p':480,'720p':720,'1080p':1080}.get(resolution,720)
    ratios = {'16:9':(16,9),'9:16':(9,16),'1:1':(1,1),'5:2':(5,2)}
    rw,rh = ratios.get(aspect_ratio,(16,9))
    if rw >= rh:
        return int(h*rw/rh)//2*2, h
    return h, int(h*rh/rw)//2*2

def read_frames(video_path: str, max_frames: int = 120):
    cap = cv2.VideoCapture(video_path); frames=[]
    while len(frames)<max_frames:
        ok, frame = cap.read()
        if not ok: break
        frames.append(frame)
    cap.release(); return frames
