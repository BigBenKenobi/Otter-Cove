from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PySide6.QtCore import QPoint
    from PySide6.QtWidgets import QApplication
    HAS_QT = True
except ModuleNotFoundError:
    HAS_QT = False


@unittest.skipUnless(HAS_QT, "PySide6 is required for shell acceptance tests")
class ShellQtAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not HAS_QT:
            return
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        if not HAS_QT:
            return
        from app import MainWindow
        from core.data import AppDataServices
        from core.settings import AppSettings

        self.tempdir = tempfile.TemporaryDirectory()
        root = Path(self.tempdir.name)
        self.settings = AppSettings(root / "settings.ini")
        self.data = AppDataServices.open(root / "stark.sqlite3")
        self.window = MainWindow(self.data, self.settings)
        self.window.show()
        self.app.processEvents()

    def tearDown(self) -> None:
        if not HAS_QT:
            return
        if self.window.isVisible():
            self.window.close()
        self.app.processEvents()
        self.tempdir.cleanup()

    def test_opening_tool_preserves_session_and_composer_draft(self) -> None:
        chat = self.window.workspace.chat
        chat.set_draft_text("unfinished draft that must survive tool routing")
        session_before = chat.session_id
        self.window._route("email")
        self.app.processEvents()
        self.assertEqual(chat.draft_text(), "unfinished draft that must survive tool routing")
        self.assertEqual(chat.session_id, session_before)
        self.assertIn("email", self.window.window_manager.windows)
        self.assertTrue(self.window.window_manager.windows["email"].isVisible())

    def test_every_registered_route_resolves_to_command_or_window(self) -> None:
        for spec in self.window.route_registry:
            if spec.key == "new_chat":
                self.window._route(spec.key)
                self.assertEqual(self.window.shell_state.active_route, "new_chat")
                continue
            self.window._route(spec.key)
            self.app.processEvents()
            self.assertIn(spec.key, self.window.window_manager.windows)
            window = self.window.window_manager.windows[spec.key]
            self.assertTrue(window.isVisible(), spec.key)

    def test_minimum_and_reference_sizes_keep_primary_controls_reachable(self) -> None:
        for width, height in ((1100, 680), (1920, 1080)):
            self.window.resize(width, height)
            self.app.processEvents()
            self.assertTrue(self.window.sidebar.isVisible())
            self.assertTrue(self.window.sidebar.settings_button.isVisible())
            prompt = self.window.workspace.chat.prompt
            top_left = prompt.mapTo(self.window.workspace, QPoint(0, 0))
            self.assertGreaterEqual(top_left.x(), 0)
            self.assertGreaterEqual(top_left.y(), 0)
            self.assertLessEqual(top_left.x() + prompt.width(), self.window.workspace.width())
            self.assertLessEqual(top_left.y() + prompt.height(), self.window.workspace.height())
            self.assertTrue(prompt.send_button.isVisible())

    def test_saved_preferences_restore_sidebar_and_geometry(self) -> None:
        # This validates the shell with non-default preferences in an isolated INI.
        self.window.sidebar.set_collapsed(True, animate=False)
        self.window.resize(1280, 760)
        self.settings.set_main_geometry(self.window.saveGeometry())
        self.settings.set_value("appearance/sidebar_collapsed", True)
        self.settings.sync()

        # Close data exactly once through the normal window lifecycle, then reopen.
        self.window.close()
        self.app.processEvents()

        from app import MainWindow
        from core.data import AppDataServices
        from core.settings import AppSettings

        root = Path(self.tempdir.name)
        self.settings = AppSettings(root / "settings.ini")
        self.data = AppDataServices.open(root / "stark.sqlite3")
        self.window = MainWindow(self.data, self.settings)
        self.window.show()
        self.app.processEvents()
        self.assertTrue(self.window.sidebar.is_collapsed())
        self.assertGreaterEqual(self.window.width(), 1100)
        self.assertGreaterEqual(self.window.height(), 680)


if __name__ == "__main__":
    unittest.main()
