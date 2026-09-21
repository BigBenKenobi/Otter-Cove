from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, slots=True)
class CommandSpec:
    command_id: str
    label: str
    default_binding: str
    scope: str = "window"
    enabled: bool = True
    disabled_reason: str = ""


DEFAULT_COMMANDS = (
    CommandSpec("navigation.new_chat", "New Chat", "Ctrl+N"),
    CommandSpec("navigation.search", "Search", "Ctrl+F"),
    CommandSpec("navigation.theme", "Theme", "Ctrl+Shift+T"),
    CommandSpec("navigation.settings", "Settings", "Ctrl+,"),
    CommandSpec("session.favorite", "Favourite current session", "Ctrl+Alt+F", enabled=False, disabled_reason="Session favourites arrive with the session-management milestone."),
    CommandSpec("session.delete", "Delete current session", "Ctrl+Shift+Delete", enabled=False, disabled_reason="Session deletion UI arrives with the session-management milestone."),
    CommandSpec("session.incognito", "Toggle Nobody mode", "Ctrl+Shift+I"),
    CommandSpec("tools.open", "Open Tools", "Ctrl+Shift+O"),
    CommandSpec("speech.tts", "TTS demo", "Ctrl+Shift+S"),
)


class ShortcutConflict(ValueError):
    def __init__(self, sequence: str, existing_command: str) -> None:
        super().__init__(f"{sequence} is already assigned to {existing_command}")
        self.sequence = sequence
        self.existing_command = existing_command


class CommandBindings:
    """Pure command/binding model with conflict detection and reset semantics."""

    def __init__(self, specs: Iterable[CommandSpec] = DEFAULT_COMMANDS, custom: dict[str, str] | None = None) -> None:
        specs = tuple(specs)
        self.specs = {spec.command_id: spec for spec in specs}
        if len(self.specs) != len(specs):
            raise ValueError("Duplicate command IDs are not allowed")
        self._bindings = {command_id: spec.default_binding for command_id, spec in self.specs.items()}
        for command_id, sequence in (custom or {}).items():
            if command_id in self.specs:
                self._bindings[command_id] = self.normalize(sequence)
        self._validate_conflicts()

    @staticmethod
    def normalize(sequence: str) -> str:
        # Qt canonicalization happens in CommandManager. The pure layer keeps a
        # stable human-readable form and treats case/whitespace as insignificant.
        return "+".join(part.strip() for part in str(sequence).strip().split("+") if part.strip())

    def binding(self, command_id: str) -> str:
        return self._bindings[command_id]

    def all_bindings(self) -> dict[str, str]:
        return dict(self._bindings)

    def rebind(self, command_id: str, sequence: str) -> None:
        self._require(command_id)
        normalized = self.normalize(sequence)
        if normalized:
            conflict = self.conflict_for(command_id, normalized)
            if conflict is not None:
                raise ShortcutConflict(normalized, conflict)
        self._bindings[command_id] = normalized

    def clear(self, command_id: str) -> None:
        self._require(command_id)
        self._bindings[command_id] = ""

    def reset(self, command_id: str) -> None:
        self._require(command_id)
        default = self.specs[command_id].default_binding
        conflict = self.conflict_for(command_id, default)
        if conflict is not None:
            raise ShortcutConflict(default, conflict)
        self._bindings[command_id] = default

    def reset_all(self) -> None:
        defaults = {cid: spec.default_binding for cid, spec in self.specs.items()}
        old = self._bindings
        self._bindings = defaults
        try:
            self._validate_conflicts()
        except Exception:
            self._bindings = old
            raise

    def conflict_for(self, command_id: str, sequence: str) -> str | None:
        normalized = self.normalize(sequence).casefold()
        if not normalized:
            return None
        scope = self.specs[command_id].scope
        for other_id, other_binding in self._bindings.items():
            if other_id == command_id:
                continue
            if self.specs[other_id].scope != scope:
                continue
            if self.normalize(other_binding).casefold() == normalized:
                return other_id
        return None

    def _require(self, command_id: str) -> None:
        if command_id not in self.specs:
            raise KeyError(command_id)

    def _validate_conflicts(self) -> None:
        for command_id, sequence in self._bindings.items():
            if sequence:
                conflict = self.conflict_for(command_id, sequence)
                if conflict is not None:
                    raise ShortcutConflict(sequence, conflict)
