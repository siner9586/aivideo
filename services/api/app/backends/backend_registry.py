"""Backend registry for mock, ComfyUI, Diffusers and local open video adapters."""
from __future__ import annotations
import os
from typing import Dict
from app.backends.base import VideoBackend
from app.backends.mock_backend import MockVideoBackend

class BackendRegistry:
    def __init__(self) -> None:
        self._backends: Dict[str, VideoBackend] = {}
    def register_backend(self, name: str, backend: VideoBackend) -> None:
        if not name: raise ValueError('backend name is required')
        self._backends[name] = backend
    def get_backend(self, name: str | None = None) -> VideoBackend:
        key = name or self.get_default_backend()
        if key == 'diffusers': key = 'diffusers_t2v'
        if key not in self._backends:
            raise KeyError(f'Unknown backend: {key}. Available: {", ".join(self.list_backends())}')
        return self._backends[key]
    def list_backends(self) -> list[str]: return sorted(self._backends.keys())
    def get_default_backend(self) -> str: return os.getenv('VIDEO_BACKEND') or os.getenv('MODEL_BACKEND') or 'mock'
    def validate_backend(self, name: str) -> dict:
        try:
            backend = self.get_backend(name); ok, message = backend.validate()
            return {'name': name, 'available': ok, 'message': message}
        except Exception as exc: return {'name': name, 'available': False, 'message': str(exc)}

registry = BackendRegistry()

def build_default_registry() -> BackendRegistry:
    from app.backends.diffusers_t2v_backend import DiffusersTextToVideoBackend
    from app.backends.diffusers_i2v_backend import DiffusersImageToVideoBackend
    from app.backends.comfyui_backend import ComfyUIBackend
    from app.backends.external_api_backend import ExternalApiBackend
    from app.backends.local_open_video_backend import LocalOpenVideoBackend
    from app.backends.wan_backend import WanBackend
    from app.backends.cogvideox_backend import CogVideoXBackend
    from app.backends.hunyuan_backend import HunyuanBackend
    from app.backends.ltx_backend import LTXBackend
    registry.register_backend('mock', MockVideoBackend())
    registry.register_backend('diffusers', DiffusersTextToVideoBackend())
    registry.register_backend('diffusers_t2v', DiffusersTextToVideoBackend())
    registry.register_backend('diffusers_i2v', DiffusersImageToVideoBackend())
    registry.register_backend('local_open_video', LocalOpenVideoBackend())
    registry.register_backend('comfyui', ComfyUIBackend())
    registry.register_backend('external', ExternalApiBackend())
    registry.register_backend('wan', WanBackend())
    registry.register_backend('cogvideox', CogVideoXBackend())
    registry.register_backend('hunyuan', HunyuanBackend())
    registry.register_backend('ltx', LTXBackend())
    return registry

def get_registry() -> BackendRegistry:
    if not registry.list_backends(): build_default_registry()
    return registry