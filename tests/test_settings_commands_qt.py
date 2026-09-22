"""Qt acceptance tests for live Settings and canonical keyboard commands.

The suite mounts the real shell with isolated settings/data, then verifies reuse,
live preference propagation, persistence, conflict recovery, and honest disabled
states for capabilities whose runtime consumers are not implemented.
"""

from __future__ import annotations

import json
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


@unittest.skipUnless(HAS_QT, "PySide6 is required for Settings/command acceptance tests")
class SettingsAndCommandQtAcceptanceTests(unittest.TestCase):
    """Exercise Settings-to-shell behavior through real Qt controls."""

    @classmethod
    def setUpClass(cls) -> None:
        if HAS_QT:
            cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        if not HAS_QT:
            return
        from app import MainWindow
        from core.data import AppDataServices
        from core.settings import AppSettings
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
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
        self.tmp.cleanup()

    def test_settings_route_is_real_and_reused(self) -> None:
        from ui.settings_panel import SettingsPanel
        self.window._route("settings")
        self.app.processEvents()
        first = self.window.window_manager.windows["settings"]
        self.assertIsInstance(first.content_widget(), SettingsPanel)
        self.window._route("settings")
        self.assertIs(self.window.window_manager.windows["settings"], first)

    def test_appearance_changes_update_open_chat_and_sidebar_without_losing_draft(self) -> None:
        chat = self.window.workspace.chat
        chat.set_draft_text("preserve me")
        normal_max = chat.prompt.maximumWidth()
        self.window._apply_appearance_changes({"full_width": True, "show_welcome": False, "show_web_search": False, "emoji_mode": "Minimal"})
        self.window._set_sidebar_visibility("email", False)
        self.app.processEvents()
        self.assertEqual(chat.draft_text(), "preserve me")
        self.assertGreater(chat.prompt.maximumWidth(), normal_max)
        self.assertFalse(chat.hero_title.isVisible())
        self.assertFalse(chat.prompt.search_button.isVisible())
        self.assertEqual(chat.hero_title.text(), "Otter Cove")
        self.assertFalse(self.window.sidebar.buttons["email"].isVisible())

    def test_new_chat_and_settings_commands_remain_available_when_navigation_entries_hidden(self) -> None:
        self.window._set_sidebar_visibility("new_chat", False)
        self.assertFalse(self.window.sidebar.buttons["new_chat"].isVisible())
        self.assertTrue(self.window.command_manager.actions["navigation.new_chat"].isEnabled())
        self.assertTrue(self.window.command_manager.actions["navigation.settings"].isEnabled())
        self.assertTrue(self.window.command_manager.binding("navigation.settings"))

    def test_unimplemented_appearance_capabilities_are_labelled_and_disabled(self) -> None:
        """Stored future preferences must not be presented as working features."""

        self.window._route("settings")
        self.app.processEvents()
        panel = self.window.window_manager.windows["settings"].content_widget()

        for key in ("sensitive_blur", "show_web_search", "show_shell"):
            checkbox = panel.appearance_checks[key]
            self.assertFalse(checkbox.isEnabled())
            self.assertIn("unavailable", checkbox.text().casefold())
            self.assertTrue(checkbox.toolTip())

        chat = self.window.workspace.chat
        self.assertFalse(chat.prompt.search_button.isEnabled())
        self.assertIn("unavailable", chat.prompt.search_button.toolTip().casefold())
        self.assertFalse(chat.prompt.shell_button.isEnabled())
        self.assertIn("unavailable", chat.prompt.shell_button.toolTip().casefold())
        self.assertIsNone(chat.property("sensitiveBlurEnabled"))

    def test_local_data_gui_exports_reports_errors_and_confirms_reset(self) -> None:
        """Settings must expose service operations with explicit scope and consent."""

        from PySide6.QtWidgets import QMessageBox

        session = self.data.sessions.create_session("Keep until reset")
        self.data.sessions.add_message(session.id, "user", "export me")
        self.window._route("settings")
        self.app.processEvents()
        panel = self.window.window_manager.windows["settings"].content_widget()

        self.assertEqual(panel.data_tab.text(), "Local Data")
        for button in (panel.data_export_button, panel.data_import_button, panel.data_reset_button):
            self.assertTrue(button.isEnabled())
            self.assertTrue(button.accessibleName() or button.text())

        export_path = Path(self.tmp.name) / "gui-export.json"
        with patch("app.QFileDialog.getSaveFileName", return_value=(str(export_path), "JSON")):
            self.window._export_local_data()
        self.assertTrue(export_path.exists())
        self.assertIn("Export completed", panel.data_result.text())
        self.assertIn("Excluded:", panel.data_result.text())
        self.assertIn("Nobody/incognito sessions", panel.data_result.text())

        malformed = Path(self.tmp.name) / "malformed.json"
        malformed.write_text("not json", encoding="utf-8")
        with (
            patch("app.QFileDialog.getOpenFileName", return_value=(str(malformed), "JSON")),
            patch("app.QMessageBox.question", return_value=QMessageBox.Yes),
        ):
            self.window._import_local_data()
        self.assertIn("Cannot read", panel.data_result.text())
        self.assertIsNotNone(self.data.sessions.get_persistent_session(session.id))

        nested_malformed = Path(self.tmp.name) / "nested-malformed.json"
        payload = self.data.local_data.snapshot()
        payload["content"]["sessions"][0]["metadata_json"] = "{not nested json"
        nested_malformed.write_text(json.dumps(payload), encoding="utf-8")
        with (
            patch("app.QFileDialog.getOpenFileName", return_value=(str(nested_malformed), "JSON")),
            patch("app.QMessageBox.question", return_value=QMessageBox.Yes),
        ):
            self.window._import_local_data()
        self.assertIn("nested JSON is malformed", panel.data_result.text())
        self.assertIsNotNone(self.data.sessions.get_persistent_session(session.id))

        with patch("app.QMessageBox.warning", return_value=QMessageBox.No):
            self.window._reset_local_data()
        self.assertIsNotNone(self.data.sessions.get_persistent_session(session.id))

        with patch("app.QMessageBox.warning", return_value=QMessageBox.Yes):
            self.window._reset_local_data()
        self.assertEqual(self.data.sessions.list_persistent_sessions(), [])
        self.assertIn("Reset completed", panel.data_result.text())
        self.assertIn("Excluded:", panel.data_result.text())

    def test_rebinding_persists_and_conflicts_do_not_replace_existing_binding(self) -> None:
        from core.command_registry import ShortcutConflict
        original_search = self.window.command_manager.binding("navigation.search")
        self.window.command_manager.rebind("navigation.theme", "Ctrl+Alt+T")
        self.assertEqual(self.window.command_manager.binding("navigation.theme"), "Ctrl+Alt+T")
        with self.assertRaises(ShortcutConflict):
            self.window.command_manager.rebind("navigation.theme", original_search)
        self.assertEqual(self.window.command_manager.binding("navigation.theme"), "Ctrl+Alt+T")
        self.settings.sync()

        # Closing/reopening verifies the custom binding is restored from QSettings.
        self.window.close()
        self.app.processEvents()
        from app import MainWindow
        from core.data import AppDataServices
        from core.settings import AppSettings
        root = Path(self.tmp.name)
        self.settings = AppSettings(root / "settings.ini")
        self.data = AppDataServices.open(root / "otter-cove.sqlite3")
        self.window = MainWindow(self.data, self.settings)
        self.window.show()
        self.app.processEvents()
        self.assertEqual(self.window.command_manager.binding("navigation.theme"), "Ctrl+Alt+T")

    def test_conflicting_persisted_shortcuts_recover_to_defaults_without_startup_failure(self) -> None:
        self.window.close()
        self.app.processEvents()
        self.settings.set_value(
            "shortcuts/bindings",
            json.dumps({
                "navigation.search": "Ctrl+F",
                "navigation.theme": "Ctrl+F",
            }),
        )
        self.settings.sync()

        from app import MainWindow
        from core.data import AppDataServices
        from core.settings import AppSettings
        root = Path(self.tmp.name)
        self.settings = AppSettings(root / "settings.ini")
        self.data = AppDataServices.open(root / "otter-cove.sqlite3")
        self.window = MainWindow(self.data, self.settings)
        self.window.show()
        self.app.processEvents()

        self.assertTrue(self.window.command_manager.load_warning)
        self.assertEqual(self.window.command_manager.binding("navigation.search"), "Ctrl+F")
        self.assertEqual(self.window.command_manager.binding("navigation.theme"), "Ctrl+Shift+T")

    def test_disabled_commands_surface_a_reason(self) -> None:
        favorite = self.window.command_manager.actions["session.favorite"]
        self.assertFalse(favorite.isEnabled())
        self.assertTrue(favorite.statusTip())
        self.assertIn("milestone", self.window.command_manager.tooltip("session.favorite"))


if __name__ == "__main__":
    unittest.main()
