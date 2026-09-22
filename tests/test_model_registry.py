"""Behavioral tests for model configuration and capability-default resolution.

The fixtures use isolated SQLite and QSettings files. They verify validation,
editing/removal, compatibility filtering, restart persistence and stale-reference
handling without contacting Ollama or any external provider.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.data import AppDataServices, DataValidationError, PersistencePolicyError
from core.model_defaults import ModelDefaults
from core.settings import AppSettings


class ModelRegistryTests(unittest.TestCase):
    """Exercise the public registry/default contracts with real local persistence."""

    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.data = AppDataServices.open(self.root / "data.sqlite3")
        self.settings = AppSettings(self.root / "settings.ini")
        self.defaults = ModelDefaults(self.settings, self.data.models)

    def tearDown(self) -> None:
        self.data.close()
        self.tempdir.cleanup()

    def test_configure_validates_fields_and_duplicate_names(self) -> None:
        with self.assertRaisesRegex(DataValidationError, "name"):
            self.data.models.configure(" ", "ollama", "http://localhost:11434", ["chat"])
        with self.assertRaisesRegex(DataValidationError, "endpoint"):
            self.data.models.configure("Local", "ollama", " ", ["chat"])
        with self.assertRaisesRegex(DataValidationError, "chat"):
            self.data.models.configure("Vision", "ollama", "http://localhost:11434", ["vision"])

        self.data.models.configure("Qwen", "ollama", "http://localhost:11434", ["chat"])
        with self.assertRaisesRegex(DataValidationError, "already exists"):
            self.data.models.configure("qWEN", "ollama", "http://localhost:11434", ["chat"])

    def test_credential_bearing_endpoints_are_rejected_and_never_exported(self) -> None:
        """URL userinfo/query secrets must not enter SQLite or exported JSON."""

        rejected = (
            "https://user:pass@example.invalid/v1",
            "https://example.invalid/v1?api_key=do-not-store",
            "https://example.invalid/v1?next=token%3Ddo-not-store",
        )
        for endpoint in rejected:
            with self.subTest(endpoint=endpoint):
                with self.assertRaises(PersistencePolicyError):
                    self.data.models.configure("Unsafe", "custom-api", endpoint, ["chat"])

        safe = self.data.models.configure(
            "Safe", "custom-api", "https://example.invalid/v1?region=nz", ["chat"]
        )
        export_path = self.root / "models.json"
        self.data.local_data.export_json(export_path)
        exported = export_path.read_text(encoding="utf-8")
        self.assertIn(safe.endpoint, exported)
        self.assertNotIn("do-not-store", exported)
        self.assertNotIn("user:pass", exported)

    def test_edit_preserves_identity_and_remove_reports_missing(self) -> None:
        original = self.data.models.configure(
            "Local", "ollama", "http://localhost:11434", ["chat", "vision"]
        )
        edited = self.data.models.configure(
            "Local Vision", "ollama", "http://127.0.0.1:11434", ["chat", "vision"],
            model_id=original.id,
        )
        self.assertEqual(edited.id, original.id)
        self.assertEqual(edited.created_at, original.created_at)
        self.assertEqual(edited.name, "Local Vision")
        self.assertTrue(self.data.models.remove(original.id))
        self.assertFalse(self.data.models.remove(original.id))

    def test_compatible_returns_only_enabled_capable_models(self) -> None:
        vision = self.data.models.configure(
            "Vision", "ollama", "http://localhost:11434", ["chat", "vision"]
        )
        self.data.models.configure(
            "Chat", "ollama", "http://localhost:11434", ["chat"]
        )
        self.data.models.configure(
            "Disabled Vision", "ollama", "http://localhost:11434", ["chat", "vision"], enabled=False
        )
        self.assertEqual([record.id for record in self.data.models.compatible("vision")], [vision.id])

    def test_defaults_reject_incompatible_models_and_round_trip_restart(self) -> None:
        chat = self.data.models.configure(
            "Chat", "ollama", "http://localhost:11434", ["chat"]
        )
        vision = self.data.models.configure(
            "Vision", "ollama", "http://localhost:11434", ["chat", "vision"]
        )
        with self.assertRaisesRegex(DataValidationError, "does not support vision"):
            self.defaults.assign("vision", chat.id)
        self.defaults.assign("chat", chat.id)
        self.defaults.assign("vision", vision.id)

        reopened = ModelDefaults(AppSettings(self.root / "settings.ini"), self.data.models)
        self.assertEqual(reopened.resolve("chat").id, chat.id)
        self.assertEqual(reopened.resolve("vision").id, vision.id)

    def test_removed_or_disabled_model_never_resolves(self) -> None:
        model = self.data.models.configure(
            "Temporary", "ollama", "http://localhost:11434", ["chat", "utility"]
        )
        self.defaults.assign("chat", model.id)
        self.defaults.assign("utility", model.id)
        self.assertEqual(self.defaults.invalidate(model.id), ("chat", "utility"))
        self.assertIsNone(self.defaults.resolve("chat"))

        self.defaults.assign("chat", model.id)
        self.data.models.remove(model.id)
        self.assertIsNone(self.defaults.resolve("chat"))

    def test_fallbacks_preserve_order_remove_duplicates_and_invalidate(self) -> None:
        first = self.data.models.configure(
            "First", "ollama", "http://localhost:11434", ["chat"]
        )
        second = self.data.models.configure(
            "Second", "ollama", "http://localhost:11434", ["chat", "utility"]
        )
        self.defaults.set_fallbacks([second.id, first.id, second.id])
        self.assertEqual([record.id for record in self.defaults.fallbacks()], [second.id, first.id])

        self.defaults.invalidate(second.id)
        self.assertEqual([record.id for record in self.defaults.fallbacks()], [first.id])


if __name__ == "__main__":
    unittest.main()
