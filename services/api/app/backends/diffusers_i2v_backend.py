"""Diffusers image-to-video backend placeholder."""
from app.backends.mock_backend import MockVideoBackend
class DiffusersImageToVideoBackend(MockVideoBackend):
    name='diffusers_i2v'
