from __future__ import annotations

import json
import unittest

from core.appearance import AppearancePreferences, DEFAULTS
from core.command_registry import CommandBindings, DEFAULT_COMMANDS, ShortcutConflict


class FakeSettings:
    def __init__(self):
        self.values = {}
    def value(self, key, default=None):
        return self.values.get(key, default)
    def set_value(self, key, value):
        self.values[key] = value


class AppearancePreferencesTests(unittest.TestCase):
    def setUp(self):
        self.settings = FakeSettings()
        self.prefs = AppearancePreferences(self.settings, ("new_chat", "search", "email"))

    def test_documented_defaults_are_explicit(self):
        snapshot = self.prefs.snapshot()
        self.assertEqual(snapshot["full_width"], DEFAULTS.full_width)
        self.assertEqual(snapshot["show_welcome"], DEFAULTS.show_welcome)
        self.assertEqual(snapshot["show_nobody"], DEFAULTS.show_nobody)
        self.assertEqual(snapshot["emoji_mode"], "Native")
        self.assertTrue(all(snapshot["sidebar_visible"].values()))

    def test_changes_and_sidebar_visibility_round_trip(self):
        self.prefs.set("full_width", True)
        self.prefs.set("emoji_mode", "Minimal")
        self.prefs.set_sidebar_visible("email", False)
        restored = AppearancePreferences(self.settings, ("new_chat", "search", "email"))
        self.assertTrue(restored.get("full_width"))
        self.assertEqual(restored.get("emoji_mode"), "Minimal")
        self.assertFalse(restored.get("sidebar_visible")["email"])

    def test_reset_restores_all_defaults(self):
        self.prefs.set("show_welcome", False)
        self.prefs.set_sidebar_visible("search", False)
        self.prefs.reset()
        snapshot = self.prefs.snapshot()
        self.assertTrue(snapshot["show_welcome"])
        self.assertTrue(snapshot["sidebar_visible"]["search"])

    def test_invalid_emoji_mode_is_rejected(self):
        with self.assertRaises(ValueError):
            self.prefs.set("emoji_mode", "Anything")


class CommandBindingsTests(unittest.TestCase):
    def test_default_command_ids_and_bindings_are_unique(self):
        bindings = CommandBindings()
        self.assertEqual(len(bindings.specs), len(DEFAULT_COMMANDS))
        used = [value.casefold() for value in bindings.all_bindings().values() if value]
        self.assertEqual(len(used), len(set(used)))

    def test_rebind_detects_same_scope_conflict(self):
        bindings = CommandBindings()
        with self.assertRaises(ShortcutConflict):
            bindings.rebind("navigation.theme", bindings.binding("navigation.search"))
        self.assertEqual(bindings.binding("navigation.theme"), "Ctrl+Shift+T")

    def test_clear_and_reset_are_deterministic(self):
        bindings = CommandBindings()
        bindings.clear("navigation.theme")
        self.assertEqual(bindings.binding("navigation.theme"), "")
        bindings.reset("navigation.theme")
        self.assertEqual(bindings.binding("navigation.theme"), "Ctrl+Shift+T")

    def test_custom_bindings_restore(self):
        bindings = CommandBindings(custom={"navigation.theme": "Ctrl+Alt+T"})
        self.assertEqual(bindings.binding("navigation.theme"), "Ctrl+Alt+T")

    def test_disabled_commands_explain_why(self):
        specs = {spec.command_id: spec for spec in DEFAULT_COMMANDS}
        self.assertFalse(specs["session.favorite"].enabled)
        self.assertTrue(specs["session.favorite"].disabled_reason)
        self.assertFalse(specs["session.delete"].enabled)
        self.assertTrue(specs["session.delete"].disabled_reason)


if __name__ == "__main__":
    unittest.main()
