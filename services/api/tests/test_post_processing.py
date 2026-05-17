from pathlib import Path
from app.models.schemas import TextToVideoRequest
from app.skills.text_to_video import generate_text_to_video
from app.skills.post_processing import resize_video, change_fps, compose_multi_shot_video

def test_post_processing(tmp_path):
    r=generate_text_to_video(TextToVideoRequest(prompt='测试视频', duration=1, fps=5, resolution='480p'))
    resized=tmp_path/'resized.mp4'; fpsed=tmp_path/'fps.mp4'; composed=tmp_path/'composed.mp4'
    resize_video(r.output_path, str(resized), 320, 180); assert resized.exists()
    change_fps(r.output_path, str(fpsed), 8); assert fpsed.exists()
    compose_multi_shot_video([r.output_path, r.output_path], str(composed), []); assert composed.exists()
