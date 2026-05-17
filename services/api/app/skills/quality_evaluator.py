"""Heuristic video quality evaluator for beta workspace."""
from __future__ import annotations
from pathlib import Path
from typing import Any
import cv2
import numpy as np
from app.skills.safety_guard import check_prompt_safety
from app.projects.project_manager import get_project_manager


def _clamp(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def evaluate_video(video_path: str, prompt_spec: dict[str, Any] | None = None) -> dict:
    prompt_spec = prompt_spec or {}
    path = Path(video_path)
    if not path.exists():
        return {'video_path': video_path, 'overall_score': 0.0, 'issues': ['video file not found']}
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 12
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = frames / fps if fps else 0
    sharpness=[]; brightness=[]; diffs=[]; prev_gray=None
    sample_step=max(1, frames//48) if frames else 1; idx=0
    while True:
        ok, frame = cap.read()
        if not ok: break
        if idx % sample_step == 0:
            gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            sharpness.append(float(cv2.Laplacian(gray, cv2.CV_64F).var()))
            brightness.append(float(gray.mean()))
            if prev_gray is not None: diffs.append(float(np.mean(cv2.absdiff(gray, prev_gray))))
            prev_gray=gray
        idx += 1
    cap.release()
    target_duration = float(prompt_spec.get('duration') or prompt_spec.get('target_duration') or duration or 1)
    duration_match = _clamp(1 - abs(duration-target_duration)/max(target_duration,1))
    sharpness_score = _clamp((np.mean(sharpness) if sharpness else 0) / 500.0)
    brightness_mean = np.mean(brightness) if brightness else 0
    brightness_score = _clamp(1 - abs(brightness_mean - 125) / 125)
    motion_smoothness = _clamp(1 - (np.std(diffs) if diffs else 0) / 60)
    temporal_consistency = _clamp(1 - (np.mean(diffs) if diffs else 0) / 100)
    compression_score = _clamp(path.stat().st_size / max(duration,1) / 200000)
    prompt = str(prompt_spec.get('prompt') or prompt_spec.get('original_prompt') or '')
    safety = check_prompt_safety(prompt); safety_score = 1.0 if safety.allowed else 0.0
    prompt_alignment = 0.72 if prompt else 0.5
    scores = {'prompt_alignment_score': prompt_alignment, 'temporal_consistency_score': temporal_consistency, 'motion_smoothness_score': motion_smoothness, 'sharpness_score': sharpness_score, 'brightness_score': brightness_score, 'compression_score': compression_score, 'duration_match_score': duration_match, 'safety_score': safety_score}
    overall = sum(scores.values()) / len(scores)
    issues=[]
    if sharpness_score < .35: issues.append('Sharpness is low; increase resolution or reduce compression.')
    if motion_smoothness < .45: issues.append('Frame differences are unstable; check flicker or camera shake.')
    if duration_match < .75: issues.append('Duration does not match target duration.')
    return {'video_path': video_path, **scores, 'overall_score': round(overall, 3), 'duration': duration, 'issues': issues, 'suggestions': issues or ['Quality metrics look acceptable.']}


def evaluate_project(project_id: str) -> dict:
    project = get_project_manager().get_project(project_id)
    if not project: raise KeyError('project not found')
    reports=[]
    for shot in project.shots:
        if shot.output_video_path:
            reports.append(evaluate_video(shot.output_video_path, {'prompt': shot.visual_prompt, 'duration': shot.duration}))
    overall = sum(r.get('overall_score',0) for r in reports)/len(reports) if reports else 0
    return {'project_id': project_id, 'overall_score': round(overall,3), 'shots': reports}


def compare_candidates(candidate_paths: list[str]) -> dict:
    reports = [evaluate_video(p, {}) for p in candidate_paths]
    reports.sort(key=lambda r:r.get('overall_score',0), reverse=True)
    return {'best': reports[0] if reports else None, 'candidates': reports}


def quality_report_to_markdown(report: dict) -> str:
    lines = ['# Video Quality Report', f"Overall: {report.get('overall_score', 0)}", '']
    for k,v in report.items():
        if k.endswith('_score'): lines.append(f'- {k}: {v}')
    for issue in report.get('issues', []): lines.append(f'- Issue: {issue}')
    return '\n'.join(lines)
