"""Shot editing helpers for beta timeline workflows."""
from __future__ import annotations
from app.projects.project_schema import Shot


def reorder_shots(shots: list[Shot], ordered_ids: list[str]) -> list[Shot]:
    by_id = {s.shot_id: s for s in shots}
    ordered = [by_id[i] for i in ordered_ids if i in by_id]
    ordered.extend([s for s in shots if s.shot_id not in ordered_ids])
    return ordered


def merge_prompt_parts(shot: Shot) -> str:
    parts = [shot.visual_prompt, shot.action_prompt, f'Camera motion: {shot.camera_motion}', f'Style: {shot.style}']
    if shot.notes:
        parts.append(f'Notes: {shot.notes}')
    return '\n'.join([p for p in parts if p])


def update_shot_duration(shot: Shot, duration: float) -> Shot:
    shot.duration = max(0.5, float(duration))
    return shot
