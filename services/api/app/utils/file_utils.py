"""Safe file helpers."""
from pathlib import Path
from uuid import uuid4

def safe_output_path(suffix: str = '.mp4', root: str | Path = 'data/outputs') -> Path:
    root = Path(root); root.mkdir(parents=True, exist_ok=True)
    return root / f'{uuid4().hex}{suffix}'

def ensure_within_root(path: str | Path, root: str | Path) -> Path:
    p = Path(path).resolve(); r = Path(root).resolve()
    if r not in p.parents and p != r:
        raise ValueError('unsafe path outside allowed root')
    return p
