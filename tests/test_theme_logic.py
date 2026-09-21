from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from core.theme_logic import (
    THEME_BUNDLE_VERSION,
    ThemeBundleError,
    generate_harmony,
    harmony_to_theme_changes,
    load_theme_bundle,
    make_theme_bundle,
    save_theme_bundle_atomic,
    validate_theme_bundle,
)


PALETTE = {
    "background": "#102018",
    "panel": "#18251f",
    "sidebar": "#0d1712",
    "border": "#315744",
    "text": "#d9f4e4",
    "muted": "#759786",
    "accent": "#67cf92",
    "input_bg": "#17231d",
    "send_bg": "#315d43",
}

EFFECT = {
    "name": "Leaves",
    "color": "#67cf92",
    "speed": 1.0,
    "intensity": 1.0,
    "quality": 1.0,
    "size": 1.0,
    "paused": False,
}


class ThemeLogicTests(unittest.TestCase):
    def test_all_harmony_modes_are_deterministic_and_keep_exact_accent(self):
        for harmony in ("Complementary", "Analogous", "Triadic", "Split Complementary"):
            for appearance in ("Light", "Dark"):
                first = generate_harmony("#67CF92", harmony, appearance)
                second = generate_harmony("#67cf92", harmony, appearance)
                self.assertEqual(first, second)
                self.assertEqual(first[2], "#67cf92")
                self.assertEqual(len(first), 5)

    def test_neutral_harmony_is_valid_and_deterministic(self):
        palette = generate_harmony("#777777", "Triadic", "Dark")
        self.assertEqual(palette[2], "#777777")
        for color in palette:
            self.assertRegex(color, r"^#[0-9a-f]{6}$")

    def test_harmony_apply_mapping_has_all_semantic_tokens(self):
        palette = generate_harmony("#4488cc", "Analogous", "Light")
        changes = harmony_to_theme_changes(palette, "Light")
        self.assertEqual(changes["accent"], "#4488cc")
        self.assertEqual(
            set(changes),
            {"background", "panel", "sidebar", "border", "text", "muted", "accent", "input_bg", "send_bg"},
        )

    def test_bundle_round_trip_is_versioned_and_preserves_fields(self):
        bundle = make_theme_bundle(
            "Remote Batch",
            PALETTE,
            font="Monospace",
            text_size="Large",
            density="Roomy",
            frosted=True,
            effect=EFFECT,
        )
        self.assertEqual(bundle["version"], THEME_BUNDLE_VERSION)
        self.assertEqual(bundle["typography"]["density"], "Roomy")
        self.assertTrue(bundle["typography"]["frosted"])
        self.assertEqual(bundle["effect"]["name"], "Leaves")

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "theme.starktheme.json"
            save_theme_bundle_atomic(path, bundle)
            loaded = load_theme_bundle(path)
        self.assertEqual(loaded, bundle)

    def test_invalid_color_does_not_validate(self):
        raw = make_theme_bundle(
            "Valid",
            PALETTE,
            font="Monospace",
            text_size="Default",
            density="Comfortable",
            frosted=False,
            effect=EFFECT,
        )
        raw["palette"]["accent"] = "green"
        with self.assertRaises(ThemeBundleError):
            validate_theme_bundle(raw)

    def test_unsupported_version_is_rejected(self):
        raw = {
            "version": 999,
            "name": "Nope",
            "palette": PALETTE,
            "typography": {"font": "Monospace", "text_size": "Default", "density": "Comfortable", "frosted": False},
            "effect": EFFECT,
        }
        with self.assertRaises(ThemeBundleError):
            validate_theme_bundle(raw)

    def test_invalid_json_never_overwrites_existing_file(self):
        bundle = make_theme_bundle(
            "Atomic",
            PALETTE,
            font="Monospace",
            text_size="Default",
            density="Comfortable",
            frosted=False,
            effect=EFFECT,
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "theme.json"
            path.write_text("sentinel", encoding="utf-8")
            bad = dict(bundle)
            bad["palette"] = dict(PALETTE, accent="invalid")
            with self.assertRaises(ThemeBundleError):
                save_theme_bundle_atomic(path, bad)
            self.assertEqual(path.read_text(encoding="utf-8"), "sentinel")


if __name__ == "__main__":
    unittest.main()
