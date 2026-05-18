"""Diffusers local/open-source text-to-video backend.

This backend no longer stops at a placeholder. It delegates to the shared
LocalOpenVideoBackend, which can run local/open-weight Diffusers-compatible
video pipelines such as LTX-Video, CogVideoX, HunyuanVideo or Wan when the
model and optional dependencies are installed.
"""
from __future__ import annotations

from app.backends.local_open_video_backend import LocalOpenVideoBackend


class DiffusersTextToVideoBackend(LocalOpenVideoBackend):
    name = 'diffusers_t2v'
    family = 'local_open_video'

    def __init__(self) -> None:
        super().__init__(family='local_open_video')
