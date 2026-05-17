# Frontend Timeline Editor

The Beta workspace uses a three-column layout.

## Left column

- `ProjectSidebar`: create and select projects.
- `PromptTemplateLibrary`: apply safe prompt templates.
- `AssetLibrary`: upload images, audio and videos.

## Center column

- `PromptEditor`: write the main creative prompt.
- `GenerationSettings`: set duration, fps, aspect ratio, resolution and backend.
- `StoryboardPanel`: inspect parsed prompt and storyboard output.
- `TimelineEditor`: edit project shots.
- `ShotCard`: edit per-shot title, duration, visual prompt, action prompt, camera motion and backend.

## Right column

- `QueuePanel`: show task progress, status, errors, cancel and retry.
- `VideoPreview`: preview a quick generated clip.
- `ComposerPanel`: compose shots into a final mp4 and export project zip.
- `QualityPanel`: evaluate video or project quality.

## API clients

All new Beta API calls are placed under `apps/web/src/lib/`:

- `projectApi.ts`
- `queueApi.ts`
- `templateApi.ts`
- `composerApi.ts`

## Environment variables

The frontend reads either:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

or the older:

```bash
VITE_API_BASE=http://localhost:8000
```

## Design style

The UI keeps a white, card-based, professional tool style. It is intentionally not a heavy visual poster page. The goal is a stable beta workbench that can support real model backends later.
