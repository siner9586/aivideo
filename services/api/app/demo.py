from app.models.schemas import TextToVideoRequest
from app.skills.text_to_video import generate_text_to_video
if __name__ == '__main__':
    r=generate_text_to_video(TextToVideoRequest(prompt='生成一段 8 秒电影级写实风格视频：夜晚的中国传统茶楼，暖金色光线，镜头缓慢推进。', duration=5, resolution='480p', camera_motion='slow_push_in'))
    print(r.output_path)
