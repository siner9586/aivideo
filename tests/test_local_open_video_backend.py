from app.backends.backend_registry import get_registry
from app.models.schemas import TextToVideoRequest


def test_local_open_video_backend_is_registered():
    registry = get_registry()
    names = registry.list_backends()
    assert 'local_open_video' in names
    assert 'ltx' in names
    assert 'wan' in names
    assert 'cogvideox' in names
    assert 'hunyuan' in names


def test_local_open_video_request_schema_accepts_quality_preset():
    req = TextToVideoRequest(
        prompt='vertical short drama shot, stable character, cinematic lighting',
        backend='local_open_video',
        aspect_ratio='9:16',
        resolution='720p',
        quality_preset='short_drama',
    )
    assert req.backend == 'local_open_video'
    assert req.quality_preset == 'short_drama'


def test_backend_validation_reports_missing_local_model_without_crashing(monkeypatch):
    monkeypatch.delenv('LOCAL_VIDEO_MODEL_PATH', raising=False)
    monkeypatch.delenv('LOCAL_VIDEO_MODEL_ID', raising=False)
    monkeypatch.delenv('MODEL_PATH', raising=False)
    monkeypatch.delenv('MODEL_ID', raising=False)
    monkeypatch.delenv('LOCAL_VIDEO_ALLOW_DEFAULT_DOWNLOAD', raising=False)
    status = get_registry().validate_backend('local_open_video')
    assert status['name'] == 'local_open_video'
    assert status['available'] is False
    assert 'not configured' in status['message']
