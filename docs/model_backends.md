# Model Backends

## MockVideoBackend

Best for local testing, demos, CI and CPU-only environments. It creates MP4 files with OpenCV gradients, subtitles and simple camera transforms.

## Hugging Face Diffusers Text-to-Video

Suitable for research models exposed through Diffusers. Set `MODEL_BACKEND=diffusers` and `MODEL_PATH=/path/to/model`. Recommended VRAM depends on model size; use fp16, attention slicing, VAE tiling and CPU offload for limited memory.

## AnimateDiff

Good for short stylized motion clips and controllable workflows. Often used through Diffusers or ComfyUI.

## CogVideoX

Good for higher-quality prompt-following video if adequate GPU memory is available. Configure through model path; do not auto-download in production.

## HunyuanVideo

Good for high-quality text-to-video generation. Requires substantial GPU memory; prefer server-side deployment.

## Wan2.1 / Wan2.2

Good for modern open video generation and image-to-video workflows. Use a dedicated backend class or ComfyUI workflow.

## LTX-Video / LTX-2

Good for faster generation and lightweight experimentation where supported.

## ComfyUI workflow

Set `MODEL_BACKEND=comfyui` and `COMFYUI_URL=http://127.0.0.1:8188`. Submit workflow JSON to the local ComfyUI server; keep workflow files under docs or examples.

## CPU offload

Use `recommend_inference_config()` to select fp16/bf16/offload/attention slicing/VAE tiling. Always test with mock first.
