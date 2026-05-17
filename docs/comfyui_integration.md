# ComfyUI Integration

AI Video Studio Beta can call a running ComfyUI server through a workflow JSON template. The default system still uses `mock`; ComfyUI is opt-in.

## Environment variables

```bash
VIDEO_BACKEND=comfyui
COMFYUI_BASE_URL=http://127.0.0.1:8188
COMFYUI_WORKFLOW_PATH=examples/workflows/comfyui_text_to_video_example.json
```

## How it works

`services/api/app/backends/comfyui_backend.py` provides:

- `validate_comfyui_connection()`
- `load_workflow_template(path)`
- `inject_prompt_into_workflow(workflow, prompt)`
- `inject_image_into_workflow(workflow, image_path)`
- `submit_workflow(workflow)`
- `poll_comfyui_job(prompt_id)`
- `fetch_comfyui_outputs(prompt_id)`
- `generate_with_comfyui(request)`

The backend attempts to submit the configured workflow to ComfyUI. If ComfyUI is unavailable or no workflow is configured, it falls back to the mock backend and adds a clear log message.

## Workflow template rule

Export a workflow from ComfyUI, then keep text fields such as `text`, `prompt`, `positive` or `caption` easy to replace. For image-to-video workflows, keep image fields such as `image`, `image_path`, `init_image` or `reference_image` easy to replace.

See:

- `examples/workflows/comfyui_text_to_video_example.json`
- `examples/workflows/comfyui_image_to_video_example.json`

## Safety notes

Do not commit model weights, API keys, private media or ComfyUI cache files. Keep workflows as lightweight JSON templates only.
