"""Wan local open-source video backend."""
from __future__ import annotations
from app.backends.local_open_video_backend import LocalOpenVideoBackend

class WanBackend(LocalOpenVideoBackend):
    name = 'wan'
    family = 'wan'
    def __init__(self) -> None:
        super().__init__(family='wan')
