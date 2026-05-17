"""Video composition utilities for shot timeline export."""
from __future__ import annotations
import shutil
from pathlib import Path
from typing import Any
import cv2
import numpy as np
from app.config import settings
from app.projects.project_manager import get_project_manager
from app.utils.video_utils import ratio_to_size


def _placeholder_video(path: str | Path, title: str = 'Missing shot', width: int = 854, height: int = 480, fps: int = 12, seconds: float = 1.0) -> str:
    path = str(path)
    writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    for _ in range(max(2, int(fps * seconds))):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        cv2.putText(frame, title[:60], (32, height // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        writer.write(frame)
    writer.release()
    return path


def normalize_shot_video(input_path: str, output_path: str, width: int, height: int, fps: int) -> str:
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        return _placeholder_video(output_path, 'Missing or unreadable shot', width, height, fps)
    writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        writer.write(cv2.resize(frame, (width, height)))
    cap.release(); writer.release()
    return output_path


def concatenate_videos(video_paths: list[str], output_path: str) -> str:
    if not video_paths:
        return _placeholder_video(output_path, 'No generated shots')
    first = cv2.VideoCapture(video_paths[0])
    fps = int(first.get(cv2.CAP_PROP_FPS) or 12)
    width = int(first.get(cv2.CAP_PROP_FRAME_WIDTH) or 854)
    height = int(first.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)
    first.release()
    writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    for path in video_paths:
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            continue
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            writer.write(cv2.resize(frame, (width, height)))
        cap.release()
    writer.release()
    return output_path


def add_opening_title(input_path: str, output_path: str, title: str) -> str:
    cap = cv2.VideoCapture(input_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS) or 12); width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 854); height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)
    writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    for _ in range(fps):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        cv2.putText(frame, title[:50], (40, height // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        writer.write(frame)
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        writer.write(cv2.resize(frame, (width, height)))
    cap.release(); writer.release()
    return output_path


def add_ending_card(input_path: str, output_path: str, text: str) -> str:
    cap = cv2.VideoCapture(input_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS) or 12); width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 854); height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)
    writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        writer.write(cv2.resize(frame, (width, height)))
    for _ in range(fps):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        cv2.putText(frame, text[:50], (40, height // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        writer.write(frame)
    cap.release(); writer.release()
    return output_path


def compose_project_video(project_id: str, settings_payload: dict[str, Any] | None = None) -> dict:
    settings_payload = settings_payload or {}
    manager = get_project_manager(); project = manager.get_project(project_id)
    if not project:
        raise KeyError('project not found')
    default_w, default_h = ratio_to_size(project.generation_settings.get('aspect_ratio', '16:9'), project.generation_settings.get('resolution', '480p'))
    width = int(settings_payload.get('width') or default_w); height = int(settings_payload.get('height') or default_h)
    fps = int(settings_payload.get('fps') or project.generation_settings.get('fps', 12))
    out_dir = manager.project_dir(project_id) / 'outputs'; normalized = []
    for idx, shot in enumerate(project.shots):
        src = shot.output_video_path; dst = out_dir / f'normalized_{idx+1:02d}.mp4'
        if src and Path(src).exists():
            normalize_shot_video(src, str(dst), width, height, fps)
        else:
            _placeholder_video(dst, shot.title, width, height, fps, shot.duration)
        normalized.append(str(dst))
    composed = out_dir / 'composed.mp4'; concatenate_videos(normalized, str(composed))
    final = composed
    if settings_payload.get('title'):
        titled = out_dir / 'composed_title.mp4'; add_opening_title(str(final), str(titled), settings_payload['title']); final = titled
    if settings_payload.get('ending_text'):
        ended = out_dir / 'final.mp4'; add_ending_card(str(final), str(ended), settings_payload['ending_text']); final = ended
    project.output_videos.append(str(final)); manager.save_project(project)
    return {'project_id': project_id, 'output_video_path': str(final), 'shots': normalized}


def export_project_zip(project_id: str) -> str:
    return get_project_manager().export_project(project_id)
