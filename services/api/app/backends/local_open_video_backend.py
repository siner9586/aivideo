"""Local open-source video model backend.

This adapter solves the real-video-quality path without paid external APIs. It
runs local/open-weight Diffusers-compatible video models such as LTX-Video,
CogVideoX, HunyuanVideo and Wan when the required packages and weights are
installed.

It intentionally does not bundle model weights. Configure a local model path or
Hugging Face model id through environment variables, then run on a machine with
sufficient GPU/VRAM.
"""
from __future__ import annotations

import os
from functools import lru_cache
from uuid import uuid4
from typing import Any

from app.backends.mock_backend import MockVideoBackend
from app.models.schemas import ImageToVideoRequest, TextToVideoRequest, VideoGenerationResult
from app.config import settings
from app.utils.video_utils import ratio_to_size

MODEL_DEFAULTS = {
    "ltx": {
        "env": "LTX_MODEL_ID",
        "path_env": "LTX_MODEL_PATH",
        "default_id": "Lightricks/LTX-Video",
        "pipeline_classes": ["LTXPipeline", "LTXVideoPipeline", "DiffusionPipeline"],
    },
    "cogvideox": {
        "env": "COGVIDEOX_MODEL_ID",
        "path_env": "COGVIDEOX_MODEL_PATH",
        "default_id": "THUDM/CogVideoX-5b",
        "pipeline_classes": ["CogVideoXPipeline", "DiffusionPipeline"],
    },
    "hunyuan": {
        "env": "HUNYUAN_MODEL_ID",
        "path_env": "HUNYUAN_MODEL_PATH",
        "default_id": "tencent/HunyuanVideo",
        "pipeline_classes": ["HunyuanVideoPipeline", "DiffusionPipeline"],
    },
    "wan": {
        "env": "WAN_MODEL_ID",
        "path_env": "WAN_MODEL_PATH",
        "default_id": "Wan-AI/Wan2.1-T2V-1.3B-Diffusers",
        "pipeline_classes": ["WanPipeline", "WanT2VPipeline", "DiffusionPipeline"],
    },
    "local_open_video": {
        "env": "LOCAL_VIDEO_MODEL_ID",
        "path_env": "LOCAL_VIDEO_MODEL_PATH",
        "default_id": "Lightricks/LTX-Video",
        "pipeline_classes": ["LTXPipeline", "CogVideoXPipeline", "HunyuanVideoPipeline", "WanPipeline", "DiffusionPipeline"],
    },
}

QUALITY_PRESETS = {
    "draft": {"steps": 16, "guidance": 4.5, "fps": 8, "num_frames": 49, "max_resolution": "480p"},
    "balanced": {"steps": 28, "guidance": 6.0, "fps": 12, "num_frames": 65, "max_resolution": "720p"},
    "quality": {"steps": 40, "guidance": 7.0, "fps": 16, "num_frames": 81, "max_resolution": "720p"},
    "short_drama": {"steps": 32, "guidance": 6.5, "fps": 16, "num_frames": 81, "max_resolution": "720p"},
}


