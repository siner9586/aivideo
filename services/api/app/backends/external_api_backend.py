"""External commercial or remote inference backend skeleton."""
from app.backends.mock_backend import MockVideoBackend
class ExternalApiBackend(MockVideoBackend):
    name='external'
