"""Diffusers local/open-source image-to-video backend.

Delegates to LocalOpenVideoBackend so image-to-video can use local/open-weight
Diffusers-compatible video pipelines where supported by the selected model.
"""
from __future__ import annotations

from app.backends.local_open_video_backend import LocalOpenVideoBackend


class DiffusersImageToVideoBackend(LocalOpenVideoBackend):
    name = 'diffusers_i2v'
    family = 'local_open_video'

    def __init__(self) -> None:
        super().__init__(family='local_open_video')
