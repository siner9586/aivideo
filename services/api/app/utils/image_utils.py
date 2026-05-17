"""Image validation helpers."""
from pathlib import Path
from PIL import Image

def image_info(path: str) -> dict:
    with Image.open(path) as im:
        return {'path': path, 'width': im.width, 'height': im.height, 'format': im.format}

def is_allowed_image(path: str) -> bool:
    return Path(path).suffix.lower() in {'.png','.jpg','.jpeg','.webp'}
