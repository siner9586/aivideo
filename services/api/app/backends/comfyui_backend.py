"""ComfyUI workflow backend adapter."""
from __future__ import annotations
import copy, json, os, time, urllib.parse, urllib.request
from pathlib import Path
from typing import Any
from app.backends.mock_backend import MockVideoBackend
from app.config import settings
from app.models.schemas import TextToVideoRequest, ImageToVideoRequest, VideoGenerationResult

class ComfyUIBackend(MockVideoBackend):
    name = 'comfyui'
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or os.getenv('COMFYUI_BASE_URL') or getattr(settings,'comfyui_base_url',None) or settings.comfyui_url).rstrip('/')
    def validate(self) -> tuple[bool, str]: return self.validate_comfyui_connection()
    def validate_comfyui_connection(self) -> tuple[bool, str]:
        try:
            with urllib.request.urlopen(f'{self.base_url}/system_stats', timeout=2) as resp:
                return resp.status < 500, f'ComfyUI reachable at {self.base_url}'
        except Exception as exc: return False, f'ComfyUI unavailable at {self.base_url}: {exc}'
    def load_workflow_template(self, path: str | Path) -> dict[str, Any]:
        with open(path, 'r', encoding='utf-8') as f: return json.load(f)
    def inject_prompt_into_workflow(self, workflow: dict[str, Any], prompt: str) -> dict[str, Any]:
        wf = copy.deepcopy(workflow)
        def walk(node: Any) -> None:
            if isinstance(node, dict):
                if 'text' in node and isinstance(node['text'], str): node['text'] = prompt
                if 'prompt' in node and isinstance(node['prompt'], str): node['prompt'] = prompt
                inputs = node.get('inputs')
                if isinstance(inputs, dict):
                    for key in ('text','prompt','positive','caption'):
                        if key in inputs and isinstance(inputs[key], str): inputs[key] = prompt
                for v in node.values(): walk(v)
            elif isinstance(node, list):
                for v in node: walk(v)
        walk(wf); return wf
    def inject_image_into_workflow(self, workflow: dict[str, Any], image_path: str) -> dict[str, Any]:
        wf = copy.deepcopy(workflow)
        def walk(node: Any) -> None:
            if isinstance(node, dict):
                if 'image' in node and isinstance(node['image'], str): node['image'] = image_path
                inputs = node.get('inputs')
                if isinstance(inputs, dict):
                    for key in ('image','image_path','init_image','reference_image'):
                        if key in inputs and isinstance(inputs[key], str): inputs[key] = image_path
                for v in node.values(): walk(v)
            elif isinstance(node, list):
                for v in node: walk(v)
        walk(wf); return wf
    def submit_workflow(self, workflow: dict[str, Any]) -> str:
        data = json.dumps({'prompt': workflow}).encode('utf-8')
        req = urllib.request.Request(f'{self.base_url}/prompt', data=data, headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req, timeout=10) as resp: payload = json.loads(resp.read().decode('utf-8'))
        return payload.get('prompt_id') or payload.get('id') or ''
    def poll_comfyui_job(self, prompt_id: str, timeout_s: int = 300) -> dict[str, Any]:
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            with urllib.request.urlopen(f'{self.base_url}/history/{urllib.parse.quote(prompt_id)}', timeout=10) as resp:
                payload = json.loads(resp.read().decode('utf-8'))
            if payload.get(prompt_id): return payload[prompt_id]
            time.sleep(2)
        raise TimeoutError(f'ComfyUI job timeout: {prompt_id}')
    def fetch_comfyui_outputs(self, prompt_id: str, output_dir: str | Path | None = None) -> list[str]:
        history = self.poll_comfyui_job(prompt_id); out_dir = Path(output_dir or settings.output_dir); out_dir.mkdir(parents=True, exist_ok=True); outputs=[]
        for node in history.get('outputs', {}).values():
            for item in node.get('videos', []) + node.get('gifs', []) + node.get('images', []):
                filename=item.get('filename'); subfolder=item.get('subfolder',''); ftype=item.get('type','output')
                if not filename: continue
                query=urllib.parse.urlencode({'filename':filename,'subfolder':subfolder,'type':ftype}); target=out_dir/filename
                try: urllib.request.urlretrieve(f'{self.base_url}/view?{query}', target); outputs.append(str(target))
                except Exception: continue
        return outputs
    def generate_with_comfyui(self, request: TextToVideoRequest | ImageToVideoRequest) -> VideoGenerationResult:
        ok, message = self.validate_comfyui_connection()
        if not ok: raise RuntimeError(message)
        workflow_path = os.getenv('COMFYUI_WORKFLOW_PATH')
        if not workflow_path: raise RuntimeError('COMFYUI_WORKFLOW_PATH is not configured')
        workflow = self.inject_prompt_into_workflow(self.load_workflow_template(workflow_path), request.prompt)
        if hasattr(request, 'image_path'): workflow = self.inject_image_into_workflow(workflow, getattr(request, 'image_path'))
        prompt_id = self.submit_workflow(workflow); outputs = self.fetch_comfyui_outputs(prompt_id)
        mp4 = next((p for p in outputs if p.lower().endswith('.mp4')), outputs[0] if outputs else '')
        if not mp4: raise RuntimeError('ComfyUI completed but no output file was found')
        return VideoGenerationResult(task_id=Path(mp4).stem, output_path=mp4, preview_url=f'/api/assets/{Path(mp4).stem}/video', metadata={'backend':'comfyui','prompt_id':prompt_id}, logs=['comfyui workflow completed'])
    def generate_text(self, request: TextToVideoRequest) -> VideoGenerationResult:
        try: return self.generate_with_comfyui(request)
        except Exception as exc:
            result = super().generate_text(request.model_copy(update={'backend':'mock'})); result.metadata['requested_backend']='comfyui'; result.logs.append(f'ComfyUI fallback to mock: {exc}'); return result
    def generate_image(self, request: ImageToVideoRequest) -> VideoGenerationResult:
        try: return self.generate_with_comfyui(request)
        except Exception as exc:
            result = super().generate_image(request.model_copy(update={'backend':'mock'})); result.metadata['requested_backend']='comfyui'; result.logs.append(f'ComfyUI fallback to mock: {exc}'); return result
