"""File-system backed project manager."""
from __future__ import annotations
import shutil
from pathlib import Path
from uuid import uuid4
from app.config import settings
from app.projects.project_schema import Project, Shot, now_iso

class ProjectManager:
    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root or settings.project_dir); self.root.mkdir(parents=True, exist_ok=True)
    def project_path(self, project_id: str) -> Path: return self.root / project_id / 'project.json'
    def project_dir(self, project_id: str) -> Path:
        d = self.root / project_id
        for sub in ['assets','outputs']: (d/sub).mkdir(parents=True, exist_ok=True)
        return d
    def create_project(self, payload: dict | None = None) -> Project:
        payload = payload or {}; project_id = payload.get('project_id') or uuid4().hex
        project = Project(project_id=project_id, **{k:v for k,v in payload.items() if k!='project_id'})
        self.save_project(project); return project
    def save_project(self, project: Project) -> Project:
        project.updated_at = now_iso(); self.project_dir(project.project_id)
        self.project_path(project.project_id).write_text(project.model_dump_json(indent=2), encoding='utf-8')
        return project
    def list_projects(self) -> list[Project]:
        projects=[]
        for path in self.root.glob('*/project.json'):
            try: projects.append(Project.model_validate_json(path.read_text(encoding='utf-8')))
            except Exception: continue
        return sorted(projects, key=lambda p:p.updated_at, reverse=True)
    def get_project(self, project_id: str) -> Project | None:
        path = self.project_path(project_id)
        if not path.exists(): return None
        return Project.model_validate_json(path.read_text(encoding='utf-8'))
    def update_project(self, project_id: str, updates: dict) -> Project:
        project = self.get_project(project_id)
        if not project: raise KeyError('project not found')
        data = project.model_dump(); data.update({k:v for k,v in updates.items() if k not in {'project_id','created_at'}})
        return self.save_project(Project.model_validate(data))
    def delete_project(self, project_id: str) -> bool:
        d = self.root / project_id
        if not d.exists(): return False
        shutil.rmtree(d); return True
    def add_shot(self, project_id: str, payload: dict) -> Shot:
        project = self.get_project(project_id)
        if not project: raise KeyError('project not found')
        shot = Shot(shot_id=payload.get('shot_id') or uuid4().hex, **{k:v for k,v in payload.items() if k!='shot_id'})
        project.shots.append(shot); self.save_project(project); return shot
    def update_shot(self, project_id: str, shot_id: str, updates: dict) -> Shot:
        project = self.get_project(project_id)
        if not project: raise KeyError('project not found')
        for idx, shot in enumerate(project.shots):
            if shot.shot_id == shot_id:
                data = shot.model_dump(); data.update({k:v for k,v in updates.items() if k!='shot_id'})
                project.shots[idx] = Shot.model_validate(data); self.save_project(project); return project.shots[idx]
        raise KeyError('shot not found')
    def delete_shot(self, project_id: str, shot_id: str) -> bool:
        project = self.get_project(project_id)
        if not project: raise KeyError('project not found')
        before = len(project.shots); project.shots = [s for s in project.shots if s.shot_id != shot_id]
        self.save_project(project); return len(project.shots) < before
    def export_project(self, project_id: str) -> str:
        project = self.get_project(project_id)
        if not project: raise KeyError('project not found')
        archive_base = self.root / project_id / f'{project_id}_export'
        return shutil.make_archive(str(archive_base), 'zip', self.root / project_id)

_default_manager: ProjectManager | None = None

def get_project_manager() -> ProjectManager:
    global _default_manager
    if _default_manager is None: _default_manager = ProjectManager()
    return _default_manager
