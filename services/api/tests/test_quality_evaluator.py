import cv2
import numpy as np
from app.skills.quality_evaluator import evaluate_video, quality_report_to_markdown


def test_quality_evaluator_scores_mock_video(tmp_path):
    path = tmp_path / 'q.mp4'
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*'mp4v'), 8, (160, 90))
    for i in range(8):
        frame = np.full((90, 160, 3), 80 + i * 5, dtype=np.uint8)
        writer.write(frame)
    writer.release()
    report = evaluate_video(str(path), {'prompt': 'safe demo', 'duration': 1})
    assert 0 <= report['overall_score'] <= 1
    md = quality_report_to_markdown(report)
    assert 'Video Quality Report' in md
