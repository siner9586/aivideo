from app.backends.backend_registry import get_registry

def get_backend(name: str):
    try:
        return get_registry().get_backend(name)
    except Exception:
        return get_registry().get_backend('mock')
