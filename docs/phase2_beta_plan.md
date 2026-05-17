# Phase 2 Beta Plan

Phase 2 upgrades AI Video Studio from a runnable MVP into a beta workspace while preserving the Phase 1 mock generation loop.

## Goals

- Keep mock backend as the default CPU-only path.
- Add queue-based asynchronous shot generation.
- Add persistent project management under `data/projects`.
- Add backend registry for mock, ComfyUI, Diffusers, external, Wan, CogVideoX, Hunyuan and LTX.
- Add prompt templates, asset library, timeline editor, video composer and quality panel.
- Add deployment documentation for local, Netlify frontend, cloud backend and GPU server.

## Non-goals

- No model training.
- No automatic download of large model weights.
- No API keys or private assets in the repository.
- No removal of Phase 1 APIs.

## Beta workflow

1. Create a project.
2. Enter a prompt and parse it.
3. Generate storyboard shots.
4. Edit each shot in the timeline.
5. Select backend per shot.
6. Submit shot generation to queue.
7. Preview generated clips.
8. Compose the final mp4.
9. Evaluate quality.
10. Export project zip.
