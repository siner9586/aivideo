# Deployment: Netlify Frontend + FastAPI Backend

This document describes five deployment modes for AI Video Studio Beta.

## 1. Local development

```bash
make setup
make api
# new terminal
make web
```

Or run manually:

```bash
PYTHONPATH=services/api uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
cd apps/web
npm install
npm run dev
```

Use `VIDEO_BACKEND=mock` for the lowest-cost demo path.

## 2. Netlify frontend

Deploy `apps/web` to Netlify.

Recommended build settings:

- Base directory: `apps/web`
- Build command: `npm run build`
- Publish directory: `dist`

Set environment variable:

```bash
VITE_API_BASE_URL=https://your-backend.example.com
```

If you also keep the old variable name, this frontend supports:

```bash
VITE_API_BASE=http://localhost:8000
```

Backend CORS is open in development. For production, restrict CORS origins to your Netlify domain.

## 3. Cloud backend

Run FastAPI on a server with persistent storage:

```bash
PYTHONPATH=services/api uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Mount these folders persistently:

- `data/projects`
- `data/tasks`
- `data/assets`
- `data/outputs`

Use a reverse proxy such as Nginx or Caddy, then enable HTTPS.

## 4. GPU server

Install CUDA, PyTorch, Diffusers or ComfyUI separately. Keep model weights outside the repository.

```bash
VIDEO_BACKEND=comfyui
COMFYUI_BASE_URL=http://127.0.0.1:8188
COMFYUI_WORKFLOW_PATH=/srv/aivideo/workflows/t2v.json
```

For Diffusers:

```bash
VIDEO_BACKEND=diffusers_t2v
DIFFUSERS_MODEL_PATH=/models/your-video-model
DIFFUSERS_DEVICE=auto
ENABLE_CPU_OFFLOAD=true
```

Keep queue concurrency low until VRAM usage is stable.

## 5. Pure demo mode

Use only mock backend:

```bash
VIDEO_BACKEND=mock
```

This mode is suitable for product demonstrations, frontend testing, classroom explanation and low-cost deployment. It does not require GPU or model weights.
