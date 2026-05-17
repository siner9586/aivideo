"""Abstract video backend interfaces."""
from abc import ABC, abstractmethod
from app.models.schemas import TextToVideoRequest, ImageToVideoRequest, VideoGenerationResult

class VideoBackend(ABC):
    name: str = 'base'
    def validate(self) -> tuple[bool, str]:
        return True, f'{self.name} backend is available.'
    @abstractmethod
    def generate_text(self, request: TextToVideoRequest) -> VideoGenerationResult: ...
    @abstractmethod
    def generate_image(self, request: ImageToVideoRequest) -> VideoGenerationResult: ...
