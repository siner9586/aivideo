"""Tiny JSON task store."""
import json
from pathlib import Path
from app.config import settings

def save_task(task_id: str, payload: dict) -> None:
    settings.task_dir.mkdir(parents=True, exist_ok=True)
    (settings.task_dir / f'{task_id}.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

def load_task(task_id: str) -> dict | None:
    p=Path(settings.task_dir)/f'{task_id}.json'
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else None
