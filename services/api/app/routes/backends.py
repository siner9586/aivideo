"""Backend inspection routes."""
from __future__ import annotations

from fastapi import APIRouter

from app.backends.backend_registry import get_registry

router = APIRouter(prefix='/api/backends', tags=['backends'])


@router.get('')
def list_backends() -> dict[str, object]:
    registry = get_registry()
    names = registry.list_backends()
    return {
        'default_backend': registry.get_default_backend(),
        'backends': names,
        'validation': [registry.validate_backend(name) for name in names],
    }


@router.get('/{backend_name}')
def validate_backend(backend_name: str) -> dict[str, object]:
    return get_registry().validate_backend(backend_name)