def _truthy(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def _safe_torch_dtype(torch: Any) -> Any:
    dtype = os.getenv("LOCAL_VIDEO_DTYPE", "auto").lower()
    if dtype == "fp32":
        return torch.float32
    if dtype == "fp16":
        return torch.float16
    if dtype == "bf16":
        return torch.bfloat16
    if torch.cuda.is_available():
        major, _minor = torch.cuda.get_device_capability(0)
        return torch.bfloat16 if major >= 8 else torch.float16
    return torch.float32


def _device(torch: Any) -> str:
    configured = os.getenv("LOCAL_VIDEO_DEVICE", os.getenv("DIFFUSERS_DEVICE", "auto")).lower()
    if configured != "auto":
        return configured
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def _resolution_for_request(aspect_ratio: str, resolution: str, preset: dict[str, Any]) -> tuple[int, int]:
    requested = resolution
    allowed = str(preset.get("max_resolution") or resolution)
    order = {"360p": 360, "480p": 480, "720p": 720, "1080p": 1080}
    if order.get(requested, 720) > order.get(allowed, 720):
        requested = allowed
    return ratio_to_size(aspect_ratio, requested)


class LocalOpenVideoBackend(MockVideoBackend):
    """Run local/open-weight Diffusers video models with mock fallback control."""

    name = "local_open_video"
    family = "local_open_video"

    def __init__(self, family: str | None = None) -> None:
        self.family = family or self.family

    def _model_id(self) -> str:
        cfg = MODEL_DEFAULTS.get(self.family, MODEL_DEFAULTS["local_open_video"])
        return (
            os.getenv(str(cfg["path_env"]))
            or os.getenv(str(cfg["env"]))
            or os.getenv("LOCAL_VIDEO_MODEL_PATH")
            or os.getenv("LOCAL_VIDEO_MODEL_ID")
            or os.getenv("MODEL_PATH")
            or os.getenv("MODEL_ID")
            or (str(cfg["default_id"]) if _truthy(os.getenv("LOCAL_VIDEO_ALLOW_DEFAULT_DOWNLOAD"), False) else "")
        )

    def validate(self) -> tuple[bool, str]:
        model = self._model_id()
        if not model:
            return False, (
                f"{self.family} local model is not configured. Set LOCAL_VIDEO_MODEL_PATH/ID "
                f"or {MODEL_DEFAULTS.get(self.family, {}).get('path_env')} / {MODEL_DEFAULTS.get(self.family, {}).get('env')}."
            )
        try:
            import torch  # type: ignore
            import diffusers  # type: ignore
        except Exception as exc:
            return False, f"Install optional local video dependencies first: {exc}"
        device = _device(torch)
        return True, f"{self.family} local video backend configured: model={model}, device={device}, diffusers={getattr(diffusers, '__version__', 'unknown')}"

    def generate_text(self, request: TextToVideoRequest) -> VideoGenerationResult:
        model = self._model_id()
        if not model:
            return self._fallback(request, "local open video model is not configured")
        try:
            pipe = _load_pipeline(self.family, model)
            preset = self._preset(request)
            frames = self._run_text_pipeline(pipe, request, preset)
            out = settings.output_dir / f"{uuid4().hex}.mp4"
            _export_video(frames, str(out), preset.get("fps", request.fps))
            return VideoGenerationResult(
                task_id=out.stem,
                output_path=str(out),
                preview_url=f"/api/assets/{out.stem}/video",
                metadata={"backend": self.family, "model": model, "real_video": True, "quality_preset": request.quality_preset},
                logs=["local open-source text-to-video completed"],
            )
        except Exception as exc:
            return self._fallback(request, f"local open video generation failed: {exc}")

    def generate_image(self, request: ImageToVideoRequest) -> VideoGenerationResult:
        model = self._model_id()
        if not model:
            return self._fallback(request, "local open video model is not configured", image=True)
        try:
            pipe = _load_pipeline(self.family, model, image=True)
            preset = self._preset(request)
            frames = self._run_image_pipeline(pipe, request, preset)
            out = settings.output_dir / f"{uuid4().hex}.mp4"
            _export_video(frames, str(out), preset.get("fps", request.fps))
            return VideoGenerationResult(
                task_id=out.stem,
                output_path=str(out),
                preview_url=f"/api/assets/{out.stem}/video",
                metadata={"backend": self.family, "model": model, "real_video": True, "mode": "image-to-video", "quality_preset": request.quality_preset},
                logs=["local open-source image-to-video completed"],
            )
        except Exception as exc:
            return self._fallback(request, f"local open image-to-video generation failed: {exc}", image=True)

    def _preset(self, request: TextToVideoRequest | ImageToVideoRequest) -> dict[str, Any]:
        name = os.getenv("LOCAL_VIDEO_QUALITY_PRESET") or getattr(request, "quality_preset", "short_drama") or "short_drama"
        return QUALITY_PRESETS.get(str(name), QUALITY_PRESETS["short_drama"])

    def _run_text_pipeline(self, pipe: Any, request: TextToVideoRequest, preset: dict[str, Any]) -> list[Any]:
        width, height = _resolution_for_request(request.aspect_ratio, request.resolution, preset)
        num_frames = int(os.getenv("LOCAL_VIDEO_NUM_FRAMES", request.num_frames or preset["num_frames"]))
        steps = int(os.getenv("LOCAL_VIDEO_STEPS", preset["steps"]))
        guidance = float(os.getenv("LOCAL_VIDEO_GUIDANCE", request.guidance_scale or preset["guidance"]))
        seed = int(request.seed if request.seed is not None else int(os.getenv("LOCAL_VIDEO_SEED", "42")))

        import torch  # type: ignore

        generator = torch.Generator(device=_device(torch)).manual_seed(seed) if _device(torch) != "mps" else torch.Generator().manual_seed(seed)
        kwargs = {
            "prompt": request.prompt,
            "negative_prompt": request.negative_prompt or _default_negative_prompt(),
            "num_inference_steps": steps,
            "guidance_scale": guidance,
            "num_frames": num_frames,
            "height": height,
            "width": width,
            "generator": generator,
        }
        result = _call_pipeline(pipe, kwargs)
        return _frames_from_result(result)

    def _run_image_pipeline(self, pipe: Any, request: ImageToVideoRequest, preset: dict[str, Any]) -> list[Any]:
        width, height = _resolution_for_request(request.aspect_ratio, request.resolution, preset)
        num_frames = int(os.getenv("LOCAL_VIDEO_NUM_FRAMES", request.num_frames or preset["num_frames"]))
        steps = int(os.getenv("LOCAL_VIDEO_STEPS", preset["steps"]))
        guidance = float(os.getenv("LOCAL_VIDEO_GUIDANCE", request.guidance_scale or preset["guidance"]))
        seed = int(request.seed if request.seed is not None else int(os.getenv("LOCAL_VIDEO_SEED", "42")))

        import torch  # type: ignore
        from PIL import Image  # type: ignore

        image = Image.open(request.image_path).convert("RGB").resize((width, height))
        generator = torch.Generator(device=_device(torch)).manual_seed(seed) if _device(torch) != "mps" else torch.Generator().manual_seed(seed)
        kwargs = {
            "prompt": request.prompt,
            "image": image,
            "negative_prompt": request.negative_prompt or _default_negative_prompt(),
            "num_inference_steps": steps,
            "guidance_scale": guidance,
            "num_frames": num_frames,
            "height": height,
            "width": width,
            "generator": generator,
        }
        result = _call_pipeline(pipe, kwargs)
        return _frames_from_result(result)

    def _fallback(self, request: TextToVideoRequest | ImageToVideoRequest, reason: str, image: bool = False) -> VideoGenerationResult:
        if not _truthy(os.getenv("LOCAL_VIDEO_ALLOW_MOCK_FALLBACK"), True):
            raise RuntimeError(reason)
        if image and isinstance(request, ImageToVideoRequest):
            result = super().generate_image(request.model_copy(update={"backend": "mock"}))
        else:
            result = super().generate_text(request.model_copy(update={"backend": "mock"}))
        result.metadata["requested_backend"] = self.family
        result.metadata["real_video"] = False
        result.logs.append(f"local open video fallback to mock: {reason}")
        return result


@lru_cache(maxsize=4)
def _load_pipeline(family: str, model: str, image: bool = False) -> Any:
    import torch  # type: ignore
    import diffusers  # type: ignore

    cfg = MODEL_DEFAULTS.get(family, MODEL_DEFAULTS["local_open_video"])
    classes = list(cfg["pipeline_classes"])
    if image:
        classes = [c.replace("Pipeline", "ImageToVideoPipeline") for c in classes if c != "DiffusionPipeline"] + classes
    pipeline_cls = None
    for class_name in classes:
        pipeline_cls = getattr(diffusers, class_name, None)
        if pipeline_cls is not None:
            break
    if pipeline_cls is None:
        pipeline_cls = getattr(diffusers, "DiffusionPipeline")

    kwargs: dict[str, Any] = {}
    torch_dtype = _safe_torch_dtype(torch)
    if torch_dtype is not None:
        kwargs["torch_dtype"] = torch_dtype
    if _truthy(os.getenv("LOCAL_VIDEO_LOCAL_FILES_ONLY"), False):
        kwargs["local_files_only"] = True

    pipe = pipeline_cls.from_pretrained(model, **kwargs)
    if _truthy(os.getenv("ENABLE_MODEL_CPU_OFFLOAD"), True) and hasattr(pipe, "enable_model_cpu_offload") and _device(torch) == "cuda":
        pipe.enable_model_cpu_offload()
    else:
        pipe = pipe.to(_device(torch))
    if _truthy(os.getenv("ENABLE_ATTENTION_SLICING"), True) and hasattr(pipe, "enable_attention_slicing"):
        pipe.enable_attention_slicing()
    if _truthy(os.getenv("ENABLE_VAE_TILING"), True) and hasattr(pipe, "enable_vae_tiling"):
        pipe.enable_vae_tiling()
    if _truthy(os.getenv("ENABLE_VAE_SLICING"), True) and hasattr(pipe, "enable_vae_slicing"):
        pipe.enable_vae_slicing()
    return pipe


def _call_pipeline(pipe: Any, kwargs: dict[str, Any]) -> Any:
    """Call a pipeline while dropping unsupported kwargs for model-specific APIs."""
    try:
        return pipe(**kwargs)
    except TypeError as exc:
        message = str(exc)
        trimmed = dict(kwargs)
        for key in ["negative_prompt", "height", "width", "num_frames", "guidance_scale", "generator"]:
            if key in trimmed and key in message:
                trimmed.pop(key, None)
        if trimmed == kwargs:
            for key in ["negative_prompt", "height", "width"]:
                trimmed.pop(key, None)
        return pipe(**trimmed)


def _frames_from_result(result: Any) -> list[Any]:
    frames = getattr(result, "frames", None)
    if frames is None and isinstance(result, dict):
        frames = result.get("frames") or result.get("videos")
    if frames is None:
        videos = getattr(result, "videos", None)
        frames = videos
    if isinstance(frames, list) and frames and isinstance(frames[0], list):
        return frames[0]
    if isinstance(frames, tuple) and frames and isinstance(frames[0], list):
        return frames[0]
    if frames is None:
        raise RuntimeError("pipeline result did not include frames/videos")
    return list(frames)


def _export_video(frames: list[Any], path: str, fps: int | float) -> None:
    try:
        from diffusers.utils import export_to_video  # type: ignore
        export_to_video(frames, path, fps=int(fps))
    except Exception:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
        from PIL import Image  # type: ignore
        converted = []
        for frame in frames:
            if isinstance(frame, Image.Image):
                arr = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
            else:
                arr = np.asarray(frame)
                if arr.ndim == 3 and arr.shape[-1] == 3:
                    arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            converted.append(arr)
        h, w = converted[0].shape[:2]
        writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), int(fps), (w, h))
        for frame in converted:
            writer.write(frame)
        writer.release()


def _default_negative_prompt() -> str:
    return (
        "low quality, blurry, watermark, logo, flicker, jitter, deformed hands, "
        "extra fingers, face drift, identity drift, random costume change, bad anatomy"
    )
