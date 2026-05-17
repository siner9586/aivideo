"""LTX backend adapter placeholder with explicit-configuration fallback."""
from __future__ import annotations
import os
from app.backends.mock_backend import MockVideoBackend

class LTXBackend(MockVideoBackend):
    name = 'ltx'
    def validate(self) -> tuple[bool, str]:
        model_path = os.getenv('LTX_MODEL_PATH') or os.getenv('MODEL_PATH')
        if not model_path: return False, 'ltx model path is not configured; mock fallback will be used.'
        return True, 'ltx model path configured: ' + model_path
