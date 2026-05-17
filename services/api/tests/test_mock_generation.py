from pathlib import Path
from PIL import Image
from app.models.schemas import TextToVideoRequest, ImageToVideoRequest
from app.skills.text_to_video import generate_text_to_video
from app.skills.image_to_video import generate_image_to_video

def test_mock_t2v():
    r=generate_text_to_video(TextToVideoRequest(prompt='生成 2 秒风景视频', duration=2, fps=6, resolution='480p'))
    assert Path(r.output_path).exists() and Path(r.output_path).stat().st_size>0

def test_mock_i2v(tmp_path):
    img=tmp_path/'in.png'; Image.new('RGB',(320,180),(80,120,160)).save(img)
    r=generate_image_to_video(ImageToVideoRequest(prompt='图片动画', image_path=str(img), duration=2, fps=6, resolution='480p'))
    assert Path(r.output_path).exists() and Path(r.output_path).stat().st_size>0
