# ComfyUI Workflows for AI Video Studio

This directory stores verified ComfyUI workflows and their companion profiles.

## Files

- `comfyui_i2v_short_drama.workflow.json`
  - Must be a real ComfyUI **API-format** workflow exported from a local, tested ComfyUI setup.
  - Intended for short-drama image-to-video generation.
  - Must accept a first-frame image and export an MP4.

- `comfyui_i2v_short_drama.profile.json`
  - Not a ComfyUI workflow itself.
  - Describes how the FastAPI backend injects prompt, negative prompt, input image, seed, width, height, frames, fps and output prefix into the workflow.

## Required node titles

To keep backend injection stable, key ComfyUI nodes should use these exact titles:

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

The backend resolves nodes by title through the profile, not by fragile node ids.

## Export rule

In ComfyUI:

1. Build and test an I2V workflow locally.
2. Rename the key nodes to the titles above.
3. Use `Save (API Format)`.
4. Save or replace the file at:

```text
examples/workflows/comfyui_i2v_short_drama.workflow.json
```

## Recommended first stable target

- Mode: image-to-video
- Aspect ratio: 9:16
- Initial generation size: 720x1280
- Frames: 65
- FPS: 16
- Shot duration: about 4 seconds
- Output: MP4

Start with short, independent shots. After the shot-level workflow is reliable, use post-processing for interpolation, upscaling, subtitles, audio and final platform export.

## What not to do

- Do not commit random unverified community workflows as production defaults.
- Do not use ordinary UI workflow JSON when the backend expects API-format JSON.
- Do not hardcode ComfyUI node ids in backend code.
- Do not commit model weights, private media, API keys or generated large videos.
