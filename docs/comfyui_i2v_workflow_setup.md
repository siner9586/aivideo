# ComfyUI I2V Workflow Setup

This guide explains how to connect a stable ComfyUI image-to-video workflow to AI Video Studio.

## 1. Goal

The goal is to support this production path:

```text
GPT short-drama script and shot plan
→ character reference image or first-frame image
→ ComfyUI I2V workflow
→ shot-level MP4 output
→ final editing, subtitles, dubbing, upscaling and platform export
```

The default workflow is designed for short, independent vertical micro-drama shots rather than long single-pass generation.

## 2. Why I2V is the default

For short drama, image-to-video is more reliable than direct text-to-video because it gives better control over:

- protagonist identity
- costume continuity
- scene continuity
- first-frame composition
- key prop placement
- episode-to-episode visual consistency

Use text-to-video only as a secondary creative option. For production, generate or upload a first-frame image and then run I2V.

## 3. Required dependencies

Install and verify:

- ComfyUI
- ffmpeg
- ComfyUI-VideoHelperSuite or an equivalent video export node set
- the selected I2V model wrapper
- the selected I2V model weights

Do not commit model weights to this repository.

## 4. Prepare the workflow in ComfyUI

### Step 1: Build and test locally

Create an I2V workflow that:

- accepts a source / first-frame image
- accepts positive and negative prompts
- supports seed, size, frame count and fps controls
- exports MP4
- runs successfully at least once in ComfyUI

### Step 2: Rename key nodes

Rename key node titles exactly as below:

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

The backend uses these titles through `comfyui_i2v_short_drama.profile.json`.

### Step 3: Export API-format JSON

Use ComfyUI's `Save (API Format)` and overwrite:

```text
examples/workflows/comfyui_i2v_short_drama.workflow.json
```

The repository includes a placeholder at this path to document the contract. It is not a runnable workflow until replaced with your local API-format export.

## 5. Default profile

The profile file is:

```text
examples/workflows/comfyui_i2v_short_drama.profile.json
```

It maps backend semantic fields to workflow node titles and input names. The backend injects:

- `input_image`
- `last_frame_image` optional
- `positive_prompt`
- `negative_prompt`
- `seed`
- `width`
- `height`
- `num_frames`
- `fps`
- `guidance_scale`
- `output_prefix`

If your actual I2V node uses different input names, update the profile instead of changing backend code.

## 6. Recommended first stable settings

Start with:

```text
width = 720
height = 1280
fps = 16
num_frames = 65
guidance_scale = 6.5
shot duration ≈ 4 seconds
```

After the pipeline is stable, use post-processing to upscale to 1080x1920 and interpolate to 24/30fps if needed.

## 7. Environment variables

Recommended local `.env`:

```bash
VIDEO_BACKEND=comfyui
COMFYUI_BASE_URL=http://127.0.0.1:8188
COMFYUI_I2V_WORKFLOW_PATH=examples/workflows/comfyui_i2v_short_drama.workflow.json
COMFYUI_I2V_PROFILE_PATH=examples/workflows/comfyui_i2v_short_drama.profile.json
COMFYUI_TIMEOUT_SECONDS=900
COMFYUI_POLL_INTERVAL_SECONDS=1.5
COMFYUI_OUTPUT_SUBDIR=comfyui_downloads
```

## 8. Smoke test checklist

Before using the workflow for batch short-drama generation, verify:

1. ComfyUI opens and runs the workflow manually.
2. The exported file is API-format JSON.
3. The required node titles exist.
4. A single I2V request returns a ComfyUI `prompt_id`.
5. The backend polls until completion.
6. The backend downloads an MP4 to `data/outputs`.
7. The generated shot can be composed with other shots.

## 9. Production rule

Do not treat a workflow as stable until it can produce 10 consecutive 3-5 second MP4 shots from fixed seed and fixed first-frame inputs without node errors, missing outputs or severe identity drift.
