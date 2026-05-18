#!/usr/bin/env python3
"""Render a text-free oriental futurism tiger-and-rose seamless loop preview.

This CPU-only OpenCV renderer is a concept preview for composition, timing,
loop anchors and color direction. It does not replace a real text-to-video model
for photorealistic fur, petals or high-end generative motion.
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
    except Exception as exc:  # pragma: no cover
        raise argparse.ArgumentTypeError("resolution must look like 1280x720") from exc


def ease(x: float) -> float:
    return 0.5 - 0.5 * math.cos(2 * math.pi * x)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def add_glow(frame: np.ndarray, layer: np.ndarray, sigma: int = 21, alpha: float = 0.7) -> np.ndarray:
    blur = cv2.GaussianBlur(layer, (0, 0), sigma)
    return cv2.addWeighted(frame, 1.0, blur, alpha, 0)


def ellipse_poly(center: tuple[float, float], axes: tuple[float, float], angle_deg: float, n: int = 160) -> np.ndarray:
    cx, cy = center
    ax, ay = axes
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    pts = []
    for i in range(n):
        th = 2 * math.pi * i / n
        x, y = ax * math.cos(th), ay * math.sin(th)
        pts.append((int(cx + x * ca - y * sa), int(cy + x * sa + y * ca)))
    return np.array(pts, dtype=np.int32)


def draw_background(frame: np.ndarray, t: float, w: int, h: int) -> None:
    y = np.linspace(0, 1, h)[:, None]
    x = np.linspace(0, 1, w)[None, :]
    pulse = 0.5 + 0.5 * math.sin(2 * math.pi * t)

    # Deep ink-green to purple-red warm-gold gradient, BGR.
    b = 26 + 28 * (1 - y) + 12 * np.sin(2 * math.pi * (x + t))
    g = 23 + 28 * y + 10 * np.cos(2 * math.pi * (x * 0.5 - t))
    r = 42 + 54 * (1 - y) + 26 * pulse
    frame[:] = np.dstack([b.repeat(w, axis=1), g.repeat(w, axis=1), r.repeat(w, axis=1)]).clip(0, 255).astype(np.uint8)

    # Southern / upper Li-fire halo.
    glow = np.zeros_like(frame)
    halo_center = (int(w * 0.52), int(h * 0.18))
    for radius, color, a in [
        (int(w * 0.24), (45, 48, 135), 0.32),
        (int(w * 0.16), (60, 70, 180), 0.28),
        (int(w * 0.08), (70, 120, 215), 0.24),
    ]:
        cv2.circle(glow, halo_center, radius, color, -1, cv2.LINE_AA)
        frame[:] = add_glow(frame, glow, sigma=max(9, radius // 4), alpha=a)
        glow[:] = 0

    # Nine implicit warm light points, not readable digits or symbols.
    for i in range(9):
        ang = 2 * math.pi * i / 9 + 0.06 * math.sin(2 * math.pi * t)
        px = int(halo_center[0] + math.cos(ang) * w * 0.13)
        py = int(halo_center[1] + math.sin(ang) * h * 0.06)
        rad = int(2 + 2 * (0.5 + 0.5 * math.sin(2 * math.pi * (t + i / 9))))
        cv2.circle(frame, (px, py), rad, (80, 165, 245), -1, cv2.LINE_AA)

    # Courtyard silhouettes: moon gate, eaves, corridor, distant mountains.
    ink = (18, 28, 34)
    metal = (42, 58, 67)
    jade = (58, 96, 85)
    cv2.ellipse(frame, (int(w * 0.50), int(h * 0.58)), (int(w * 0.31), int(h * 0.34)), 0, 180, 360, metal, 5, cv2.LINE_AA)
    cv2.rectangle(frame, (int(w * 0.17), int(h * 0.54)), (int(w * 0.83), int(h * 0.57)), metal, -1)
    for k in range(7):
        x0 = int(w * (0.18 + k * 0.105))
        cv2.line(frame, (x0, int(h * 0.31)), (x0 + int(w * 0.04), int(h * 0.54)), (35, 55, 60), 2, cv2.LINE_AA)
    # flying eaves as quiet arcs / triangles
    roof = np.array([
        (int(w * 0.18), int(h * 0.33)), (int(w * 0.35), int(h * 0.25)),
        (int(w * 0.50), int(h * 0.29)), (int(w * 0.65), int(h * 0.25)),
        (int(w * 0.82), int(h * 0.33)), (int(w * 0.73), int(h * 0.35)),
        (int(w * 0.50), int(h * 0.34)), (int(w * 0.27), int(h * 0.35)),
    ], dtype=np.int32)
    cv2.polylines(frame, [roof], True, (44, 68, 77), 3, cv2.LINE_AA)
    # mountains
    mts = np.array([
        (0, int(h * 0.50)), (int(w * 0.12), int(h * 0.42)), (int(w * 0.24), int(h * 0.48)),
        (int(w * 0.36), int(h * 0.38)), (int(w * 0.52), int(h * 0.50)),
        (int(w * 0.69), int(h * 0.40)), (int(w * 0.84), int(h * 0.49)),
        (w, int(h * 0.43)), (w, int(h * 0.61)), (0, int(h * 0.61)),
    ], dtype=np.int32)
    overlay = frame.copy()
    cv2.fillPoly(overlay, [mts], ink)
    cv2.addWeighted(overlay, 0.35, frame, 0.65, 0, frame)

    # Left green pine/bamboo-like organic strokes; right moon-white crystal steps.
    for i in range(9):
        base_x = int(w * (0.08 + 0.018 * i))
        sway = int(8 * math.sin(2 * math.pi * (t + i * 0.07)))
        cv2.line(frame, (base_x, int(h * 0.42)), (base_x + sway, int(h * 0.22 + i * h * 0.012)), jade, 2, cv2.LINE_AA)
    for i in range(5):
        x0 = int(w * (0.72 + i * 0.035))
        y0 = int(h * (0.66 + i * 0.025))
        cv2.line(frame, (x0, y0), (x0 + int(w * 0.12), y0 + int(h * 0.01)), (128, 132, 128), 2, cv2.LINE_AA)


def draw_water(frame: np.ndarray, t: float, w: int, h: int) -> None:
    water_y = int(h * 0.73)
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, water_y), (w, h), (35, 41, 55), -1)
    cv2.addWeighted(overlay, 0.42, frame, 0.58, 0, frame)
    for j in range(14):
        phase = (t + j / 14) % 1.0
        cx = int(w * (0.5 + 0.16 * math.sin(2 * math.pi * (phase + 0.1))))
        cy = int(lerp(h * 0.76, h * 0.90, j / 14))
        rx = int(w * (0.025 + 0.085 * phase))
        ry = int(h * (0.006 + 0.018 * phase))
        col = (70, 92, 112)
        cv2.ellipse(frame, (cx, cy), (rx, ry), 0, 0, 360, col, 1, cv2.LINE_AA)


def draw_tiger(frame: np.ndarray, t: float, w: int, h: int) -> None:
    breath = math.sin(2 * math.pi * t)
    cx, cy = w * 0.46, h * (0.64 - 0.004 * breath)
    scale = min(w, h) / 720
    body_col = (40, 72, 132)
    shadow_col = (14, 22, 30)
    stripe_col = (16, 24, 32)
    gold = (70, 160, 225)

    # Body, shoulder and head as painterly ellipses.
    body = ellipse_poly((cx - 30 * scale, cy + 10 * scale), (190 * scale, 72 * scale), -5, 180)
    cv2.fillPoly(frame, [body], body_col, cv2.LINE_AA)
    cv2.polylines(frame, [body], True, (68, 105, 160), 2, cv2.LINE_AA)
    shoulder = ellipse_poly((cx - 120 * scale, cy - 3 * scale), (82 * scale, 80 * scale), 8, 120)
    cv2.fillPoly(frame, [shoulder], (45, 82, 144), cv2.LINE_AA)
    head = ellipse_poly((cx + 130 * scale, cy - 35 * scale), (77 * scale, 63 * scale), -10, 140)
    cv2.fillPoly(frame, [head], (49, 88, 151), cv2.LINE_AA)
    muzzle = ellipse_poly((cx + 188 * scale, cy - 25 * scale), (35 * scale, 24 * scale), -7, 80)
    cv2.fillPoly(frame, [muzzle], (83, 116, 158), cv2.LINE_AA)

    # Ears with occasional tiny motion.
    ear_twist = 5 * math.sin(2 * math.pi * (t * 2 + 0.15))
    for ex, ey, sign in [(cx + 88 * scale, cy - 91 * scale, -1), (cx + 145 * scale, cy - 94 * scale, 1)]:
        pts = np.array([
            (int(ex), int(ey)),
            (int(ex + sign * 28 * scale), int(ey - 38 * scale + ear_twist)),
            (int(ex + sign * 42 * scale), int(ey + 9 * scale)),
        ], dtype=np.int32)
        cv2.fillPoly(frame, [pts], (41, 76, 131), cv2.LINE_AA)
        cv2.polylines(frame, [pts], True, gold, 1, cv2.LINE_AA)

    # Legs / paws resting, non-aggressive.
    for px, py, ax, ay in [
        (cx - 135 * scale, cy + 74 * scale, 72, 23),
        (cx + 55 * scale, cy + 78 * scale, 88, 25),
        (cx + 165 * scale, cy + 36 * scale, 62, 20),
    ]:
        paw = ellipse_poly((px, py), (ax * scale, ay * scale), -5, 70)
        cv2.fillPoly(frame, [paw], shadow_col, cv2.LINE_AA)

    # Tail curve.
    tail_pts = []
    for i in range(80):
        u = i / 79
        x = cx - 205 * scale - 55 * scale * math.sin(math.pi * u)
        y = cy + 10 * scale - 80 * scale * u + 12 * scale * math.sin(2 * math.pi * (u + t))
        tail_pts.append((int(x), int(y)))
    cv2.polylines(frame, [np.array(tail_pts, dtype=np.int32)], False, (43, 78, 138), int(16 * scale), cv2.LINE_AA)
    cv2.polylines(frame, [np.array(tail_pts, dtype=np.int32)], False, (80, 125, 176), int(2 * scale), cv2.LINE_AA)

    # Stripes and gold nano-cloud lines.
    for i in range(16):
        u = i / 15
        sx = int(cx - 195 * scale + u * 330 * scale)
        sy = int(cy - 62 * scale + 12 * scale * math.sin(2 * math.pi * (u + t * 0.2)))
        ex = int(sx + 18 * scale * math.sin(i))
        ey = int(sy + 70 * scale)
        cv2.line(frame, (sx, sy), (ex, ey), stripe_col, max(1, int(4 * scale)), cv2.LINE_AA)
        if i % 3 == 0:
            pulse = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(2 * math.pi * (t + i * 0.08)))
            cv2.line(frame, (sx, sy + int(4 * scale)), (ex, ey - int(6 * scale)), tuple(int(c * pulse) for c in gold), 1, cv2.LINE_AA)
    for i in range(6):
        sx = int(cx + 82 * scale + i * 18 * scale)
        cv2.line(frame, (sx, int(cy - 78 * scale)), (sx - int(12 * scale), int(cy - 28 * scale)), stripe_col, 3, cv2.LINE_AA)

    # Calm eye, nose, whiskers.
    blink = 1.0 if (0.46 < t < 0.49) else 0.0
    eye_y = int(cy - 53 * scale)
    eye_x = int(cx + 152 * scale)
    if blink:
        cv2.line(frame, (eye_x - int(8 * scale), eye_y), (eye_x + int(8 * scale), eye_y), (15, 22, 24), 2, cv2.LINE_AA)
    else:
        cv2.ellipse(frame, (eye_x, eye_y), (int(10 * scale), int(5 * scale)), 0, 0, 360, (25, 40, 42), -1, cv2.LINE_AA)
        cv2.circle(frame, (eye_x + int(3 * scale), eye_y - int(1 * scale)), max(1, int(2 * scale)), (120, 210, 240), -1, cv2.LINE_AA)
    cv2.circle(frame, (int(cx + 213 * scale), int(cy - 24 * scale)), max(2, int(5 * scale)), (16, 22, 26), -1, cv2.LINE_AA)
    whisker_shift = int(3 * scale * math.sin(2 * math.pi * (t * 2)))
    for dy in [-12, -4, 5]:
        start = (int(cx + 190 * scale), int(cy - 24 * scale + dy * scale))
        end = (int(cx + 260 * scale), int(cy - 46 * scale + dy * scale + whisker_shift))
        cv2.line(frame, start, end, (140, 150, 145), 1, cv2.LINE_AA)

    # Fur shimmer as sparse short strokes.
    rng = np.random.default_rng(100)
    for _ in range(120):
        u = rng.random()
        px = int(cx - 190 * scale + u * 350 * scale)
        py = int(cy - 50 * scale + rng.random() * 95 * scale)
        if ((px - (cx - 30 * scale)) / (190 * scale)) ** 2 + ((py - (cy + 10 * scale)) / (72 * scale)) ** 2 < 1.0:
            dx = int(6 * scale)
            cv2.line(frame, (px, py), (px + dx, py - 1), (70, 105, 148), 1, cv2.LINE_AA)


def draw_rose(frame: np.ndarray, t: float, w: int, h: int) -> None:
    scale = min(w, h) / 720
    sway = math.sin(2 * math.pi * t) * 8 * scale
    base = (int(w * 0.62), int(h * 0.70))
    flower = (int(w * 0.66 + sway), int(h * 0.55 + 3 * scale * math.sin(2 * math.pi * (t + 0.2))))
    stem_col = (50, 120, 92)
    cv2.line(frame, base, flower, stem_col, max(1, int(3 * scale)), cv2.LINE_AA)

    glow = np.zeros_like(frame)
    for i in range(18):
        ang = 2 * math.pi * i / 18 + 0.08 * math.sin(2 * math.pi * t)
        rad = 14 * scale + 13 * scale * (i % 3)
        cx = flower[0] + int(math.cos(ang) * rad * 0.40)
        cy = flower[1] + int(math.sin(ang) * rad * 0.28)
        axes = (int((19 + i % 4 * 4) * scale), int((8 + i % 5 * 2) * scale))
        color = (90 + i % 4 * 15, 58 + i % 3 * 18, 150 + i % 5 * 18)  # BGR pink/crimson/purple
        cv2.ellipse(frame, (cx, cy), axes, math.degrees(ang), 0, 360, color, -1, cv2.LINE_AA)
        cv2.ellipse(glow, (cx, cy), axes, math.degrees(ang), 0, 360, (90, 80, 210), 1, cv2.LINE_AA)
    frame[:] = add_glow(frame, glow, sigma=13, alpha=0.45)
    cv2.circle(frame, flower, max(3, int(7 * scale)), (70, 120, 225), -1, cv2.LINE_AA)

    # Fragrance-like spiral particles near rose and tiger nose.
    for i in range(44):
        phase = (t + i / 44) % 1.0
        ang = 2 * math.pi * (phase * 1.4 + i * 0.03)
        rr = scale * (10 + 85 * phase)
        px = int(flower[0] + math.cos(ang) * rr + 42 * scale * phase)
        py = int(flower[1] + math.sin(ang) * rr * 0.35 - 20 * scale * phase)
        alpha = 1 - phase
        col = tuple(int(c * alpha) for c in (85, 155, 245))
        cv2.circle(frame, (px, py), max(1, int(2 * scale * alpha + 1)), col, -1, cv2.LINE_AA)

    # Falling petals as looping anchors.
    for i in range(7):
        phase = (t + i / 7) % 1.0
        px = int(w * (0.54 + 0.18 * phase + 0.015 * math.sin(2 * math.pi * (phase + i))))
        py = int(h * (0.42 + 0.30 * phase))
        cv2.ellipse(frame, (px, py), (int(8 * scale), int(3 * scale)), 30 + 40 * math.sin(2 * math.pi * phase), 0, 360, (96, 62, 185), -1, cv2.LINE_AA)


def draw_particles_and_holograms(frame: np.ndarray, t: float, w: int, h: int) -> None:
    scale = min(w, h) / 720
    # Elegant light bands / data particles, no readable symbols.
    for j in range(5):
        pts = []
        for i in range(120):
            u = i / 119
            x = int(w * (0.18 + 0.65 * u))
            y = int(h * (0.28 + j * 0.045 + 0.018 * math.sin(2 * math.pi * (u + t + j * 0.1))))
            pts.append((x, y))
        cv2.polylines(frame, [np.array(pts, dtype=np.int32)], False, (70, 82, 116), 1, cv2.LINE_AA)
    rng = np.random.default_rng(12)
    for i in range(160):
        u = rng.random()
        v = rng.random()
        phase = (t + rng.random()) % 1.0
        x = int(w * u + 10 * math.sin(2 * math.pi * (phase + u)))
        y = int(h * (0.18 + 0.62 * v))
        if rng.random() < 0.5:
            col = (50, 120, 180)
        else:
            col = (55, 95, 135)
        cv2.circle(frame, (x, y), max(1, int(scale * (0.7 + 1.5 * math.sin(math.pi * phase) ** 2))), col, -1, cv2.LINE_AA)


def render_frame(i: int, total_loop_frames: int, w: int, h: int) -> np.ndarray:
    t = (i % total_loop_frames) / total_loop_frames
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    draw_background(frame, t, w, h)
    draw_particles_and_holograms(frame, t, w, h)
    draw_water(frame, t, w, h)
    draw_rose(frame, t, w, h)
    draw_tiger(frame, t, w, h)

    # Subtle cinematic diffusion, but no text/logo/watermark.
    glow = cv2.GaussianBlur(frame, (0, 0), 3)
    frame = cv2.addWeighted(frame, 0.86, glow, 0.14, 0)
    vignette = np.zeros_like(frame, dtype=np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    dist = ((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2
    mask = np.clip(1.05 - 0.38 * dist, 0.62, 1.0)[..., None]
    frame = (frame.astype(np.float32) * mask).clip(0, 255).astype(np.uint8)
    return frame


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=180, help="final duration in seconds")
    parser.add_argument("--loop-seconds", type=float, default=12, help="base seamless loop duration")
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--resolution", type=parse_resolution, default=parse_resolution("1280x720"))
    parser.add_argument("--output", type=Path, default=Path("data/outputs/oriental_future_tiger_rose_loop.mp4"))
    args = parser.parse_args()

    w, h = args.resolution
    args.output.parent.mkdir(parents=True, exist_ok=True)
    total_frames = int(args.seconds * args.fps)
    loop_frames = max(2, int(args.loop_seconds * args.fps))
    writer = cv2.VideoWriter(str(args.output), cv2.VideoWriter_fourcc(*"mp4v"), args.fps, (w, h))
    if not writer.isOpened():
        raise RuntimeError(f"failed to open writer for {args.output}")
    for i in range(total_frames):
        writer.write(render_frame(i, loop_frames, w, h))
    writer.release()
    print(args.output)


if __name__ == "__main__":
    main()
