# ComfyUI Workflow Contract

This document defines the contract between AI Video Studio and ComfyUI workflows.

## 1. Why this contract exists

ComfyUI node ids are fragile. They can change when a workflow is re-saved, copied or rearranged. If backend code hardcodes node ids, parameter injection breaks easily.

AI Video Studio therefore uses:

- node titles
- a companion `profile.json`
- semantic injection fields such as `positive_prompt`, `input_image`, `fps`, `num_frames`

The backend resolves nodes by title and writes values into the configured input names.

## 2. Workflow requirements

### 2.1 API-format JSON

A production workflow must be exported from ComfyUI as **API format** and must be directly submit-able to ComfyUI's `/prompt` endpoint.

Do not use a normal UI-only workflow JSON when the backend expects API format.

### 2.2 Required node titles

For the default I2V short-drama workflow, these titles are expected:

- `INPUT_IMAGE`
- `LAST_FRAME_IMAGE` optional
- `POSITIVE_PROMPT`
- `NEGATIVE_PROMPT`
- `SEED`
- `SIZE`
- `FRAME_COUNT`
- `FPS`
- `GUIDANCE`
- `OUTPUT_VIDEO`

The exact node class is allowed to vary by model wrapper. The stable part is the node title and the input name declared in the profile.

### 2.3 Recommended node meaning

- `INPUT_IMAGE`: first-frame image or source image for I2V.
- `LAST_FRAME_IMAGE`: optional end-frame control.
- `POSITIVE_PROMPT`: main cinematic prompt.
- `NEGATIVE_PROMPT`: quality and safety negative prompt.
- `SEED`: random seed.
- `SIZE`: width and height.
- `FRAME_COUNT`: generated frame count.
- `FPS`: video frame rate.
- `GUIDANCE`: guidance scale / CFG.
- `OUTPUT_VIDEO`: video combine/export node that produces MP4.

## 3. Profile mapping

Each workflow should have a companion profile like:

```text
examples/workflows/comfyui_i2v_short_drama.profile.json
```

The profile tells the backend where to inject values:

- `positive_prompt`
- `negative_prompt`
- `input_image`
- `last_frame_image`
- `seed`
- `width`
- `height`
- `num_frames`
- `fps`
- `guidance_scale`
- `output_prefix`

If a workflow does not support one field, remove that field from `injection_targets` or mark it optional.

## 4. Output contract

The default expected output is MP4.

Recommended output node behavior:

- format: `mp4`
- save output: true
- frame rate: 16 or 24
- filename prefix: `short_drama/<project_id>/<shot_id>/shot` or the backend-provided output prefix

VideoHelperSuite's video combine node is a common option, but the project does not require a specific node class as long as the history output contains a downloadable video file.

## 5. Recommended first stable settings

For short-drama shot production:

- aspect ratio: `9:16`
- initial size: `720x1280`
- fps: `16`
- frames: `65`
- duration: around `4s`

Generate independent short shots first. Then use post-processing for interpolation, upscaling, final subtitles, dubbing, music and platform export.

## 6. Safety and reproducibility

Do not commit:

- model weights
- private images or videos
- API keys
- large generated MP4 files
- unverifiable community workflow bundles with unknown custom node code

A workflow should be considered production-ready only after it runs successfully on the target ComfyUI machine several times with fixed seed, fixed input image and stable MP4 output.
