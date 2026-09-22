from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .errors import DataMigrationError, DataStoreCorruptError, DataStoreUnavailableError
from .migrations import MIGRATIONS, SCHEMA_VERSION

_RECOVERY_OPTIONS = (
    "Make a backup copy of the database file before changing anything.",
    "Restore a previously exported Otter Cove local-data JSON file.",
    "Move the database aside manually and start a new store only if you accept losing local content from the active store.",
)


class SQLiteStore:
    """Versioned SQLite store with explicit transactions and non-destructive failure handling."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser().resolve()
        self._connection: sqlite3.Connection | None = None
        self._open()

    @property
    def connection(self) -> sqlite3.Connection:
        if self._connection is None:
            raise DataStoreUnavailableError("The local-data store is closed.", path=self.path)
        return self._connection

    def _open(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(self.path, timeout=5.0, isolation_level=None)
            self._connection = conn
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA busy_timeout = 5000")
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            self._check_integrity()
            self._migrate()
        except (DataStoreCorruptError, DataMigrationError):
            self.close()
            raise
        except (sqlite3.DatabaseError, OSError) as exc:
            self.close()
            raise self._classify_open_error(exc) from exc

    def _classify_open_error(self, exc: Exception):
        text = str(exc).lower()
        error_cls = DataStoreCorruptError if (
            "malformed" in text or "not a database" in text or "file is encrypted" in text
        ) else DataStoreUnavailableError
        return error_cls(
            f"Otter Cove could not open its local-data store: {exc}",
            path=self.path,
            recovery_options=_RECOVERY_OPTIONS,
        )

    def _check_integrity(self) -> None:
        try:
            row = self.connection.execute("PRAGMA quick_check").fetchone()
        except sqlite3.DatabaseError as exc:
            raise DataStoreCorruptError(
                f"The local-data store could not be checked: {exc}",
                path=self.path,
                recovery_options=_RECOVERY_OPTIONS,
            ) from exc
        if row is None or str(row[0]).lower() != "ok":
            detail = row[0] if row else "unknown integrity error"
            raise DataStoreCorruptError(
                f"The local-data store failed SQLite integrity checking: {detail}",
                path=self.path,
                recovery_options=_RECOVERY_OPTIONS,
            )

    def _migrate(self) -> None:
        current = int(self.connection.execute("PRAGMA user_version").fetchone()[0])
        if current > SCHEMA_VERSION:
            raise DataMigrationError(
                f"Local-data schema {current} is newer than this build supports ({SCHEMA_VERSION}).",
                path=self.path,
                recovery_options=("Open the store with a newer compatible Otter Cove build.",),
            )
        for migration in MIGRATIONS:
            if migration.version <= current:
                continue
            try:
                # executescript is used because migrations contain multiple DDL statements.
                # The BEGIN/COMMIT live inside the script so the whole migration is atomic.
                self.connection.executescript(
                    "BEGIN IMMEDIATE;\n"
                    + migration.sql
                    + f"\nPRAGMA user_version = {migration.version};\nCOMMIT;"
                )
            except sqlite3.DatabaseError as exc:
                if self.connection.in_transaction:
                    self.connection.execute("ROLLBACK")
                raise DataMigrationError(
                    f"Schema migration {migration.version} ({migration.name}) failed: {exc}",
                    path=self.path,
                    recovery_options=_RECOVERY_OPTIONS,
                ) from exc
            current = migration.version

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        conn = self.connection
        try:
            conn.execute("BEGIN IMMEDIATE")
        except sqlite3.DatabaseError as exc:
            raise self._classify_open_error(exc) from exc
        try:
            yield conn
        except sqlite3.IntegrityError:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        except sqlite3.DatabaseError as exc:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise self._classify_open_error(exc) from exc
        except Exception:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        else:
            try:
                conn.execute("COMMIT")
            except sqlite3.DatabaseError as exc:
                if conn.in_transaction:
                    conn.execute("ROLLBACK")
                raise self._classify_open_error(exc) from exc

    def schema_version(self) -> int:
        return int(self.connection.execute("PRAGMA user_version").fetchone()[0])

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def __enter__(self) -> "SQLiteStore":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
