from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PySide6.QtWidgets import QApplication
    HAS_QT = True
except ModuleNotFoundError:
    HAS_QT = False


@unittest.skipUnless(HAS_QT, "PySide6 is required for effect acceptance tests")
class EffectQtAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if HAS_QT:
            cls.app = QApplication.instance() or QApplication([])

    def test_solid_never_runs_timer_and_animated_effect_does(self) -> None:
        from effects.manager import BackgroundEffectManager
        manager = BackgroundEffectManager()
        manager.set_effect("Solid")
        self.assertFalse(manager.animated)
        self.assertFalse(manager.timer_active)
        manager.set_effect("Leaves")
        self.assertTrue(manager.animated)
        self.assertTrue(manager.timer_active)

    def test_suspend_is_independent_from_user_pause(self) -> None:
        from effects.manager import BackgroundEffectManager
        manager = BackgroundEffectManager()
        manager.set_effect("Rain")
        manager.set_paused(True)
        self.assertTrue(manager.paused)
        self.assertFalse(manager.timer_active)
        manager.set_suspended(True)
        manager.set_suspended(False)
        self.assertTrue(manager.paused)
        self.assertFalse(manager.timer_active)
        manager.set_paused(False)
        self.assertTrue(manager.timer_active)
        manager.set_suspended(True)
        self.assertFalse(manager.timer_active)
        manager.set_suspended(False)
        self.assertTrue(manager.timer_active)

    def test_all_effects_switch_repeatedly_without_losing_registered_names(self) -> None:
        from effects.manager import BackgroundEffectManager
        manager = BackgroundEffectManager()
        expected = {"Solid", "Dots", "Synapse", "Rain", "Constellations", "Perlin Flow", "Petals", "Sparkles", "Embers", "Leaves"}
        self.assertEqual(set(manager.available_effects), expected)
        for _ in range(3):
            for name in manager.available_effects:
                manager.set_effect(name)
                manager.resize(900, 600)
                manager.set_speed(1.1)
                manager.set_intensity(0.9)
                manager.set_quality(1.0)
                manager.set_size(1.05)
                self.assertEqual(manager.effect_name, name)

    def test_canvas_visibility_and_external_suspension_do_not_clobber_each_other(self) -> None:
        from core.theme import THEMES
        from ui.background import BackgroundCanvas
        canvas = BackgroundCanvas(THEMES["forest"])
        canvas.resize(600, 400)
        canvas.show()
        self.app.processEvents()
        canvas.set_effect("Leaves")
        canvas.set_effect_suspended(True)
        self.assertTrue(canvas.effects.suspended)
        canvas.hide()
        canvas.show()
        self.app.processEvents()
        self.assertTrue(canvas.effects.suspended)
        canvas.set_effect_suspended(False)
        self.assertFalse(canvas.effects.suspended)
        canvas.close()


if __name__ == "__main__":
    unittest.main()
