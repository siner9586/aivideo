"""JSONL-backed task persistence for the lightweight generation queue."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from pydantic import BaseModel, Field
from app.config import settings

TaskStatus = Literal['pending','running','completed','failed','cancelled']

class GenerationTask(BaseModel):
    task_id: str
    project_id: str | None = None
    shot_id: str | None = None
    backend: str = 'mock'
    status: TaskStatus = 'pending'
    progress: float = 0.0
    input_prompt: str = ''
    input_assets: list[str] = Field(default_factory=list)
    output_video_path: str | None = None
    error_message: str | None = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = Field(default_factory=dict)

class TaskStore:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path or settings.task_dir / 'tasks.jsonl')
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)
    def _read_all_versions(self) -> list[GenerationTask]:
        items: list[GenerationTask] = []
        for line in self.path.read_text(encoding='utf-8').splitlines():
            if not line.strip(): continue
            try: items.append(GenerationTask.model_validate(json.loads(line)))
            except Exception: continue
        return items
    def list_tasks(self) -> list[GenerationTask]:
        latest: dict[str, GenerationTask] = {}
        for item in self._read_all_versions(): latest[item.task_id] = item
        return sorted(latest.values(), key=lambda x: x.created_at, reverse=True)
    def get_task(self, task_id: str) -> GenerationTask | None:
        for item in self.list_tasks():
            if item.task_id == task_id: return item
        return None
    def save_task(self, task: GenerationTask) -> GenerationTask:
        task.updated_at = datetime.now(timezone.utc).isoformat()
        with self.path.open('a', encoding='utf-8') as f:
            f.write(task.model_dump_json() + '\n')
        return task
    def update_task(self, task_id: str, **updates: Any) -> GenerationTask:
        task = self.get_task(task_id)
        if not task: raise KeyError(f'task not found: {task_id}')
        for k, v in updates.items():
            if hasattr(task, k): setattr(task, k, v)
        return self.save_task(task)
