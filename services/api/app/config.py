"""Central configuration."""
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = 'AI Video Studio'
    model_backend: str = 'mock'
    model_path: str = ''
    output_dir: Path = Path('data/outputs')
    upload_dir: Path = Path('data/uploads')
    task_dir: Path = Path('data/tasks')
    feedback_dir: Path = Path('data/feedback')
    max_upload_mb: int = 20
    comfyui_url: str = 'http://127.0.0.1:8188'
    external_api_url: str = ''
    external_api_key: str = ''
    class Config:
        env_file = '.env'

settings = Settings()
for p in [settings.output_dir, settings.upload_dir, settings.task_dir, settings.feedback_dir, Path('data/logs')]:
    p.mkdir(parents=True, exist_ok=True)
