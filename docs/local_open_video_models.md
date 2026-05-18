# Local Open Video Models

This guide explains how to solve the real-video-quality problem without paid external model APIs.

The repository now includes a `local_open_video` backend and maps `ltx`, `wan`, `cogvideox`, `hunyuan`, `diffusers_t2v`, and `diffusers_i2v` to a shared local/open-weight Diffusers-compatible adapter.

## What changed

Before this upgrade, several real-model backends were placeholders and fell back to the OpenCV mock backend. After this upgrade:

- `local_open_video` is available as a first-class backend.
- `ltx`, `wan`, `cogvideox`, and `hunyuan` try to load local/open video model weights.
- `diffusers_t2v` and `diffusers_i2v` delegate to the same local open video adapter.
- The mock backend remains available for CPU-only demos.
- No paid external video-generation API is required.

## Recommended open/local model families

### LTX-Video

Good for iterative workflows, image-to-video, multi-keyframe/control workflows, and faster production loops. Use this first if you want a practical local pipeline.

Environment examples:

```bash
VIDEO_BACKEND=ltx
LTX_MODEL_PATH=/models/ltx-video
# or
LTX_MODEL_ID=Lightricks/LTX-Video
```

### Wan

Good target for high-quality open text-to-video or image-to-video, especially if you have enough VRAM. The smaller 1.3B model is more practical for consumer GPUs.

```bash
VIDEO_BACKEND=wan
WAN_MODEL_PATH=/models/wan2.1-t2v-1.3b
# or
WAN_MODEL_ID=Wan-AI/Wan2.1-T2V-1.3B-Diffusers
```

### CogVideoX

Good open-source video-generation family for text-to-video and image-to-video workflows.

```bash
VIDEO_BACKEND=cogvideox
COGVIDEOX_MODEL_PATH=/models/cogvideox
# or
COGVIDEOX_MODEL_ID=THUDM/CogVideoX-5b
```

### HunyuanVideo

High-capacity open video model family. Expect heavier hardware requirements.

```bash
VIDEO_BACKEND=hunyuan
HUNYUAN_MODEL_PATH=/models/hunyuanvideo
# or
HUNYUAN_MODEL_ID=tencent/HunyuanVideo
```

### Generic Diffusers-compatible model

```bash
VIDEO_BACKEND=local_open_video
LOCAL_VIDEO_MODEL_PATH=/models/your-diffusers-video-model
# or
LOCAL_VIDEO_MODEL_ID=your-org/your-video-model
```

## Install optional dependencies

Do not install these on lightweight CPU-only demo machines.

```bash
pip install -r requirements.txt
# Install the correct torch build for your CUDA / ROCm / CPU platform first.
# Example only; adjust to your machine:
pip install --index-url https://download.pytorch.org/whl/cu121 torch torchvision torchaudio
pip install -r requirements-local-video.txt
```

## Quality presets

The backend supports these presets:

| Preset | Use case | Default behavior |
|---|---|---|
| `draft` | quick test | lower steps, 480p cap |
| `balanced` | preview production | medium steps, 720p cap |
| `quality` | better shot rendering | higher steps, 720p cap |
| `short_drama` | default for short-drama shots | 16fps, 81 frames, 720p cap |

Environment override:

```bash
LOCAL_VIDEO_QUALITY_PRESET=short_drama
LOCAL_VIDEO_STEPS=32
LOCAL_VIDEO_NUM_FRAMES=81
LOCAL_VIDEO_GUIDANCE=6.5
LOCAL_VIDEO_DTYPE=auto
LOCAL_VIDEO_DEVICE=auto
```

Queue jobs can also pass:

```json
{
  "metadata": {
    "quality_preset": "short_drama",
    "aspect_ratio": "9:16",
    "resolution": "720p"
  }
}
```

## Fallback policy

By default, if local weights or dependencies are missing, the system falls back to the mock backend so the product demo still runs:

```bash
LOCAL_VIDEO_ALLOW_MOCK_FALLBACK=true
```

For strict production validation, disable fallback:

```bash
LOCAL_VIDEO_ALLOW_MOCK_FALLBACK=false
```

Then missing weights or runtime errors will fail loudly instead of producing a mock clip.

## Short-drama workflow

1. Open the web app.
2. Use AI短剧工作台.
3. Select `local_open_video`, `ltx`, `wan`, `cogvideox`, or `hunyuan` as backend.
4. Generate a short-drama plan.
5. Create project.
6. Write shots to timeline.
7. Submit batch jobs.
8. Watch QueuePanel.
9. Compose final video after shots complete.

## Hardware expectations

Local video models are VRAM-heavy. Practical guidance:

- Start with small/distilled models and short clips.
- Use `draft` first, then `balanced`, then `short_drama` or `quality`.
- Prefer 9:16 480p or 720p for short-drama shots.
- Use `ENABLE_MODEL_CPU_OFFLOAD=true`, `ENABLE_VAE_TILING=true`, and `ENABLE_ATTENTION_SLICING=true`.
- Use one shot at a time when VRAM is limited.

## What this does not solve yet

This upgrade removes the placeholder problem and enables local open models, but these production items still require further work:

- model-specific optimized pipelines for each family;
- LoRA/IP-Adapter binding per character;
- RIFE/EMA-VFI frame interpolation;
- Real-ESRGAN or similar upscaling;
- automatic retry with lower preset when VRAM is insufficient;
- shot-to-shot identity verification.

Those are next steps for improving stability and visual consistency beyond base model quality.
