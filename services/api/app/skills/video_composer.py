"""Video composition utilities for shot timeline export."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np

from app.skills.cinematic_prompt_compiler import get_delivery_profile
from app.config import settings
from app.projects.project_manager import get_project_manager
from app.utils.ffmpeg_utils import has_ffmpeg, run_ffmpeg
from app.utils.video_utils import ratio_to_size


def _placeholder_video(path: str | Path, title: str = "Missing shot", width: int = 854, height: int = 480, fps: int = 12, seconds: float = 1.0) -> str:
    path = str(path)
    writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    for _ in range(max(2, int(fps * seconds))):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        cv2.putText(frame, title[:60], (32, height // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        writer.write(frame)
    writer.release()
    return path


def normalize_shot_video(input_path: str, output_path: str, width: int, height: int, fps: int) -> str:
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        return _placeholder_video(output_path, "Missing or unreadable shot", width, height, fps)
    writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        writer.write(cv2.resize(frame, (width, height)))
    cap.release()
    writer.release()
    return output_path


def concatenate_videos(video_paths: list[str], output_path: str) -> str:
    if not video_paths:
        return _placeholder_video(output_path, "No generated shots")
    first = cv2.VideoCapture(video_paths[0])
    fps = int(first.get(cv2.CAP_PROP_FPS) or 12)
    width = int(first.get(cv2.CAP_PROP_FRAME_WIDTH) or 854)
    height = int(first.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)
    first.release()
    writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
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
    fps = int(cap.get(cv2.CAP_PROP_FPS) or 12)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 854)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)
    writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    for _ in range(fps):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        cv2.putText(frame, title[:50], (40, height // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        writer.write(frame)
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        writer.write(cv2.resize(frame, (width, height)))
    cap.release()
    writer.release()
    return output_path


def add_ending_card(input_path: str, output_path: str, text: str) -> str:
    cap = cv2.VideoCapture(input_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS) or 12)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 854)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)
    writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        writer.write(cv2.resize(frame, (width, height)))
    for _ in range(fps):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        cv2.putText(frame, text[:50], (40, height // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        writer.write(frame)
    cap.release()
    writer.release()
    return output_path


def compose_project_video(project_id: str, settings_payload: dict[str, Any] | None = None) -> dict:
    settings_payload = settings_payload or {}
    manager = get_project_manager()
    project = manager.get_project(project_id)
    if not project:
        raise KeyError("project not found")
    default_w, default_h = ratio_to_size(
        project.generation_settings.get("aspect_ratio", "16:9"),
        project.generation_settings.get("resolution", "480p"),
    )
    width = int(settings_payload.get("width") or default_w)
    height = int(settings_payload.get("height") or default_h)
    fps = int(settings_payload.get("fps") or project.generation_settings.get("fps", 12))
    out_dir = manager.project_dir(project_id) / "outputs"
    normalized = []
    for idx, shot in enumerate(project.shots):
        src = shot.output_video_path
        dst = out_dir / f"normalized_{idx+1:02d}.mp4"
        if src and Path(src).exists():
            normalize_shot_video(src, str(dst), width, height, fps)
        else:
            _placeholder_video(dst, shot.title, width, height, fps, shot.duration)
        normalized.append(str(dst))
    composed = out_dir / "composed.mp4"
    concatenate_videos(normalized, str(composed))
    final = composed
    if settings_payload.get("title"):
        titled = out_dir / "composed_title.mp4"
        add_opening_title(str(final), str(titled), settings_payload["title"])
        final = titled
    if settings_payload.get("ending_text"):
        ended = out_dir / "final.mp4"
        add_ending_card(str(final), str(ended), settings_payload["ending_text"])
        final = ended
    project.output_videos.append(str(final))
    manager.save_project(project)
    return {"project_id": project_id, "output_video_path": str(final), "shots": normalized}


def export_upload_ready_video(input_path: str, output_path: str | None = None, platform: str = "hongguo") -> dict[str, Any]:
    """Normalize a composed video into a conservative vertical upload MP4.

    FFmpeg is used when available so the output is H.264/AAC with faststart.
    OpenCV fallback keeps the project runnable in CPU-only demo environments,
    but the codec will depend on the local OpenCV build.
    """
    source = Path(input_path)
    if not source.exists():
        raise FileNotFoundError(f"input video not found: {input_path}")
    profile = get_delivery_profile(platform)
    out = Path(output_path) if output_path else source.with_name(f"{source.stem}_{platform}_upload_ready.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)
    logs: list[str] = []
    if has_ffmpeg():
        vf = (
            f"scale={profile['width']}:{profile['height']}:force_original_aspect_ratio=decrease,"
            f"pad={profile['width']}:{profile['height']}:(ow-iw)/2:(oh-ih)/2,"
            f"format={profile['pixel_format']}"
        )
        run_ffmpeg(
            [
                "-i",
                str(source),
                "-vf",
                vf,
                "-r",
                str(profile["fps"]),
                "-c:v",
                "libx264",
                "-profile:v",
                "high",
                "-level:v",
                "4.2",
                "-pix_fmt",
                profile["pixel_format"],
                "-movflags",
                "+faststart",
                "-c:a",
                "aac",
                "-ar",
                str(profile["audio_sample_rate"]),
                "-b:a",
                "160k",
                str(out),
            ]
        )
        logs.append("ffmpeg h264/aac export completed")
    else:
        normalize_shot_video(str(source), str(out), int(profile["width"]), int(profile["height"]), int(profile["fps"]))
        logs.append("opencv fallback export completed; install ffmpeg for h264/aac faststart")
    return {
        "input_path": str(source),
        "output_path": str(out),
        "platform": platform,
        "delivery_profile": profile,
        "logs": logs,
    }


def export_project_zip(project_id: str) -> str:
    return get_project_manager().export_project(project_id)
