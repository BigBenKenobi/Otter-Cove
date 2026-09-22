"""UI-facing local-data services and import/export coordination.

Repositories own durable SQLite operations, while these services enforce the
application's higher-level persistence boundaries.  In particular,
``SessionService`` keeps Nobody sessions entirely in memory and provides explicit
disposal so presentation code can end their lifecycle without leaving transient
messages reachable inside the running process.
"""

from __future__ import annotations

import json
import os
import sqlite3
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .database import SQLiteStore
from .errors import DataValidationError
from .ids import new_id
from .models import MessageRecord, SessionRecord
from .policy import assert_no_credentials
from .repositories import (
    BrainRepository,
    DocumentRepository,
    GalleryRepository,
    ModelRepository,
    NoteRepository,
    SessionRepository,
    TaskRepository,
)
from .timeutil import utc_now

EXPORT_FORMAT = "otter-cove-local-data"
EXPORT_VERSION = 1


def default_data_dir() -> Path:
    root = os.environ.get("XDG_DATA_HOME")
    if root:
        return Path(root).expanduser() / "otter-cove"
    return Path.home() / ".local" / "share" / "otter-cove"


def default_database_path() -> Path:
    override = os.environ.get("OTTER_COVE_DATA_DIR")
    return (Path(override).expanduser() if override else default_data_dir()) / "otter-cove.sqlite3"


@dataclass(frozen=True)
class DataOperationReport:
    operation: str
    path: str | None
    counts: dict[str, int]
    affected: tuple[str, ...]
    excluded: tuple[str, ...] = ("credentials", "Nobody/incognito sessions", "QSettings preferences/geometry")


class SessionService:
    """Present persistent and process-local Nobody sessions through one API.

    Persistent records are delegated to ``SessionRepository``. Nobody records and
    messages are owned by this service for the process lifetime and must be
    explicitly disposed when their UI session closes.
    """

    def __init__(self, repository: SessionRepository) -> None:
        self.repository = repository
        self._incognito_sessions: dict[str, SessionRecord] = {}
        self._incognito_messages: dict[str, list[MessageRecord]] = {}

    def create_session(self, title: str = "New Chat", *, incognito: bool = False) -> SessionRecord:
        """Create a durable session or allocate a memory-only Nobody session."""

        if not incognito:
            return self.repository.create(title)
        now = utc_now()
        record = SessionRecord(new_id("incognito"), title or "New Chat", now, now, False, {"incognito": True})
        self._incognito_sessions[record.id] = record
        self._incognito_messages[record.id] = []
        return record

    def add_message(self, session_id: str, role: str, content: str, *, metadata: dict[str, Any] | None = None) -> MessageRecord:
        """Append to the matching memory-only or persistent session."""

        if session_id in self._incognito_sessions:
            messages = self._incognito_messages[session_id]
            record = MessageRecord(
                new_id("incognito_message"), session_id, role, content, utc_now(), len(messages), dict(metadata or {})
            )
            messages.append(record)
            return record
        return self.repository.add_message(session_id, role, content, metadata=metadata)

    def messages(self, session_id: str) -> list[MessageRecord]:
        """Return an isolated copy of Nobody messages or durable session rows."""

        if session_id in self._incognito_sessions:
            return list(self._incognito_messages[session_id])
        return self.repository.messages(session_id)

    def latest_persistent_session(self) -> SessionRecord | None:
        return self.repository.latest()

    def list_persistent_sessions(self) -> list[SessionRecord]:
        return self.repository.list()

    def get_persistent_session(self, session_id: str) -> SessionRecord | None:
        return self.repository.get(session_id)

    def get_session(self, session_id: str | None) -> SessionRecord | None:
        """Return either kind of session without exposing the internal stores."""

        if not session_id:
            return None
        return self._incognito_sessions.get(session_id) or self.repository.get(session_id)

    def dispose_incognito_session(self, session_id: str | None) -> bool:
        """Permanently remove one process-local Nobody session and its messages.

        Persistent IDs and unknown IDs are safe no-ops.  Returning whether a
        transient record was removed lets lifecycle owners verify cleanup without
        inspecting service internals.
        """

        if not session_id or session_id not in self._incognito_sessions:
            return False
        del self._incognito_sessions[session_id]
        self._incognito_messages.pop(session_id, None)
        return True

    def is_incognito(self, session_id: str | None) -> bool:
        """Report whether ``session_id`` currently names a live Nobody session."""

        return bool(session_id and session_id in self._incognito_sessions)


class ModelService:
    def __init__(self, repository: ModelRepository) -> None:
        self._repository = repository

    def create(self, name: str, provider: str, **kwargs):
        return self._repository.create(name, provider, **kwargs)

    def list(self):
        return self._repository.list()


