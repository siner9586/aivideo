# Real Model Setup

Phase 2 keeps real model execution opt-in. The repository contains interfaces, configuration points and fallback behavior, but no model weights.

## Supported backend names

- `mock`
- `comfyui`
- `diffusers_t2v`
- `diffusers_i2v`
- `external`
- `wan`
- `cogvideox`
- `hunyuan`
- `ltx`

## Recommended setup pattern

1. Confirm the app works with `VIDEO_BACKEND=mock`.
2. Install GPU runtime separately from the default CPU demo environment.
3. Place model weights outside the repository, for example `/models/aivideo/...`.
4. Configure model paths with environment variables.
5. Start with a single backend and one short shot.
6. Keep queue concurrency low until VRAM usage is known.

## Environment examples

```bash
VIDEO_BACKEND=mock

# ComfyUI
VIDEO_BACKEND=comfyui
COMFYUI_BASE_URL=http://127.0.0.1:8188
COMFYUI_WORKFLOW_PATH=examples/workflows/comfyui_text_to_video_example.json

# Diffusers
VIDEO_BACKEND=diffusers_t2v
DIFFUSERS_MODEL_PATH=/models/your-video-model
DIFFUSERS_DEVICE=auto
ENABLE_CPU_OFFLOAD=true
ENABLE_ATTENTION_SLICING=true
ENABLE_VAE_TILING=true

# Family-specific placeholders
WAN_MODEL_PATH=/models/wan
COGVIDEOX_MODEL_PATH=/models/cogvideox
HUNYUAN_MODEL_PATH=/models/hunyuan
LTX_MODEL_PATH=/models/ltx
```

## Fallback behavior

If the selected real backend is not configured or unavailable, the app falls back to the mock backend and returns a log message explaining the fallback. This keeps the product workflow usable on CPU-only machines.

## Do not commit

- Model weights
- API keys
- Private media
- Generated videos under `data/outputs`
- Local caches
- `node_modules`, `venv`, `.env`
