# Cinematic Short-Drama Pipeline

This document describes the production path for turning one GPT prompt into a render-ready vertical short-drama package for Hongguo/Douyin-style delivery.

## What changed

The repository now has a dedicated cinematic compiler layer:

```text
User premise / novel fragment
-> Local planner or optional GPT planner
-> Cinematic prompt compiler
-> Platform delivery profile
-> Character continuity lock
-> Shot-level render prompts
-> Queue jobs with 1080p vertical metadata
-> Video backend: ComfyUI / Diffusers / Wan / CogVideoX / Hunyuan / LTX / external / mock
-> Quality gates
-> Composer / final MP4 export
```

The important distinction is this:

- `/api/short-drama/plan` creates the story plan.
- `/api/short-drama/cinematic-package` creates the render-ready production package.

Use `cinematic-package` for real production.

## Recommended request

```bash
curl -X POST http://localhost:8000/api/short-drama/cinematic-package \
  -H 'Content-Type: application/json' \
  -d '{
    "premise":"被背叛的女主重回宴会现场，当众夺回公司控制权，反派以为她只是弃子，下一秒董事长亲自向她递交任命书",
    "genre":"revenge",
    "visual_mode":"cinematic_realistic",
    "platform":"hongguo",
    "target_platform":"hongguo",
    "episodes":3,
    "shots_per_episode":6,
    "seconds_per_episode":60,
    "use_gpt":true,
    "fallback_to_local":true,
    "render_quality":"upload_ready",
    "backend":"comfyui",
    "submit_to_queue":false
  }'
```

If `OPENAI_API_KEY` is configured, the planner uses GPT first. If no key is configured and `fallback_to_local=true`, it still returns a deterministic local plan.

## Submit all compiled shots to the queue

You can either set `submit_to_queue: true` in the request above, or submit an already-created package:

```bash
curl -X POST http://localhost:8000/api/short-drama/submit-cinematic-jobs \
  -H 'Content-Type: application/json' \
  -d '{
    "backend":"comfyui",
    "project_id":"optional_project_id",
    "plan": { "...": "the cinematic package JSON" }
  }'
```

Each queue job contains:

- `input_prompt`: long cinematic render prompt
- `metadata.aspect_ratio`: `9:16`
- `metadata.resolution`: `1080p`
- `metadata.fps`: `24`
- `metadata.negative_prompt`: anti-drift / anti-artifact prompt
- `metadata.quality_preset`: `short_drama`
- `metadata.subtitle`: short subtitle/action line for later subtitle rendering

## Delivery profiles

Available profiles:

```http
GET /api/short-drama/delivery-profiles
```

Built-in targets:

- `hongguo`
- `douyin`
- `kuaishou`
- `generic_vertical`

All profiles default to vertical 1080x1920, H.264/AAC-style export assumptions and 24 fps render metadata. Final upload acceptance still depends on the platform's current app-side rules and moderation review.

## Quality gate

The package includes `quality_gates` and a manual review checklist. A shot should be regenerated when any of the following appears:

- protagonist face, hairstyle, clothing or age drifts across shots
- hand, eye, teeth or subtitle artifacts are obvious
- camera jitters, background tears or flickers
- first 3 seconds lack conflict or a clear visual hook
- ending reveals too much and loses cliffhanger value
- there is a watermark, public-figure impersonation, non-consensual face swap or copyright-character imitation

## Real cinematic quality depends on the backend

The mock backend is only a CPU demo. For film-like quality, configure a real backend and prefer image-to-video or reference-frame workflows for character continuity:

- ComfyUI workflow with text-to-video or image-to-video nodes
- Diffusers adapter for a local model
- Wan / CogVideoX / Hunyuan / LTX adapters when local weights are installed
- External inference backend when legally and commercially allowed

The repository does not include model weights. Store weights outside git and point adapters to local model paths or service URLs.

## Safe production boundary

Do not use the system for non-consensual deepfakes, public-figure impersonation, explicit sexual deepfakes, copyrighted-character cloning, fraud ads, medical/financial false claims, political deception or platform-rule evasion. Keep a manual review step before upload.
