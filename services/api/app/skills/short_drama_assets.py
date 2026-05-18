"""Character bible, dubbing, and subtitle helpers for short-drama projects."""
from __future__ import annotations

from typing import Any


def build_character_asset_pack(characters: list[dict[str, Any]], project_id: str | None = None) -> dict[str, Any]:
    """Create model-agnostic character asset metadata.

    The result can be bound later to reference images, LoRA names, IP-Adapter
    image paths, ComfyUI nodes, or external model IDs.
    """
    assets = []
    for idx, character in enumerate(characters, start=1):
        name = character.get("name") or f"character_{idx}"
        visual_anchor = character.get("visual_anchor") or character.get("continuity_rule") or "stable face, stable costume"
        assets.append(
            {
                "character_id": f"char_{idx:02d}",
                "name": name,
                "role": character.get("role", "supporting role"),
                "visual_anchor": visual_anchor,
                "voice": character.get("voice", "natural short-drama delivery"),
                "reference_images": [],
                "lora": None,
                "ip_adapter_images": [],
                "comfyui_overrides": {},
                "continuity_prompt": (
                    f"Keep {name} visually consistent across all shots: {visual_anchor}. "
                    "Do not change hairstyle, face shape, costume color, age, or identity."
                ),
            }
        )
    return {"project_id": project_id, "characters": assets}


def build_srt_from_plan(plan: dict[str, Any]) -> str:
    """Create a rough SRT subtitle draft from a short-drama plan."""
    lines: list[str] = []
    cursor = 0.0
    index = 1
    episodes = plan.get("episodes") or []
    for episode in episodes:
        shots = episode.get("storyboard", {}).get("shots") or episode.get("shots") or []
        for shot in shots:
            duration = float(shot.get("duration") or 4)
            text = shot.get("subtitle") or shot.get("action_prompt") or episode.get("cliffhanger") or ""
            start = _fmt_time(cursor)
            end = _fmt_time(cursor + duration)
            lines.extend([str(index), f"{start} --> {end}", str(text).strip()[:80] or "……", ""])
            cursor += duration
            index += 1
    return "\n".join(lines).strip() + "\n"


def build_dubbing_script(plan: dict[str, Any]) -> dict[str, Any]:
    """Create a dubbing script draft grouped by episode and shot."""
    script = []
    for episode in plan.get("episodes") or []:
        episode_id = episode.get("episode_id", len(script) + 1)
        shots = episode.get("storyboard", {}).get("shots") or episode.get("shots") or []
        items = []
        for shot in shots:
            text = shot.get("subtitle") or shot.get("action_prompt") or ""
            items.append(
                {
                    "shot_id": shot.get("shot_id"),
                    "duration": shot.get("duration"),
                    "speaker": "narrator_or_character",
                    "line": text,
                    "emotion": "tense" if "真相" in str(text) or "反" in str(text) else "dramatic",
                    "voice_hint": shot.get("dubbing_hint") or shot.get("audio_hint") or "short-drama pacing",
                }
            )
        script.append({"episode_id": episode_id, "items": items})
    return {"dubbing_backend": "placeholder", "episodes": script}


def _fmt_time(seconds: float) -> str:
    ms = int(round((seconds - int(seconds)) * 1000))
    total = int(seconds)
    s = total % 60
    m = (total // 60) % 60
    h = total // 3600
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
