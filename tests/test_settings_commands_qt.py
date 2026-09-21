from __future__ import annotations

import json
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


@unittest.skipUnless(HAS_QT, "PySide6 is required for Settings/command acceptance tests")
class SettingsAndCommandQtAcceptanceTests(unittest.TestCase):
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
        self.assertEqual(chat.hero_title.text(), "Stark Studio")
        self.assertFalse(self.window.sidebar.buttons["email"].isVisible())

    def test_new_chat_and_settings_commands_remain_available_when_navigation_entries_hidden(self) -> None:
        self.window._set_sidebar_visibility("new_chat", False)
        self.assertFalse(self.window.sidebar.buttons["new_chat"].isVisible())
        self.assertTrue(self.window.command_manager.actions["navigation.new_chat"].isEnabled())
        self.assertTrue(self.window.command_manager.actions["navigation.settings"].isEnabled())
        self.assertTrue(self.window.command_manager.binding("navigation.settings"))

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
        self.data = AppDataServices.open(root / "stark.sqlite3")
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
        self.data = AppDataServices.open(root / "stark.sqlite3")
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
