"""Preference scoring framework for future Video RLHF integration."""
import json
from pathlib import Path
from statistics import mean
from app.config import settings
from app.models.schemas import PreferenceReport

def score_video_candidate(video_path, prompt_spec, reports) -> PreferenceReport:
    """Score one candidate with heuristic dimensions."""
    temporal=float(getattr(reports.get('temporal'), 'consistency_score', 0.75)) if isinstance(reports, dict) else 0.75
    safety=float(getattr(reports.get('safety'), 'allowed', True)) if isinstance(reports, dict) else 1.0
    vals={'prompt_alignment':0.75,'visual_quality':0.70,'motion_smoothness':temporal,'temporal_consistency':temporal,'character_consistency':0.75,'camera_quality':0.72,'safety_score':safety}
    overall=mean(vals.values())
    return PreferenceReport(video_path=str(video_path), overall_score=overall, notes=['heuristic MVP score'], **vals)

def rank_video_candidates(candidates) -> list:
    """Sort candidates by overall_score descending."""
    return sorted(candidates, key=lambda c: getattr(c, 'overall_score', c.get('overall_score',0)), reverse=True)

def save_human_feedback(task_id, feedback) -> str:
    """Persist human feedback as JSON."""
    settings.feedback_dir.mkdir(parents=True, exist_ok=True)
    path=settings.feedback_dir / f'{task_id}.json'
    path.write_text(json.dumps({'task_id':task_id,'feedback':feedback}, ensure_ascii=False, indent=2), encoding='utf-8')
    return str(path)

def load_feedback_dataset() -> list:
    """Load all saved human feedback records."""
    items=[]
    for p in Path(settings.feedback_dir).glob('*.json'):
        items.append(json.loads(p.read_text(encoding='utf-8')))
    return items
