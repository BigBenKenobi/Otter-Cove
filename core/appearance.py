from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from typing import Any


@dataclass(frozen=True)
class AppearanceDefaults:
    full_width: bool = False
    show_welcome: bool = True
    show_nobody: bool = True
    emoji_mode: str = "Native"
    show_status_summaries: bool = False
    sensitive_blur: bool = True
    show_web_search: bool = True
    show_shell: bool = True


DEFAULTS = AppearanceDefaults()
EMOJI_MODES = ("Native", "Minimal")


class AppearancePreferences:
    """Declarative preference model backed by the existing AppSettings wrapper.

    It intentionally contains no Qt imports, so defaults/reset/serialization can be
    tested headlessly. UI modules receive one snapshot and decide presentation.
    """

    def __init__(self, settings, sidebar_routes: tuple[str, ...]) -> None:
        self.settings = settings
        self.sidebar_routes = tuple(sidebar_routes)
        self._values = self._load_values()
        self._sidebar_visible = self._load_sidebar_visibility()

    def snapshot(self) -> dict[str, Any]:
        result = dict(self._values)
        result["sidebar_visible"] = dict(self._sidebar_visible)
        return result

    def get(self, key: str):
        if key == "sidebar_visible":
            return dict(self._sidebar_visible)
        return self._values[key]

    def set(self, key: str, value) -> None:
        if key == "emoji_mode":
            value = str(value)
            if value not in EMOJI_MODES:
                raise ValueError(f"Unsupported emoji mode: {value!r}")
        if key not in self._values:
            raise KeyError(key)
        if isinstance(self._values[key], bool):
            value = bool(value)
        self._values[key] = value
        self.settings.set_value(f"appearance/preferences/{key}", value)

    def set_sidebar_visible(self, route: str, visible: bool) -> None:
        if route not in self._sidebar_visible:
            raise KeyError(route)
        self._sidebar_visible[route] = bool(visible)
        self.settings.set_value(
            "appearance/preferences/sidebar_visible",
            json.dumps(self._sidebar_visible, sort_keys=True),
        )

    def reset(self) -> None:
        self._values = asdict(DEFAULTS)
        self._sidebar_visible = {route: True for route in self.sidebar_routes}
        for key, value in self._values.items():
            self.settings.set_value(f"appearance/preferences/{key}", value)
        self.settings.set_value(
            "appearance/preferences/sidebar_visible",
            json.dumps(self._sidebar_visible, sort_keys=True),
        )

    def _load_values(self) -> dict[str, Any]:
        result = asdict(DEFAULTS)
        for key, default in tuple(result.items()):
            stored = self.settings.value(f"appearance/preferences/{key}", default)
            if isinstance(default, bool):
                if isinstance(stored, bool):
                    result[key] = stored
                else:
                    result[key] = str(stored).strip().lower() in {"1", "true", "yes", "on"}
            else:
                result[key] = str(stored)
        if result["emoji_mode"] not in EMOJI_MODES:
            result["emoji_mode"] = DEFAULTS.emoji_mode
        return result

    def _load_sidebar_visibility(self) -> dict[str, bool]:
        result = {route: True for route in self.sidebar_routes}
        raw = self.settings.value("appearance/preferences/sidebar_visible", "")
        if not raw:
            return result
        try:
            parsed = json.loads(str(raw))
        except (TypeError, json.JSONDecodeError):
            return result
        if not isinstance(parsed, dict):
            return result
        for route in result:
            if route in parsed:
                result[route] = bool(parsed[route])
        return result
