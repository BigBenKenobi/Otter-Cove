from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PySide6.QtWidgets import QApplication
    HAS_QT = True
except ModuleNotFoundError:
    HAS_QT = False


@unittest.skipUnless(HAS_QT, "PySide6 is required for theme acceptance tests")
class ThemeQtAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if HAS_QT:
            cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        if not HAS_QT:
            return
        from core.settings import AppSettings
        from core.theme import ThemeManager

        self.tempdir = tempfile.TemporaryDirectory()
        self.path = Path(self.tempdir.name) / "settings.ini"
        self.settings = AppSettings(self.path)
        self.manager = ThemeManager(self.settings)

    def tearDown(self) -> None:
        if HAS_QT:
            self.tempdir.cleanup()

    def test_custom_overrides_round_trip_and_builtin_selection_clears_them(self) -> None:
        from core.settings import AppSettings
        from core.theme import THEMES, ThemeManager

        self.manager.customize({"accent": "#123456", "input_bg": "#112233"})
        self.settings.sync()
        restored = ThemeManager(AppSettings(self.path))
        self.assertEqual(restored.theme.accent, "#123456")
        self.assertEqual(restored.theme.input_bg, "#112233")

        restored.select("ocean")
        restored.settings.sync()
        again = ThemeManager(AppSettings(self.path))
        self.assertEqual(again.theme_key, "ocean")
        self.assertEqual(again.theme.accent, THEMES["ocean"].accent)
        self.assertEqual(again.custom_overrides, {})

    def test_named_saved_theme_restores_palette_typography_layout_and_effect_bundle(self) -> None:
        from core.settings import AppSettings
        from core.theme import ThemeManager

        self.manager.customize({"accent": "#345678"})
        self.manager.set_typography("Sans Serif", "Large")
        self.manager.set_layout("Roomy", True)
        effect = {
            "name": "Rain", "color": "#abcdef", "speed": 1.65,
            "intensity": 1.2, "quality": 1.35, "size": 0.9, "paused": True,
        }
        key = self.manager.save_current("Storm Glass", effect)
        self.assertTrue(key.startswith("custom:"))
        self.settings.sync()

        restored = ThemeManager(AppSettings(self.path))
        bundles = []
        restored.themeBundleApplied.connect(bundles.append)
        restored.select(key)
        self.assertEqual(restored.theme.accent, "#345678")
        self.assertEqual(restored.font_kind, "Sans Serif")
        self.assertEqual(restored.text_size, "Large")
        self.assertEqual(restored.density, "Roomy")
        self.assertTrue(restored.frosted)
        self.assertEqual(bundles[-1]["effect"]["name"], "Rain")
        self.assertTrue(bundles[-1]["effect"]["paused"])

    def test_duplicate_saved_theme_is_rejected_without_changing_current_theme(self) -> None:
        from core.theme_logic import ThemeBundleError

        effect = {
            "name": "Leaves", "color": self.manager.theme.accent, "speed": 1.0,
            "intensity": 1.0, "quality": 1.0, "size": 1.0, "paused": False,
        }
        self.manager.save_current("One", effect)
        before_key = self.manager.theme_key
        before_theme = self.manager.theme
        with self.assertRaises(ThemeBundleError):
            self.manager.save_current("One", effect)
        self.assertEqual(self.manager.theme_key, before_key)
        self.assertEqual(self.manager.theme, before_theme)

    def test_stylesheet_uses_live_typography_density_and_translucent_frosted_surface(self) -> None:
        self.manager.set_typography(text_size="Large")
        self.manager.set_layout("Compact", True)
        sheet = self.manager.stylesheet()
        self.assertIn("font-size: 12pt", sheet)
        self.assertIn("rgba(", sheet)
        self.assertIn("QAbstractScrollArea::viewport { background:transparent; }", sheet)


@unittest.skipUnless(HAS_QT, "PySide6 is required for theme panel acceptance tests")
class ThemePanelQtAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if HAS_QT:
            cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        if not HAS_QT:
            return
        from core.theme import THEMES
        from ui.theme_panel import ThemePanel
        self.panel = ThemePanel("forest", THEMES["forest"])
        self.panel.show()
        self.app.processEvents()

    def tearDown(self) -> None:
        if HAS_QT:
            self.panel.close()
            self.app.processEvents()

    def test_more_colors_are_real_controls_and_toggle_visibility(self) -> None:
        # Exercise the control through the same visible path a user takes.
        self.panel.custom_tab.click()
        self.app.processEvents()
        self.assertFalse(self.panel.more_colors_host.isVisible())

        self.panel.more_colors_button.click()
        self.app.processEvents()
        self.assertTrue(self.panel.more_colors_host.isVisible())
        self.assertTrue(self.panel._more_colors_expanded)
        self.assertIn("muted", self.panel.color_dots)
        self.assertIn("input_bg", self.panel.color_dots)
        self.assertIn("send_bg", self.panel.color_dots)

        self.panel.more_colors_button.click()
        self.app.processEvents()
        self.assertFalse(self.panel.more_colors_host.isVisible())
        self.assertFalse(self.panel._more_colors_expanded)

    def test_harmony_generate_is_preview_only_until_apply(self) -> None:
        changes = []
        self.panel.customChanged.connect(changes.append)
        self.panel._generate_harmony()
        self.assertEqual(changes, [])
        self.assertTrue(self.panel.harmony_apply.isEnabled())
        self.panel._apply_harmony()
        self.assertEqual(len(changes), 1)
        self.assertIn("accent", changes[0])
        self.panel._reset_harmony_preview()
        self.assertFalse(self.panel.harmony_apply.isEnabled())

    def test_solid_disables_irrelevant_animation_controls_with_explanation(self) -> None:
        self.panel.effect_combo.setCurrentText("Solid")
        self.app.processEvents()
        for widget in (
            self.panel.speed_combo, self.panel.quality_combo, self.panel.intensity_slider,
            self.panel.size_slider, self.panel.pause_animation, self.panel.effect_color,
        ):
            self.assertFalse(widget.isEnabled())
            self.assertIn("not applicable", widget.toolTip())


if __name__ == "__main__":
    unittest.main()
