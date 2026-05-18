# AI Short Drama Architecture

## Overview

`AI Video Studio` 已从通用 AI 视频生成器扩展为 `AI Short Drama Studio`。

新增能力：

- 红果 / 抖音式短剧节奏
- 3 秒 Hook 结构
- Cliffhanger 悬念切断
- 角色一致性提示
- 竖屏 9:16 镜头语法
- 分集结构化 storyboard
- 批量镜头 generation jobs
- Viral Score 启发式评分

---

## New API

### Create short drama package

```http
POST /api/short-drama/plan
```

Example:

```json
{
  "premise": "被豪门陷害的女主重回宴会现场反击",
  "genre": "revenge",
  "visual_mode": "cinematic_realistic",
  "platform": "hongguo",
  "episodes": 3,
  "shots_per_episode": 6,
  "seconds_per_episode": 60
}
```

Response includes:

- character bible
- episode arcs
- cliffhangers
- storyboard shots
- generation jobs
- negative prompts
- production notes

---

### Viral score

```http
POST /api/short-drama/viral-score
```

This endpoint estimates:

- hook strength
- cliffhanger density
- conflict intensity
- reversal density
- close-up ratio
- subtitle pacing

---

## Production Pipeline

```text
Novel / Premise
→ Genre Template
→ Hook Engine
→ Episode Arc
→ Character Continuity
→ Director Shot Planning
→ Generation Jobs
→ Queue
→ ComfyUI / Diffusers / External Backend
→ Subtitle / Dubbing
→ Composer
→ Viral Score
```

---

## Recommended Model Stack

| Capability | Recommended |
|---|---|
| Character images | Flux / SDXL |
| Character consistency | IP-Adapter / LoRA |
| I2V | Kling / Wan / LTX |
| Voice | CosyVoice / GPT-SoVITS |
| Subtitle | Whisper |
| Editing | Premiere / CapCut |

---

## Future Directions

### Phase 3

- Character embedding registry
- Automatic subtitle pacing
- AI dubbing pipeline
- Emotion curve editor
- Scene template marketplace
- Director-style presets
- Batch rendering dashboard
- Timeline drag editor
- AI trailer generation
- Publishing adapters for Rednote / Douyin / Hongguo

### Phase 4

- Multi-agent production pipeline
- AI editor agent
- AI director agent
- AI continuity supervisor
- AI recommendation optimizer
- Automatic A/B hook testing
