"""Cinematic prompt compiler and upload packaging for AI short drama.

This module is intentionally model-agnostic.  It does not ship model weights or
pretend that a CPU mock backend can produce real cinematic video.  Instead it
turns a GPT/local short-drama plan into render-ready shot prompts, queue jobs,
delivery specs and quality gates that can be used by ComfyUI, Diffusers,
external video APIs or any future local open-video adapter.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

CINEMATIC_NEGATIVE_PROMPT = (
    "low quality, lowres, blurry, noisy, jpeg artifacts, over-sharpened, "
    "plastic skin, waxy face, inconsistent identity, face drift, age drift, "
    "random costume change, different hairstyle, extra fingers, missing fingers, "
    "deformed hands, broken anatomy, distorted eyes, crossed eyes, bad teeth, "
    "unstable camera, jitter, flicker, warped background, duplicated people, "
    "watermark, logo, text artifacts, subtitles burned in, black border, "
    "overexposed highlights, crushed shadows, bad lip sync, unsafe deepfake"
)

CINEMATIC_STYLE_PRESETS: dict[str, dict[str, str]] = {
    "cinematic_realistic": {
        "look": "cinematic live-action realism, premium Chinese vertical micro-drama look",
        "lens": "35mm and 50mm cinema lens language, shallow depth of field when appropriate",
        "lighting": "motivated soft key light, practical background light, controlled contrast, natural skin tone",
        "color": "filmic color grading, clean highlight roll-off, rich but not oversaturated colors",
        "motion": "stable gimbal or dolly movement, no random shake unless requested",
    },
    "hybrid_live_action": {
        "look": "semi-realistic AI live-action with stylized production design",
        "lens": "clean portrait lens, controlled focus, consistent perspective",
        "lighting": "dramatic but readable studio lighting",
        "color": "high-retention short-drama color, warm skin, clear subject separation",
        "motion": "smooth readable motion, restrained camera move",
    },
    "ai_manhua": {
        "look": "high-end AI manhua animation, dramatic Chinese micro-drama composition",
        "lens": "comic panel framing mixed with cinematic close-ups",
        "lighting": "stylized rim light and clean character silhouette",
        "color": "strong visual hierarchy, clean palette, readable foreground",
        "motion": "limited but expressive motion, crisp reaction beats",
    },
}

DELIVERY_PROFILES: dict[str, dict[str, Any]] = {
    "douyin": {
        "display_name": "Douyin vertical upload",
        "aspect_ratio": "9:16",
        "resolution": "1080p",
        "width": 1080,
        "height": 1920,
        "fps": 24,
        "codec": "h264",
        "pixel_format": "yuv420p",
        "audio_codec": "aac",
        "audio_sample_rate": 44100,
        "safe_title_area": "keep key faces and subtitles inside the central 80% width and 82% height",
        "episode_seconds": 60,
        "hook_seconds": 3,
    },
    "hongguo": {
        "display_name": "Hongguo vertical short-drama upload",
        "aspect_ratio": "9:16",
        "resolution": "1080p",
        "width": 1080,
        "height": 1920,
        "fps": 24,
        "codec": "h264",
        "pixel_format": "yuv420p",
        "audio_codec": "aac",
        "audio_sample_rate": 44100,
        "safe_title_area": "keep dialogue subtitle lines in lower-middle safe zone, avoid platform UI edges",
        "episode_seconds": 60,
        "hook_seconds": 3,
    },
    "kuaishou": {
        "display_name": "Kuaishou vertical upload",
        "aspect_ratio": "9:16",
        "resolution": "1080p",
        "width": 1080,
        "height": 1920,
        "fps": 24,
        "codec": "h264",
        "pixel_format": "yuv420p",
        "audio_codec": "aac",
        "audio_sample_rate": 44100,
        "safe_title_area": "center faces, hands, key props and subtitles away from edges",
        "episode_seconds": 60,
        "hook_seconds": 3,
    },
    "generic_vertical": {
        "display_name": "Generic vertical short video",
        "aspect_ratio": "9:16",
        "resolution": "1080p",
        "width": 1080,
        "height": 1920,
        "fps": 24,
        "codec": "h264",
        "pixel_format": "yuv420p",
        "audio_codec": "aac",
        "audio_sample_rate": 44100,
        "safe_title_area": "center important action and subtitle text",
        "episode_seconds": 45,
        "hook_seconds": 3,
    },
}

QUALITY_GATES: dict[str, Any] = {
    "min_visual_score": 82,
    "min_motion_smoothness": 78,
    "min_temporal_consistency": 80,
    "min_character_consistency": 85,
    "max_face_drift_warning": 1,
    "required_manual_review": [
        "主角是否换脸、换发型、换服装或年龄漂移",
        "手部、牙齿、眼睛、字幕边缘是否明显畸变",
        "前 3 秒是否出现强冲突/异常画面/关键台词",
        "结尾是否在真相揭露前切断形成追更钩子",
        "画面是否存在平台水印、侵权角色或公众人物冒充",
        "是否存在非自愿换脸、欺诈广告、医疗/金融虚假承诺等风险",
    ],
}


def get_delivery_profile(platform: str | None) -> dict[str, Any]:
    """Return a normalized upload profile for a target platform."""
    key = (platform or "hongguo").lower().strip()
    aliases = {
        "redfruit": "hongguo",
        "红果": "hongguo",
        "抖音": "douyin",
        "tiktok_cn": "douyin",
        "ks": "kuaishou",
        "快手": "kuaishou",
    }
    key = aliases.get(key, key)
    return deepcopy(DELIVERY_PROFILES.get(key, DELIVERY_PROFILES["generic_vertical"]))


def _character_lock(characters: list[dict[str, Any]]) -> str:
    if not characters:
        return (
            "Character continuity lock: generate a stable protagonist identity; "
            "do not change face, hairstyle, clothing color or age across shots."
        )
    lines = []
    for c in characters:
        name = c.get("name", "character")
        role = c.get("role", "role")
        visual = c.get("visual_anchor") or c.get("visual_anchor_prompt") or ""
        continuity = c.get("continuity_rule", "")
        voice = c.get("voice", "")
        lines.append(
            f"{name}({role}) visual anchor: {visual}; voice: {voice}; continuity rule: {continuity}"
        )
    return "Character continuity lock: " + " | ".join(lines)


def _extract_shots_from_episode(episode: dict[str, Any]) -> list[dict[str, Any]]:
    """Handle both local planner schema and GPT schema."""
    if isinstance(episode.get("shots"), list):
        return [dict(s) for s in episode["shots"]]
    storyboard = episode.get("storyboard") or {}
    if isinstance(storyboard, dict) and isinstance(storyboard.get("shots"), list):
        return [dict(s) for s in storyboard["shots"]]
    return []


def _episode_id(episode: dict[str, Any], fallback: int) -> int:
    try:
        return int(episode.get("episode_id") or fallback)
    except Exception:
        return fallback


def compile_cinematic_shot_prompt(
    *,
    shot: dict[str, Any],
    episode: dict[str, Any],
    plan: dict[str, Any],
    delivery_profile: dict[str, Any],
    visual_mode: str | None = None,
    render_quality: str = "upload_ready",
) -> dict[str, Any]:
    """Compile one storyboard shot into a backend-agnostic render prompt."""
    mode = visual_mode or str(plan.get("visual_mode") or "cinematic_realistic")
    style = CINEMATIC_STYLE_PRESETS.get(mode, CINEMATIC_STYLE_PRESETS["cinematic_realistic"])
    premise = plan.get("premise") or plan.get("logline") or plan.get("title") or ""
    genre = plan.get("genre", "short_drama")
    title = plan.get("title", "AI short drama")
    ep_id = _episode_id(episode, 1)
    shot_id = shot.get("shot_id", 1)
    duration = float(shot.get("duration") or 4)
    camera_angle = shot.get("camera_angle", "close-up")
    camera_motion = shot.get("camera_motion", "slow_push_in")
    visual_prompt = shot.get("visual_prompt", "")
    action_prompt = shot.get("action_prompt", "")
    transition = shot.get("transition", "cut")
    subtitle = shot.get("subtitle") or action_prompt
    character_lock = _character_lock([dict(c) for c in plan.get("characters", [])])

    prompt_parts = [
        f"Project: {title}.",
        f"Target platform: {delivery_profile['display_name']}, {delivery_profile['width']}x{delivery_profile['height']}, {delivery_profile['aspect_ratio']} vertical video.",
        f"Genre: {genre}; premise: {premise}.",
        f"Episode {ep_id}, shot {shot_id}, duration {duration:.2f}s.",
        f"Shot goal: {episode.get('hook') or episode.get('beat') or ''}",
        f"Visual direction: {visual_prompt}",
        f"Action beat: {action_prompt}",
        f"Camera: {camera_angle}, {camera_motion}; maintain readable vertical composition.",
        f"Style: {style['look']}; {style['lens']}; {style['lighting']}; {style['color']}; {style['motion']}.",
        character_lock,
        "Micro-drama pacing: first frame must be immediately understandable, one clear emotion per shot, strong facial reaction, clean key prop visibility.",
        f"Safe area: {delivery_profile['safe_title_area']}. Do not place important faces, hands, props or subtitles at the edge.",
        "Production quality: cinematic blocking, detailed but not cluttered background, natural facial expression, coherent eyeline, stable costume, consistent lighting direction, no watermark.",
    ]
    if render_quality == "draft":
        prompt_parts.append("Draft render: prioritize speed and composition preview.")
    else:
        prompt_parts.append(
            "Upload-ready render: prioritize face stability, temporal consistency, clean hands, natural motion, detail density and compression-safe contrast."
        )

    negative_prompt = ", ".join(
        x
        for x in [
            str(plan.get("negative_prompt") or ""),
            CINEMATIC_NEGATIVE_PROMPT,
        ]
        if x
    )
    positive_prompt = " ".join(p for p in prompt_parts if p and str(p).strip())

    return {
        "shot_id": shot_id,
        "episode_id": ep_id,
        "duration": duration,
        "camera_motion": camera_motion,
        "transition": transition,
        "positive_prompt": positive_prompt,
        "negative_prompt": negative_prompt,
        "subtitle": str(subtitle or "")[:120],
        "render_metadata": {
            "aspect_ratio": delivery_profile["aspect_ratio"],
            "resolution": delivery_profile["resolution"],
            "width": delivery_profile["width"],
            "height": delivery_profile["height"],
            "fps": delivery_profile["fps"],
            "quality_preset": "short_drama",
            "render_quality": render_quality,
            "camera_motion": camera_motion,
            "duration": duration,
            "negative_prompt": negative_prompt,
            "episode_id": ep_id,
            "transition": transition,
            "subtitle": str(subtitle or "")[:120],
        },
        "qc_checklist": [
            "同一角色脸型、发型、服装与年龄是否稳定",
            "镜头运动是否平滑，没有突然抖动或背景撕裂",
            "关键台词/道具是否在竖屏安全区内清楚可见",
            "表情是否符合当前情绪爆点",
            "无水印、无侵权角色、无公众人物冒充、无不合规深伪",
        ],
    }


def enrich_short_drama_plan_for_cinema(
    plan: dict[str, Any],
    *,
    target_platform: str = "hongguo",
    render_quality: str = "upload_ready",
    backend: str = "comfyui",
) -> dict[str, Any]:
    """Add cinematic render prompts, queue jobs and delivery gates to a plan."""
    enriched = deepcopy(plan)
    delivery_profile = get_delivery_profile(target_platform)
    visual_mode = str(enriched.get("visual_mode") or "cinematic_realistic")

    compiled_shots: list[dict[str, Any]] = []
    queue_jobs: list[dict[str, Any]] = []
    episodes = enriched.get("episodes") or []
    for fallback_ep, episode in enumerate(episodes, start=1):
        if not isinstance(episode, dict):
            continue
        ep_id = _episode_id(episode, fallback_ep)
        shots = _extract_shots_from_episode(episode)
        compiled_for_episode = []
        for fallback_shot, shot in enumerate(shots, start=1):
            if "shot_id" not in shot:
                shot["shot_id"] = (ep_id - 1) * max(len(shots), 1) + fallback_shot
            compiled = compile_cinematic_shot_prompt(
                shot=shot,
                episode=episode,
                plan=enriched,
                delivery_profile=delivery_profile,
                visual_mode=visual_mode,
                render_quality=render_quality,
            )
            compiled_shots.append(compiled)
            compiled_for_episode.append(compiled)
            queue_jobs.append(
                {
                    "project_id": None,
                    "shot_id": f"ep{compiled['episode_id']}_shot{compiled['shot_id']}",
                    "backend": backend,
                    "input_prompt": compiled["positive_prompt"],
                    "input_assets": [],
                    "metadata": compiled["render_metadata"],
                }
            )
        episode["compiled_cinematic_shots"] = compiled_for_episode

    enriched["delivery_profile"] = delivery_profile
    enriched["compiled_cinematic_shots"] = compiled_shots
    enriched["cinematic_queue_jobs"] = queue_jobs
    enriched["quality_gates"] = deepcopy(QUALITY_GATES)
    enriched["render_pipeline"] = [
        "1. GPT/local planner writes episode arcs, hook, cliffhanger and shot beats.",
        "2. Cinematic compiler locks platform profile, character identity, lens language, lighting and negative prompts.",
        "3. Queue sends each shot to ComfyUI/Diffusers/external backend; image-to-video is preferred when reference frames exist.",
        "4. Quality gate checks sharpness, motion smoothness, temporal consistency, character consistency and safety.",
        "5. Failed shots are regenerated with stricter negative prompt or reference image before final composition.",
        "6. Composer exports vertical H.264/AAC MP4 for Hongguo/Douyin-style upload review.",
    ]
    enriched["human_review_required"] = True
    enriched["upload_ready_claim"] = (
        "The package is render-ready and upload-spec aligned. Actual cinematic quality still depends on the configured video model, GPU, reference images and manual review."
    )
    return enriched


def build_ffmpeg_delivery_command(input_path: str, output_path: str, profile: dict[str, Any]) -> list[str]:
    """Return a conservative ffmpeg command for platform-ready MP4 export."""
    return [
        "ffmpeg",
        "-y",
        "-i",
        input_path,
        "-vf",
        f"scale={profile['width']}:{profile['height']}:force_original_aspect_ratio=decrease,pad={profile['width']}:{profile['height']}:(ow-iw)/2:(oh-ih)/2,format={profile['pixel_format']}",
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
        output_path,
    ]
