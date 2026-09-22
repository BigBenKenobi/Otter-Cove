from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from typing import Any, Iterator

from .database import SQLiteStore
from .ids import new_id
from .models import (
    BrainItemRecord,
    DocumentRecord,
    GalleryItemRecord,
    MessageRecord,
    ModelRecord,
    NoteRecord,
    SessionRecord,
    TaskRecord,
)
from .policy import assert_no_credentials
from .timeutil import utc_now


def _dump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _load(value: str, fallback):
    try:
        return json.loads(value)
    except (TypeError, ValueError, json.JSONDecodeError):
        return fallback


class RepositoryBase:
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    @contextmanager
    def _writer(self, connection: sqlite3.Connection | None = None) -> Iterator[sqlite3.Connection]:
        if connection is not None:
            yield connection
        else:
            with self.store.transaction() as conn:
                yield conn


class SessionRepository(RepositoryBase):
    def create(
        self,
        title: str = "New Chat",
        *,
        record_id: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
        archived: bool = False,
        metadata: dict[str, Any] | None = None,
        connection: sqlite3.Connection | None = None,
    ) -> SessionRecord:
        now = created_at or utc_now()
        record = SessionRecord(
            id=record_id or new_id("session"),
            title=title.strip() or "New Chat",
            created_at=now,
            updated_at=updated_at or now,
            archived=bool(archived),
            metadata=dict(metadata or {}),
        )
        assert_no_credentials(record.metadata, path="session.metadata")
        with self._writer(connection) as conn:
            conn.execute(
                "INSERT INTO sessions(id,title,created_at,updated_at,archived,metadata_json) VALUES(?,?,?,?,?,?)",
                (record.id, record.title, record.created_at, record.updated_at, int(record.archived), _dump(record.metadata)),
            )
        return record

    def get(self, record_id: str) -> SessionRecord | None:
        row = self.store.connection.execute("SELECT * FROM sessions WHERE id=?", (record_id,)).fetchone()
        return self._session_from_row(row) if row else None

    def list(self, *, include_archived: bool = True) -> list[SessionRecord]:
        sql = "SELECT * FROM sessions"
        params: tuple[Any, ...] = ()
        if not include_archived:
            sql += " WHERE archived=0"
        sql += " ORDER BY updated_at DESC"
        return [self._session_from_row(row) for row in self.store.connection.execute(sql, params).fetchall()]

    def latest(self) -> SessionRecord | None:
        row = self.store.connection.execute(
            "SELECT * FROM sessions WHERE archived=0 ORDER BY updated_at DESC LIMIT 1"
        ).fetchone()
        return self._session_from_row(row) if row else None

    def touch(self, record_id: str, *, title: str | None = None, connection: sqlite3.Connection | None = None) -> None:
        now = utc_now()
        with self._writer(connection) as conn:
            if title is None:
                conn.execute("UPDATE sessions SET updated_at=? WHERE id=?", (now, record_id))
            else:
                conn.execute("UPDATE sessions SET title=?, updated_at=? WHERE id=?", (title, now, record_id))

    def delete(self, record_id: str, *, connection: sqlite3.Connection | None = None) -> None:
        with self._writer(connection) as conn:
            conn.execute("DELETE FROM sessions WHERE id=?", (record_id,))

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        *,
        record_id: str | None = None,
        created_at: str | None = None,
        ordinal: int | None = None,
        metadata: dict[str, Any] | None = None,
        connection: sqlite3.Connection | None = None,
    ) -> MessageRecord:
        meta = dict(metadata or {})
        assert_no_credentials(meta, path="message.metadata")
        with self._writer(connection) as conn:
            if ordinal is None:
                ordinal = int(
                    conn.execute("SELECT COALESCE(MAX(ordinal), -1)+1 FROM messages WHERE session_id=?", (session_id,)).fetchone()[0]
                )
            record = MessageRecord(
                id=record_id or new_id("message"),
                session_id=session_id,
                role=role,
                content=content,
                created_at=created_at or utc_now(),
                ordinal=int(ordinal),
                metadata=meta,
            )
            conn.execute(
                "INSERT INTO messages(id,session_id,role,content,created_at,ordinal,metadata_json) VALUES(?,?,?,?,?,?,?)",
                (
                    record.id,
                    record.session_id,
                    record.role,
                    record.content,
                    record.created_at,
                    record.ordinal,
                    _dump(record.metadata),
                ),
            )
            conn.execute("UPDATE sessions SET updated_at=? WHERE id=?", (record.created_at, session_id))
        return record

    def messages(self, session_id: str) -> list[MessageRecord]:
        rows = self.store.connection.execute(
            "SELECT * FROM messages WHERE session_id=? ORDER BY ordinal ASC", (session_id,)
        ).fetchall()
        return [self._message_from_row(row) for row in rows]

    @staticmethod
    def _session_from_row(row: sqlite3.Row) -> SessionRecord:
        return SessionRecord(
            id=row["id"],
            title=row["title"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            archived=bool(row["archived"]),
            metadata=_load(row["metadata_json"], {}),
        )

    @staticmethod
    def _message_from_row(row: sqlite3.Row) -> MessageRecord:
        return MessageRecord(
            id=row["id"],
            session_id=row["session_id"],
            role=row["role"],
            content=row["content"],
            created_at=row["created_at"],
            ordinal=int(row["ordinal"]),
            metadata=_load(row["metadata_json"], {}),
        )


class ModelRepository(RepositoryBase):
    """Persist model registry records without owning provider behavior.

    The repository stores non-secret configuration only. Higher-level validation,
    capability matching and reference invalidation belong to ``ModelService`` and
    the defaults resolver so import/export can continue using this narrow data API.
    """

    def create(
        self,
        name: str,
        provider: str,
        *,
        endpoint: str = "",
        enabled: bool = True,
        config: dict[str, Any] | None = None,
        record_id: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
        connection: sqlite3.Connection | None = None,
    ) -> ModelRecord:
        safe_config = dict(config or {})
        assert_no_credentials(safe_config, path="model.config")
        now = created_at or utc_now()
        record = ModelRecord(
            id=record_id or new_id("model"),
            name=name,
            provider=provider,
            endpoint=endpoint,
            enabled=bool(enabled),
            created_at=now,
            updated_at=updated_at or now,
            config=safe_config,
        )
        with self._writer(connection) as conn:
            conn.execute(
                "INSERT INTO models(id,name,provider,endpoint,enabled,created_at,updated_at,config_json) VALUES(?,?,?,?,?,?,?,?)",
                (record.id, record.name, record.provider, record.endpoint, int(record.enabled), record.created_at, record.updated_at, _dump(record.config)),
            )
        return record

    def list(self) -> list[ModelRecord]:
        rows = self.store.connection.execute("SELECT * FROM models ORDER BY name COLLATE NOCASE").fetchall()
        return [self._from_row(row) for row in rows]

    def get(self, record_id: str) -> ModelRecord | None:
        """Return one model record, or ``None`` when its stable ID is unknown."""

        row = self.store.connection.execute("SELECT * FROM models WHERE id=?", (record_id,)).fetchone()
        return self._from_row(row) if row else None

    def update(
        self,
        record_id: str,
        *,
        name: str,
        provider: str,
        endpoint: str,
        enabled: bool,
        config: dict[str, Any],
        connection: sqlite3.Connection | None = None,
    ) -> ModelRecord | None:
        """Replace editable fields while preserving identity and creation time."""

        safe_config = dict(config)
        assert_no_credentials(safe_config, path="model.config")
        updated_at = utc_now()
        with self._writer(connection) as conn:
            cursor = conn.execute(
                "UPDATE models SET name=?,provider=?,endpoint=?,enabled=?,updated_at=?,config_json=? WHERE id=?",
                (name, provider, endpoint, int(enabled), updated_at, _dump(safe_config), record_id),
            )
        return self.get(record_id) if cursor.rowcount else None

    def delete(self, record_id: str, *, connection: sqlite3.Connection | None = None) -> bool:
        """Delete one registry record and report whether it existed."""

        with self._writer(connection) as conn:
            cursor = conn.execute("DELETE FROM models WHERE id=?", (record_id,))
        return bool(cursor.rowcount)

    @staticmethod
    def _from_row(row: sqlite3.Row) -> ModelRecord:
        """Map the SQLite representation to the immutable public record."""

        return ModelRecord(
            id=row["id"], name=row["name"], provider=row["provider"], endpoint=row["endpoint"],
            enabled=bool(row["enabled"]), created_at=row["created_at"], updated_at=row["updated_at"],
            config=_load(row["config_json"], {}),
        )


class DocumentRepository(RepositoryBase):
    def create(
        self,
        title: str,
        *,
        content: str = "",
        mime_type: str = "text/plain",
        path: str | None = None,
        source: str = "local",
        metadata: dict[str, Any] | None = None,
        record_id: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
        connection: sqlite3.Connection | None = None,
    ) -> DocumentRecord:
        meta = dict(metadata or {})
        assert_no_credentials(meta, path="document.metadata")
        now = created_at or utc_now()
        record = DocumentRecord(record_id or new_id("document"), title, content, mime_type, path, source, now, updated_at or now, meta)
        with self._writer(connection) as conn:
            conn.execute(
                "INSERT INTO documents(id,title,content,mime_type,path,created_at,updated_at,metadata_json,source) VALUES(?,?,?,?,?,?,?,?,?)",
                (record.id, record.title, record.content, record.mime_type, record.path, record.created_at, record.updated_at, _dump(record.metadata), record.source),
            )
        return record

    def list(self) -> list[DocumentRecord]:
        rows = self.store.connection.execute("SELECT * FROM documents ORDER BY updated_at DESC").fetchall()
        return [DocumentRecord(
            row["id"], row["title"], row["content"], row["mime_type"], row["path"], row["source"],
            row["created_at"], row["updated_at"], _load(row["metadata_json"], {})
        ) for row in rows]


class BrainRepository(RepositoryBase):
    def create(
        self,
        kind: str,
        title: str,
        content: str,
        *,
        enabled: bool = True,
        confidence: float = 0.0,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        record_id: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
        connection: sqlite3.Connection | None = None,
    ) -> BrainItemRecord:
        meta = dict(metadata or {})
        assert_no_credentials(meta, path="brain.metadata")
        now = created_at or utc_now()
        record = BrainItemRecord(
            record_id or new_id("brain"), kind, title, content, bool(enabled), float(confidence), now,
            updated_at or now, list(tags or []), meta
        )
        with self._writer(connection) as conn:
            conn.execute(
                "INSERT INTO brain_items(id,kind,title,content,enabled,confidence,created_at,updated_at,tags_json,metadata_json) VALUES(?,?,?,?,?,?,?,?,?,?)",
                (record.id, record.kind, record.title, record.content, int(record.enabled), record.confidence, record.created_at, record.updated_at, _dump(record.tags), _dump(record.metadata)),
            )
        return record

    def list(self, kind: str | None = None) -> list[BrainItemRecord]:
        if kind is None:
            rows = self.store.connection.execute("SELECT * FROM brain_items ORDER BY updated_at DESC").fetchall()
        else:
            rows = self.store.connection.execute("SELECT * FROM brain_items WHERE kind=? ORDER BY updated_at DESC", (kind,)).fetchall()
        return [BrainItemRecord(
            row["id"], row["kind"], row["title"], row["content"], bool(row["enabled"]), float(row["confidence"]),
            row["created_at"], row["updated_at"], _load(row["tags_json"], []), _load(row["metadata_json"], {})
        ) for row in rows]


class NoteRepository(RepositoryBase):
    def create(
        self,
        title: str,
        *,
        body: str = "",
        archived: bool = False,
        pinned: bool = False,
        metadata: dict[str, Any] | None = None,
        record_id: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
        connection: sqlite3.Connection | None = None,
    ) -> NoteRecord:
        meta = dict(metadata or {})
        assert_no_credentials(meta, path="note.metadata")
        now = created_at or utc_now()
        record = NoteRecord(record_id or new_id("note"), title, body, bool(archived), bool(pinned), now, updated_at or now, meta)
        with self._writer(connection) as conn:
            conn.execute(
                "INSERT INTO notes(id,title,body,archived,pinned,created_at,updated_at,metadata_json) VALUES(?,?,?,?,?,?,?,?)",
                (record.id, record.title, record.body, int(record.archived), int(record.pinned), record.created_at, record.updated_at, _dump(record.metadata)),
            )
        return record

    def list(self) -> list[NoteRecord]:
        rows = self.store.connection.execute("SELECT * FROM notes ORDER BY pinned DESC, updated_at DESC").fetchall()
        return [NoteRecord(
            row["id"], row["title"], row["body"], bool(row["archived"]), bool(row["pinned"]),
            row["created_at"], row["updated_at"], _load(row["metadata_json"], {})
        ) for row in rows]


class TaskRepository(RepositoryBase):
    def create(
        self,
        title: str,
        *,
        description: str = "",
        status: str = "pending",
        due_at: str | None = None,
        metadata: dict[str, Any] | None = None,
        record_id: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
        connection: sqlite3.Connection | None = None,
    ) -> TaskRecord:
        meta = dict(metadata or {})
        assert_no_credentials(meta, path="task.metadata")
        now = created_at or utc_now()
        record = TaskRecord(record_id or new_id("task"), title, description, status, due_at, now, updated_at or now, meta)
        with self._writer(connection) as conn:
            conn.execute(
                "INSERT INTO tasks(id,title,description,status,due_at,created_at,updated_at,metadata_json) VALUES(?,?,?,?,?,?,?,?)",
                (record.id, record.title, record.description, record.status, record.due_at, record.created_at, record.updated_at, _dump(record.metadata)),
            )
        return record

    def list(self) -> list[TaskRecord]:
        rows = self.store.connection.execute("SELECT * FROM tasks ORDER BY updated_at DESC").fetchall()
        return [TaskRecord(
            row["id"], row["title"], row["description"], row["status"], row["due_at"], row["created_at"], row["updated_at"], _load(row["metadata_json"], {})
        ) for row in rows]


class GalleryRepository(RepositoryBase):
    def create(
        self,
        path: str,
        *,
        kind: str = "image",
        favourite: bool = False,
        metadata: dict[str, Any] | None = None,
        record_id: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
        connection: sqlite3.Connection | None = None,
    ) -> GalleryItemRecord:
        meta = dict(metadata or {})
        assert_no_credentials(meta, path="gallery.metadata")
        now = created_at or utc_now()
        record = GalleryItemRecord(record_id or new_id("gallery"), path, kind, bool(favourite), now, updated_at or now, meta)
        with self._writer(connection) as conn:
            conn.execute(
                "INSERT INTO gallery_items(id,path,kind,favourite,created_at,updated_at,metadata_json) VALUES(?,?,?,?,?,?,?)",
                (record.id, record.path, record.kind, int(record.favourite), record.created_at, record.updated_at, _dump(record.metadata)),
            )
        return record

    def list(self) -> list[GalleryItemRecord]:
        rows = self.store.connection.execute("SELECT * FROM gallery_items ORDER BY updated_at DESC").fetchall()
        return [GalleryItemRecord(
            row["id"], row["path"], row["kind"], bool(row["favourite"]), row["created_at"], row["updated_at"], _load(row["metadata_json"], {})
        ) for row in rows]
