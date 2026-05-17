"""Asset library for uploaded images, audio and videos."""
from __future__ import annotations
import json
from pathlib import Path
from uuid import uuid4
from pydantic import BaseModel, Field
from PIL import Image
from app.config import settings
from app.projects.project_manager import get_project_manager

IMAGE_EXT = {'.jpg','.jpeg','.png','.webp'}
VIDEO_EXT = {'.mp4','.mov','.webm'}
AUDIO_EXT = {'.mp3','.wav','.m4a'}
ALL_EXT = IMAGE_EXT | VIDEO_EXT | AUDIO_EXT

class AssetRecord(BaseModel):
    asset_id: str
    filename: str
    path: str
    asset_type: str
    size_bytes: int
    thumbnail_path: str | None = None
    project_id: str | None = None
    shot_id: str | None = None
    metadata: dict = Field(default_factory=dict)

class AssetManager:
    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root or settings.asset_dir); self.root.mkdir(parents=True, exist_ok=True)
        self.index = self.root / 'assets.jsonl'; self.index.touch(exist_ok=True)
    def asset_type_for(self, ext: str) -> str:
        ext = ext.lower()
        if ext in IMAGE_EXT: return 'image'
        if ext in VIDEO_EXT: return 'video'
        if ext in AUDIO_EXT: return 'audio'
        raise ValueError(f'unsupported format: {ext}')
    def _save_record(self, rec: AssetRecord) -> AssetRecord:
        with self.index.open('a', encoding='utf-8') as f: f.write(rec.model_dump_json()+'\n')
        return rec
    def _latest(self) -> dict[str, AssetRecord]:
        latest={}
        for line in self.index.read_text(encoding='utf-8').splitlines():
            try:
                rec=AssetRecord.model_validate(json.loads(line)); latest[rec.asset_id]=rec
            except Exception: continue
        return latest
    def list_assets(self) -> list[AssetRecord]: return list(self._latest().values())
    def get_asset(self, asset_id: str) -> AssetRecord | None: return self._latest().get(asset_id)
    def create_thumbnail(self, path: Path, asset_type: str) -> str | None:
        if asset_type != 'image': return None
        try:
            thumb = path.with_name(path.stem + '_thumb.jpg')
            img = Image.open(path); img.thumbnail((320, 180)); img.convert('RGB').save(thumb, 'JPEG')
            return str(thumb)
        except Exception: return None
    def save_upload_bytes(self, filename: str, data: bytes, project_id: str | None = None, shot_id: str | None = None) -> AssetRecord:
        ext = Path(filename or '').suffix.lower()
        if ext not in ALL_EXT: raise ValueError(f'unsupported format: {ext}')
        if len(data) > settings.max_upload_mb * 1024 * 1024: raise ValueError('file too large')
        asset_id = uuid4().hex; asset_type = self.asset_type_for(ext); target = self.root / f'{asset_id}{ext}'
        target.write_bytes(data); thumb = self.create_thumbnail(target, asset_type)
        return self._save_record(AssetRecord(asset_id=asset_id, filename=filename, path=str(target), asset_type=asset_type, size_bytes=len(data), thumbnail_path=thumb, project_id=project_id, shot_id=shot_id))
    def delete_asset(self, asset_id: str) -> bool:
        rec = self.get_asset(asset_id)
        if not rec: return False
        for p in [rec.path, rec.thumbnail_path]:
            if p and Path(p).exists(): Path(p).unlink()
        rec.metadata['deleted'] = True; self._save_record(rec); return True
    def bind_to_project(self, project_id: str, asset_id: str) -> dict:
        rec = self.get_asset(asset_id)
        if not rec: raise KeyError('asset not found')
        project = get_project_manager().get_project(project_id)
        if not project: raise KeyError('project not found')
        if asset_id not in project.assets: project.assets.append(asset_id)
        get_project_manager().save_project(project); rec.project_id = project_id; self._save_record(rec)
        return {'project_id': project_id, 'asset_id': asset_id}
    def bind_to_shot(self, project_id: str, shot_id: str, asset_id: str) -> dict:
        rec = self.get_asset(asset_id)
        if not rec: raise KeyError('asset not found')
        manager = get_project_manager(); project = manager.get_project(project_id)
        if not project: raise KeyError('project not found')
        for shot in project.shots:
            if shot.shot_id == shot_id:
                if asset_id not in shot.assets: shot.assets.append(asset_id)
                rec.project_id = project_id; rec.shot_id = shot_id; self._save_record(rec); manager.save_project(project)
                return {'project_id': project_id, 'shot_id': shot_id, 'asset_id': asset_id}
        raise KeyError('shot not found')

_default_assets: AssetManager | None = None

def get_asset_manager() -> AssetManager:
    global _default_assets
    if _default_assets is None: _default_assets = AssetManager()
    return _default_assets
