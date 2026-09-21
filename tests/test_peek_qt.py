from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PySide6.QtCore import QRect
    from PySide6.QtWidgets import QApplication, QLabel, QWidget
    HAS_QT = True
except ModuleNotFoundError:
    HAS_QT = False


@unittest.skipUnless(HAS_QT, "PySide6 is required for Peek acceptance tests")
class PeekQtAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if HAS_QT:
            cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        if not HAS_QT:
            return
        from core.settings import AppSettings
        from ui.studio_window import StudioWindowManager
        self.tmp = tempfile.TemporaryDirectory()
        self.host = QWidget()
        self.host.resize(900, 650)
        self.host.show()
        self.manager = StudioWindowManager(self.host, AppSettings(Path(self.tmp.name) / "settings.ini"))
        self.window = self.manager.open_window("theme", "Theme", lambda: QLabel("content"), default_rect=QRect(50, 50, 500, 400))
        self.app.processEvents()

    def tearDown(self) -> None:
        if HAS_QT:
            self.host.close()
            self.app.processEvents()
            self.tmp.cleanup()

    def test_peek_fades_only_body_and_restores_exact_opacity(self) -> None:
        self.window.set_peeked(True)
        effect = self.window.body.graphicsEffect()
        self.assertAlmostEqual(effect.opacity(), 0.18, places=2)
        self.assertTrue(self.window.titlebar.isVisible())
        self.assertTrue(self.window.titlebar.peek_button.isEnabled())
        self.window.set_peeked(False)
        self.assertAlmostEqual(effect.opacity(), 1.0, places=2)

    def test_peek_survives_minimize_restore_close_reopen_and_style_change(self) -> None:
        self.window.set_peeked(True)
        self.window.set_minimized(True)
        self.window.set_minimized(False)
        self.assertTrue(self.window.is_peeked())
        self.assertAlmostEqual(self.window.body.graphicsEffect().opacity(), 0.18, places=2)
        self.window.setStyleSheet("#StudioWindow { background: #123456; }")
        self.assertAlmostEqual(self.window.body.graphicsEffect().opacity(), 0.18, places=2)
        self.manager.hide_window("theme")
        reopened = self.manager.open_window("theme", "Theme", lambda: QLabel("new"), default_rect=QRect(50, 50, 500, 400))
        self.assertIs(reopened, self.window)
        self.assertTrue(reopened.is_peeked())
        self.assertAlmostEqual(reopened.body.graphicsEffect().opacity(), 0.18, places=2)


if __name__ == "__main__":
    unittest.main()
