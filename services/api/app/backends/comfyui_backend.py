"""ComfyUI backend with profile-driven workflow injection.

This backend is designed for real ComfyUI API-format workflows and a companion
profile.json that maps semantic fields such as prompt, image, seed, fps and
frames to workflow node titles and input names.

It intentionally does not hardcode ComfyUI node ids. A stable production
workflow should be exported from ComfyUI as API-format JSON and paired with a
profile that describes where values should be injected.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from uuid import uuid4

import httpx

from app.backends.base import VideoBackend
from app.config import settings
from app.models.schemas import ImageToVideoRequest, TextToVideoRequest, VideoGenerationResult


class ComfyUIBackend(VideoBackend):
    name = "comfyui"

    def __init__(self) -> None:
        self.base_url = os.getenv("COMFYUI_BASE_URL", os.getenv("COMFYUI_URL", "http://127.0.0.1:8188")).rstrip("/")
        self.timeout_seconds = float(os.getenv("COMFYUI_TIMEOUT_SECONDS", "900"))
        self.poll_interval_seconds = float(os.getenv("COMFYUI_POLL_INTERVAL_SECONDS", "1.5"))
        self.output_subdir = os.getenv("COMFYUI_OUTPUT_SUBDIR", "comfyui_downloads")
        self.local_output_dir = Path(settings.output_dir)
        self.local_output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public backend API
    # ------------------------------------------------------------------

    def validate(self) -> tuple[bool, str]:
        """Check ComfyUI connectivity and validate the configured I2V workflow contract."""
        try:
            with httpx.Client(timeout=20) as client:
                response = client.get(f"{self.base_url}/system_stats")
                response.raise_for_status()

            workflow_path, profile_path = self._resolve_paths(mode="image_to_video")
            prompt_graph = self._load_api_workflow(workflow_path)
            profile = self._load_json(profile_path)
            self._validate_workflow_contract(prompt_graph, profile)
            return True, "ComfyUI backend is available and the I2V workflow contract is valid."
        except Exception as exc:
            return False, f"ComfyUI backend unavailable or workflow invalid: {exc}"

    def generate_text(self, request: TextToVideoRequest) -> VideoGenerationResult:
        """Run a text-to-video ComfyUI workflow when a T2V profile is configured."""
        workflow_path, profile_path = self._resolve_paths(mode="text_to_video")
        profile = self._load_json(profile_path)
        mode = str(profile.get("mode", "text_to_video"))
        if mode != "text_to_video":
            raise ValueError(
                "Configured ComfyUI profile is not text_to_video. "
                "Set COMFYUI_T2V_WORKFLOW_PATH and COMFYUI_T2V_PROFILE_PATH for T2V."
            )
        return self._run_text_to_video(request, workflow_path, profile)

    def generate_image(self, request: ImageToVideoRequest) -> VideoGenerationResult:
        """Run the default image-to-video short-drama workflow."""
        workflow_path, profile_path = self._resolve_paths(mode="image_to_video")
        profile = self._load_json(profile_path)
        mode = str(profile.get("mode", "image_to_video"))
        if mode != "image_to_video":
            raise ValueError(
                "Configured ComfyUI profile is not image_to_video. "
                "Set COMFYUI_I2V_WORKFLOW_PATH and COMFYUI_I2V_PROFILE_PATH for I2V."
            )
        return self._run_image_to_video(request, workflow_path, profile)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def _run_text_to_video(
        self,
        request: TextToVideoRequest,
        workflow_path: str,
        profile: dict[str, Any],
    ) -> VideoGenerationResult:
        prompt_graph = self._load_api_workflow(workflow_path)
        self._validate_workflow_contract(prompt_graph, profile)
        task_id = uuid4().hex
        filename_prefix = f"{self.output_subdir}/{task_id}/shot"
        defaults = profile.get("recommended_defaults", {}) or {}

        self._inject_common_fields(
            prompt_graph=prompt_graph,
            profile=profile,
            positive_prompt=request.prompt,
            negative_prompt=request.negative_prompt or "",
            seed=request.seed if request.seed is not None else defaults.get("seed", 42),
            width=self._resolution_width(request, defaults),
            height=self._resolution_height(request, defaults),
            num_frames=request.num_frames or self._infer_num_frames(request, defaults),
            fps=request.fps or int(defaults.get("fps", 16)),
            guidance_scale=request.guidance_scale,
            output_prefix=filename_prefix,
        )

        prompt_id = self._submit_prompt(prompt_graph)
        history_item = self._poll_history(prompt_id)
        remote_file = self._find_best_video_output(history_item)
        local_path = self._download_output_file(remote_file, task_id)

        return VideoGenerationResult(
            task_id=task_id,
            status="completed",
            output_path=str(local_path),
            preview_url=None,
            metadata={
                "backend": "comfyui",
                "mode": "text_to_video",
                "prompt_id": prompt_id,
                "workflow_path": workflow_path,
                "profile_name": profile.get("name"),
            },
            logs=["comfyui text-to-video completed", f"prompt_id={prompt_id}", f"saved={local_path}"],
        )

    def _run_image_to_video(
        self,
        request: ImageToVideoRequest,
        workflow_path: str,
        profile: dict[str, Any],
    ) -> VideoGenerationResult:
        if not request.image_path:
            raise ValueError("image_path is required for image-to-video generation")

        prompt_graph = self._load_api_workflow(workflow_path)
        self._validate_workflow_contract(prompt_graph, profile)
        task_id = uuid4().hex
        filename_prefix = f"{self.output_subdir}/{task_id}/shot"
        defaults = profile.get("recommended_defaults", {}) or {}

        self._inject_common_fields(
            prompt_graph=prompt_graph,
            profile=profile,
            positive_prompt=request.prompt,
            negative_prompt=request.negative_prompt or "",
            seed=request.seed if request.seed is not None else defaults.get("seed", 42),
            width=self._resolution_width(request, defaults),
            height=self._resolution_height(request, defaults),
            num_frames=request.num_frames or self._infer_num_frames(request, defaults),
            fps=request.fps or int(defaults.get("fps", 16)),
            guidance_scale=request.guidance_scale,
            output_prefix=filename_prefix,
        )
        self._inject_profile_field(prompt_graph, profile, "input_image", request.image_path, required=True)
        if request.last_frame_path:
            self._inject_profile_field(prompt_graph, profile, "last_frame_image", request.last_frame_path, required=False)

        prompt_id = self._submit_prompt(prompt_graph)
        history_item = self._poll_history(prompt_id)
        remote_file = self._find_best_video_output(history_item)
        local_path = self._download_output_file(remote_file, task_id)

        return VideoGenerationResult(
            task_id=task_id,
            status="completed",
            output_path=str(local_path),
            preview_url=None,
            metadata={
                "backend": "comfyui",
                "mode": "image_to_video",
                "prompt_id": prompt_id,
                "workflow_path": workflow_path,
                "profile_name": profile.get("name"),
                "source_image_path": request.image_path,
            },
            logs=["comfyui image-to-video completed", f"prompt_id={prompt_id}", f"saved={local_path}"],
        )

    # ------------------------------------------------------------------
    # Injection helpers
    # ------------------------------------------------------------------

    def _inject_common_fields(
        self,
        *,
        prompt_graph: dict[str, Any],
        profile: dict[str, Any],
        positive_prompt: str,
        negative_prompt: str,
        seed: int | None,
        width: int,
        height: int,
        num_frames: int,
        fps: int,
        guidance_scale: float | None,
        output_prefix: str,
    ) -> None:
        self._inject_profile_field(prompt_graph, profile, "positive_prompt", positive_prompt, required=True)
        self._inject_profile_field(prompt_graph, profile, "negative_prompt", negative_prompt, required=False)
        if seed is not None:
            self._inject_profile_field(prompt_graph, profile, "seed", int(seed), required=False)
        self._inject_profile_field(prompt_graph, profile, "width", int(width), required=False)
        self._inject_profile_field(prompt_graph, profile, "height", int(height), required=False)
        self._inject_profile_field(prompt_graph, profile, "num_frames", int(num_frames), required=False)
        self._inject_profile_field(prompt_graph, profile, "fps", int(fps), required=False)
        if guidance_scale is not None:
            self._inject_profile_field(prompt_graph, profile, "guidance_scale", float(guidance_scale), required=False)
        self._inject_profile_field(prompt_graph, profile, "output_prefix", output_prefix, required=False)

    def _inject_profile_field(
        self,
        prompt_graph: dict[str, Any],
        profile: dict[str, Any],
        field_name: str,
        value: Any,
        *,
        required: bool = False,
    ) -> None:
        targets = profile.get("injection_targets", {}) or {}
        spec = targets.get(field_name)
        if not spec:
            if required:
                raise ValueError(f"Profile missing injection target for required field: {field_name}")
            return

        node_title = spec.get("node_title")
        input_name = spec.get("input_name")
        optional = bool(spec.get("optional", False))
        if not node_title or not input_name:
            if required:
                raise ValueError(f"Invalid injection target for required field: {field_name}")
            return

        try:
            node_id = self._find_node_id_by_title(prompt_graph, str(node_title))
        except KeyError:
            if optional or not required:
                return
            raise

        node = prompt_graph[node_id]
        inputs = node.setdefault("inputs", {})
        inputs[str(input_name)] = value

    # ------------------------------------------------------------------
    # ComfyUI HTTP
    # ------------------------------------------------------------------

    def _submit_prompt(self, prompt_graph: dict[str, Any]) -> str:
        payload = {"prompt": prompt_graph, "client_id": uuid4().hex}
        with httpx.Client(timeout=60) as client:
            response = client.post(f"{self.base_url}/prompt", json=payload)
            response.raise_for_status()
            data = response.json()
        prompt_id = data.get("prompt_id")
        if not prompt_id:
            raise RuntimeError(f"ComfyUI did not return prompt_id: {data}")
        return str(prompt_id)

    def _poll_history(self, prompt_id: str) -> dict[str, Any]:
        deadline = time.time() + self.timeout_seconds
        with httpx.Client(timeout=60) as client:
            while time.time() < deadline:
                response = client.get(f"{self.base_url}/history/{prompt_id}")
                response.raise_for_status()
                data = response.json()
                if prompt_id in data:
                    return data[prompt_id]
                time.sleep(self.poll_interval_seconds)
        raise TimeoutError(f"Timed out waiting for ComfyUI prompt_id={prompt_id}")

    def _download_output_file(self, file_info: dict[str, Any], task_id: str) -> Path:
        filename = str(file_info.get("filename") or "")
        subfolder = str(file_info.get("subfolder") or "")
        file_type = str(file_info.get("type") or "output")
        if not filename:
            raise RuntimeError(f"Invalid ComfyUI output file info: {file_info}")

        query = urlencode({"filename": filename, "subfolder": subfolder, "type": file_type})
        suffix = Path(filename).suffix or ".mp4"
        local_path = self.local_output_dir / f"{task_id}{suffix}"
        with httpx.Client(timeout=None) as client:
            response = client.get(f"{self.base_url}/view?{query}")
            response.raise_for_status()
            local_path.write_bytes(response.content)
        return local_path

    # ------------------------------------------------------------------
    # Output parsing
    # ------------------------------------------------------------------

    def _find_best_video_output(self, history_item: dict[str, Any]) -> dict[str, Any]:
        outputs = history_item.get("outputs", {}) or {}
        candidates: list[dict[str, Any]] = []
        for node_output in outputs.values():
            candidates.extend(self._video_files_from_output(node_output))

        if not candidates:
            raise RuntimeError("No downloadable video output found in ComfyUI history outputs")

        def score(item: dict[str, Any]) -> tuple[int, str]:
            suffix = Path(str(item.get("filename", ""))).suffix.lower()
            if suffix == ".mp4":
                return (0, suffix)
            if suffix == ".webm":
                return (1, suffix)
            if suffix in {".gif", ".mov"}:
                return (2, suffix)
            return (9, suffix)

        candidates.sort(key=score)
        return candidates[0]

    def _video_files_from_output(self, node_output: dict[str, Any]) -> list[dict[str, Any]]:
        files: list[dict[str, Any]] = []
        for key in ["gifs", "videos", "files", "images"]:
            for item in node_output.get(key, []) or []:
                if not isinstance(item, dict) or not item.get("filename"):
                    continue
                suffix = Path(str(item.get("filename"))).suffix.lower()
                if suffix in {".mp4", ".webm", ".mov", ".gif"}:
                    files.append(item)
        return files

    # ------------------------------------------------------------------
    # Workflow/profile loading and validation
    # ------------------------------------------------------------------

    def _resolve_paths(self, mode: str) -> tuple[str, str]:
        if mode == "image_to_video":
            workflow_path = (
                os.getenv("COMFYUI_I2V_WORKFLOW_PATH")
                or os.getenv("COMFYUI_WORKFLOW_PATH")
                or "examples/workflows/comfyui_i2v_short_drama.workflow.json"
            )
            profile_path = (
                os.getenv("COMFYUI_I2V_PROFILE_PATH")
                or os.getenv("COMFYUI_WORKFLOW_PROFILE_PATH")
                or "examples/workflows/comfyui_i2v_short_drama.profile.json"
            )
            return workflow_path, profile_path

        workflow_path = (
            os.getenv("COMFYUI_T2V_WORKFLOW_PATH")
            or os.getenv("COMFYUI_WORKFLOW_PATH")
            or "examples/workflows/comfyui_t2v_short_drama.workflow.json"
        )
        profile_path = (
            os.getenv("COMFYUI_T2V_PROFILE_PATH")
            or os.getenv("COMFYUI_WORKFLOW_PROFILE_PATH")
            or "examples/workflows/comfyui_t2v_short_drama.profile.json"
        )
        return workflow_path, profile_path

    def _load_api_workflow(self, path_str: str) -> dict[str, Any]:
        path = Path(path_str)
        if not path.exists():
            raise FileNotFoundError(f"ComfyUI workflow file not found: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))

        if isinstance(data, dict) and data.get("_placeholder"):
            raise ValueError(
                f"{path} is a placeholder, not a runnable ComfyUI workflow. "
                "Replace it with a real ComfyUI Save (API Format) export."
            )
        if isinstance(data, dict) and "prompt" in data and isinstance(data["prompt"], dict):
            return data["prompt"]
        if self._looks_like_api_prompt_graph(data):
            return data
        raise ValueError("Workflow file is not ComfyUI API-format JSON. Export with Save (API Format).")

    def _load_json(self, path_str: str) -> dict[str, Any]:
        path = Path(path_str)
        if not path.exists():
            raise FileNotFoundError(f"JSON file not found: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"JSON file must contain an object: {path}")
        return data

    def _looks_like_api_prompt_graph(self, data: Any) -> bool:
        if not isinstance(data, dict) or not data:
            return False
        for node_id, node in data.items():
            if not isinstance(node_id, str) or not isinstance(node, dict):
                return False
            if "class_type" not in node:
                return False
        return True

    def _validate_workflow_contract(self, prompt_graph: dict[str, Any], profile: dict[str, Any]) -> None:
        required_titles = profile.get("validation", {}).get("must_have_titles", []) or []
        found_titles = self._collect_titles(prompt_graph)
        missing = [title for title in required_titles if title not in found_titles]
        if missing:
            raise ValueError(f"Workflow missing required node titles: {missing}")

    def _collect_titles(self, prompt_graph: dict[str, Any]) -> set[str]:
        titles: set[str] = set()
        for node in prompt_graph.values():
            if not isinstance(node, dict):
                continue
            meta = node.get("_meta", {}) or {}
            title = meta.get("title") or node.get("title")
            if isinstance(title, str) and title.strip():
                titles.add(title.strip())
        return titles

    def _find_node_id_by_title(self, prompt_graph: dict[str, Any], title: str) -> str:
        for node_id, node in prompt_graph.items():
            meta = node.get("_meta", {}) or {}
            current_title = meta.get("title") or node.get("title")
            if current_title == title:
                return node_id
        raise KeyError(f"Node title not found in workflow: {title}")

    # ------------------------------------------------------------------
    # Resolution helpers
    # ------------------------------------------------------------------

    def _resolution_width(self, request: TextToVideoRequest | ImageToVideoRequest, defaults: dict[str, Any]) -> int:
        if request.resolution == "1080p" and request.aspect_ratio == "9:16":
            return 1080
        if request.resolution == "720p" and request.aspect_ratio == "9:16":
            return 720
        return int(defaults.get("width", 720))

    def _resolution_height(self, request: TextToVideoRequest | ImageToVideoRequest, defaults: dict[str, Any]) -> int:
        if request.resolution == "1080p" and request.aspect_ratio == "9:16":
            return 1920
        if request.resolution == "720p" and request.aspect_ratio == "9:16":
            return 1280
        return int(defaults.get("height", 1280))

    def _infer_num_frames(self, request: TextToVideoRequest | ImageToVideoRequest, defaults: dict[str, Any]) -> int:
        if request.num_frames is not None:
            return int(request.num_frames)
        fps = request.fps or int(defaults.get("fps", 16))
        duration = request.duration or float(defaults.get("duration_seconds", 4))
        return max(1, int(round(fps * duration)))
