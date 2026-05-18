#!/usr/bin/env python3
"""Check files that should stay out of normal Git blobs.

Usage:
  python scripts/check_lfs_pointers.py
  python scripts/check_lfs_pointers.py --max-mb 10
"""
from __future__ import annotations

import argparse
import fnmatch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LFS_PATTERNS = [
    "*.safetensors", "*.bin", "*.ckpt", "*.pt", "*.pth", "*.onnx", "*.gguf", "*.ggml",
    "*.npz", "*.npy", "*.msgpack",
    "*.tar", "*.tar.gz", "*.tgz", "*.zip", "*.7z", "*.rar",
    "*.mp4", "*.mov", "*.webm", "*.mkv", "*.avi",
    "*.wav", "*.mp3", "*.m4a", "*.flac",
    "*.ply", "*.splat", "*.ksplat", "*.glb", "*.gltf", "*.obj", "*.fbx",
]

SKIP_PREFIXES = [
    ".git/", ".venv/", "venv/", "node_modules/", ".next/", "dist/", "build/",
    "models/", "weights/", "checkpoints/", "data/outputs/", "data/uploads/", "data/logs/",
]


def is_skipped(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    return any(rel.startswith(prefix) for prefix in SKIP_PREFIXES)


def matches_pattern(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix().lower()
    name = path.name.lower()
    return any(fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(rel, pattern) for pattern in LFS_PATTERNS)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check model/media files before pushing.")
    parser.add_argument("--max-mb", type=float, default=50.0, help="Warn on files larger than this size.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    max_bytes = int(args.max_mb * 1024 * 1024)
    findings: list[tuple[str, float, str]] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or is_skipped(path):
            continue
        size = path.stat().st_size
        if matches_pattern(path) or size >= max_bytes:
            rel = path.relative_to(ROOT).as_posix()
            reason = "extension" if matches_pattern(path) else f">={args.max_mb:g} MiB"
            findings.append((rel, size / 1024 / 1024, reason))
    if not findings:
        print("OK: no suspicious large model/media files found outside ignored folders.")
        return 0
    print("Review these files before pushing:")
    for rel, size_mb, reason in findings:
        print(f"- {rel} ({size_mb:.2f} MiB, {reason})")
    print("Keep real model weights under models/, weights/, or checkpoints/, or manage intentionally with Git LFS.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
