"""Cinematic CPU preview backend.

This backend is still a deterministic local preview renderer, not a diffusion/video
foundation model. It exists for zero-GPU demos and for checking storyboard timing,
camera motion, subtitles, scene layout and character blocking.

The previous mock produced flat cards, which made misconfigured "real" backends look
like broken video generation. This renderer now creates staged short-drama scenes
with characters, props, camera movement, lighting and depth cues, and its metadata
clearly marks the output as ``cinematic_preview``.
"""
from __future__ import annotations

import math
import os
import re
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from app.backends.base import VideoBackend
from app.config import settings
from app.models.schemas import ImageToVideoRequest, TextToVideoRequest, VideoGenerationResult
from app.utils.video_utils import ratio_to_size


@dataclass(frozen=True)
class CharacterLook:
    name: str
    role: str
    coat: tuple[int, int, int]
    accent: tuple[int, int, int]
    hair: tuple[int, int, int]
    skin: tuple[int, int, int]
    height_scale: float = 1.0


SCENE_ALIASES = {
    "banquet": ["宴会", "婚礼", "家族会议", "老宅", "客厅", "茶楼", "宫廷", "雅集"],
    "office": ["办公室", "董事会", "会议室", "金融中心", "发布会", "公司", "电梯"],
    "hospital": ["医院", "病房", "走廊"],
    "night_street": ["雨夜", "街", "巷", "停车场", "车库", "夜"],
    "xianxia": ["仙山", "宗门", "竹林", "秘境", "古战场", "修仙", "仙门"],
}


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        os.getenv("AIVIDEO_FONT_PATH", ""),
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
    ]
    for font_path in candidates:
        if font_path and Path(font_path).exists():
            try:
                return ImageFont.truetype(font_path, size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def _motion_name(request: TextToVideoRequest | ImageToVideoRequest) -> str:
    if isinstance(request, ImageToVideoRequest):
        return request.motion_type or request.camera_motion or "slow_push_in"
    return request.camera_motion or "slow_push_in"


def _wrap_text(text: str, max_chars: int) -> list[str]:
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]
    lines: list[str] = []
    current = ""
    for ch in text:
        current += ch
        if len(current) >= max_chars:
            lines.append(current)
            current = ""
    if current:
        lines.append(current)
    return lines


def _extract_field(prompt: str, field: str) -> str | None:
    pattern = rf"{re.escape(field)}\s*:\s*(.*?)(?:\. [A-Z][A-Za-z ]+:\s|$)"
    match = re.search(pattern, prompt, re.S)
    if match:
        return match.group(1).strip(" .。")
    return None


def _scene_kind(prompt: str) -> str:
    scene_text = (_extract_field(prompt, "Scene") or prompt or "").lower()
    for kind, words in SCENE_ALIASES.items():
        if any(word.lower() in scene_text for word in words):
            return kind
    return "banquet"


def _palette(scene: str) -> dict[str, tuple[int, int, int]]:
    palettes = {
        "banquet": {
            "bg_top": (23, 16, 24), "bg_bottom": (86, 39, 32), "floor": (74, 30, 26),
            "gold": (222, 166, 72), "light": (255, 213, 132), "shadow": (14, 10, 16),
        },
        "office": {
            "bg_top": (20, 28, 44), "bg_bottom": (47, 58, 79), "floor": (39, 43, 51),
            "gold": (118, 154, 196), "light": (207, 225, 255), "shadow": (10, 15, 23),
        },
        "hospital": {
            "bg_top": (205, 219, 221), "bg_bottom": (157, 181, 189), "floor": (132, 157, 164),
            "gold": (110, 154, 171), "light": (244, 255, 255), "shadow": (89, 107, 115),
        },
        "night_street": {
            "bg_top": (10, 14, 29), "bg_bottom": (28, 35, 54), "floor": (24, 26, 35),
            "gold": (184, 70, 155), "light": (91, 190, 255), "shadow": (3, 6, 13),
        },
        "xianxia": {
            "bg_top": (39, 50, 65), "bg_bottom": (115, 133, 132), "floor": (50, 66, 61),
            "gold": (177, 210, 199), "light": (230, 245, 236), "shadow": (20, 34, 35),
        },
    }
    return palettes.get(scene, palettes["banquet"])


