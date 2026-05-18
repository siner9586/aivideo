"""Short-drama production routes.

These endpoints expose a Hongguo/Douyin-style AI short-drama planning layer
on top of the generic video generation pipeline. They produce episode arcs,
shot plans, character continuity anchors, vertical-video defaults and batch
job prompts that can be sent to the existing queue/generation backends.
"""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.skills.gpt_short_drama_adapter import enhance_short_drama_with_gpt
from app.skills.short_drama_assets import build_character_asset_pack, build_dubbing_script, build_srt_from_plan
from app.skills.short_drama_planner import (
    GENRE_PRESETS,
    VisualMode,
    infer_platform_profile,
    plan_short_drama,
)

router = APIRouter(prefix="/api/short-drama", tags=["short-drama"])


class ShortDramaPlanRequest(BaseModel):
    premise: str = Field(..., min_length=2, description="Story premise, novel fragment, or short-drama idea.")
    genre: str = Field("revenge", description="Genre preset: revenge, rebirth, urban_romance, xianxia, business, family, suspense, comedy.")
    visual_mode: VisualMode = "cinematic_realistic"
    platform: str = "hongguo"
    episodes: int = Field(3, ge=1, le=24)
    shots_per_episode: int = Field(6, ge=4, le=10)
    seconds_per_episode: float | None = Field(None, ge=12, le=180)
    use_gpt: bool = Field(False, description="Use optional GPT refinement when OPENAI_API_KEY is configured.")
    fallback_to_local: bool = Field(True, description="Fall back to deterministic local planner when GPT is unavailable.")


class ViralScoreRequest(BaseModel):
    hook_text: str = ""
    cliffhanger_text: str = ""
    conflict_level: int = Field(3, ge=1, le=5)
    reversal_count: int = Field(1, ge=0, le=6)
    closeup_ratio: float = Field(0.35, ge=0, le=1)
    subtitle_density: float = Field(0.55, ge=0, le=1)


class ShortDramaPlanPayload(BaseModel):
    plan: dict = Field(default_factory=dict)
    project_id: str | None = None


@router.get("/genres")
def list_short_drama_genres() -> dict[str, object]:
    """List built-in short-drama genre presets."""
    return {"genres": sorted(GENRE_PRESETS.keys()), "presets": GENRE_PRESETS}


@router.get("/platform-profile/{platform}")
def get_platform_profile(platform: str) -> dict[str, object]:
    """Return vertical-video defaults for a target distribution platform."""
    return {"platform": platform, "profile": infer_platform_profile(platform)}


@router.post("/plan")
def create_short_drama_plan(body: ShortDramaPlanRequest) -> dict[str, object]:
    """Create a complete short-drama production package.

    The result includes title, platform defaults, character bible, continuity
    rules, episode beats, cliffhangers, shot prompts and batch generation jobs.
    When `use_gpt=true`, this endpoint tries optional GPT refinement first.
    """
    local_plan = plan_short_drama(
        premise=body.premise,
        genre=body.genre,
        visual_mode=body.visual_mode,
        platform=body.platform,
        episodes=body.episodes,
        shots_per_episode=body.shots_per_episode,
        seconds_per_episode=body.seconds_per_episode,
    )
    if not body.use_gpt:
        local_plan["provider"] = "local"
        return local_plan
    try:
        gpt_plan = enhance_short_drama_with_gpt(
            premise=body.premise,
            genre=body.genre,
            visual_mode=body.visual_mode,
            platform=body.platform,
            episodes=body.episodes,
            shots_per_episode=body.shots_per_episode,
        )
        gpt_plan.setdefault("platform_profile", local_plan.get("platform_profile"))
        gpt_plan.setdefault("negative_prompt", local_plan.get("negative_prompt"))
        gpt_plan.setdefault("production_notes", local_plan.get("production_notes"))
        return gpt_plan
    except Exception as exc:
        if not body.fallback_to_local:
            raise
        local_plan["provider"] = "local_fallback"
        local_plan["gpt_warning"] = str(exc)
        return local_plan


@router.post("/character-assets")
def create_character_assets(body: ShortDramaPlanPayload) -> dict[str, object]:
    """Build a model-agnostic character asset pack from a short-drama plan."""
    return build_character_asset_pack(body.plan.get("characters") or [], body.project_id)


@router.post("/subtitles/srt")
def create_srt_subtitles(body: ShortDramaPlanPayload) -> dict[str, object]:
    """Create a rough SRT subtitle draft from the plan's shots."""
    return {"format": "srt", "content": build_srt_from_plan(body.plan)}


@router.post("/dubbing-script")
def create_dubbing_script(body: ShortDramaPlanPayload) -> dict[str, object]:
    """Create a dubbing script draft grouped by episode and shot."""
    return build_dubbing_script(body.plan)


@router.post("/viral-score")
def score_short_drama_virality(body: ViralScoreRequest) -> dict[str, object]:
    """Heuristic score for short-drama retention potential.

    This is not a platform predictor. It is a production-side checklist that
    nudges creators toward strong hooks, conflict, reversals, closeups and
    cliffhangers.
    """
    hook = min(25, len(body.hook_text.strip()) * 0.7)
    cliffhanger = min(25, len(body.cliffhanger_text.strip()) * 0.65)
    conflict = body.conflict_level * 8
    reversals = min(18, body.reversal_count * 4)
    closeup = body.closeup_ratio * 12
    subtitle = body.subtitle_density * 10
    score = round(min(100, hook + cliffhanger + conflict + reversals + closeup + subtitle), 2)
    notes: list[str] = []
    if not body.hook_text.strip():
        notes.append("缺少前 3 秒钩子，建议用强冲突台词或异常画面开场。")
    if not body.cliffhanger_text.strip():
        notes.append("缺少结尾悬念，建议在真相揭露前切断。")
    if body.conflict_level < 3:
        notes.append("冲突强度偏低，短剧场景需要更明确的对抗关系。")
    if body.closeup_ratio < 0.25:
        notes.append("特写比例偏低，竖屏短剧建议增加表情和反应镜头。")
    return {
        "viral_score": score,
        "dimensions": {
            "hook": round(hook, 2),
            "cliffhanger": round(cliffhanger, 2),
            "conflict": conflict,
            "reversals": reversals,
            "closeup": round(closeup, 2),
            "subtitle": round(subtitle, 2),
        },
        "notes": notes,
    }
