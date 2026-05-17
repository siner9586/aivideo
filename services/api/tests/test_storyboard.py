from app.skills.prompt_parser import parse_prompt
from app.skills.storyboard_planner import plan_storyboard

def test_storyboard_three_shots():
    sb=plan_storyboard(parse_prompt('生成 8 秒电影级茶楼视频，镜头缓慢推进'), 3)
    assert len(sb.shots)>=3
    assert abs(sb.total_duration-8)<0.2
    assert all(s.visual_prompt for s in sb.shots)
