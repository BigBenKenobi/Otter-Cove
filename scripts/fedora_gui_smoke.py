#!/usr/bin/env python3
"""Deterministic native Qt smoke pass for the deferred Phase A batch.

Uses isolated temporary SQLite/QSettings storage and does not modify the user's
normal Otter Cove profile. Run from the project root on Fedora/Wayland.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

if "--offscreen" in sys.argv:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from app import MainWindow
from core.data import AppDataServices
from core.settings import AppSettings
from core.theme import THEMES


def pump(app: QApplication, count: int = 4) -> None:
    for _ in range(count):
        app.processEvents()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    app = QApplication.instance() or QApplication([])
    app.setQuitOnLastWindowClosed(False)

    with tempfile.TemporaryDirectory(prefix="otter-cove-phase-a-smoke-") as tmp:
        root = Path(tmp)
        settings_path = root / "settings.ini"
        db_path = root / "otter-cove.sqlite3"
        settings = AppSettings(settings_path)
        data = AppDataServices.open(db_path)
        window = MainWindow(data, settings)
        window.resize(1280, 760)
        window.show()
        pump(app)

        # Shell/draft preservation while tools are opened and reused.
        chat = window.workspace.chat
        chat.set_draft_text("phase-a-smoke-draft")
        window._route("theme")
        window._route("settings")
        window._route("email")
        pump(app)
        require(chat.draft_text() == "phase-a-smoke-draft", "Opening tools lost the composer draft")
        require(len(window.window_manager.windows) == 3, "Unexpected tool-window count")

        theme_window = window.window_manager.windows["theme"]
        same_theme = window.window_manager.open_window(
            "theme", "Theme", lambda: (_ for _ in ()).throw(RuntimeError("factory should not rerun"))
        )
        require(theme_window is same_theme, "Opening an existing tool created a duplicate")
        theme_window.set_minimized(True)
        require(theme_window.is_minimized(), "Theme tool did not minimize")
        window._route("theme")
        pump(app)
        require(not theme_window.is_minimized(), "Opening a minimized tool did not restore it")

        # Peek is visual-only and must survive ordinary lifecycle/style activity.
        theme_window.set_peeked(True)
        require(theme_window.is_peeked(), "Peek did not enable")
        theme_window.set_minimized(True)
        theme_window.set_minimized(False)
        require(theme_window.is_peeked(), "Peek was lost across minimize/restore")

        # Every built-in theme must be selectable while tools are already open.
        for key in THEMES:
            window._select_theme(key)
            pump(app, 1)
            require(window.theme_manager.theme_key == key, f"Theme {key} did not select")
        window._select_theme("forest")
        pump(app)

        # Live appearance changes must not mutate draft/session state.
        window._apply_appearance_changes({
            "full_width": True,
            "show_welcome": False,
            "show_web_search": False,
            "show_shell": False,
        })
        pump(app)
        require(chat.draft_text() == "phase-a-smoke-draft", "Appearance changes lost the draft")
        window._reset_appearance()
        pump(app)

        # All effects can be switched repeatedly. Solid must not animate.
        for effect in window.workspace.background.available_effects():
            window.set_effect(effect)
            pump(app, 2)
            manager = window.workspace.background.effects
            require(manager.effect_name == effect, f"Effect {effect} did not activate")
            if effect == "Solid":
                require(not manager.timer_active, "Solid incorrectly left animation timer running")
        window.set_effect("Leaves")
        window.apply_effect_settings({
            "color": "#67cf92",
            "speed": 1.1,
            "intensity": 0.9,
            "quality": 1.0,
            "size": 1.05,
            "paused": True,
        })
        manager = window.workspace.background.effects
        require(manager.paused, "User Pause did not apply")
        window.workspace.background.set_effect_suspended(True)
        require(manager.suspended and manager.paused, "Suspension overwrote user Pause")
        window.workspace.background.set_effect_suspended(False)
        require(not manager.suspended and manager.paused, "Restoring suspension overwrote user Pause")
        window.apply_effect_settings({"paused": False})

        # Host shrink must retain reachable tool geometry.
        window.resize(1100, 680)
        pump(app)
        window.window_manager.keep_in_bounds()
        for key, tool in window.window_manager.windows.items():
            if not tool.isVisible():
                continue
            require(tool.x() >= 0 and tool.y() >= 0, f"{key} tool moved outside host origin")
            require(tool.x() + tool.width() <= window.workspace.width() + 1, f"{key} tool exceeds host width")
            require(tool.y() + tool.height() <= window.workspace.height() + 1, f"{key} tool exceeds host height")

        # Persist the chosen theme/geometry, then reconstruct from the same isolated profile.
        theme_window.set_peeked(False)
        window.theme_manager.select("midnight")
        window.window_manager.save_all()
        settings.set_main_geometry(window.saveGeometry())
        settings.sync()
        window.close()
        pump(app)

        settings2 = AppSettings(settings_path)
        data2 = AppDataServices.open(db_path)
        restored = MainWindow(data2, settings2)
        restored.show()
        pump(app)
        require(restored.theme_manager.theme_key == "midnight", "Selected theme did not round-trip")
        restored.close()
        pump(app)

    print("Phase A native GUI smoke: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Phase A native GUI smoke: FAIL: {exc}", file=sys.stderr)
        raise
