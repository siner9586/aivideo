"""Central configuration."""
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = 'AI Video Studio'
    video_backend: str = 'mock'
    model_backend: str = 'mock'
    model_path: str = ''
    diffusers_model_id: str = ''
    diffusers_model_path: str = ''
    diffusers_device: str = 'auto'
    diffusers_dtype: str = 'auto'
    enable_cpu_offload: bool = True
    enable_attention_slicing: bool = True
    enable_vae_tiling: bool = True
    output_dir: Path = Path('data/outputs')
    upload_dir: Path = Path('data/uploads')
    task_dir: Path = Path('data/tasks')
    project_dir: Path = Path('data/projects')
    asset_dir: Path = Path('data/assets')
    feedback_dir: Path = Path('data/feedback')
    max_upload_mb: int = 50
    comfyui_base_url: str = 'http://127.0.0.1:8188'
    comfyui_url: str = 'http://127.0.0.1:8188'
    external_api_url: str = ''
    external_api_key: str = ''
    class Config:
        env_file = '.env'
        extra = 'ignore'

settings = Settings()
for p in [settings.output_dir, settings.upload_dir, settings.task_dir, settings.project_dir, settings.asset_dir, settings.feedback_dir, Path('data/logs')]:
    p.mkdir(parents=True, exist_ok=True)
