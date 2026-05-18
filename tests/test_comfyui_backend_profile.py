import json

import pytest

from app.backends.comfyui_backend import ComfyUIBackend


def _workflow_graph():
    return {
        "1": {"class_type": "LoadImage", "inputs": {}, "_meta": {"title": "INPUT_IMAGE"}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {}, "_meta": {"title": "POSITIVE_PROMPT"}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {}, "_meta": {"title": "NEGATIVE_PROMPT"}},
        "4": {"class_type": "Seed", "inputs": {}, "_meta": {"title": "SEED"}},
        "5": {"class_type": "Size", "inputs": {}, "_meta": {"title": "SIZE"}},
        "6": {"class_type": "FrameCount", "inputs": {}, "_meta": {"title": "FRAME_COUNT"}},
        "7": {"class_type": "FPS", "inputs": {}, "_meta": {"title": "FPS"}},
        "8": {"class_type": "Guidance", "inputs": {}, "_meta": {"title": "GUIDANCE"}},
        "9": {"class_type": "VideoCombine", "inputs": {}, "_meta": {"title": "OUTPUT_VIDEO"}},
    }


def _profile():
    return {
        "name": "unit_test_i2v",
        "mode": "image_to_video",
        "injection_targets": {
            "input_image": {"node_title": "INPUT_IMAGE", "input_name": "image"},
            "positive_prompt": {"node_title": "POSITIVE_PROMPT", "input_name": "text"},
            "negative_prompt": {"node_title": "NEGATIVE_PROMPT", "input_name": "text"},
            "seed": {"node_title": "SEED", "input_name": "seed"},
            "width": {"node_title": "SIZE", "input_name": "width"},
            "height": {"node_title": "SIZE", "input_name": "height"},
            "num_frames": {"node_title": "FRAME_COUNT", "input_name": "frames"},
            "fps": {"node_title": "FPS", "input_name": "fps"},
            "guidance_scale": {"node_title": "GUIDANCE", "input_name": "cfg"},
            "output_prefix": {"node_title": "OUTPUT_VIDEO", "input_name": "filename_prefix"},
        },
        "validation": {
            "must_have_titles": [
                "INPUT_IMAGE",
                "POSITIVE_PROMPT",
                "NEGATIVE_PROMPT",
                "SEED",
                "SIZE",
                "FRAME_COUNT",
                "FPS",
                "OUTPUT_VIDEO",
            ]
        },
    }


def test_profile_driven_injection_sets_expected_workflow_inputs():
    backend = ComfyUIBackend()
    graph = _workflow_graph()
    profile = _profile()

    backend._validate_workflow_contract(graph, profile)
    backend._inject_common_fields(
        prompt_graph=graph,
        profile=profile,
        positive_prompt="cinematic short drama close-up",
        negative_prompt="low quality, blurry, watermark",
        seed=123,
        width=720,
        height=1280,
        num_frames=65,
        fps=16,
        guidance_scale=6.5,
        output_prefix="comfyui_downloads/test/shot",
    )
    backend._inject_profile_field(graph, profile, "input_image", "data/uploads/first_frame.png", required=True)

    assert graph["1"]["inputs"]["image"] == "data/uploads/first_frame.png"
    assert graph["2"]["inputs"]["text"] == "cinematic short drama close-up"
    assert graph["3"]["inputs"]["text"] == "low quality, blurry, watermark"
    assert graph["4"]["inputs"]["seed"] == 123
    assert graph["5"]["inputs"]["width"] == 720
    assert graph["5"]["inputs"]["height"] == 1280
    assert graph["6"]["inputs"]["frames"] == 65
    assert graph["7"]["inputs"]["fps"] == 16
    assert graph["8"]["inputs"]["cfg"] == 6.5
    assert graph["9"]["inputs"]["filename_prefix"] == "comfyui_downloads/test/shot"


def test_validate_workflow_contract_reports_missing_titles():
    backend = ComfyUIBackend()
    graph = _workflow_graph()
    graph.pop("9")

    with pytest.raises(ValueError, match="OUTPUT_VIDEO"):
        backend._validate_workflow_contract(graph, _profile())


def test_load_api_workflow_rejects_placeholder(tmp_path):
    backend = ComfyUIBackend()
    placeholder = tmp_path / "placeholder.workflow.json"
    placeholder.write_text(json.dumps({"_placeholder": True}), encoding="utf-8")

    with pytest.raises(ValueError, match="placeholder"):
        backend._load_api_workflow(str(placeholder))


def test_find_best_video_output_prefers_mp4():
    backend = ComfyUIBackend()
    history = {
        "outputs": {
            "9": {
                "gifs": [{"filename": "preview.gif", "subfolder": "", "type": "output"}],
                "videos": [
                    {"filename": "shot.webm", "subfolder": "", "type": "output"},
                    {"filename": "shot.mp4", "subfolder": "", "type": "output"},
                ],
            }
        }
    }

    assert backend._find_best_video_output(history)["filename"] == "shot.mp4"
