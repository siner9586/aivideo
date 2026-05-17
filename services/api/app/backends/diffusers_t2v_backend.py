"""Diffusers text-to-video backend placeholder with safe fallback semantics."""
from app.backends.mock_backend import MockVideoBackend
from app.models.schemas import TextToVideoRequest, VideoGenerationResult

class DiffusersTextToVideoBackend(MockVideoBackend):
    name='diffusers'
    def generate_text(self, request: TextToVideoRequest) -> VideoGenerationResult:
        result = super().generate_text(request)
        result.logs.append('Diffusers backend is configured as interface placeholder; set MODEL_PATH to enable real pipeline.')
        result.metadata['requested_backend']='diffusers'
        return result
