# AI Short Drama Studio

This document describes the short-drama production layer added on top of AI Video Studio.

The goal is not to copy a closed commercial platform. The goal is to provide an extensible engineering framework for Hongguo/Douyin-style AI short-drama workflows: premise-to-episode planning, strong hooks, cliffhangers, vertical-video defaults, character continuity, shot-level director prompts and batch generation jobs.

## Why this layer exists

Generic video generation usually follows:

```text
Prompt -> Storyboard -> Generate -> Compose
```

Short-drama production needs a different structure:

```text
Premise / Novel fragment
-> Genre template
-> Hook and conflict design
-> Episode arc
-> Character bible
-> Director shot plan
-> Cliffhanger
-> Batch generation jobs
-> Queue / Backend / Composer
```

## New API endpoints

### List genre presets

```http
GET /api/short-drama/genres
```

Built-in genres:

- `revenge`
- `rebirth`
- `urban_romance`
- `xianxia`
- `business`
- `family`
- `suspense`
- `comedy`

### Get platform defaults

```http
GET /api/short-drama/platform-profile/hongguo
```

The default profile is vertical-first:

```json
{
  "aspect_ratio": "9:16",
  "resolution": "720p",
  "fps": 16,
  "episode_seconds": 60,
  "hook_seconds": 3
}
```

### Plan a short drama

```http
POST /api/short-drama/plan
```

Example request:

```json
{
  "premise": "被背叛的女主重回宴会现场，当众夺回公司控制权",
  "genre": "revenge",
  "visual_mode": "cinematic_realistic",
  "platform": "hongguo",
  "episodes": 3,
  "shots_per_episode": 6,
  "seconds_per_episode": 60
}
```

Example output includes:

- `title`
- `platform_profile`
- `characters`
- `episodes`
- `generation_jobs`
- `negative_prompt`
- `production_notes`
- `markdown`

### Score short-drama virality heuristics

```http
POST /api/short-drama/viral-score
```

Example request:

```json
{
  "hook_text": "你被开除了。下一秒，董事长却向她鞠躬。",
  "cliffhanger_text": "她刚要说出真相，门被推开。",
  "conflict_level": 5,
  "reversal_count": 2,
  "closeup_ratio": 0.45,
  "subtitle_density": 0.65
}
```

The score is a production-side checklist, not a real platform predictor.

## Production logic

Each episode is decomposed into a repeatable short-drama grammar:

1. 3-second hook
2. relationship setup
3. conflict escalation
4. evidence / prop insert
5. emotional peak
6. cliffhanger cut

This is mapped to shot-level prompts with camera angle, motion, action prompt, audio hint and consistency notes.

## Character consistency

The planner generates a character bible with continuity anchors, such as:

- stable hairstyle
- stable costume palette
- stable facial description
- voice / delivery style
- anti-drift prompt notes

In production, these anchors should be bound to reference images, LoRA, IP-Adapter, ComfyUI workflows or external image-to-video backends.

## Recommended next implementation steps

1. Add a frontend `ShortDramaWorkspace` page.
2. Add a `CharacterBiblePanel` for reference images and LoRA/IP-Adapter metadata.
3. Add batch submission from `generation_jobs` to `/api/queue/submit`.
4. Add subtitle and dubbing adapters for CosyVoice / GPT-SoVITS.
5. Add per-shot continuity quality checks after generation.
6. Add a project export preset for vertical micro-drama delivery.

## Safety boundary

Do not use this system for non-consensual face swaps, public-figure impersonation, explicit deepfakes, copyright character cloning, fraud ads, political deception, medical/financial false claims or extreme violent content.
