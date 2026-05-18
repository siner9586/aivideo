"""Character bible, subtitle, and dubbing helpers for AI short drama."""
from __future__ import annotations

from typing import Any


def build_character_asset_pack(characters: list[dict[str, Any]], project_id: str | None = None) -> dict[str, Any]:
    assets = []
    for idx, character in enumerate(characters, start=1):
        name = character.get("name") or f"character_{idx}"
        visual_anchor = character.get("visual_anchor") or character.get("continuity_rule") or "stable face and costume"
        assets.append({
            "character_id": f"char_{idx:02d}",
            "name": name,
            "role": character.get("role", "supporting role"),
            "visual_anchor": visual_anchor,
            "voice": character.get("voice", "dramatic short-drama delivery"),
            "reference_images": [],
            "lora": None,
            "ip_adapter_images": [],
            "continuity_prompt": f"Keep {name} visually consistent across all shots. {visual_anchor}",
        })
    return {"project_id": project_id, "characters": assets}


def build_srt_from_plan(plan: dict[str, Any]) -> str:
    lines=[]
    cursor=0.0
    index=1
    for episode in plan.get('episodes') or []:
        shots=episode.get('storyboard',{}).get('shots') or episode.get('shots') or []
        for shot in shots:
            duration=float(shot.get('duration') or 4)
            text=shot.get('subtitle') or shot.get('action_prompt') or episode.get('cliffhanger') or '……'
            start=_fmt(cursor)
            end=_fmt(cursor+duration)
            lines.extend([str(index),f'{start} --> {end}',str(text)[:80],''])
            cursor+=duration
            index+=1
    return '\n'.join(lines).strip()+'\n'


def build_dubbing_script(plan: dict[str, Any]) -> dict[str, Any]:
    episodes=[]
    for episode in plan.get('episodes') or []:
        items=[]
        shots=episode.get('storyboard',{}).get('shots') or episode.get('shots') or []
        for shot in shots:
            text=shot.get('subtitle') or shot.get('action_prompt') or ''
            items.append({
                'shot_id':shot.get('shot_id'),
                'duration':shot.get('duration'),
                'speaker':'narrator_or_character',
                'line':text,
                'emotion':'dramatic',
                'voice_hint':shot.get('dubbing_hint') or shot.get('audio_hint') or 'short-drama pacing'
            })
        episodes.append({'episode_id':episode.get('episode_id'),'items':items})
    return {'dubbing_backend':'placeholder','episodes':episodes}


def _fmt(seconds: float) -> str:
    ms=int(round((seconds-int(seconds))*1000))
    total=int(seconds)
    s=total%60
    m=(total//60)%60
    h=total//3600
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'
