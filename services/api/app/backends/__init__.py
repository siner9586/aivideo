"""Backend lookup helpers.

Do not silently fall back to ``mock`` when a real backend is requested. Silent
fallback is exactly what makes a misconfigured ComfyUI/Diffusers setup produce
flat demo videos while users believe they are running a real generation model.
Set AIVIDEO_ALLOW_BACKEND_FALLBACK=1 only for local demos.
"""
from __future__ import annotations

import os

from app.backends.backend_registry import get_registry


def _allow_fallback() -> bool:
    return os.getenv("AIVIDEO_ALLOW_BACKEND_FALLBACK", "0").lower() in {"1", "true", "yes", "on"}


def get_backend(name: str):
    try:
        return get_registry().get_backend(name)
    except Exception as exc:
        if _allow_fallback():
            return get_registry().get_backend("mock")
        raise RuntimeError(
            f"Video backend '{name}' is not available. Fix the backend configuration instead of falling back to mock. "
            "For CPU-only preview, explicitly set backend='mock' or VIDEO_BACKEND=mock. "
            "For temporary demo fallback, set AIVIDEO_ALLOW_BACKEND_FALLBACK=1."
        ) from exc
