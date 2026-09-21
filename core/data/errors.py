from __future__ import annotations

from pathlib import Path


class DataStoreError(RuntimeError):
    """Base error for local-data failures that must never silently destroy data."""

    def __init__(self, message: str, *, path: Path | None = None, recovery_options: tuple[str, ...] = ()) -> None:
        super().__init__(message)
        self.path = path
        self.recovery_options = recovery_options

    def user_message(self) -> str:
        lines = [str(self)]
        if self.path is not None:
            lines.append(f"Store: {self.path}")
        if self.recovery_options:
            lines.append("")
            lines.append("Recovery options:")
            lines.extend(f"• {option}" for option in self.recovery_options)
        lines.append("")
        lines.append("Stark Studio will not delete or replace this store automatically.")
        return "\n".join(lines)


class DataStoreCorruptError(DataStoreError):
    pass


class DataStoreUnavailableError(DataStoreError):
    pass


class DataMigrationError(DataStoreError):
    pass


class DataValidationError(ValueError):
    pass


class PersistencePolicyError(DataValidationError):
    pass
