"""Pydantic schemas for AI Video Studio."""
from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field

RiskLevel = Literal['low','medium','high','blocked']
BackendName = Literal['mock','diffusers','external','comfyui']

class SafetyReport(BaseModel):
    risk_level: RiskLevel = 'low'
    allowed: bool = True
    reasons: list[str] = Field(default_factory=list)
    safe_alternative: str | None = None

class VideoPromptSpec(BaseModel):
    original_prompt: str
    subject: str = 'unspecified subject'
    scene: str = 'clean studio scene'
    style: str = 'cinematic realistic'
    motion: str = 'subtle natural motion'
    camera: str = 'static'
    lighting: str = 'soft balanced light'
    mood: str = 'calm'
    duration: float = 8.0
    aspect_ratio: str = '16:9'
    resolution: str = '720p'
    negative_prompt: str = ''
    language: str = 'auto'

class StoryboardShot(BaseModel):
    shot_id: int
    duration: float
    camera_angle: str
    camera_motion: str
    visual_prompt: str
    action_prompt: str
    transition: str = 'cut'
    audio_hint: str = 'subtle ambience'
    consistency_notes: str = 'keep subject, style, lighting consistent'

class Storyboard(BaseModel):
    title: str = 'AI Video Studio storyboard'
    total_duration: float
    shots: list[StoryboardShot]
    markdown: str = ''

class GenerationJob(BaseModel):
    shot_id: int | None = None
    prompt: str
    duration: float = 8
    camera_motion: str = 'static'
    output_path: str | None = None

class TextToVideoRequest(BaseModel):
    prompt: str
    backend: BackendName = 'mock'
    duration: float = 8
    fps: int = 12
    num_frames: int | None = None
    seed: int | None = 42
    guidance_scale: float = 7.5
    negative_prompt: str = ''
    aspect_ratio: str = '16:9'
    resolution: str = '720p'
    camera_motion: str | None = None

class ImageToVideoRequest(TextToVideoRequest):
    image_path: str
    last_frame_path: str | None = None
    reference_frames: list[str] = Field(default_factory=list)
    motion_type: str = 'zoom_in'

class VideoGenerationResult(BaseModel):
    task_id: str
    status: str = 'completed'
    output_path: str
    preview_url: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    logs: list[str] = Field(default_factory=list)

class CharacterProfile(BaseModel):
    name: str
    age_range: str | None = None
    gender_expression: str | None = None
    hair: str | None = None
    clothing: str | None = None
    facial_features: str | None = None
    personality: str | None = None
    visual_anchor_prompt: str | None = None
    reference_image_path: str | None = None

class CameraMotionSpec(BaseModel):
    motion_type: str = 'static'
    intensity: float = 0.35
    direction: str | None = None
    shot_size: str | None = None

class KeyframeValidationReport(BaseModel):
    valid: bool
    warnings: list[str] = Field(default_factory=list)
    files: list[dict[str, Any]] = Field(default_factory=list)

class KeyframeSpec(BaseModel):
    first_frame: str | None = None
    last_frame: str | None = None
    references: list[str] = Field(default_factory=list)

class TemporalConsistencyReport(BaseModel):
    avg_frame_diff: float
    max_frame_diff: float
    flicker_score: float
    motion_smoothness_score: float
    consistency_score: float
    warnings: list[str] = Field(default_factory=list)

class PreferenceReport(BaseModel):
    video_path: str
    prompt_alignment: float
    visual_quality: float
    motion_smoothness: float
    temporal_consistency: float
    character_consistency: float
    camera_quality: float
    safety_score: float
    overall_score: float
    notes: list[str] = Field(default_factory=list)

class RuntimeDeviceReport(BaseModel):
    device: str
    cuda_available: bool = False
    mps_available: bool = False
    details: dict[str, Any] = Field(default_factory=dict)

class InferenceConfig(BaseModel):
    device: str = 'cpu'
    dtype: str = 'fp32'
    offload: bool = False
    attention_slicing: bool = True
    vae_tiling: bool = True
    compile_mode: str | None = None
    notes: list[str] = Field(default_factory=list)

class PostProcessSettings(BaseModel):
    fps: int | None = None
    width: int | None = None
    height: int | None = None
    aspect_ratio: str | None = None
    subtitle: str | None = None
    add_intro: bool = False
    add_outro: bool = False
    sharpen: bool = False
    denoise: bool = False

class PostProcessResult(BaseModel):
    output_path: str
    settings: PostProcessSettings
    logs: list[str] = Field(default_factory=list)
