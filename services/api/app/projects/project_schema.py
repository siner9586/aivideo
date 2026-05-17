"""Project and shot schemas for persistent AI video creation."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

class Shot(BaseModel):
    shot_id: str
    title: str = 'Untitled shot'
    duration: float = 4.0
    visual_prompt: str = ''
    action_prompt: str = ''
    camera_motion: str = 'slow_push_in'
    style: str = 'cinematic realistic'
    reference_image: str | None = None
    first_frame: str | None = None
    last_frame: str | None = None
    backend: str = 'mock'
    seed: int | None = 42
    status: str = 'draft'
    output_video_path: str | None = None
    notes: str = ''
    assets: list[str] = Field(default_factory=list)

class Project(BaseModel):
    project_id: str
    title: str = 'Untitled project'
    description: str = ''
    original_prompt: str = ''
    parsed_spec: dict[str, Any] = Field(default_factory=dict)
    storyboard: dict[str, Any] = Field(default_factory=dict)
    shots: list[Shot] = Field(default_factory=list)
    assets: list[str] = Field(default_factory=list)
    generation_settings: dict[str, Any] = Field(default_factory=lambda: {'backend':'mock','fps':12,'aspect_ratio':'16:9','resolution':'480p'})
    output_videos: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
