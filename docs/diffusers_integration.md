# Diffusers Integration

Diffusers support in Phase 2 is configuration-driven and safe by default. AI Video Studio does not download large model weights automatically. If no model path or model id is configured, the system falls back to the mock backend.

## Environment variables

```bash
VIDEO_BACKEND=diffusers_t2v
DIFFUSERS_MODEL_ID=
DIFFUSERS_MODEL_PATH=/models/your-video-model
DIFFUSERS_DEVICE=auto
DIFFUSERS_DTYPE=auto
ENABLE_CPU_OFFLOAD=true
ENABLE_ATTENTION_SLICING=true
ENABLE_VAE_TILING=true
```

## Backends

- `diffusers_t2v`: text-to-video interface.
- `diffusers_i2v`: image-to-video interface.

Both adapters live under `services/api/app/backends/`.

## Current beta behavior

Phase 2 provides a robust adapter boundary and fallback semantics. Because video pipelines differ across AnimateDiff, CogVideoX, Wan, HunyuanVideo, LTX and other model families, the generic Diffusers adapter avoids hard-coding one pipeline. A concrete model-specific adapter should be added once you choose the target model.

## Recommended local sequence

1. Run the app with `VIDEO_BACKEND=mock`.
2. Confirm project, queue and composer work.
3. Install GPU dependencies in a separate environment.
4. Set `DIFFUSERS_MODEL_PATH` or `DIFFUSERS_MODEL_ID`.
5. Add a concrete pipeline export function for the selected model.
6. Keep fallback to mock enabled during development.

## Important notes

- Do not commit model weights.
- Do not commit Hugging Face tokens or API keys.
- Keep model paths in `.env` or server environment variables.
- For CPU-only demos, keep `VIDEO_BACKEND=mock`.
