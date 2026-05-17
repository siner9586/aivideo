"""Diffusers text-to-video backend adapter with safe mock fallback."""
from __future__ import annotations
import os
from app.backends.mock_backend import MockVideoBackend
from app.models.schemas import TextToVideoRequest, VideoGenerationResult

class DiffusersTextToVideoBackend(MockVideoBackend):
    name = 'diffusers_t2v'
    def _configured_model(self) -> str:
        return os.getenv('DIFFUSERS_MODEL_PATH') or os.getenv('DIFFUSERS_MODEL_ID') or os.getenv('MODEL_PATH') or ''
    def validate(self) -> tuple[bool, str]:
        model = self._configured_model()
        if not model: return False, 'No DIFFUSERS_MODEL_ID / DIFFUSERS_MODEL_PATH configured; using mock fallback.'
        return True, f'Diffusers model configured: {model}'
    def generate_text(self, request: TextToVideoRequest) -> VideoGenerationResult:
        model = self._configured_model()
        if not model:
            result = super().generate_text(request.model_copy(update={'backend':'mock'}))
            result.metadata['requested_backend'] = self.name
            result.logs.append('Diffusers T2V not configured; generated via mock fallback.')
            return result
        try:
            import torch  # type: ignore
            from diffusers import DiffusionPipeline  # type: ignore
            device = os.getenv('DIFFUSERS_DEVICE', 'auto')
            if device == 'auto': device = 'cuda' if torch.cuda.is_available() else 'cpu'
            pipe = DiffusionPipeline.from_pretrained(model).to(device)
            if os.getenv('ENABLE_ATTENTION_SLICING', 'true').lower() == 'true' and hasattr(pipe, 'enable_attention_slicing'):
                pipe.enable_attention_slicing()
            raise RuntimeError('Diffusers pipeline loaded, but generic video export is model-specific. Add a concrete adapter for your selected pipeline.')
        except Exception as exc:
            result = super().generate_text(request.model_copy(update={'backend':'mock'}))
            result.metadata['requested_backend'] = self.name
            result.logs.append(f'Diffusers T2V fallback to mock: {exc}')
            return result
