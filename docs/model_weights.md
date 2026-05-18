# Local video model weights

Real video model weights are not committed to this repository. The repository stores only:

- a model manifest: `config/model_weights.example.json`
- a downloader: `scripts/download_model_weights.py`
- ignored local folders: `models/`, `weights/`, `checkpoints/`
- environment-variable templates in `.env.example`

This is intentional. Many video model checkpoints are multiple GB or tens of GB, and their licenses may require users to accept terms upstream before download or commercial use.

## Quick start

List configured models:

```bash
make models-list
```

Download Wan text-to-video weights locally:

```bash
make models-wan
```

For gated Hugging Face models, provide a token after accepting the model license upstream:

```bash
HF_TOKEN=hf_xxx make models-cogvideox
```

The script writes a local `.env.models.local` fragment such as:

```bash
WAN_MODEL_PATH=/absolute/path/to/aivideo/models/wan/Wan2.1-T2V-1.3B-Diffusers
# VIDEO_BACKEND=wan
```

Copy those lines into `.env`, then run:

```bash
VIDEO_BACKEND=wan PYTHONPATH=services/api uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Supported manifest entries

The example manifest currently contains:

- `wan_t2v_1_3b` -> `Wan-AI/Wan2.1-T2V-1.3B-Diffusers`
- `ltx_video` -> `Lightricks/LTX-Video`
- `cogvideox_5b` -> `THUDM/CogVideoX-5b`
- `hunyuan_video` -> `tencent/HunyuanVideo`

You can add more entries to your own private manifest, for example `config/model_weights.local.json`, then run:

```bash
python scripts/download_model_weights.py --manifest config/model_weights.local.json --model your_model_key
```

## Why not commit weights?

Do not put checkpoint files into git history:

```text
*.safetensors
*.bin
*.ckpt
*.pt
*.pth
*.onnx
*.gguf
```

They are ignored by `.gitignore`. If a weight file is accidentally committed, remove it from history before pushing.

## Optional Git LFS

Git LFS can track large files as pointer files, but it still has storage, bandwidth and per-file limits, and it does not solve upstream model-license redistribution. For this project, prefer local download from the upstream model host instead of storing weights in this repo.

## Recommended production pattern

1. Keep `aivideo` code in GitHub.
2. Store model weights under local `models/` or a mounted volume such as `/models/aivideo`.
3. Set `WAN_MODEL_PATH`, `LTX_MODEL_PATH`, `COGVIDEOX_MODEL_PATH`, `HUNYUAN_MODEL_PATH`, or `LOCAL_VIDEO_MODEL_PATH`.
4. Keep `.env` private.
5. Use `POST /api/short-drama/cinematic-package` to create shot prompts.
6. Use `VIDEO_BACKEND=wan` or another real backend for generation.
7. Use `POST /api/composer/export-upload-ready` for vertical MP4 export.

## Safety and license boundary

Check every upstream model license before commercial use. Do not redistribute gated or license-restricted weights through this repository. Do not use downloaded models for non-consensual deepfakes, public-figure impersonation, explicit sexual deepfakes, fraud ads, political deception, medical/financial false claims or platform-rule evasion.
