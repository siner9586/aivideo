"""Optional GPT adapter for short-drama planning.

The core short-drama planner is deterministic and can run without network or
API keys. This adapter optionally asks a GPT-compatible OpenAI model to refine
a premise into a stronger micro-drama package.

Configuration:
- OPENAI_API_KEY: required to enable GPT planning
- OPENAI_MODEL: optional, defaults to gpt-4.1-mini

No secret is stored in the repository. If the OpenAI SDK or key is missing,
the caller should fall back to the local planner.
"""
from __future__ import annotations

import json
import os
from typing import Any

SYSTEM_PROMPT = """You are a senior Chinese AI short-drama producer.
Return ONLY valid JSON. Design a Hongguo/Douyin-style vertical AI short drama.
Focus on a strong first-3-second hook, compressed conflict, character continuity,
shot-level director prompts, subtitles, dubbing cues, and cliffhangers.
Avoid illegal, unsafe, non-consensual face swap, public-figure impersonation,
explicit deepfake, copyright character cloning, fraud ads and political deception.
"""


def _extract_output_text(response: Any) -> str:
    """Best-effort extraction across OpenAI Python SDK response shapes."""
    text = getattr(response, "output_text", None)
    if isinstance(text, str) and text.strip():
        return text
    chunks: list[str] = []
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            value = getattr(content, "text", None)
            if isinstance(value, str):
                chunks.append(value)
    return "\n".join(chunks).strip()


def enhance_short_drama_with_gpt(
    premise: str,
    genre: str = "revenge",
    episodes: int = 3,
    shots_per_episode: int = 6,
    visual_mode: str = "cinematic_realistic",
    platform: str = "hongguo",
) -> dict[str, Any]:
    """Return a GPT-refined short-drama JSON package.

    Raises RuntimeError when GPT integration is not configured; callers can
    catch it and fall back to the deterministic planner.
    """
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not configured")
    try:
        from openai import OpenAI  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency path
        raise RuntimeError("openai package is not installed") from exc

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    user_payload = {
        "premise": premise,
        "genre": genre,
        "episodes": episodes,
        "shots_per_episode": shots_per_episode,
        "visual_mode": visual_mode,
        "platform": platform,
        "required_json_schema": {
            "title": "string",
            "logline": "string",
            "characters": [
                {
                    "name": "string",
                    "role": "string",
                    "visual_anchor": "string",
                    "voice": "string",
                    "continuity_rule": "string",
                }
            ],
            "episodes": [
                {
                    "episode_id": "number",
                    "hook": "string",
                    "beat": "string",
                    "cliffhanger": "string",
                    "shots": [
                        {
                            "shot_id": "number",
                            "duration": "number",
                            "camera_angle": "string",
                            "camera_motion": "string",
                            "visual_prompt": "string",
                            "action_prompt": "string",
                            "subtitle": "string",
                            "dubbing_hint": "string",
                            "transition": "string",
                        }
                    ],
                }
            ],
            "generation_jobs": [
                {
                    "shot_id": "number",
                    "prompt": "string",
                    "duration": "number",
                    "camera_motion": "string",
                }
            ],
            "safety_notes": ["string"],
        },
    }
    client = OpenAI()
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
        ],
    )
    raw = _extract_output_text(response)
    if not raw:
        raise RuntimeError("GPT response did not contain text")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start < 0 or end < start:
            raise RuntimeError("GPT response was not valid JSON")
        data = json.loads(raw[start : end + 1])
    data["provider"] = "openai"
    data["model"] = model
    return data
