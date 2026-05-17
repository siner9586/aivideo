from app.skills.safety_guard import check_prompt_safety

def test_blocked():
    r=check_prompt_safety('制作色情深伪 未授权换脸')
    assert r.risk_level=='blocked' and not r.allowed

def test_low():
    assert check_prompt_safety('生成正常风景、产品展示、教育科普视频').risk_level=='low'
