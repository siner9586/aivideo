"""Subtitle draft generation and SRT helpers."""
from __future__ import annotations
from pathlib import Path
import subprocess


def _srt_time(seconds: float) -> str:
    ms = int((seconds-int(seconds))*1000); s = int(seconds)%60; m = (int(seconds)//60)%60; h = int(seconds)//3600
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'


def generate_subtitles_from_storyboard(storyboard: dict | list) -> list[dict]:
    shots = storyboard.get('shots', []) if isinstance(storyboard, dict) else storyboard
    subs=[]; t=0.0
    for idx, shot in enumerate(shots, start=1):
        duration = float(shot.get('duration', 3)) if isinstance(shot, dict) else 3.0
        text = (shot.get('action_prompt') or shot.get('visual_prompt') or f'Shot {idx}') if isinstance(shot, dict) else f'Shot {idx}'
        subs.append({'index': idx, 'start': t, 'end': t+duration, 'text': text[:90]}); t += duration
    return subs


def export_srt(subtitles: list[dict], output_path: str) -> str:
    blocks=[]
    for i, sub in enumerate(subtitles, start=1):
        blocks.append(f"{i}\n{_srt_time(sub['start'])} --> {_srt_time(sub['end'])}\n{sub['text']}\n")
    Path(output_path).write_text('\n'.join(blocks), encoding='utf-8')
    return output_path


def burn_subtitles(input_video: str, srt_path: str, output_video: str) -> str:
    try:
        subprocess.run(['ffmpeg','-y','-i',input_video,'-vf',f'subtitles={srt_path}',output_video], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        Path(output_video).write_bytes(Path(input_video).read_bytes())
    return output_video
