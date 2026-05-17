from app.backends.backend_registry import get_registry


def test_backend_registry_lists_and_validates():
    registry = get_registry()
    names = registry.list_backends()
    assert 'mock' in names
    assert 'comfyui' in names
    assert registry.get_backend('mock').name == 'mock'
    report = registry.validate_backend('not_exists')
    assert report['available'] is False
