"""Qt acceptance coverage for shell routing, layout, and composer integrity.

The tests construct the real ``MainWindow`` with isolated settings and SQLite
storage.  They exercise presentation-to-service boundaries offscreen so routing,
geometry, draft retention, and successful persistence remain regression-tested
without touching a user's desktop profile.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PySide6.QtCore import QPoint
    from PySide6.QtWidgets import QApplication
    HAS_QT = True
except ModuleNotFoundError:
    HAS_QT = False


@unittest.skipUnless(HAS_QT, "PySide6 is required for shell acceptance tests")
class ShellQtAcceptanceTests(unittest.TestCase):
    """Exercise shell behavior through real widgets and isolated local services."""

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
        self.data = AppDataServices.open(root / "otter-cove.sqlite3")
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

    def test_failed_send_preserves_complete_draft_and_retry_adds_one_message(self) -> None:
        """A transient storage failure must leave one safe, lossless retry."""

        from core.data import DataStoreUnavailableError

        chat = self.window.workspace.chat
        draft = "  first line\nsecond line with spacing  "
        chat.set_draft_text(draft)
        chat.prompt.chat_button.setChecked(True)

        # Session creation is allowed to complete, then message persistence is
        # failed at the service boundary to reproduce the reported data-loss path.
        with patch.object(
            chat.sessions,
            "add_message",
            side_effect=DataStoreUnavailableError("injected message-store failure"),
        ):
            chat.prompt.submit()
        self.app.processEvents()

        self.assertEqual(chat.draft_text(), draft)
        self.assertEqual(chat.prompt.mode(), "Chat")
        self.assertIsNotNone(chat.session_id)
        self.assertEqual(chat.sessions.messages(chat.session_id), [])

        # Retrying the same retained draft uses the already-created session.  A
        # successful acceptance clears once and yields one durable/UI message.
        chat.prompt.submit()
        self.app.processEvents()

        self.assertEqual(chat.draft_text(), "")
        messages = chat.sessions.messages(chat.session_id)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].content, draft.strip())
        self.assertEqual(messages[0].metadata["mode"], "Chat")
        self.assertEqual(chat.message_layout.count(), 2)  # one message plus stretch

    def test_normal_and_nobody_views_keep_messages_status_and_drafts_isolated(self) -> None:
        """Privacy-mode switches restore only state owned by the selected view."""

        chat = self.window.workspace.chat
        chat.set_draft_text("normal message")
        chat.prompt.submit()
        normal_id = chat.session_id
        chat.set_draft_text("normal unsent draft")

        chat.nobody.setChecked(True)
        self.app.processEvents()
        self.assertIsNone(chat.session_id)
        self.assertEqual(chat.draft_text(), "")
        self.assertIn("memory only", chat.status_summary.text())
        self.assertEqual(chat.message_layout.count(), 1)

        chat.set_draft_text("private message")
        chat.prompt.submit()
        private_id = chat.session_id
        chat.set_draft_text("private unsent draft")
        self.assertTrue(chat.sessions.is_incognito(private_id))
        self.assertEqual(chat.message_layout.count(), 2)

        chat.nobody.setChecked(False)
        self.app.processEvents()
        self.assertEqual(chat.session_id, normal_id)
        self.assertEqual(chat.draft_text(), "normal unsent draft")
        self.assertIn("persistent storage", chat.status_summary.text())
        self.assertEqual(chat.message_layout.count(), 2)
        self.assertIn("normal message", chat.message_layout.itemAt(0).widget().text())

        chat.nobody.setChecked(True)
        self.app.processEvents()
        self.assertEqual(chat.session_id, private_id)
        self.assertEqual(chat.draft_text(), "private unsent draft")
        self.assertEqual(chat.message_layout.count(), 2)
        self.assertIn("private message", chat.message_layout.itemAt(0).widget().text())

    def test_new_chat_disposes_private_session_and_clears_pending_draft(self) -> None:
        """New Chat explicitly closes Nobody state and starts with an empty draft."""

        chat = self.window.workspace.chat
        chat.nobody.setChecked(True)
        chat.set_draft_text("private message")
        chat.prompt.submit()
        private_id = chat.session_id
        chat.set_draft_text("private unsent draft")

        self.window._route("new_chat")
        self.app.processEvents()

        self.assertFalse(chat.sessions.is_incognito(private_id))
        self.assertIsNone(chat.session_id)
        self.assertFalse(chat.nobody.isChecked())
        self.assertEqual(chat.draft_text(), "")
        self.assertEqual(chat.prompt.mode(), "Agent")
        self.assertEqual(chat.message_layout.count(), 1)
        self.assertIn("persistent storage", chat.status_summary.text())

    def test_large_roomy_nobody_control_expands_to_its_label(self) -> None:
        """Large typography must grow the Nobody button instead of clipping it."""

        self.window.resize(1100, 680)
        self.window.theme_manager.set_typography("Sans Serif", "Large")
        self.window.theme_manager.set_layout("Roomy", self.window.theme_manager.frosted)
        self.app.processEvents()

        nobody = self.window.workspace.chat.nobody
        self.assertGreaterEqual(nobody.width(), nobody.sizeHint().width())
        self.assertGreater(nobody.width(), 82)

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
        self.data = AppDataServices.open(root / "otter-cove.sqlite3")
        self.window = MainWindow(self.data, self.settings)
        self.window.show()
        self.app.processEvents()
        self.assertTrue(self.window.sidebar.is_collapsed())
        self.assertGreaterEqual(self.window.width(), 1100)
        self.assertGreaterEqual(self.window.height(), 680)


if __name__ == "__main__":
    unittest.main()
