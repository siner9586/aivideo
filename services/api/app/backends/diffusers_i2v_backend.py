"""Diffusers image-to-video backend adapter with safe mock fallback."""
from __future__ import annotations
import os
from app.backends.mock_backend import MockVideoBackend
from app.models.schemas import ImageToVideoRequest, VideoGenerationResult

class DiffusersImageToVideoBackend(MockVideoBackend):
    name = 'diffusers_i2v'
    def _configured_model(self) -> str:
        return os.getenv('DIFFUSERS_MODEL_PATH') or os.getenv('DIFFUSERS_MODEL_ID') or os.getenv('MODEL_PATH') or ''
    def validate(self) -> tuple[bool, str]:
        model = self._configured_model()
        if not model: return False, 'No DIFFUSERS_MODEL_ID / DIFFUSERS_MODEL_PATH configured; using mock fallback.'
        return True, f'Diffusers I2V model configured: {model}'
    def generate_image(self, request: ImageToVideoRequest) -> VideoGenerationResult:
        if not self._configured_model():
            result = super().generate_image(request.model_copy(update={'backend':'mock'}))
            result.metadata['requested_backend'] = self.name
            result.logs.append('Diffusers I2V not configured; generated via mock fallback.')
            return result
        result = super().generate_image(request.model_copy(update={'backend':'mock'}))
        result.metadata['requested_backend'] = self.name
        result.logs.append('Concrete Diffusers I2V adapter pending for selected model; mock fallback used safely.')
        return result