class DocumentService:
    def __init__(self, repository: DocumentRepository) -> None:
        self._repository = repository

    def create(self, title: str, **kwargs):
        return self._repository.create(title, **kwargs)

    def list(self):
        return self._repository.list()


class BrainService:
    def __init__(self, repository: BrainRepository) -> None:
        self._repository = repository

    def create(self, kind: str, title: str, content: str, **kwargs):
        return self._repository.create(kind, title, content, **kwargs)

    def list(self, kind: str | None = None):
        return self._repository.list(kind)


class NoteService:
    def __init__(self, repository: NoteRepository) -> None:
        self._repository = repository

    def create(self, title: str, **kwargs):
        return self._repository.create(title, **kwargs)

    def list(self):
        return self._repository.list()


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def create(self, title: str, **kwargs):
        return self._repository.create(title, **kwargs)

    def list(self):
        return self._repository.list()


class GalleryService:
    def __init__(self, repository: GalleryRepository) -> None:
        self._repository = repository

    def create(self, path: str, **kwargs):
        return self._repository.create(path, **kwargs)

    def list(self):
        return self._repository.list()


class LocalDataService:
    """Own the versioned, credential-safe local-data import/export boundary.

    ``AppDataServices`` constructs this coordinator around the same repositories
    used by the GUI.  It snapshots only the durable tables listed below, keeping
    Nobody sessions and QSettings outside exports.  Import validation happens
    before replacement where possible, while the SQLite transaction guarantees
    malformed rows cannot partially erase a user's current local content.
    """

    TABLES = (
        "sessions",
        "messages",
        "models",
        "documents",
        "brain_items",
        "notes",
        "tasks",
        "gallery_items",
    )

    # Every exported row must retain these stable identity/lifecycle fields. The
    # repository APIs use direct lookups for them, so checking before replacement
    # turns a hand-edited or truncated export into actionable recovery feedback.
    REQUIRED_FIELDS = {
        "sessions": ("id", "created_at", "updated_at"),
        "messages": ("id", "session_id", "role", "content", "created_at", "ordinal"),
        "models": ("id", "name", "provider", "created_at", "updated_at"),
        "documents": ("id", "title", "created_at", "updated_at"),
        "brain_items": ("id", "kind", "title", "content", "created_at", "updated_at"),
        "notes": ("id", "title", "created_at", "updated_at"),
        "tasks": ("id", "title", "created_at", "updated_at"),
        "gallery_items": ("id", "path", "created_at", "updated_at"),
    }

    def __init__(
        self,
        store: SQLiteStore,
        sessions: SessionRepository,
        models: ModelRepository,
        documents: DocumentRepository,
        brain: BrainRepository,
        notes: NoteRepository,
        tasks: TaskRepository,
        gallery: GalleryRepository,
    ) -> None:
        """Retain the shared store and repositories used for durable transfers.

        The service deliberately receives repository instances instead of opening
        another database connection.  Import can therefore run every table write
        within the caller's one SQLite transaction and leave all prior content
        intact when any record is rejected.
        """

        self.store = store
        self.sessions = sessions
        self.models = models
        self.documents = documents
        self.brain = brain
        self.notes = notes
        self.tasks = tasks
        self.gallery = gallery

    def snapshot(self) -> dict[str, Any]:
        """Return the complete credential-free durable-data export payload.

        Rows are read directly from the versioned SQLite tables to preserve stable
        IDs and timestamps for a later import.  The persistence policy check is a
        final guard: an unsafe record is never serialized as a local-data export.
        """

        conn = self.store.connection
        content: dict[str, list[dict[str, Any]]] = {}
        for table in self.TABLES:
            rows = conn.execute(f"SELECT * FROM {table}").fetchall()
            content[table] = [dict(row) for row in rows]
        payload = {
            "format": EXPORT_FORMAT,
            "version": EXPORT_VERSION,
            "schema_version": self.store.schema_version(),
            "exported_at": utc_now(),
            "content": content,
        }
        assert_no_credentials(payload, path="export")
        return payload

    def export_json(self, path: str | Path) -> DataOperationReport:
        """Atomically serialize :meth:`snapshot` to ``path`` and report its scope.

        The temporary sibling file is flushed before ``os.replace`` publishes it,
        so a failed export leaves a pre-existing destination untouched.  Filesystem
        errors intentionally propagate to the shell, which owns user feedback.
        """

        target = Path(path).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = self.snapshot()
        encoded = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
        fd, temp_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(encoded)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, target)
        except Exception:
            try:
                os.unlink(temp_name)
            except OSError:
                pass
            raise
        counts = {table: len(rows) for table, rows in payload["content"].items()}
        return DataOperationReport("export", str(target), counts, self.TABLES)

    def import_json(self, path: str | Path, *, replace: bool = True) -> DataOperationReport:
        """Validate then transactionally import a versioned local-data snapshot.

        ``replace`` clears supported durable tables only inside the transaction;
        invalid roots, missing row fields, nested JSON, conversion failures, and
        constraint violations leave existing local content unchanged.  Expected
        malformed-file failures are normalized to :class:`DataValidationError` so
        the Settings shell can show recovery feedback instead of leaking Python
        parsing exceptions through a Qt signal handler.
        """

        source = Path(path).expanduser().resolve()
        try:
            payload = json.loads(source.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise DataValidationError(f"Cannot read Otter Cove data export: {exc}") from exc
        self._validate_import(payload)
        content = payload["content"]
        self._validate_row_shapes(content)
        counts = {table: len(content.get(table, [])) for table in self.TABLES}
        try:
            # Replacement is deliberately deferred until every structural check
            # above has passed. Any semantic failure below rolls back this scope.
            with self.store.transaction() as conn:
                if replace:
                    for table in reversed(self.TABLES):
                        conn.execute(f"DELETE FROM {table}")
                self._import_rows(content, conn)
        except DataValidationError:
            raise
        except sqlite3.IntegrityError as exc:
            raise DataValidationError(f"Import violates the local-data schema: {exc}") from exc
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            raise DataValidationError(
                f"Import contains malformed record values: {exc}"
            ) from exc
        return DataOperationReport("import", str(source), counts, self.TABLES)

    def reset_local_content(self) -> DataOperationReport:
        """Transactionally delete exportable durable content and report row counts.

        Preferences, geometry, credentials, and process-local Nobody records never
        belong to ``TABLES`` and are therefore intentionally outside this reset.
        """

        before = {table: int(self.store.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]) for table in self.TABLES}
        with self.store.transaction() as conn:
            for table in reversed(self.TABLES):
                conn.execute(f"DELETE FROM {table}")
        return DataOperationReport("reset", None, before, self.TABLES)

    def _validate_import(self, payload: Any) -> None:
        """Reject an incompatible root, table collection, or credential-like data.

        This phase validates the versioned envelope before reading individual rows.
        Row-shape and nested-JSON checks follow separately because they need the
        table names to produce specific recovery messages.
        """

        if not isinstance(payload, dict):
            raise DataValidationError("Import root must be a JSON object.")
        if payload.get("format") != EXPORT_FORMAT:
            raise DataValidationError("This is not an Otter Cove local-data export.")
        if payload.get("version") != EXPORT_VERSION:
            raise DataValidationError(f"Unsupported local-data export version: {payload.get('version')!r}")
        if not isinstance(payload.get("content"), dict):
            raise DataValidationError("Export content is missing or invalid.")
        unknown = set(payload["content"]) - set(self.TABLES)
        if unknown:
            raise DataValidationError(f"Export contains unsupported content tables: {', '.join(sorted(unknown))}")
        assert_no_credentials(payload, path="import")

    def _validate_row_shapes(self, content: dict[str, Any]) -> None:
        """Require the repository fields needed by every imported record.

        Missing keys previously escaped as ``KeyError`` after the transaction had
        started.  This preflight keeps the database untouched and names the exact
        table, row, and omitted fields for the Settings recovery surface.
        """

        for table in self.TABLES:
            for index, row in enumerate(self._rows(content, table)):
                missing = [field for field in self.REQUIRED_FIELDS[table] if field not in row]
                if missing:
                    raise DataValidationError(
                        f"Cannot import {table}[{index}]: missing required fields "
                        f"{', '.join(missing)}."
                    )

    @staticmethod
    def _rows(content: dict[str, Any], table: str) -> list[dict[str, Any]]:
        """Return one table's object rows or reject an invalid table shape."""

        rows = content.get(table, [])
        if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
            raise DataValidationError(f"Import table '{table}' must be a list of objects.")
        return rows

    @staticmethod
    def _nested_json(
        row: dict[str, Any],
        table: str,
        field: str,
        expected_type: type,
    ) -> Any:
        """Decode one JSON-in-SQL field as a user-facing validation boundary.

        Export rows contain metadata/config/tags as encoded SQLite text. A valid
        outer export may still carry malformed nested JSON, so decoding failures
        and wrong decoded shapes become ``DataValidationError``. This lets the
        surrounding transaction roll back and the Settings handler show recovery
        feedback instead of leaking ``JSONDecodeError`` from the service layer.
        """

        fallback = "[]" if expected_type is list else "{}"
        raw = row.get(field, fallback)
        try:
            value = json.loads(raw)
        except (TypeError, json.JSONDecodeError) as exc:
            raise DataValidationError(
                f"Cannot import {table}.{field}: nested JSON is malformed."
            ) from exc
        if not isinstance(value, expected_type):
            raise DataValidationError(
                f"Cannot import {table}.{field}: expected {expected_type.__name__} JSON."
            )
        return value

    def _import_rows(self, content: dict[str, Any], conn) -> None:
        """Write validated rows in foreign-key order within the active transaction.

        Parent sessions precede their messages; all other repository writes retain
        their exported IDs.  Callers must run the envelope and row-shape preflight
        first, but nested field and value conversion checks remain defensive here.
        """

        # Parent records first. Repository create methods preserve IDs and validate metadata.
        for row in self._rows(content, "sessions"):
            self.sessions.create(
                row.get("title", "New Chat"), record_id=row["id"], created_at=row["created_at"], updated_at=row["updated_at"],
                archived=bool(row.get("archived", 0)),
                metadata=self._nested_json(row, "sessions", "metadata_json", dict), connection=conn,
            )
        for row in self._rows(content, "messages"):
            self.sessions.add_message(
                row["session_id"], row["role"], row["content"], record_id=row["id"], created_at=row["created_at"],
                ordinal=int(row["ordinal"]),
                metadata=self._nested_json(row, "messages", "metadata_json", dict), connection=conn,
            )
        for row in self._rows(content, "models"):
            self.models.create(
                row["name"], row["provider"], endpoint=row.get("endpoint", ""), enabled=bool(row.get("enabled", 1)),
                config=self._nested_json(row, "models", "config_json", dict),
                record_id=row["id"], created_at=row["created_at"], updated_at=row["updated_at"], connection=conn,
            )
        for row in self._rows(content, "documents"):
            self.documents.create(
                row["title"], content=row.get("content", ""), mime_type=row.get("mime_type", "text/plain"), path=row.get("path"),
                source=row.get("source", "local"),
                metadata=self._nested_json(row, "documents", "metadata_json", dict), record_id=row["id"],
                created_at=row["created_at"], updated_at=row["updated_at"], connection=conn,
            )
        for row in self._rows(content, "brain_items"):
            self.brain.create(
                row["kind"], row["title"], row["content"], enabled=bool(row.get("enabled", 1)), confidence=float(row.get("confidence", 0.0)),
                tags=self._nested_json(row, "brain_items", "tags_json", list),
                metadata=self._nested_json(row, "brain_items", "metadata_json", dict), record_id=row["id"],
                created_at=row["created_at"], updated_at=row["updated_at"], connection=conn,
            )
        for row in self._rows(content, "notes"):
            self.notes.create(
                row["title"], body=row.get("body", ""), archived=bool(row.get("archived", 0)), pinned=bool(row.get("pinned", 0)),
                metadata=self._nested_json(row, "notes", "metadata_json", dict),
                record_id=row["id"], created_at=row["created_at"], updated_at=row["updated_at"], connection=conn,
            )
        for row in self._rows(content, "tasks"):
            self.tasks.create(
                row["title"], description=row.get("description", ""), status=row.get("status", "pending"), due_at=row.get("due_at"),
                metadata=self._nested_json(row, "tasks", "metadata_json", dict),
                record_id=row["id"], created_at=row["created_at"], updated_at=row["updated_at"], connection=conn,
            )
        for row in self._rows(content, "gallery_items"):
            self.gallery.create(
                row["path"], kind=row.get("kind", "image"), favourite=bool(row.get("favourite", 0)),
                metadata=self._nested_json(row, "gallery_items", "metadata_json", dict),
                record_id=row["id"], created_at=row["created_at"], updated_at=row["updated_at"], connection=conn,
            )
        for row in self._rows(content, "sessions"):
            conn.execute("UPDATE sessions SET updated_at=? WHERE id=?", (row["updated_at"], row["id"]))


@dataclass
class AppDataServices:
    store: SQLiteStore
    sessions: SessionService
    models: ModelService
    documents: DocumentService
    brain: BrainService
    notes: NoteService
    tasks: TaskService
    gallery: GalleryService
    local_data: LocalDataService

    @classmethod
    def open(cls, path: str | Path | None = None) -> "AppDataServices":
        store = SQLiteStore(path or default_database_path())
        session_repository = SessionRepository(store)
        model_repository = ModelRepository(store)
        document_repository = DocumentRepository(store)
        brain_repository = BrainRepository(store)
        note_repository = NoteRepository(store)
        task_repository = TaskRepository(store)
        gallery_repository = GalleryRepository(store)
        return cls(
            store=store,
            sessions=SessionService(session_repository),
            models=ModelService(model_repository),
            documents=DocumentService(document_repository),
            brain=BrainService(brain_repository),
            notes=NoteService(note_repository),
            tasks=TaskService(task_repository),
            gallery=GalleryService(gallery_repository),
            local_data=LocalDataService(
                store, session_repository, model_repository, document_repository, brain_repository,
                note_repository, task_repository, gallery_repository,
            ),
        )

    def close(self) -> None:
        self.store.close()
