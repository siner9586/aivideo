"""FFmpeg helpers."""
import shutil, subprocess

def has_ffmpeg() -> bool:
    return shutil.which('ffmpeg') is not None

def run_ffmpeg(args: list[str]) -> None:
    subprocess.run(['ffmpeg','-y',*args], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
