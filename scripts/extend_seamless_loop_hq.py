#!/usr/bin/env python3
"""Extend a high-quality seamless loop clip to a longer final MP4.

Use this after generating a 10-15 second seamless loop with a real video model.
The script uses ffmpeg through imageio-ffmpeg and does not add text, subtitles,
watermarks, logos, intro or outro frames.
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import imageio_ffmpeg


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="source seamless loop mp4, usually 10-15 seconds")
    parser.add_argument("--output", type=Path, default=Path("data/outputs/oriental_future_tiger_rose_180s_hq.mp4"))
    parser.add_argument("--duration", type=float, default=180.0, help="final duration in seconds")
    parser.add_argument("--fps", type=int, default=30, help="output fps")
    parser.add_argument("--width", type=int, default=3840, help="output width; height is derived from source aspect ratio")
    parser.add_argument("--crf", type=int, default=14, help="x264 quality: lower is higher quality; 12-16 recommended")
    parser.add_argument("--preset", default="slow", help="x264 preset: slow/veryslow for higher quality")
    parser.add_argument("--keep-audio", action="store_true", help="keep audio if the source has it; default removes audio")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.input.exists():
        raise FileNotFoundError(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    vf = f"fps={args.fps},scale={args.width}:-2:flags=lanczos,format=yuv420p"
    cmd = [
        ffmpeg,
        "-y",
        "-stream_loop",
        "-1",
        "-i",
        str(args.input),
        "-t",
        str(args.duration),
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-preset",
        args.preset,
        "-crf",
        str(args.crf),
        "-movflags",
        "+faststart",
    ]
    if args.keep_audio:
        cmd += ["-c:a", "aac", "-b:a", "192k"]
    else:
        cmd += ["-an"]
    cmd.append(str(args.output))
    subprocess.run(cmd, check=True)
    print(args.output)


if __name__ == "__main__":
    main()
