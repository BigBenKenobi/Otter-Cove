#!/usr/bin/env python3
"""Measure native Otter Cove background frame intervals and paint costs.

Run from the repository root in the intended Fedora desktop session. The default
rejects offscreen/minimal Qt platforms because those results cannot establish the
native animation acceptance target. ``--allow-offscreen`` exists only to validate
the measurement plumbing and labels its output supplementary.
"""

from __future__ import annotations

import argparse
import os
import platform
import statistics
import sys
import tempfile
from pathlib import Path
from time import perf_counter

from PySide6 import __version__ as pyside_version
from PySide6.QtCore import QTimer, qVersion
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from app import MainWindow
from core.data import AppDataServices
from core.settings import AppSettings


def percentile(values: list[float], percentile_value: float) -> float:
    """Return a deterministic nearest-rank percentile for collected samples."""

    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, round((len(ordered) - 1) * percentile_value)))
    return ordered[index]


def parse_args() -> argparse.Namespace:
    """Parse effect, duration, and supplementary-run options."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--effect", default="Leaves")
    parser.add_argument("--duration", type=float, default=60.0)
    parser.add_argument("--allow-offscreen", action="store_true")
    return parser.parse_args()


def main() -> int:
    """Run one isolated window and print reproducible frame statistics."""

    args = parse_args()
    if args.duration <= 0:
        raise ValueError("--duration must be positive")
    app = QApplication.instance() or QApplication([])
    app.setQuitOnLastWindowClosed(False)
    qt_platform = QGuiApplication.platformName()
    supplementary = qt_platform in {"offscreen", "minimal"}
    if supplementary and not args.allow_offscreen:
        print(
            f"Refusing Qt platform {qt_platform!r}; run in native Fedora Wayland/X11 "
            "or pass --allow-offscreen only to validate plumbing.",
            file=sys.stderr,
        )
        return 2

    intervals_ms: list[float] = []
    paint_ms: list[float] = []
    last_frame: float | None = None

    with tempfile.TemporaryDirectory(prefix="otter-cove-animation-measure-") as tmp:
        root = Path(tmp)
        window = MainWindow(
            AppDataServices.open(root / "otter-cove.sqlite3"),
            AppSettings(root / "settings.ini"),
        )
        window.resize(1720, 900)
        window.show()
        window.set_effect(args.effect)
        window.apply_effect_settings({"quality": 1.0, "paused": False})
        if supplementary:
            window.workspace.background.set_effect_suspended(False)

        def record_frame(elapsed_ms: float) -> None:
            """Record paint cost and wall interval after warm-up begins."""

            nonlocal last_frame
            now = perf_counter()
            if last_frame is not None:
                intervals_ms.append((now - last_frame) * 1000.0)
            last_frame = now
            paint_ms.append(float(elapsed_ms))

        window.workspace.background.framePainted.connect(record_frame)
        QTimer.singleShot(round(args.duration * 1000), app.quit)
        started = perf_counter()
        app.exec()
        elapsed = perf_counter() - started
        window.close()

    if not intervals_ms or not paint_ms:
        print("No animated frames were recorded; ensure the app is visible and active.", file=sys.stderr)
        return 3

    fps = len(intervals_ms) / elapsed
    scope = "SUPPLEMENTARY/OFFSCREEN" if supplementary else "NATIVE"
    print(f"Scope: {scope}")
    print(f"OS: {platform.platform()}")
    print(f"Desktop: {os.environ.get('XDG_CURRENT_DESKTOP', 'unknown')}")
    print(f"Session: {os.environ.get('XDG_SESSION_TYPE', 'unknown')}")
    print(f"Qt platform: {qt_platform}")
    print(f"Python: {platform.python_version()}  PySide6: {pyside_version}  Qt: {qVersion()}")
    print(f"Effect: {args.effect}  quality: Balanced (1.0)  size: 1720x900")
    print(f"Duration: {elapsed:.2f}s  frames: {len(paint_ms)}  observed FPS: {fps:.2f}")
    print(
        "Frame interval ms: "
        f"median={statistics.median(intervals_ms):.2f} "
        f"p95={percentile(intervals_ms, 0.95):.2f} max={max(intervals_ms):.2f}"
    )
    print(
        "Paint cost ms: "
        f"median={statistics.median(paint_ms):.2f} "
        f"p95={percentile(paint_ms, 0.95):.2f} max={max(paint_ms):.2f}"
    )
    passed = fps >= 55.0 and percentile(intervals_ms, 0.95) <= 33.0
    print(f"Target (about 60 FPS, p95 interval <=33ms): {'PASS' if passed else 'REVIEW'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
