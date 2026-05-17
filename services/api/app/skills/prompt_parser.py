"""Rule-based prompt-to-video semantic parser."""
from __future__ import annotations
import re
from app.models.schemas import VideoPromptSpec
from app.skills.camera_motion import parse_camera_motion

STYLE_WORDS = ['电影级','写实','赛博朋克','水墨','产品广告','教育','cinematic','realistic','anime','documentary','commercial']
LIGHT_WORDS = ['暖金色','霓虹','柔和','逆光','夜晚','白天','warm','neon','soft','backlit','night','daylight']
SCENE_HINTS = ['茶楼','宫廷','街道','森林','海边','办公室','工厂','教室','studio','teahouse','street','forest','office','classroom']

def _pick(text: str, words: list[str], default: str) -> str:
    found = [w for w in words if w.lower() in text.lower()]
    return ', '.join(found) if found else default

def parse_prompt(prompt: str) -> VideoPromptSpec:
    """Parse Chinese or English natural-language prompt into VideoPromptSpec."""
    if not prompt or not prompt.strip():
        raise ValueError('prompt must not be empty')
    text = prompt.strip()
    lang = 'zh' if re.search(r'[\u4e00-\u9fff]', text) else 'en'
    duration = 8.0
    m = re.search(r'(\d+(?:\.\d+)?)\s*(秒|s|sec|seconds?)', text, re.I)
    if m: duration = float(m.group(1))
    aspect = '16:9'
    for r in ['16:9','9:16','1:1','5:2']:
        if r in text: aspect = r
    res = '720p'
    for r in ['480p','720p','1080p']:
        if r.lower() in text.lower(): res = r
    camera = parse_camera_motion(text).motion_type
    scene = _pick(text, SCENE_HINTS, 'night cinematic interior' if lang=='en' else '电影感室内场景')
    style = _pick(text, STYLE_WORDS, 'cinematic realistic' if lang=='en' else '电影级写实')
    lighting = _pick(text, LIGHT_WORDS, 'soft warm lighting' if lang=='en' else '柔和暖光')
    subject = '人物与环境' if lang=='zh' else 'people and environment'
    if '产品' in text or 'product' in text.lower(): subject = 'product'
    if '风景' in text or 'landscape' in text.lower(): subject = 'landscape'
    spec = VideoPromptSpec(original_prompt=text, subject=subject, scene=scene, style=style, motion='natural subtle action', camera=camera, lighting=lighting, mood='高级、稳定、细节丰富' if lang=='zh' else 'polished, stable, detailed', duration=duration, aspect_ratio=aspect, resolution=res, language=lang)
    return normalize_video_spec(spec)

def normalize_video_spec(spec: VideoPromptSpec) -> VideoPromptSpec:
    """Clamp duration and fill defaults."""
    spec.duration = max(2.0, min(float(spec.duration), 30.0))
    if spec.aspect_ratio not in {'16:9','9:16','1:1','5:2'}: spec.aspect_ratio='16:9'
    if spec.resolution not in {'480p','720p','1080p'}: spec.resolution='720p'
    spec.negative_prompt = spec.negative_prompt or build_negative_prompt(spec)
    return spec

def build_generation_prompt(spec: VideoPromptSpec) -> str:
    """Build final model prompt from structured fields."""
    return f"{spec.subject}, {spec.scene}, {spec.style}, {spec.motion}, {spec.camera}, {spec.lighting}, mood: {spec.mood}, stable temporal consistency, high detail"

def build_negative_prompt(spec: VideoPromptSpec) -> str:
    """Build a safe default negative prompt."""
    return 'low quality, blurry, flicker, jitter, distorted hands, text artifacts, watermark, unsafe deepfake, copyright character copy'
