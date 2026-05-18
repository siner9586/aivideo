"""AI short-drama planning utilities.

This module turns a long-form idea or web-novel style premise into a
vertical short-drama production package: episode beats, cliffhangers,
shot-level prompts, character continuity notes, audio/subtitle cues and
batch-generation jobs.

It intentionally stays model-agnostic. The generated prompts can be sent to
ComfyUI, Diffusers adapters, external APIs, or the existing mock backend.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.models.schemas import GenerationJob, Storyboard, StoryboardShot

DramaGenre = Literal[
    "urban_romance",
    "revenge",
    "rebirth",
    "xianxia",
    "business",
    "family",
    "suspense",
    "comedy",
]

VisualMode = Literal["ai_manhua", "cinematic_realistic", "hybrid_live_action"]

GENRE_PRESETS: dict[str, dict[str, object]] = {
    "urban_romance": {
        "title_prefix": "契约与心动",
        "tropes": ["误会", "身份反差", "暧昧拉扯", "情绪爆点"],
        "settings": ["豪门客厅", "公司走廊", "雨夜街边", "电梯门口"],
        "emotion": "high-tension romantic conflict",
    },
    "revenge": {
        "title_prefix": "逆袭归来",
        "tropes": ["背叛", "忍辱", "反转", "当众打脸"],
        "settings": ["宴会厅", "办公室", "家族会议", "地下停车场"],
        "emotion": "compressed revenge and reveal",
    },
    "rebirth": {
        "title_prefix": "重生改命",
        "tropes": ["前世遗憾", "重来一次", "预知反击", "命运转折"],
        "settings": ["医院走廊", "婚礼现场", "老宅书房", "暴雨夜"],
        "emotion": "urgent second-chance transformation",
    },
    "xianxia": {
        "title_prefix": "仙门风云",
        "tropes": ["废柴觉醒", "师门危机", "秘境奇遇", "身份揭露"],
        "settings": ["云雾仙山", "宗门大殿", "竹林石阶", "古战场"],
        "emotion": "epic fantasy escalation",
    },
    "business": {
        "title_prefix": "商战暗涌",
        "tropes": ["危机决策", "权力博弈", "证据反转", "会议对峙"],
        "settings": ["董事会会议室", "金融中心", "深夜办公室", "发布会后台"],
        "emotion": "strategic pressure and controlled confrontation",
    },
    "family": {
        "title_prefix": "亲情裂痕",
        "tropes": ["误解", "牺牲", "认亲", "和解或反击"],
        "settings": ["老宅餐厅", "病房", "小区楼下", "家族聚会"],
        "emotion": "family melodrama with moral choice",
    },
    "suspense": {
        "title_prefix": "真相倒计时",
        "tropes": ["线索", "误导", "追问", "最后一秒反转"],
        "settings": ["昏暗书房", "监控室", "雨夜巷口", "废弃仓库"],
        "emotion": "tight mystery and escalating danger",
    },
    "comedy": {
        "title_prefix": "反套路人生",
        "tropes": ["错位", "反差", "尴尬升级", "笑点回收"],
        "settings": ["办公室", "便利店", "相亲现场", "电梯间"],
        "emotion": "fast comic reversal",
    },
}

SHOT_TEMPLATES = [
    ("3秒钩子", "extreme close-up", "fast push-in", "用一句强冲突台词或视觉异常抓住注意力"),
    ("关系建立", "medium two-shot", "slow dolly", "交代人物关系、身份差异与潜在矛盾"),
    ("冲突升级", "over-the-shoulder", "handheld micro-shake", "让对峙更明确，台词短促，情绪上升"),
    ("证据/道具", "detail insert", "snap zoom", "给出戒指、合同、手机信息、令牌等关键物件"),
    ("情绪爆点", "close-up", "slow push-in", "保留人物表情和停顿，制造二次传播截图"),
    ("结尾悬念", "wide-to-close", "freeze-like hold", "在真相揭露前切断，促使点击下一集"),
]

NEGATIVE_SHORT_DRAMA_PROMPT = (
    "low quality, blurry, inconsistent face, extra fingers, distorted hands, "
    "random costume changes, identity drift, subtitle artifacts, watermark, logo, "
    "overexposed skin, chaotic camera, broken anatomy"
)

@dataclass(frozen=True)
class DramaCharacter:
    name: str
    role: str
    visual_anchor: str
    voice: str
    continuity_rule: str


def normalize_genre(genre: str | None) -> str:
    if not genre:
        return "revenge"
    return genre if genre in GENRE_PRESETS else "revenge"


def build_default_characters(genre: str, premise: str) -> list[DramaCharacter]:
    genre = normalize_genre(genre)
    if genre == "xianxia":
        return [
            DramaCharacter("女主", "fallen disciple", "清冷坚韧的年轻女修，白青色衣袍，发簪，眼神克制", "克制、低声、坚定", "每个镜头保持同一发型、衣袍色系、眉眼特征"),
            DramaCharacter("反派", "sect rival", "黑金长袍，狭长眼，笑意危险", "轻蔑、压迫", "保持黑金长袍和冷笑，不随机更换身份"),
        ]
    if genre == "business":
        return [
            DramaCharacter("主角", "young executive", "深色西装，干净短发，冷静但疲惫的眼神", "冷静、压低语速", "保持深色西装、短发、同一办公精英气质"),
            DramaCharacter("对手", "boardroom opponent", "灰色西装，银框眼镜，控制欲强", "咄咄逼人", "保持银框眼镜、灰色西装和董事会压迫感"),
        ]
    return [
        DramaCharacter("女主", "underdog protagonist", "现代都市女性，黑色长发，米白外套，眼神倔强", "先压抑后爆发", "保持黑色长发、米白外套、倔强眼神，不换脸"),
        DramaCharacter("男主", "powerful ally", "高个男性，深色大衣，轮廓清晰，表情克制", "低沉、简短、有保护感", "保持深色大衣、清晰轮廓和克制表情"),
        DramaCharacter("反派", "antagonist", "精致但刻薄，红色或深色服装，目光锋利", "尖锐、挑衅", "保持服装色彩和锋利表情，不随机变成路人"),
    ]


def infer_platform_profile(platform: str | None) -> dict[str, object]:
    """Return sensible defaults for short-drama distribution platforms."""
    platform_key = (platform or "hongguo").lower()
    if platform_key in {"hongguo", "redfruit", "douyin", "tiktok_cn"}:
        return {"aspect_ratio": "9:16", "resolution": "720p", "fps": 16, "episode_seconds": 60, "hook_seconds": 3}
    return {"aspect_ratio": "9:16", "resolution": "720p", "fps": 16, "episode_seconds": 45, "hook_seconds": 3}


def _episode_arc(episode_index: int, total_episodes: int, genre: str, premise: str) -> dict[str, str]:
    preset = GENRE_PRESETS[normalize_genre(genre)]
    tropes = preset["tropes"]
    assert isinstance(tropes, list)
    trope = str(tropes[(episode_index - 1) % len(tropes)])
    if episode_index == 1:
        beat = f"开场直接抛出核心冲突：{premise}；用{trope}制造强钩子。"
    elif episode_index == total_episodes:
        beat = f"集中回收前文伏笔，完成阶段性反击，但保留更大危机。"
    else:
        beat = f"围绕{trope}推进一次小反转，让主角获得线索或失去优势。"
    cliffhanger = [
        "门被推开，真正掌权者出现。",
        "手机屏幕亮起，一条匿名证据改变局面。",
        "主角刚要说出真相，画面切到反派微笑。",
        "关键人物认出了主角隐藏的身份。",
    ][(episode_index - 1) % 4]
    return {"beat": beat, "cliffhanger": cliffhanger}


def plan_short_drama(
    premise: str,
    genre: str | None = "revenge",
    visual_mode: VisualMode = "cinematic_realistic",
    platform: str | None = "hongguo",
    episodes: int = 3,
    shots_per_episode: int = 6,
    seconds_per_episode: float | None = None,
) -> dict[str, object]:
    """Create a production-ready AI short-drama package."""
    genre = normalize_genre(genre)
    profile = infer_platform_profile(platform)
    episodes = max(1, min(24, int(episodes)))
    shots_per_episode = max(4, min(10, int(shots_per_episode)))
    episode_seconds = float(seconds_per_episode or profile["episode_seconds"])
    preset = GENRE_PRESETS[genre]
    characters = build_default_characters(genre, premise)
    title = f"{preset['title_prefix']}：{premise[:18]}" if premise else str(preset["title_prefix"])

    drama_episodes: list[dict[str, object]] = []
    generation_jobs: list[GenerationJob] = []
    markdown_lines = [f"# {title}", "", f"- Genre: {genre}", f"- Visual mode: {visual_mode}", f"- Platform profile: {platform or 'hongguo'} / {profile['aspect_ratio']}", ""]

    character_block = "; ".join(
        f"{c.name}({c.role}): {c.visual_anchor}; continuity: {c.continuity_rule}" for c in characters
    )

    for ep in range(1, episodes + 1):
        arc = _episode_arc(ep, episodes, genre, premise)
        shot_duration = round(episode_seconds / shots_per_episode, 2)
        shots: list[StoryboardShot] = []
        markdown_lines.append(f"## Episode {ep}: {arc['beat']}")
        for shot_idx in range(1, shots_per_episode + 1):
            label, camera_angle, camera_motion, function = SHOT_TEMPLATES[(shot_idx - 1) % len(SHOT_TEMPLATES)]
            setting_list = preset["settings"]
            assert isinstance(setting_list, list)
            setting = str(setting_list[(ep + shot_idx - 2) % len(setting_list)])
            is_final = shot_idx == shots_per_episode
            action = arc["cliffhanger"] if is_final else function
            visual_prompt = (
                f"Vertical AI short drama, {visual_mode}, episode {ep}, shot {shot_idx}. "
                f"Premise: {premise}. Scene: {setting}. Shot function: {label}. "
                f"Characters: {character_block}. Keep high facial consistency, stable costume, "
                f"Chinese micro-drama pacing, cinematic lighting, clean background, no watermark."
            )
            audio_hint = "快节奏短剧配乐，关键台词前留 0.3 秒停顿，结尾上扬制造下一集点击"
            shot = StoryboardShot(
                shot_id=(ep - 1) * shots_per_episode + shot_idx,
                duration=shot_duration,
                camera_angle=camera_angle,
                camera_motion=camera_motion,
                visual_prompt=visual_prompt,
                action_prompt=action,
                transition="cut" if not is_final else "cliffhanger_cut",
                audio_hint=audio_hint,
                consistency_notes=character_block,
            )
            shots.append(shot)
            generation_jobs.append(
                GenerationJob(
                    shot_id=shot.shot_id,
                    prompt=f"{visual_prompt} Action: {action}. Negative prompt: {NEGATIVE_SHORT_DRAMA_PROMPT}",
                    duration=shot.duration,
                    camera_motion=shot.camera_motion,
                )
            )
            markdown_lines.append(
                f"- Shot {shot_idx} · {label} · {shot.duration}s · {camera_angle}/{camera_motion}: {action}"
            )
        storyboard = Storyboard(
            title=f"{title} · Episode {ep}",
            total_duration=round(sum(s.duration for s in shots), 2),
            shots=shots,
        )
        storyboard.markdown = _storyboard_markdown(storyboard)
        drama_episodes.append(
            {
                "episode_id": ep,
                "beat": arc["beat"],
                "cliffhanger": arc["cliffhanger"],
                "storyboard": storyboard.model_dump(),
            }
        )
        markdown_lines.append("")

    return {
        "title": title,
        "platform_profile": profile,
        "genre": genre,
        "visual_mode": visual_mode,
        "premise": premise,
        "characters": [c.__dict__ for c in characters],
        "episodes": drama_episodes,
        "generation_jobs": [job.model_dump() for job in generation_jobs],
        "negative_prompt": NEGATIVE_SHORT_DRAMA_PROMPT,
        "production_notes": [
            "优先使用图生视频保持角色一致性；关键人物先生成参考图或 LoRA/IP-Adapter 资产。",
            "每集前 3 秒必须给出冲突、异常或强台词；每集末尾用 cliffhanger_cut。",
            "默认竖屏 9:16，适合红果/抖音式短剧预览；长剧情建议分批生成镜头。",
            "禁止非自愿换脸、公众人物冒充、侵权角色复刻和误导性广告。",
        ],
        "markdown": "\n".join(markdown_lines),
    }


def _storyboard_markdown(storyboard: Storyboard) -> str:
    lines = [f"# {storyboard.title}", f"Total duration: {storyboard.total_duration:.1f}s"]
    for s in storyboard.shots:
        lines.append(
            f"\n## Shot {s.shot_id} · {s.duration:.1f}s"
            f"\n- Camera: {s.camera_angle} / {s.camera_motion}"
            f"\n- Visual: {s.visual_prompt}"
            f"\n- Action: {s.action_prompt}"
            f"\n- Transition: {s.transition}"
            f"\n- Audio: {s.audio_hint}"
            f"\n- Consistency: {s.consistency_notes}"
        )
    return "\n".join(lines)
