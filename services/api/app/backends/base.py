"""Abstract video backend interfaces."""
from abc import ABC, abstractmethod
from app.models.schemas import TextToVideoRequest, ImageToVideoRequest, VideoGenerationResult

class VideoBackend(ABC):
    name: str = 'base'
    @abstractmethod
    def generate_text(self, request: TextToVideoRequest) -> VideoGenerationResult: ...
    @abstractmethod
    def generate_image(self, request: ImageToVideoRequest) -> VideoGenerationResult: ...
