from app.backends.mock_backend import MockVideoBackend
from app.backends.diffusers_t2v_backend import DiffusersTextToVideoBackend
from app.backends.diffusers_i2v_backend import DiffusersImageToVideoBackend
from app.backends.comfyui_backend import ComfyUIBackend
from app.backends.external_api_backend import ExternalApiBackend

def get_backend(name: str):
    return {'mock':MockVideoBackend(),'diffusers':DiffusersTextToVideoBackend(),'comfyui':ComfyUIBackend(),'external':ExternalApiBackend()}.get(name, MockVideoBackend())
