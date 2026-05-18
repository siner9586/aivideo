from fastapi.testclient import TestClient

from app.main import app
from app.skills.cinematic_prompt_compiler import enrich_short_drama_plan_for_cinema, get_delivery_profile
from app.skills.short_drama_planner import plan_short_drama

client = TestClient(app)


def test_plan_short_drama_skill_generates_episode_and_jobs():
    result = plan_short_drama(
        premise="被背叛的女主重回宴会现场，当众夺回公司控制权",
        genre="revenge",
        episodes=2,
        shots_per_episode=4,
        seconds_per_episode=40,
    )
    assert result["genre"] == "revenge"
    assert result["platform_profile"]["aspect_ratio"] == "9:16"
    assert len(result["episodes"]) == 2
    assert len(result["characters"]) >= 2
    assert len(result["generation_jobs"]) == 8
    assert "cliffhanger_cut" in result["markdown"]


def test_short_drama_plan_api():
    response = client.post(
        "/api/short-drama/plan",
        json={
            "premise": "失业研究员意外发现公司算法黑幕，决定用证据反击",
            "genre": "business",
            "visual_mode": "cinematic_realistic",
            "episodes": 1,
            "shots_per_episode": 4,
            "seconds_per_episode": 32,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["genre"] == "business"
    assert data["provider"] == "local"
    assert data["platform_profile"]["aspect_ratio"] == "9:16"
    assert len(data["episodes"]) == 1
    assert len(data["generation_jobs"]) == 4


def test_short_drama_gpt_fallback_api_without_key():
    response = client.post(
        "/api/short-drama/plan",
        json={
            "premise": "女主发现婚礼现场所有人都在骗她",
            "genre": "rebirth",
            "use_gpt": True,
            "fallback_to_local": True,
            "episodes": 1,
            "shots_per_episode": 4,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] in {"local_fallback", "openai"}
    assert len(data["generation_jobs"]) >= 4 or len(data.get("episodes", [])) >= 1


def test_short_drama_asset_subtitle_and_dubbing_endpoints():
    plan = plan_short_drama(
        premise="被背叛的女主重回宴会现场，当众夺回公司控制权",
        genre="revenge",
        episodes=1,
        shots_per_episode=4,
        seconds_per_episode=32,
    )
    asset_response = client.post("/api/short-drama/character-assets", json={"plan": plan, "project_id": "demo"})
    assert asset_response.status_code == 200
    assert len(asset_response.json()["characters"]) >= 2

    subtitle_response = client.post("/api/short-drama/subtitles/srt", json={"plan": plan})
    assert subtitle_response.status_code == 200
    assert "-->" in subtitle_response.json()["content"]

    dubbing_response = client.post("/api/short-drama/dubbing-script", json={"plan": plan})
    assert dubbing_response.status_code == 200
    assert len(dubbing_response.json()["episodes"]) == 1


def test_short_drama_viral_score_api():
    response = client.post(
        "/api/short-drama/viral-score",
        json={
            "hook_text": "你被开除了。下一秒，董事长却向她鞠躬。",
            "cliffhanger_text": "她刚要说出真相，门被推开。",
            "conflict_level": 5,
            "reversal_count": 2,
            "closeup_ratio": 0.45,
            "subtitle_density": 0.65,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["viral_score"] > 50
    assert "dimensions" in data


def test_cinematic_compiler_generates_upload_ready_jobs():
    plan = plan_short_drama(
        premise="被背叛的女主重回宴会现场，当众夺回公司控制权",
        genre="revenge",
        episodes=1,
        shots_per_episode=4,
        seconds_per_episode=32,
    )
    package = enrich_short_drama_plan_for_cinema(plan, target_platform="douyin", backend="mock")
    assert package["delivery_profile"]["width"] == 1080
    assert package["delivery_profile"]["height"] == 1920
    assert package["delivery_profile"]["fps"] == 24
    assert len(package["compiled_cinematic_shots"]) == 4
    assert len(package["cinematic_queue_jobs"]) == 4
    first_job = package["cinematic_queue_jobs"][0]
    assert first_job["metadata"]["aspect_ratio"] == "9:16"
    assert first_job["metadata"]["resolution"] == "1080p"
    assert first_job["metadata"]["quality_preset"] == "short_drama"
    assert "Character continuity lock" in first_job["input_prompt"]
    assert "low quality" in first_job["metadata"]["negative_prompt"]


def test_cinematic_package_api_without_queue_submission():
    response = client.post(
        "/api/short-drama/cinematic-package",
        json={
            "premise": "女主在家族会议上被逐出公司，三秒后拿出董事长亲签文件",
            "genre": "revenge",
            "visual_mode": "cinematic_realistic",
            "target_platform": "hongguo",
            "episodes": 1,
            "shots_per_episode": 4,
            "seconds_per_episode": 32,
            "backend": "mock",
            "submit_to_queue": False,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["delivery_profile"]["aspect_ratio"] == "9:16"
    assert data["delivery_profile"]["resolution"] == "1080p"
    assert len(data["compiled_cinematic_shots"]) == 4
    assert len(data["cinematic_queue_jobs"]) == 4
    assert "quality_gates" in data


def test_delivery_profile_aliases():
    assert get_delivery_profile("抖音")["display_name"].startswith("Douyin")
    assert get_delivery_profile("红果")["display_name"].startswith("Hongguo")
