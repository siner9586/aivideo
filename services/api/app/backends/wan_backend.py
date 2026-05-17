"""Wan backend adapter placeholder with explicit-configuration fallback."""
from __future__ import annotations
import os
from app.backends.mock_backend import MockVideoBackend

class WanBackend(MockVideoBackend):
    name = 'wan'
    def validate(self) -> tuple[bool, str]:
        model_path = os.getenv('WAN_MODEL_PATH') or os.getenv('MODEL_PATH')
        if not model_path: return False, 'wan model path is not configured; mock fallback will be used.'
        return True, 'wan model path configured: ' + model_path
