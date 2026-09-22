"""Capability-aware AI default selection over the shared model registry.

Model records live in SQLite; lightweight user choices live in ``AppSettings``.
This resolver is the only place that turns role names into model IDs, ensuring
future composer, comparison, research and image consumers share compatibility and
stale-reference behavior. It performs no inference and stores no credentials.
"""

from __future__ import annotations

import json

from .data import DataValidationError, ModelRecord, ModelService
from .settings import AppSettings


ROLE_CAPABILITIES = {
    "chat": "chat",
    "utility": "utility",
    "vision": "vision",
    "research": "research",
    "images": "images",
}


class ModelDefaults:
    """Validate, persist and resolve capability-specific model selections.

    The application shell owns one instance alongside its ``AppSettings`` and
    ``ModelService``. Invalid or removed IDs are ignored during reads and can be
    explicitly purged, preventing downstream consumers from submitting stale IDs.
    """

    SETTINGS_KEY = "models/defaults"

    def __init__(self, settings: AppSettings, models: ModelService) -> None:
        self._settings = settings
        self._models = models

    def assignments(self) -> dict[str, str]:
        """Return only stored role assignments that remain compatible and enabled."""

        payload = self._read()
        valid: dict[str, str] = {}
        for role, capability in ROLE_CAPABILITIES.items():
            model_id = payload.get(role)
            record = self._models.get(model_id) if isinstance(model_id, str) else None
            if record and record.enabled and capability in record.config.get("capabilities", []):
                valid[role] = record.id
        return valid

    def assign(self, role: str, model_id: str | None) -> None:
        """Assign a compatible model to a role, or clear the role with ``None``."""

        normalized_role = role.strip().lower()
        if normalized_role not in ROLE_CAPABILITIES:
            raise DataValidationError(f"Unsupported model default role: {role}.")
        payload = self._read()
        if model_id is None:
            payload.pop(normalized_role, None)
        else:
            record = self._require_compatible(model_id, ROLE_CAPABILITIES[normalized_role])
            payload[normalized_role] = record.id
        self._write(payload)

    def resolve(self, role: str) -> ModelRecord | None:
        """Resolve one role to its current compatible model, if assigned."""

        model_id = self.assignments().get(role.strip().lower())
        return self._models.get(model_id) if model_id else None

    def fallbacks(self) -> list[ModelRecord]:
        """Resolve the ordered, duplicate-free chat fallback chain."""

        raw = self._read().get("fallbacks", [])
        identifiers = raw if isinstance(raw, list) else []
        resolved: list[ModelRecord] = []
        seen: set[str] = set()
        for model_id in identifiers:
            if not isinstance(model_id, str) or model_id in seen:
                continue
            record = self._models.get(model_id)
            if record and record.enabled and "chat" in record.config.get("capabilities", []):
                resolved.append(record)
                seen.add(record.id)
        return resolved

    def set_fallbacks(self, model_ids: list[str] | tuple[str, ...]) -> None:
        """Persist an ordered chat-capable fallback chain without duplicates."""

        unique_ids = list(dict.fromkeys(model_ids))
        for model_id in unique_ids:
            self._require_compatible(model_id, "chat")
        payload = self._read()
        payload["fallbacks"] = unique_ids
        self._write(payload)

    def invalidate(self, model_id: str) -> tuple[str, ...]:
        """Clear every role referencing ``model_id`` and return affected role names."""

        payload = self._read()
        affected = tuple(sorted(role for role, value in payload.items() if value == model_id))
        for role in affected:
            payload.pop(role, None)
        fallbacks = payload.get("fallbacks", [])
        removed_fallback = isinstance(fallbacks, list) and model_id in fallbacks
        if removed_fallback:
            payload["fallbacks"] = [value for value in fallbacks if value != model_id]
        if affected or removed_fallback:
            self._write(payload)
        return affected

    def _require_compatible(self, model_id: str, capability: str) -> ModelRecord:
        """Return a compatible enabled record or raise a user-oriented validation error."""

        record = self._models.get(model_id)
        if record is None:
            raise DataValidationError("The selected model no longer exists.")
        if not record.enabled:
            raise DataValidationError(f'{record.name} is disabled.')
        if capability not in record.config.get("capabilities", []):
            raise DataValidationError(f'{record.name} does not support {capability}.')
        return record

    def _read(self) -> dict[str, object]:
        """Decode the QSettings value defensively, treating malformed state as empty."""

        raw = self._settings.value(self.SETTINGS_KEY, "{}")
        try:
            value = json.loads(str(raw))
        except (TypeError, ValueError, json.JSONDecodeError):
            return {}
        return value if isinstance(value, dict) else {}

    def _write(self, payload: dict[str, object]) -> None:
        """Persist deterministic JSON so restart behavior is stable and inspectable."""

        self._settings.set_value(self.SETTINGS_KEY, json.dumps(payload, sort_keys=True))
        self._settings.sync()