def _gradient(w: int, h: int, top: tuple[int, int, int], bottom: tuple[int, int, int]) -> np.ndarray:
    y = np.linspace(0, 1, h)[:, None]
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for c in range(3):
        arr[:, :, c] = (top[c] * (1 - y) + bottom[c] * y).astype(np.uint8)
    return arr


def _draw_background(draw: ImageDraw.ImageDraw, w: int, h: int, scene: str, t: float) -> None:
    p = _palette(scene)
    draw.rectangle([0, int(h * 0.61), w, h], fill=p["floor"])

    if scene == "banquet":
        for x in [int(w * 0.10), int(w * 0.89)]:
            draw.rounded_rectangle([x - w * 0.035, h * 0.18, x + w * 0.035, h * 0.78], radius=18, fill=(106, 34, 30))
            draw.rectangle([x - w * 0.047, h * 0.18, x + w * 0.047, h * 0.21], fill=p["gold"])
        draw.rounded_rectangle([w * 0.24, h * 0.18, w * 0.76, h * 0.54], radius=22, fill=(38, 25, 28), outline=p["gold"], width=4)
        for k in range(4):
            y = h * (0.24 + k * 0.065)
            draw.line([w * 0.27, y, w * 0.73, y], fill=(79, 58, 52), width=2)
        for x in [w * 0.32, w * 0.50, w * 0.68]:
            glow = int(18 + 12 * math.sin(6 * t + x))
            draw.ellipse([x - 30 - glow, h * 0.08 - glow, x + 30 + glow, h * 0.16 + glow], fill=(120, 61, 30))
            draw.ellipse([x - 22, h * 0.085, x + 22, h * 0.155], fill=(255, 172, 74))
            draw.line([x, h * 0.04, x, h * 0.085], fill=p["gold"], width=3)
        draw.rounded_rectangle([w * 0.25, h * 0.72, w * 0.75, h * 0.80], radius=24, fill=(92, 44, 28), outline=(172, 104, 52), width=4)
        for x in [w * 0.39, w * 0.50, w * 0.61]:
            draw.ellipse([x - 20, h * 0.69, x + 20, h * 0.72], fill=(206, 124, 73))
    elif scene == "office":
        draw.rounded_rectangle([w * 0.10, h * 0.13, w * 0.90, h * 0.54], radius=18, fill=(24, 33, 52), outline=(90, 120, 150), width=3)
        for i in range(5):
            x = w * (0.16 + i * 0.16)
            draw.line([x, h * 0.14, x, h * 0.54], fill=(71, 94, 124), width=2)
        for i in range(22):
            x = int(w * (0.14 + (i % 11) * 0.07))
            y = int(h * (0.20 + (i // 11) * 0.16 + 0.01 * math.sin(t * 5 + i)))
            draw.rectangle([x, y, x + 7, y + 16], fill=(240, 210, 104))
        draw.rounded_rectangle([w * 0.16, h * 0.72, w * 0.84, h * 0.82], radius=18, fill=(45, 42, 39), outline=(105, 98, 87), width=3)
    elif scene == "hospital":
        for i in range(6):
            y = h * (0.14 + i * 0.07)
            draw.rounded_rectangle([w * 0.36, y, w * 0.64, y + h * 0.025], radius=10, fill=(238, 255, 255))
        draw.polygon([(0, h * 0.60), (w * 0.35, h * 0.38), (w * 0.65, h * 0.38), (w, h * 0.60)], fill=(181, 205, 211))
        for x in [w * 0.15, w * 0.85]:
            draw.rectangle([x - w * 0.08, h * 0.33, x + w * 0.08, h * 0.62], fill=(117, 151, 160))
            draw.rectangle([x - w * 0.04, h * 0.45, x + w * 0.04, h * 0.61], fill=(84, 117, 128))
    elif scene == "night_street":
        for i, x in enumerate([w * 0.18, w * 0.80]):
            draw.rounded_rectangle([x - 34, h * 0.16, x + 34, h * 0.66], radius=8, fill=(20, 24, 38))
            color = (90, 210, 255) if i == 0 else (236, 82, 184)
            draw.rectangle([x - 20, h * 0.19, x + 20, h * 0.42], fill=color)
        for i in range(34):
            x = (i * 47 + int(t * 110)) % w
            y = int(h * (0.10 + (i % 8) * 0.10))
            draw.line([x, y, x - 16, y + 52], fill=(112, 152, 184), width=2)
        draw.line([w * 0.05, h * 0.74, w * 0.95, h * 0.74], fill=(75, 83, 98), width=3)
    elif scene == "xianxia":
        for i in range(5):
            x0 = w * (i * 0.22 - 0.1)
            draw.polygon([(x0, h * 0.62), (x0 + w * 0.23, h * (0.24 + 0.04 * (i % 2))), (x0 + w * 0.48, h * 0.62)], fill=(48 + i * 10, 69 + i * 8, 73 + i * 7))
        for i in range(10):
            y = h * (0.22 + i * 0.035 + 0.01 * math.sin(t * 4 + i))
            draw.line([w * 0.04, y, w * 0.96, y], fill=(177, 201, 195), width=2)
        draw.rounded_rectangle([w * 0.28, h * 0.52, w * 0.72, h * 0.63], radius=12, fill=(63, 74, 64), outline=(166, 191, 174), width=3)


def _draw_light_overlays(img: Image.Image, scene: str, t: float) -> Image.Image:
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    p = _palette(scene)
    d.polygon([(0, 0), (w * 0.48, 0), (w * 0.62, h), (0, h)], fill=(*p["light"], 26))
    d.ellipse([w * 0.20, h * 0.08, w * 0.80, h * 0.62], fill=(*p["gold"], int(18 + 8 * math.sin(t * math.pi * 2))))
    d.rectangle([0, 0, w, h * 0.08], fill=(0, 0, 0, 55))
    d.rectangle([0, h * 0.92, w, h], fill=(0, 0, 0, 70))
    d.rectangle([0, 0, w * 0.05, h], fill=(0, 0, 0, 45))
    d.rectangle([w * 0.95, 0, w, h], fill=(0, 0, 0, 45))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def _characters_for_prompt(prompt: str, scene: str) -> list[CharacterLook]:
    prompt_lower = prompt.lower()
    if "反派" in prompt or "antagonist" in prompt_lower:
        return [
            CharacterLook("主角", "protagonist", (232, 225, 206), (33, 36, 44), (28, 23, 21), (232, 188, 155), 0.98),
            CharacterLook("男主", "ally", (28, 34, 45), (94, 103, 118), (22, 20, 19), (226, 180, 148), 1.08),
            CharacterLook("反派", "antagonist", (118, 28, 40), (218, 164, 84), (32, 22, 25), (229, 184, 150), 1.00),
        ]
    if scene == "xianxia":
        return [
            CharacterLook("女主", "disciple", (215, 230, 224), (107, 151, 145), (31, 29, 28), (230, 190, 156), 0.99),
            CharacterLook("反派", "rival", (28, 29, 34), (207, 163, 93), (18, 18, 21), (224, 176, 143), 1.05),
        ]
    return [
        CharacterLook("女主", "protagonist", (232, 225, 206), (33, 36, 44), (28, 23, 21), (232, 188, 155), 0.98),
        CharacterLook("男主", "ally", (28, 34, 45), (94, 103, 118), (22, 20, 19), (226, 180, 148), 1.09),
    ]


def _draw_character(draw: ImageDraw.ImageDraw, cx: float, base_y: float, scale: float, look: CharacterLook, phase: float, focus: bool = False) -> None:
    bob = math.sin(phase * math.pi * 2) * scale * 2.0
    head_r = scale * 0.085 * look.height_scale
    body_h = scale * 0.30 * look.height_scale
    shoulder = scale * 0.115
    neck_w = scale * 0.034
    head_y = base_y - body_h - head_r * 1.75 + bob
    torso_top = head_y + head_r * 1.55
    torso_bottom = base_y

    draw.ellipse([cx - shoulder * 1.25, base_y - scale * 0.018, cx + shoulder * 1.25, base_y + scale * 0.030], fill=(0, 0, 0, 80))
    leg_color = tuple(max(0, c - 18) for c in look.accent)
    draw.rounded_rectangle([cx - shoulder * 0.72, torso_bottom - scale * 0.02, cx - shoulder * 0.12, base_y + scale * 0.16], radius=10, fill=leg_color)
    draw.rounded_rectangle([cx + shoulder * 0.12, torso_bottom - scale * 0.02, cx + shoulder * 0.72, base_y + scale * 0.16], radius=10, fill=leg_color)
    draw.rounded_rectangle([cx - shoulder, torso_top, cx + shoulder, torso_bottom + scale * 0.04], radius=int(scale * 0.028), fill=look.coat)
    draw.polygon([(cx - shoulder, torso_top + 4), (cx, torso_top + scale * 0.16), (cx + shoulder, torso_top + 4)], fill=look.accent)

    hand_shift = math.sin(phase * math.pi * 2 + 0.6) * scale * 0.025
    draw.line([cx - shoulder * 0.92, torso_top + scale * 0.04, cx - shoulder * 1.28, torso_top + scale * 0.18 + hand_shift], fill=look.coat, width=max(4, int(scale * 0.024)))
    draw.line([cx + shoulder * 0.92, torso_top + scale * 0.04, cx + shoulder * 1.20, torso_top + scale * 0.18 - hand_shift], fill=look.coat, width=max(4, int(scale * 0.024)))
    draw.ellipse([cx - shoulder * 1.34, torso_top + scale * 0.17 + hand_shift, cx - shoulder * 1.21, torso_top + scale * 0.24 + hand_shift], fill=look.skin)
    draw.ellipse([cx + shoulder * 1.14, torso_top + scale * 0.16 - hand_shift, cx + shoulder * 1.28, torso_top + scale * 0.23 - hand_shift], fill=look.skin)

    draw.rounded_rectangle([cx - neck_w, head_y + head_r * 1.18, cx + neck_w, torso_top + 6], radius=8, fill=look.skin)
    draw.ellipse([cx - head_r, head_y - head_r, cx + head_r, head_y + head_r], fill=look.skin)
    draw.pieslice([cx - head_r * 1.05, head_y - head_r * 1.12, cx + head_r * 1.05, head_y + head_r * 0.7], start=180, end=360, fill=look.hair)
    draw.rectangle([cx - head_r * 0.92, head_y - head_r * 0.28, cx + head_r * 0.92, head_y + head_r * 0.05], fill=look.hair)

    eye_y = head_y + head_r * 0.10
    eye_dx = head_r * 0.35
    draw.ellipse([cx - eye_dx - 3, eye_y - 2, cx - eye_dx + 3, eye_y + 2], fill=(30, 25, 23))
    draw.ellipse([cx + eye_dx - 3, eye_y - 2, cx + eye_dx + 3, eye_y + 2], fill=(30, 25, 23))
    mouth_y = head_y + head_r * 0.42
    mouth_w = head_r * (0.35 if look.role != "antagonist" else 0.48)
    draw.arc([cx - mouth_w, mouth_y - 6, cx + mouth_w, mouth_y + 8], start=0, end=180, fill=(98, 42, 42), width=2)

    if focus:
        draw.arc([cx - shoulder * 1.25, torso_top - 20, cx + shoulder * 1.25, torso_bottom + 25], 205, 335, fill=(255, 231, 156), width=4)


def _draw_prop(draw: ImageDraw.ImageDraw, w: int, h: int, prompt: str, t: float) -> None:
    lower = prompt.lower()
    x = w * 0.52
    y = h * 0.63
    glow = int(9 + 7 * math.sin(t * math.pi * 4))
    if "手机" in prompt or "phone" in lower or "证据" in prompt:
        draw.ellipse([x - 38 - glow, y - 38 - glow, x + 38 + glow, y + 38 + glow], fill=(235, 164, 64))
        draw.rounded_rectangle([x - 22, y - 42, x + 22, y + 42], radius=8, fill=(20, 24, 28), outline=(255, 222, 145), width=3)
        draw.rectangle([x - 14, y - 26, x + 14, y + 21], fill=(50, 86, 100))
        draw.line([x - 10, y - 10, x + 10, y - 10], fill=(255, 240, 180), width=2)
        draw.line([x - 10, y + 2, x + 6, y + 2], fill=(255, 240, 180), width=2)
    elif "合同" in prompt or "contract" in lower:
        draw.ellipse([x - 48 - glow, y - 32 - glow, x + 48 + glow, y + 32 + glow], fill=(235, 164, 64))
        draw.polygon([(x - 38, y - 44), (x + 42, y - 34), (x + 32, y + 44), (x - 48, y + 32)], fill=(238, 228, 198), outline=(88, 64, 52))
        for i in range(4):
            draw.line([x - 24, y - 18 + i * 13, x + 20, y - 12 + i * 13], fill=(96, 86, 72), width=2)
    else:
        draw.ellipse([x - 34 - glow, y - 34 - glow, x + 34 + glow, y + 34 + glow], fill=(235, 164, 64))
        draw.rounded_rectangle([x - 20, y - 26, x + 20, y + 26], radius=6, fill=(45, 35, 27), outline=(255, 218, 132), width=3)


def _draw_subtitle(draw: ImageDraw.ImageDraw, w: int, h: int, text: str, font: ImageFont.ImageFont) -> None:
    lines = _wrap_text(text, 18 if w < 900 else 24)[:2]
    if not lines:
        return
    box_h = int(h * (0.105 + 0.035 * (len(lines) - 1)))
    x0, y0, x1, y1 = int(w * 0.065), int(h * 0.80), int(w * 0.935), int(h * 0.80) + box_h
    draw.rounded_rectangle([x0, y0, x1, y1], radius=22, fill=(0, 0, 0), outline=(255, 255, 255), width=2)
    y = y0 + 20
    for line in lines:
        draw.text((x0 + 24, y), line, fill=(255, 255, 255), font=font)
        y += int(font.size * 1.25) if hasattr(font, "size") else 24


def _caption_from_prompt(prompt: str) -> str:
    action = _extract_field(prompt, "Action")
    if action:
        return action
    snippets = re.findall(r"[\u4e00-\u9fffA-Za-z0-9，。！？、：；“”‘’]+", prompt or "")
    joined = "".join(snippets)
    for marker in ["你们是谁", "想看沈家翻车吗", "对不起", "我要站着封神", "真相", "证据"]:
        if marker in joined:
            start = max(0, joined.find(marker) - 6)
            return joined[start:start + 28]
    return (prompt or "短剧镜头预览")[:36]


def _compose_scene_frame(prompt: str, w: int, h: int, i: int, total: int, motion: str) -> np.ndarray:
    t = i / max(total - 1, 1)
    scene = _scene_kind(prompt)
    p = _palette(scene)
    frame = _gradient(w, h, p["bg_top"], p["bg_bottom"])
    img = Image.fromarray(frame, mode="RGB")
    draw = ImageDraw.Draw(img)

    _draw_background(draw, w, h, scene, t)

    for k in range(5):
        x = w * (0.08 + k * 0.22 + 0.01 * math.sin(t * 3 + k))
        y = h * (0.66 + 0.015 * (k % 2))
        draw.ellipse([x - 18, y - 95, x + 18, y - 58], fill=(16, 16, 20))
        draw.rounded_rectangle([x - 24, y - 58, x + 24, y + 52], radius=14, fill=(22, 23, 28))

    looks = _characters_for_prompt(prompt, scene)
    positions = [w * 0.31, w * 0.69] if len(looks) == 2 else [w * 0.25, w * 0.55, w * 0.77]
    base_y = h * 0.74
    scale = min(w, h) * 0.86
    for idx, look in enumerate(looks):
        _draw_character(
            draw,
            positions[idx],
            base_y + (idx % 2) * h * 0.015,
            scale * (0.84 if len(looks) == 3 and idx == 0 else 0.90),
            look,
            t + idx * 0.22,
            focus=(idx == 0),
        )

    _draw_prop(draw, w, h, prompt, t)

    if scene != "hospital":
        for k in range(28):
            x = int((k * 89 + t * w * 0.12) % w)
            y = int(h * (0.15 + ((k * 37) % 70) / 100))
            r = 1 + (k % 3)
            draw.ellipse([x - r, y - r, x + r, y + r], fill=(*p["light"],))

    img = _draw_light_overlays(img, scene, t)
    draw = ImageDraw.Draw(img)
    subtitle_font = _load_font(max(22, int(w * 0.036)))
    small_font = _load_font(max(15, int(w * 0.020)))
    _draw_subtitle(draw, w, h, _caption_from_prompt(prompt), subtitle_font)
    draw.rounded_rectangle([w * 0.055, h * 0.045, w * 0.48, h * 0.087], radius=12, fill=(0, 0, 0))
    draw.text((w * 0.070, h * 0.054), "AI Video Studio · cinematic preview", fill=(238, 238, 238), font=small_font)

    arr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    return _transform(arr, i, total, motion)


def _transform(img: np.ndarray, i: int, total: int, motion: str) -> np.ndarray:
    h, w = img.shape[:2]
    t = i / max(total - 1, 1)
    zoom = 1.0
    dx = dy = 0
    if motion in {"slow_push_in", "zoom_in", "close_up", "fast push-in", "slow push-in"}:
        zoom = 1 + 0.075 * t
    if motion in {"pull_back", "zoom_out"}:
        zoom = 1.08 - 0.07 * t
    if motion in {"pan_left"}:
        dx = int(-45 * t)
    if motion in {"pan_right"}:
        dx = int(45 * t)
    if motion in {"tilt_up"}:
        dy = int(-32 * t)
    if motion in {"tilt_down"}:
        dy = int(32 * t)
    if motion in {"handheld micro-shake"}:
        dx = int(math.sin(i * 0.7) * 4)
        dy = int(math.cos(i * 0.6) * 3)
        zoom = 1.025
    if motion in {"snap zoom"}:
        zoom = 1.0 + 0.11 * min(1, t * 3)
    if motion in {"freeze-like hold"}:
        zoom = 1.035
    matrix = cv2.getRotationMatrix2D((w / 2, h / 2), 0, zoom)
    matrix[:, 2] += (dx, dy)
    return cv2.warpAffine(img, matrix, (w, h), borderMode=cv2.BORDER_REFLECT)


class MockVideoBackend(VideoBackend):
    name = "mock"

    def _write(self, frames: list[np.ndarray], path: str, fps: int) -> None:
        h, w = frames[0].shape[:2]
        writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
        for frame in frames:
            writer.write(frame)
        writer.release()

    def generate_text(self, request: TextToVideoRequest) -> VideoGenerationResult:
        w, h = ratio_to_size(request.aspect_ratio, request.resolution)
        fps = int(request.fps or 16)
        total = int(request.num_frames or request.duration * fps)
        total = max(1, total)
        out = settings.output_dir / f"{uuid4().hex}.mp4"
        motion = _motion_name(request)
        frames = [_compose_scene_frame(request.prompt, w, h, i, total, motion) for i in range(total)]
        self._write(frames, str(out), fps)
        return VideoGenerationResult(
            task_id=out.stem,
            output_path=str(out),
            preview_url=f"/api/assets/{out.stem}/video",
            metadata={
                "backend": "mock",
                "renderer": "cinematic_preview",
                "real_video": False,
                "fps": fps,
                "frames": total,
                "note": "CPU preview only. Configure comfyui/local_open_video for real AI video generation.",
            },
            logs=[
                "mock cinematic preview completed",
                "This is not a diffusion model output; use VIDEO_BACKEND=comfyui or local_open_video for real generation.",
            ],
        )

    def generate_image(self, request: ImageToVideoRequest) -> VideoGenerationResult:
        w, h = ratio_to_size(request.aspect_ratio, request.resolution)
        fps = int(request.fps or 16)
        total = int(request.num_frames or request.duration * fps)
        total = max(1, total)
        img = cv2.imread(request.image_path)
        if img is None:
            raise ValueError("invalid image_path")
        img = cv2.resize(img, (w, h))
        out = settings.output_dir / f"{uuid4().hex}.mp4"
        frames = []
        scene = _scene_kind(request.prompt)
        for i in range(total):
            frame = _transform(img, i, total, request.motion_type or "zoom_in")
            pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            pil = _draw_light_overlays(pil, scene, i / max(total - 1, 1))
            d = ImageDraw.Draw(pil)
            subtitle_font = _load_font(max(22, int(w * 0.036)))
            _draw_subtitle(d, w, h, _caption_from_prompt(request.prompt), subtitle_font)
            frames.append(cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR))
        self._write(frames, str(out), fps)
        return VideoGenerationResult(
            task_id=out.stem,
            output_path=str(out),
            preview_url=f"/api/assets/{out.stem}/video",
            metadata={
                "backend": "mock",
                "renderer": "cinematic_preview_i2v",
                "real_video": False,
                "fps": fps,
                "frames": total,
                "note": "CPU preview only. Configure comfyui/local_open_video for real AI video generation.",
            },
            logs=[
                "mock cinematic image-to-video preview completed",
                "This is not a diffusion model output; use VIDEO_BACKEND=comfyui or local_open_video for real generation.",
            ],
        )
