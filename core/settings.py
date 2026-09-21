from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import QByteArray, QRect, QSettings

from .data.policy import assert_no_credentials


class AppSettings:
    """Typed QSettings wrapper for preferences and window geometry only.

    Local user content belongs in the SQLite repositories. Credential-like keys are
    deliberately rejected here so future integration secrets cannot accidentally
    leak into ordinary preferences, exports or logs.
    """

    def __init__(self, ini_path: str | Path | None = None) -> None:
        if ini_path is None:
            override = os.environ.get("STARK_STUDIO_SETTINGS_PATH")
            ini_path = Path(override).expanduser() if override else None
        if ini_path is None:
            self._settings = QSettings("Stark Studio", "Stark Studio")
        else:
            path = Path(ini_path).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            self._settings = QSettings(str(path), QSettings.Format.IniFormat)

    def value(self, key: str, default=None):
        return self._settings.value(key, default)

    def bool(self, key: str, default: bool = False) -> bool:
        value = self._settings.value(key, default)
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "yes", "on"}

    def float(self, key: str, default: float = 0.0) -> float:
        try:
            return float(self._settings.value(key, default))
        except (TypeError, ValueError):
            return float(default)

    def int(self, key: str, default: int = 0) -> int:
        try:
            return int(self._settings.value(key, default))
        except (TypeError, ValueError):
            return int(default)

    def set_value(self, key: str, value) -> None:
        assert_no_credentials({key: value}, path="QSettings")
        self._settings.setValue(key, value)

    def remove(self, key: str) -> None:
        self._settings.remove(key)

    def sync(self) -> None:
        self._settings.sync()

    def status(self) -> QSettings.Status:
        return self._settings.status()

    def window_normal_rect(self, key: str, default: QRect) -> QRect:
        """Return the persisted full-size geometry for a floating tool.

        Older builds stored one ambiguous ``rect`` value, so use it as a
        compatibility fallback exactly once rather than discarding user layout.
        """
        fallback = self._settings.value(f"windows/{key}/rect", default)
        if not isinstance(fallback, QRect):
            fallback = default
        value = self._settings.value(f"windows/{key}/normal_rect", fallback)
        return value if isinstance(value, QRect) else QRect(fallback)

    def set_window_normal_rect(self, key: str, rect: QRect) -> None:
        self._settings.setValue(f"windows/{key}/normal_rect", QRect(rect))

    def window_minimized_rect(self, key: str, default: QRect) -> QRect:
        value = self._settings.value(f"windows/{key}/minimized_rect", default)
        return value if isinstance(value, QRect) else QRect(default)

    def set_window_minimized_rect(self, key: str, rect: QRect) -> None:
        self._settings.setValue(f"windows/{key}/minimized_rect", QRect(rect))

    # Compatibility aliases for code/tests from the earlier foundation build.
    def window_rect(self, key: str, default: QRect) -> QRect:
        return self.window_normal_rect(key, default)

    def set_window_rect(self, key: str, rect: QRect) -> None:
        self.set_window_normal_rect(key, rect)

    def main_geometry(self) -> QByteArray | None:
        value = self._settings.value("main/geometry")
        return value if isinstance(value, QByteArray) and not value.isEmpty() else None

    def set_main_geometry(self, geometry: QByteArray) -> None:
        self._settings.setValue("main/geometry", geometry)
