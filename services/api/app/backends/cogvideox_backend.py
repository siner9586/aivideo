"""CogVideoX backend adapter placeholder with explicit-configuration fallback."""
from __future__ import annotations
import os
from app.backends.mock_backend import MockVideoBackend

class CogVideoXBackend(MockVideoBackend):
    name = 'cogvideox'
    def validate(self) -> tuple[bool, str]:
        model_path = os.getenv('COGVIDEOX_MODEL_PATH') or os.getenv('MODEL_PATH')
        if not model_path: return False, 'cogvideox model path is not configured; mock fallback will be used.'
        return True, 'cogvideox model path configured: ' + model_path
