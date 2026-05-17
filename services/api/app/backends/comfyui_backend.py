"""ComfyUI workflow backend skeleton."""
from app.backends.mock_backend import MockVideoBackend
class ComfyUIBackend(MockVideoBackend):
    name='comfyui'
