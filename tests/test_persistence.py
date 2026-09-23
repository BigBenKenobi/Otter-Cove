"""Behavioral tests for Otter Cove's SQLite and memory-only data boundaries.

Every test uses a temporary store. The suite covers schema migration, round trips,
atomic recovery, credential rejection, and the rule that Nobody sessions remain
outside durable storage and are erased when their process-local lifecycle ends.
"""

from __future__ import annotations

import json
import copy
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.data import (
    AppDataServices,
    DataStoreCorruptError,
    DataStoreUnavailableError,
    DataValidationError,
    PersistencePolicyError,
    SQLiteStore,
)
from core.data.migrations import SCHEMA_VERSION
from core.data.services import EXPORT_FORMAT, default_data_dir, default_database_path


class PersistenceTests(unittest.TestCase):
    """Verify durable records and transient privacy records through public services."""

    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.db_path = self.root / "otter-cove.sqlite3"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_fresh_store_creates_current_schema_and_round_trips_domain_records(self) -> None:
        services = AppDataServices.open(self.db_path)
        self.assertEqual(services.store.schema_version(), SCHEMA_VERSION)

        session = services.sessions.create_session("Persistent chat")
        services.sessions.add_message(session.id, "user", "hello", metadata={"mode": "Chat"})
        model = services.models.create("Local Demo", "local", endpoint="http://127.0.0.1:11434", config={"family": "demo"})
        document = services.documents.create("Doc", content="body")
        brain = services.brain.create("memory", "Memory", "Remember this", confidence=0.8, tags=["demo"])
        note = services.notes.create("Note", body="note body")
        task = services.tasks.create("Task", description="do it")
        gallery = services.gallery.create("/tmp/example.png", metadata={"width": 100})
        services.close()

        reopened = AppDataServices.open(self.db_path)
        self.assertEqual(reopened.sessions.get_persistent_session(session.id).title, "Persistent chat")
        self.assertEqual(reopened.sessions.messages(session.id)[0].content, "hello")
        self.assertEqual(reopened.models.list()[0].id, model.id)
        self.assertEqual(reopened.documents.list()[0].id, document.id)
        self.assertEqual(reopened.brain.list()[0].id, brain.id)
        self.assertEqual(reopened.notes.list()[0].id, note.id)
        self.assertEqual(reopened.tasks.list()[0].id, task.id)
        self.assertEqual(reopened.gallery.list()[0].id, gallery.id)
        reopened.close()

    def test_incognito_session_never_enters_sqlite_or_export(self) -> None:
        services = AppDataServices.open(self.db_path)
        normal = services.sessions.create_session("Normal", incognito=False)
        services.sessions.add_message(normal.id, "user", "persist me")
        incognito = services.sessions.create_session("Secret temporary chat", incognito=True)
        services.sessions.add_message(incognito.id, "user", "do not persist")

        ids = {record.id for record in services.sessions.list_persistent_sessions()}
        self.assertIn(normal.id, ids)
        self.assertNotIn(incognito.id, ids)
        snapshot = services.local_data.snapshot()
        serialized = json.dumps(snapshot)
        self.assertNotIn(incognito.id, serialized)
        self.assertNotIn("do not persist", serialized)
        services.close()

        reopened = AppDataServices.open(self.db_path)
        self.assertFalse(reopened.sessions.is_incognito(incognito.id))
        self.assertIsNone(reopened.sessions.get_persistent_session(incognito.id))
        reopened.close()

    def test_incognito_session_disposal_removes_messages_from_process_memory(self) -> None:
        """Closing a Nobody session must end access to its transient records."""

        services = AppDataServices.open(self.db_path)
        incognito = services.sessions.create_session("Dispose me", incognito=True)
        services.sessions.add_message(incognito.id, "user", "temporary")

        self.assertTrue(services.sessions.dispose_incognito_session(incognito.id))
        self.assertFalse(services.sessions.is_incognito(incognito.id))
        self.assertIsNone(services.sessions.get_session(incognito.id))
        self.assertFalse(services.sessions.dispose_incognito_session(incognito.id))
        services.close()

    def test_credential_like_configuration_is_rejected(self) -> None:
        services = AppDataServices.open(self.db_path)
        with self.assertRaises(PersistencePolicyError):
            services.models.create("Bad", "api", config={"api_key": "should-never-be-here"})
        self.assertEqual(services.models.list(), [])
        services.close()

    def test_atomic_export_reset_and_import_preserve_stable_ids(self) -> None:
        services = AppDataServices.open(self.db_path)
        session = services.sessions.create_session("Round trip")
        services.sessions.add_message(session.id, "user", "one")
        note = services.notes.create("Saved note", body="hello")
        export_path = self.root / "backup.json"

        report = services.local_data.export_json(export_path)
        self.assertEqual(report.operation, "export")
        self.assertTrue(export_path.exists())
        self.assertEqual(report.counts["sessions"], 1)
        self.assertIn("credentials", report.excluded)
        self.assertEqual(json.loads(export_path.read_text(encoding="utf-8"))["format"], EXPORT_FORMAT)

        reset = services.local_data.reset_local_content()
        self.assertEqual(reset.operation, "reset")
        self.assertEqual(services.sessions.list_persistent_sessions(), [])
        self.assertEqual(services.notes.list(), [])

        imported = services.local_data.import_json(export_path)
        self.assertEqual(imported.operation, "import")
        self.assertEqual(services.sessions.get_persistent_session(session.id).id, session.id)
        self.assertEqual(services.notes.list()[0].id, note.id)
        services.close()

    def test_export_rejects_active_store_aliases_and_sidecars_before_mutation(self) -> None:
        """A JSON export cannot replace a disposable live SQLite store by any alias."""

        services = AppDataServices.open(self.db_path)
        kept = services.sessions.create_session("Keep database intact")
        protected_targets = (
            self.db_path,
            self.db_path.with_name(f"{self.db_path.name}-wal"),
            self.db_path.with_name(f"{self.db_path.name}-shm"),
        )
        with self.assertRaisesRegex(DataValidationError, "protected active"):
            services.local_data.export_json(self.db_path)
        for target in protected_targets[1:]:
            with self.assertRaisesRegex(DataValidationError, "protected active"):
                services.local_data.export_json(target)
        alias = self.root / "alias.sqlite3"
        alias.symlink_to(self.db_path)
        with self.assertRaisesRegex(DataValidationError, "protected active"):
            services.local_data.export_json(alias)
        hard_link = self.root / "hard-link.sqlite3"
        os.link(self.db_path, hard_link)
        with self.assertRaisesRegex(DataValidationError, "aliases protected"):
            services.local_data.export_json(hard_link)
        parent_alias = self.root / "parent-alias"
        parent_alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(DataValidationError, "protected active"):
            services.local_data.export_json(parent_alias / self.db_path.name)
        preferences = self.root / "settings.ini"
        preferences.write_text("[appearance]\\ntheme=Forest\\n", encoding="utf-8")
        with self.assertRaisesRegex(DataValidationError, "protected active"):
            services.local_data.export_json(preferences, additional_protected_paths=(preferences,))
        self.assertIn("theme=Forest", preferences.read_text(encoding="utf-8"))
        self.assertEqual(services.sessions.get_persistent_session(kept.id).title, "Keep database intact")
        services.close()
        reopened = AppDataServices.open(self.db_path)
        self.assertEqual(reopened.sessions.get_persistent_session(kept.id).title, "Keep database intact")
        reopened.close()

    def test_otter_cove_default_paths_and_override(self) -> None:
        xdg_root = self.root / "xdg"
        otter_root = self.root / "otter"

        with patch.dict(os.environ, {"XDG_DATA_HOME": str(xdg_root)}, clear=True):
            self.assertEqual(default_data_dir(), xdg_root / "otter-cove")
            self.assertEqual(default_database_path(), xdg_root / "otter-cove" / "otter-cove.sqlite3")

        with patch.dict(
            os.environ,
            {
                "XDG_DATA_HOME": str(xdg_root),
                "OTTER_COVE_DATA_DIR": str(otter_root),
            },
            clear=True,
        ):
            self.assertEqual(default_database_path(), otter_root / "otter-cove.sqlite3")

    def test_non_current_export_marker_is_rejected(self) -> None:
        services = AppDataServices.open(self.db_path)
        rejected_export = self.root / "rejected-export.json"
        payload = services.local_data.snapshot()
        self.assertEqual(payload["format"], EXPORT_FORMAT)
        payload["format"] = "previous-product-local-data"
        rejected_export.write_text(json.dumps(payload), encoding="utf-8")

        with self.assertRaisesRegex(DataValidationError, "Otter Cove"):
            services.local_data.import_json(rejected_export)
        services.close()

    def test_v1_fixture_migrates_to_v2_without_losing_rows(self) -> None:
        fixture = Path(__file__).parent / "fixtures" / "schema_v1.sql"
        conn = sqlite3.connect(self.db_path)
        conn.executescript(fixture.read_text(encoding="utf-8"))
        conn.execute(
            "INSERT INTO documents(id,title,content,mime_type,path,created_at,updated_at,metadata_json) VALUES(?,?,?,?,?,?,?,?)",
            ("document_fixture", "Old doc", "body", "text/plain", None, "2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z", "{}"),
        )
        conn.commit()
        conn.close()

        store = SQLiteStore(self.db_path)
        self.assertEqual(store.schema_version(), SCHEMA_VERSION)
        row = store.connection.execute("SELECT id, source FROM documents WHERE id='document_fixture'").fetchone()
        self.assertEqual(row["id"], "document_fixture")
        self.assertEqual(row["source"], "local")
        store.close()


    def test_failed_import_rolls_back_without_erasing_existing_content(self) -> None:
        services = AppDataServices.open(self.db_path)
        original = services.sessions.create_session("Keep me")
        payload = services.local_data.snapshot()
        payload["content"]["sessions"].append(dict(payload["content"]["sessions"][0]))
        bad_import = self.root / "duplicate.json"
        bad_import.write_text(json.dumps(payload), encoding="utf-8")

        with self.assertRaises(DataValidationError):
            services.local_data.import_json(bad_import)
        self.assertIsNotNone(services.sessions.get_persistent_session(original.id))
        self.assertEqual(len(services.sessions.list_persistent_sessions()), 1)
        services.close()

    def test_import_contract_rejects_incomplete_future_and_broken_snapshots(self) -> None:
        """Replacement validation rejects all unsafe envelopes before deleting live rows."""

        services = AppDataServices.open(self.db_path)
        kept = services.sessions.create_session("Keep after rejected import")
        services.sessions.add_message(kept.id, "user", "stable")
        valid = services.local_data.snapshot()
        cases = []
        future = copy.deepcopy(valid); future["schema_version"] = 999; cases.append(future)
        missing = copy.deepcopy(valid); del missing["content"]["notes"]; cases.append(missing)
        null_id = copy.deepcopy(valid); null_id["content"]["sessions"][0]["id"] = None; cases.append(null_id)
        bad_ref = copy.deepcopy(valid); bad_ref["content"]["messages"][0]["session_id"] = "missing"; cases.append(bad_ref)
        for index, payload in enumerate(cases):
            path = self.root / f"rejected-{index}.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(DataValidationError):
                services.local_data.import_json(path)
            self.assertEqual(services.sessions.get_persistent_session(kept.id).title, "Keep after rejected import")
        services.close()

    def test_prepared_import_applies_validated_bytes_after_source_changes(self) -> None:
        """Confirmation applies the prepared snapshot, never a file reread later."""

        services = AppDataServices.open(self.db_path)
        original = services.sessions.create_session("Confirmed snapshot")
        source = self.root / "confirmed.json"
        source.write_text(json.dumps(services.local_data.snapshot()), encoding="utf-8")
        prepared = services.local_data.prepare_import(source)
        source.write_text(json.dumps({"format": "wrong"}), encoding="utf-8")
        services.sessions.create_session("Unconfirmed replacement")
        report = services.local_data.apply_prepared_import(prepared)
        self.assertEqual(report.counts["sessions"], 1)
        self.assertEqual(services.sessions.list_persistent_sessions()[0].id, original.id)
        services.close()

    def test_unavailable_store_reports_recovery_without_creating_replacement(self) -> None:
        blocked_parent = self.root / "not-a-directory"
        blocked_parent.write_text("block", encoding="utf-8")
        requested = blocked_parent / "otter-cove.sqlite3"
        with self.assertRaises(DataStoreUnavailableError) as caught:
            SQLiteStore(requested)
        self.assertTrue(caught.exception.recovery_options)
        self.assertEqual(blocked_parent.read_text(encoding="utf-8"), "block")

    def test_corrupt_store_is_reported_and_never_replaced(self) -> None:
        original = b"this is deliberately not sqlite"
        self.db_path.write_bytes(original)
        with self.assertRaises(DataStoreCorruptError) as caught:
            SQLiteStore(self.db_path)
        self.assertEqual(self.db_path.read_bytes(), original)
        self.assertTrue(caught.exception.recovery_options)


if __name__ == "__main__":
    unittest.main()
