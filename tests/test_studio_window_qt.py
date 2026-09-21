from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PySide6.QtCore import QPoint, QRect, Qt
    from PySide6.QtWidgets import QApplication, QLineEdit, QWidget
    HAS_QT = True
except ModuleNotFoundError:
    HAS_QT = False


@unittest.skipUnless(HAS_QT, "PySide6 is required for StudioWindow acceptance tests")
class StudioWindowQtAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if HAS_QT:
            cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        if not HAS_QT:
            return
        from core.settings import AppSettings
        from ui.studio_window import StudioWindowManager

        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.settings = AppSettings(self.root / "settings.ini")
        self.host = QWidget()
        self.host.resize(1000, 700)
        self.host.show()
        self.manager = StudioWindowManager(self.host, self.settings)
        self.app.processEvents()

    def tearDown(self) -> None:
        if HAS_QT:
            self.host.close()
            self.app.processEvents()
            self.tempdir.cleanup()

    def _open_editor(self, key: str = "notes", rect: QRect | None = None):
        return self.manager.open_window(
            key,
            key.title(),
            lambda: QLineEdit(),
            default_rect=rect or QRect(80, 70, 520, 390),
        )

    def test_reopening_existing_or_minimized_tool_reuses_and_restores_it(self) -> None:
        window = self._open_editor()
        content = window.content_widget()
        self.assertIsInstance(content, QLineEdit)
        content.setText("local state survives close/reopen")

        window.set_minimized(True)
        self.assertTrue(window.is_minimized())
        reopened = self._open_editor()
        self.app.processEvents()
        self.assertIs(reopened, window)
        self.assertFalse(reopened.is_minimized())
        self.assertTrue(reopened.isVisible())
        self.assertEqual(reopened.content_widget().text(), "local state survives close/reopen")

        self.manager.hide_window("notes")
        self.assertFalse(window.isVisible())
        reopened_again = self._open_editor()
        self.assertIs(reopened_again, window)
        self.assertEqual(reopened_again.content_widget().text(), "local state survives close/reopen")

    def test_drag_resize_raise_and_host_recovery_keep_controls_reachable(self) -> None:
        first = self._open_editor("first", QRect(100, 100, 540, 410))
        second = self._open_editor("second", QRect(130, 130, 540, 410))
        self.app.processEvents()

        # Reopening an already-visible tool raises it above an overlapping peer.
        self._open_editor("first", QRect(100, 100, 540, 410))
        self.app.processEvents()
        probe = first.geometry().intersected(second.geometry()).center()
        child = self.host.childAt(probe)
        self.assertTrue(child is first or first.isAncestorOf(child))

        # Bounded movement plus explicit drag-end commit uses the same owner path
        # as StudioTitleBar.mouseReleaseEvent; exact pointer dragging is retained
        # as a native Fedora smoke check rather than relying on QTest mouse state.
        start_pos = first.pos()
        first.move_bounded(start_pos + QPoint(45, 30))
        first.commit_geometry()
        self.assertNotEqual(first.pos(), start_pos)

        # Resize + explicit commit represents resize-handle release. The grip itself
        # is checked for reachability below after host recovery.
        before = first.size()
        first.resize(before.width() + 70, before.height() + 45)
        first.commit_geometry()
        self.assertGreater(first.width(), before.width())
        self.assertGreater(first.height(), before.height())

        first.set_minimized(True)
        self.assertFalse(first.body.isVisible())
        first.set_minimized(False)
        self.assertTrue(first.body.isVisible())

        self.host.resize(650, 470)
        self.manager.keep_in_bounds()
        self.app.processEvents()
        for window in (first, second):
            self.assertGreaterEqual(window.x(), 8)
            self.assertGreaterEqual(window.y(), 8)
            self.assertLessEqual(window.x() + window.width(), self.host.width() - 8)
            self.assertLessEqual(window.y() + window.height(), self.host.height() - 8)
            self.assertTrue(window.titlebar.isVisible())
            self.assertTrue(window.grip.isVisible())
            self.assertLess(window.grip.x(), window.width())
            self.assertLess(window.grip.y(), window.height())

    def test_normal_and_minimized_geometry_are_persisted_separately(self) -> None:
        window = self._open_editor("theme", QRect(140, 90, 610, 500))
        window.setGeometry(140, 90, 610, 500)
        window.commit_geometry()
        window.set_minimized(True)
        minimized_height = window.height()
        window.move_bounded(QPoint(230, 155))
        window.commit_geometry()
        self.settings.sync()

        normal = self.settings.window_normal_rect("theme", QRect())
        minimized = self.settings.window_minimized_rect("theme", QRect())
        self.assertEqual(normal.width(), 610)
        self.assertEqual(normal.height(), 500)
        self.assertEqual(normal.topLeft(), QPoint(230, 155))
        self.assertEqual(minimized.height(), minimized_height)
        self.assertLess(minimized.height(), normal.height())

        # A fresh manager uses the full-size record, then clips it safely to a
        # smaller host instead of restoring the collapsed bar geometry.
        from core.settings import AppSettings
        from ui.studio_window import StudioWindowManager

        new_settings = AppSettings(self.root / "settings.ini")
        small_host = QWidget()
        small_host.resize(520, 380)
        small_host.show()
        manager = StudioWindowManager(small_host, new_settings)
        restored = manager.open_window("theme", "Theme", lambda: QLineEdit(), default_rect=QRect(20, 20, 400, 300))
        self.app.processEvents()
        self.assertFalse(restored.is_minimized())
        self.assertGreater(restored.height(), minimized.height())
        self.assertLessEqual(restored.x() + restored.width(), small_host.width() - 8)
        self.assertLessEqual(restored.y() + restored.height(), small_host.height() - 8)
        small_host.close()

    def test_close_cycles_do_not_duplicate_windows_or_content(self) -> None:
        first = self._open_editor("email")
        content = first.content_widget()
        for _ in range(12):
            self.manager.hide_window("email")
            reopened = self._open_editor("email")
            self.assertIs(reopened, first)
            self.assertIs(reopened.content_widget(), content)

        from ui.studio_window import StudioWindow

        direct_windows = [child for child in self.host.children() if isinstance(child, StudioWindow)]
        self.assertEqual(len(direct_windows), 1)
        self.assertEqual(list(self.manager.windows), ["email"])


if __name__ == "__main__":
    unittest.main()
