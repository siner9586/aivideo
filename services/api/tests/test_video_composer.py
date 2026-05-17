import cv2
import numpy as np
from app.skills.video_composer import concatenate_videos, normalize_shot_video


def _video(path, color):
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*'mp4v'), 8, (160, 90))
    for _ in range(4):
        frame = np.full((90, 160, 3), color, dtype=np.uint8)
        writer.write(frame)
    writer.release()


def test_video_composer_can_merge_two_mock_videos(tmp_path):
    a = tmp_path / 'a.mp4'; b = tmp_path / 'b.mp4'; out = tmp_path / 'out.mp4'
    _video(a, 80); _video(b, 160)
    concatenate_videos([str(a), str(b)], str(out))
    assert out.exists()
    assert out.stat().st_size > 0


def test_normalize_fallback_for_missing_video(tmp_path):
    out = tmp_path / 'fallback.mp4'
    normalize_shot_video(str(tmp_path / 'missing.mp4'), str(out), 160, 90, 8)
    assert out.exists()
