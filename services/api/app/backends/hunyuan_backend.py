"""Hunyuan backend adapter placeholder with explicit-configuration fallback."""
from __future__ import annotations
import os
from app.backends.mock_backend import MockVideoBackend

class HunyuanBackend(MockVideoBackend):
    name = 'hunyuan'
    def validate(self) -> tuple[bool, str]:
        model_path = os.getenv('HUNYUAN_MODEL_PATH') or os.getenv('MODEL_PATH')
        if not model_path: return False, 'hunyuan model path is not configured; mock fallback will be used.'
        return True, 'hunyuan model path configured: ' + model_path
