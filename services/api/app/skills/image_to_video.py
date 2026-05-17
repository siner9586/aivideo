"""Image-to-video orchestration and mock animation skill."""
from app.backends import get_backend
from app.backends.mock_backend import MockVideoBackend
from app.models.schemas import ImageToVideoRequest, VideoGenerationResult
from app.skills.safety_guard import check_generation_request

def generate_image_to_video(request: ImageToVideoRequest) -> VideoGenerationResult:
    """Generate video from image using selected backend with OpenCV mock fallback."""
    safety=check_generation_request(request)
    if not safety.allowed: raise ValueError('; '.join(safety.reasons))
    try:
        return get_backend(request.backend).generate_image(request)
    except Exception as exc:
        fallback=MockVideoBackend().generate_image(request.model_copy(update={'backend':'mock'}))
        fallback.logs.append(f'fallback to mock image animation after error: {exc}')
        return fallback

def animate_image_mock(image_path: str, output_path: str, duration: float, fps: int, motion_type: str) -> str:
    """Animate a still image with mock backend and return mp4 path."""
    req=ImageToVideoRequest(prompt='mock image animation', image_path=image_path, duration=duration, fps=fps, motion_type=motion_type, aspect_ratio='16:9', resolution='480p')
    result=MockVideoBackend().generate_image(req)
    import shutil; shutil.copyfile(result.output_path, output_path)
    return output_path
