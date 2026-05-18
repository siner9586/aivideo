#!/usr/bin/env python3
"""Text-free oriental futurism tiger-and-rose seamless loop preview.

CPU-only OpenCV renderer for composition, timing and loop-anchor preview.
It intentionally avoids all text, titles, seals, logos and watermarks.
For photorealistic fur/petals, use the prompt template with a real video model.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import cv2
import numpy as np


def parse_resolution(value: str) -> tuple[int, int]:
    try:
        w, h = value.lower().split("x")
        return int(w), int(h)
    except Exception as exc:
        raise argparse.ArgumentTypeError("resolution must look like 1280x720") from exc


def ellipse_poly(cx: float, cy: float, ax: float, ay: float, angle: float, n: int = 96) -> np.ndarray:
    rad = math.radians(angle)
    ca, sa = math.cos(rad), math.sin(rad)
    pts = []
    for i in range(n):
        th = 2 * math.pi * i / n
        x, y = ax * math.cos(th), ay * math.sin(th)
        pts.append((int(cx + x * ca - y * sa), int(cy + x * sa + y * ca)))
    return np.array(pts, dtype=np.int32)


def glow(frame: np.ndarray, layer: np.ndarray, sigma: int, alpha: float) -> None:
    blur = cv2.GaussianBlur(layer, (0, 0), sigma)
    cv2.addWeighted(frame, 1.0, blur, alpha, 0, frame)


def background(t: float, w: int, h: int) -> np.ndarray:
    y = np.linspace(0, 1, h)[:, None]
    x = np.linspace(0, 1, w)[None, :]
    pulse = 0.5 + 0.5 * math.sin(2 * math.pi * t)
    b = 24 + 28 * (1 - y) + 9 * np.sin(2 * math.pi * (x + t))
    g = 24 + 28 * y + 8 * np.cos(2 * math.pi * (x * 0.45 - t))
    r = 42 + 50 * (1 - y) + 22 * pulse + 0 * x
    frame = np.dstack([b, g, r]).clip(0, 255).astype(np.uint8)

    layer = np.zeros_like(frame)
    c = (int(w * 0.52), int(h * 0.18))
    for radius, color, alpha in [
        (int(w * 0.25), (48, 50, 130), 0.32),
        (int(w * 0.16), (62, 74, 178), 0.24),
        (int(w * 0.08), (82, 134, 225), 0.22),
    ]:
        cv2.circle(layer, c, radius, color, -1, cv2.LINE_AA)
        glow(frame, layer, max(7, radius // 5), alpha)
        layer[:] = 0

    for i in range(9):
        a = 2 * math.pi * i / 9 + 0.04 * math.sin(2 * math.pi * t)
        p = (int(c[0] + math.cos(a) * w * 0.13), int(c[1] + math.sin(a) * h * 0.06))
        cv2.circle(frame, p, 2 + (i % 2), (80, 160, 245), -1, cv2.LINE_AA)

    metal, ink, jade = (44, 62, 70), (16, 26, 32), (55, 102, 84)
    cv2.ellipse(frame, (int(w * 0.50), int(h * 0.58)), (int(w * 0.31), int(h * 0.34)), 0, 180, 360, metal, 4, cv2.LINE_AA)
    cv2.rectangle(frame, (int(w * 0.17), int(h * 0.54)), (int(w * 0.83), int(h * 0.57)), metal, -1)
    roof = np.array([
        (int(w * 0.18), int(h * 0.33)), (int(w * 0.35), int(h * 0.25)),
        (int(w * 0.50), int(h * 0.29)), (int(w * 0.65), int(h * 0.25)),
        (int(w * 0.82), int(h * 0.33)), (int(w * 0.73), int(h * 0.35)),
        (int(w * 0.50), int(h * 0.34)), (int(w * 0.27), int(h * 0.35)),
    ], dtype=np.int32)
    cv2.polylines(frame, [roof], True, (48, 74, 84), 3, cv2.LINE_AA)
    mountains = np.array([
        (0, int(h * 0.50)), (int(w * 0.16), int(h * 0.42)), (int(w * 0.30), int(h * 0.49)),
        (int(w * 0.43), int(h * 0.39)), (int(w * 0.58), int(h * 0.51)),
        (int(w * 0.75), int(h * 0.41)), (w, int(h * 0.46)), (w, int(h * 0.62)), (0, int(h * 0.62)),
    ], dtype=np.int32)
    overlay = frame.copy()
    cv2.fillPoly(overlay, [mountains], ink)
    cv2.addWeighted(overlay, 0.35, frame, 0.65, 0, frame)

    for i in range(9):
        bx = int(w * (0.08 + 0.018 * i))
        sway = int(7 * math.sin(2 * math.pi * (t + i * 0.07)))
        cv2.line(frame, (bx, int(h * 0.43)), (bx + sway, int(h * 0.23 + i * h * 0.012)), jade, 2, cv2.LINE_AA)
    for i in range(5):
        x0, y0 = int(w * (0.72 + i * 0.035)), int(h * (0.66 + i * 0.025))
        cv2.line(frame, (x0, y0), (x0 + int(w * 0.12), y0 + int(h * 0.01)), (132, 134, 130), 2, cv2.LINE_AA)
    return frame


def draw_water(frame: np.ndarray, t: float, w: int, h: int) -> None:
    wy = int(h * 0.73)
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, wy), (w, h), (35, 42, 55), -1)
    cv2.addWeighted(overlay, 0.42, frame, 0.58, 0, frame)
    for j in range(12):
        phase = (t + j / 12) % 1
        cx = int(w * (0.5 + 0.16 * math.sin(2 * math.pi * (phase + 0.1))))
        cy = int(h * (0.76 + 0.13 * j / 12))
        rx, ry = int(w * (0.025 + 0.08 * phase)), int(h * (0.006 + 0.018 * phase))
        cv2.ellipse(frame, (cx, cy), (rx, ry), 0, 0, 360, (72, 94, 112), 1, cv2.LINE_AA)


def draw_particles(frame: np.ndarray, t: float, w: int, h: int) -> None:
    rng = np.random.default_rng(13)
    for j in range(4):
        pts = []
        for i in range(80):
            u = i / 79
            pts.append((int(w * (0.20 + 0.60 * u)), int(h * (0.28 + j * 0.055 + 0.015 * math.sin(2 * math.pi * (u + t + j * 0.1))))))
        cv2.polylines(frame, [np.array(pts, dtype=np.int32)], False, (70, 82, 118), 1, cv2.LINE_AA)
    for _ in range(90):
        u, v, p = rng.random(), rng.random(), rng.random()
        x = int(w * u + 8 * math.sin(2 * math.pi * (t + p + u)))
        y = int(h * (0.18 + 0.62 * v))
        cv2.circle(frame, (x, y), 1, (52, 116, 176), -1, cv2.LINE_AA)


def draw_tiger(frame: np.ndarray, t: float, w: int, h: int) -> None:
    s = min(w, h) / 720
    breath = math.sin(2 * math.pi * t)
    cx, cy = w * 0.46, h * (0.64 - 0.004 * breath)
    body, shadow, stripe, gold = (42, 76, 138), (14, 22, 30), (16, 24, 32), (76, 164, 226)
    for poly, col in [
        (ellipse_poly(cx - 30 * s, cy + 10 * s, 190 * s, 72 * s, -5), body),
        (ellipse_poly(cx - 120 * s, cy - 3 * s, 82 * s, 80 * s, 8), (46, 84, 148)),
        (ellipse_poly(cx + 130 * s, cy - 35 * s, 77 * s, 63 * s, -10), (50, 90, 154)),
        (ellipse_poly(cx + 188 * s, cy - 25 * s, 35 * s, 24 * s, -7), (84, 118, 160)),
    ]:
        cv2.fillPoly(frame, [poly], col, cv2.LINE_AA)
    cv2.polylines(frame, [ellipse_poly(cx - 30 * s, cy + 10 * s, 190 * s, 72 * s, -5)], True, (72, 110, 162), 2, cv2.LINE_AA)
    for ex, ey, sign in [(cx + 88 * s, cy - 91 * s, -1), (cx + 145 * s, cy - 94 * s, 1)]:
        twist = 5 * math.sin(2 * math.pi * (2 * t + 0.15))
        pts = np.array([(int(ex), int(ey)), (int(ex + sign * 28 * s), int(ey - 38 * s + twist)), (int(ex + sign * 42 * s), int(ey + 9 * s))], dtype=np.int32)
        cv2.fillPoly(frame, [pts], (41, 76, 132), cv2.LINE_AA)
        cv2.polylines(frame, [pts], True, gold, 1, cv2.LINE_AA)
    for px, py, ax, ay in [(cx - 135 * s, cy + 74 * s, 72, 23), (cx + 55 * s, cy + 78 * s, 88, 25), (cx + 165 * s, cy + 36 * s, 62, 20)]:
        cv2.fillPoly(frame, [ellipse_poly(px, py, ax * s, ay * s, -5, 56)], shadow, cv2.LINE_AA)
    tail = []
    for i in range(60):
        u = i / 59
        tail.append((int(cx - 205 * s - 55 * s * math.sin(math.pi * u)), int(cy + 10 * s - 80 * s * u + 12 * s * math.sin(2 * math.pi * (u + t)))))
    cv2.polylines(frame, [np.array(tail, dtype=np.int32)], False, (43, 78, 138), max(4, int(16 * s)), cv2.LINE_AA)
    for i in range(16):
        u = i / 15
        sx, sy = int(cx - 195 * s + u * 330 * s), int(cy - 62 * s + 12 * s * math.sin(2 * math.pi * (u + t * 0.2)))
        ex, ey = int(sx + 18 * s * math.sin(i)), int(sy + 70 * s)
        cv2.line(frame, (sx, sy), (ex, ey), stripe, max(1, int(4 * s)), cv2.LINE_AA)
        if i % 3 == 0:
            p = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(2 * math.pi * (t + i * 0.08)))
            cv2.line(frame, (sx, sy + int(4 * s)), (ex, ey - int(6 * s)), tuple(int(c * p) for c in gold), 1, cv2.LINE_AA)
    eye = (int(cx + 152 * s), int(cy - 53 * s))
    if 0.46 < t < 0.49:
        cv2.line(frame, (eye[0] - int(8 * s), eye[1]), (eye[0] + int(8 * s), eye[1]), (15, 22, 24), 2, cv2.LINE_AA)
    else:
        cv2.ellipse(frame, eye, (max(2, int(10 * s)), max(1, int(5 * s))), 0, 0, 360, (25, 40, 42), -1, cv2.LINE_AA)
        cv2.circle(frame, (eye[0] + int(3 * s), eye[1] - int(1 * s)), 1, (120, 210, 240), -1, cv2.LINE_AA)
    cv2.circle(frame, (int(cx + 213 * s), int(cy - 24 * s)), max(2, int(5 * s)), (16, 22, 26), -1, cv2.LINE_AA)
    ws = int(3 * s * math.sin(4 * math.pi * t))
    for dy in [-12, -4, 5]:
        cv2.line(frame, (int(cx + 190 * s), int(cy - 24 * s + dy * s)), (int(cx + 260 * s), int(cy - 46 * s + dy * s + ws)), (140, 150, 145), 1, cv2.LINE_AA)


def draw_rose(frame: np.ndarray, t: float, w: int, h: int) -> None:
    s = min(w, h) / 720
    sway = math.sin(2 * math.pi * t) * 8 * s
    base = (int(w * 0.62), int(h * 0.70))
    flower = (int(w * 0.66 + sway), int(h * 0.55 + 3 * s * math.sin(2 * math.pi * (t + 0.2))))
    cv2.line(frame, base, flower, (50, 120, 92), max(1, int(3 * s)), cv2.LINE_AA)
    layer = np.zeros_like(frame)
    for i in range(18):
        a = 2 * math.pi * i / 18 + 0.08 * math.sin(2 * math.pi * t)
        rad = 14 * s + 13 * s * (i % 3)
        c = (flower[0] + int(math.cos(a) * rad * 0.40), flower[1] + int(math.sin(a) * rad * 0.28))
        axes = (max(2, int((19 + i % 4 * 4) * s)), max(1, int((8 + i % 5 * 2) * s)))
        color = (90 + i % 4 * 15, 58 + i % 3 * 18, 150 + i % 5 * 18)
        cv2.ellipse(frame, c, axes, math.degrees(a), 0, 360, color, -1, cv2.LINE_AA)
        cv2.ellipse(layer, c, axes, math.degrees(a), 0, 360, (90, 80, 210), 1, cv2.LINE_AA)
    glow(frame, layer, 11, 0.45)
    cv2.circle(frame, flower, max(3, int(7 * s)), (70, 120, 225), -1, cv2.LINE_AA)
    for i in range(34):
        phase = (t + i / 34) % 1
        a = 2 * math.pi * (phase * 1.4 + i * 0.03)
        rr = s * (10 + 85 * phase)
        px = int(flower[0] + math.cos(a) * rr + 42 * s * phase)
        py = int(flower[1] + math.sin(a) * rr * 0.35 - 20 * s * phase)
        fade = 1 - phase
        cv2.circle(frame, (px, py), 1, tuple(int(c * fade) for c in (85, 155, 245)), -1, cv2.LINE_AA)
    for i in range(7):
        phase = (t + i / 7) % 1
        px = int(w * (0.54 + 0.18 * phase + 0.015 * math.sin(2 * math.pi * (phase + i))))
        py = int(h * (0.42 + 0.30 * phase))
        cv2.ellipse(frame, (px, py), (max(2, int(8 * s)), max(1, int(3 * s))), 30 + 40 * math.sin(2 * math.pi * phase), 0, 360, (96, 62, 185), -1, cv2.LINE_AA)


def render_frame(i: int, loop_frames: int, w: int, h: int) -> np.ndarray:
    t = (i % loop_frames) / loop_frames
    frame = background(t, w, h)
    draw_particles(frame, t, w, h)
    draw_water(frame, t, w, h)
    draw_rose(frame, t, w, h)
    draw_tiger(frame, t, w, h)
    soft = cv2.GaussianBlur(frame, (0, 0), 2)
    frame = cv2.addWeighted(frame, 0.88, soft, 0.12, 0)
    yy, xx = np.mgrid[0:h, 0:w]
    mask = np.clip(1.05 - 0.38 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2), 0.62, 1.0)[..., None]
    return (frame.astype(np.float32) * mask).clip(0, 255).astype(np.uint8)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=180)
    parser.add_argument("--loop-seconds", type=float, default=12)
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--resolution", type=parse_resolution, default=parse_resolution("1280x720"))
    parser.add_argument("--output", type=Path, default=Path("data/outputs/oriental_future_tiger_rose_loop.mp4"))
    args = parser.parse_args()

    w, h = args.resolution
    args.output.parent.mkdir(parents=True, exist_ok=True)
    total_frames = int(args.seconds * args.fps)
    loop_frames = max(2, int(args.loop_seconds * args.fps))
    frames = [render_frame(i, loop_frames, w, h) for i in range(loop_frames)]

    writer = cv2.VideoWriter(str(args.output), cv2.VideoWriter_fourcc(*"mp4v"), args.fps, (w, h))
    if not writer.isOpened():
        raise RuntimeError(f"failed to open writer for {args.output}")
    for i in range(total_frames):
        writer.write(frames[i % loop_frames])
    writer.release()
    print(args.output)


if __name__ == "__main__":
    main()
