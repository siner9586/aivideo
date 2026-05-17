"""Background music interface placeholder."""
from __future__ import annotations
from pathlib import Path
import subprocess

AUDIO_EXT = {'.mp3','.wav','.m4a'}

def validate_music_asset(music_path: str) -> bool:
    return Path(music_path).exists() and Path(music_path).suffix.lower() in AUDIO_EXT

def generate_music_prompt(project_spec: dict) -> str:
    title = project_spec.get('title') or project_spec.get('original_prompt') or 'AI video'
    return f'Create a royalty-free background music prompt for: {title}. Keep it subtle, loopable and non-distracting.'

def attach_background_music(video_path: str, music_path: str | None, output_path: str, volume: float = 0.25) -> str:
    if not music_path or not validate_music_asset(music_path):
        Path(output_path).write_bytes(Path(video_path).read_bytes()); return output_path
    try:
        subprocess.run(['ffmpeg','-y','-i',video_path,'-i',music_path,'-filter:a',f'volume={volume}','-shortest','-c:v','copy',output_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        Path(output_path).write_bytes(Path(video_path).read_bytes())
    return output_path
