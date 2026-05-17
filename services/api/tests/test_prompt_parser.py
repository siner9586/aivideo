import pytest
from app.skills.prompt_parser import parse_prompt

def test_chinese_prompt_parse():
    s=parse_prompt('生成一段 8 秒电影级写实风格视频：夜晚的中国传统茶楼，暖金色光线，镜头缓慢推进，16:9，720p')
    assert '茶楼' in s.scene and '电影级' in s.style and s.camera=='slow_push_in' and s.duration==8

def test_english_prompt_parse():
    s=parse_prompt('Create a 6 seconds cinematic realistic video in a night teahouse, warm light, slow push in, 5:2')
    assert s.duration==6 and s.aspect_ratio=='5:2' and s.language=='en'

def test_empty_prompt():
    with pytest.raises(ValueError): parse_prompt('')
