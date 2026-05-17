"""Text-to-video orchestration skill."""
from app.backends import get_backend
from app.backends.mock_backend import MockVideoBackend
from app.models.schemas import TextToVideoRequest, VideoGenerationResult
from app.skills.safety_guard import check_generation_request

def generate_text_to_video(request: TextToVideoRequest) -> VideoGenerationResult:
    """Generate video from text using selected backend with mock fallback."""
    safety=check_generation_request(request)
    if not safety.allowed: raise ValueError('; '.join(safety.reasons))
    try:
        return get_backend(request.backend).generate_text(request)
    except Exception as exc:
        fallback=MockVideoBackend().generate_text(request.model_copy(update={'backend':'mock'}))
        fallback.logs.append(f'fallback to mock after error: {exc}')
        return fallback
