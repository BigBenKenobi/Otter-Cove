from __future__ import annotations

import json
from collections.abc import Callable

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QAction, QKeySequence

from .command_registry import CommandBindings, CommandSpec, DEFAULT_COMMANDS, ShortcutConflict


class CommandManager(QObject):
    """Qt QAction layer over the pure canonical command/binding registry."""

    bindingsChanged = Signal()

    def __init__(self, owner, settings, handlers: dict[str, Callable[[], None]], parent=None) -> None:
        super().__init__(parent or owner)
        self.owner = owner
        self.settings = settings
        self.handlers = dict(handlers)
        self.load_warning = ""
        custom = self._load_custom()
        try:
            self.bindings = CommandBindings(DEFAULT_COMMANDS, custom)
        except ShortcutConflict as exc:
            # A hand-edited/corrupted settings file must never prevent the app
            # from starting. Preserve the file for inspection, fall back to the
            # documented defaults, and let the shell surface a non-modal issue.
            self.load_warning = f"Stored shortcut bindings were ignored: {exc}"
            self.bindings = CommandBindings(DEFAULT_COMMANDS)
        self.actions: dict[str, QAction] = {}
        self._install_actions()

    @property
    def specs(self) -> tuple[CommandSpec, ...]:
        return DEFAULT_COMMANDS

    def binding(self, command_id: str) -> str:
        return self.bindings.binding(command_id)

    def rebind(self, command_id: str, sequence: str) -> None:
        canonical = self._canonical(sequence)
        self.bindings.rebind(command_id, canonical)
        self._apply_action(command_id)
        self._persist()
        self.bindingsChanged.emit()

    def clear(self, command_id: str) -> None:
        self.bindings.clear(command_id)
        self._apply_action(command_id)
        self._persist()
        self.bindingsChanged.emit()

    def reset(self, command_id: str) -> None:
        self.bindings.reset(command_id)
        self._apply_action(command_id)
        self._persist()
        self.bindingsChanged.emit()

    def reset_all(self) -> None:
        self.bindings.reset_all()
        for command_id in self.actions:
            self._apply_action(command_id)
        self._persist()
        self.bindingsChanged.emit()

    def tooltip(self, command_id: str) -> str:
        spec = self.bindings.specs[command_id]
        binding = self.binding(command_id)
        suffix = f" ({binding})" if binding else " (no shortcut)"
        if not spec.enabled:
            return f"{spec.label}{suffix} — {spec.disabled_reason}"
        return f"{spec.label}{suffix}"

    def _install_actions(self) -> None:
        for spec in self.specs:
            action = QAction(spec.label, self.owner)
            action.setObjectName(f"Command::{spec.command_id}")
            action.setShortcutContext(Qt.ShortcutContext.WindowShortcut)
            handler = self.handlers.get(spec.command_id)
            enabled = spec.enabled and handler is not None
            action.setEnabled(enabled)
            if not enabled:
                action.setStatusTip(spec.disabled_reason or "No handler is available in this milestone.")
            elif handler is not None:
                action.triggered.connect(handler)
            self.actions[spec.command_id] = action
            self.owner.addAction(action)
            self._apply_action(spec.command_id)

    def _apply_action(self, command_id: str) -> None:
        action = self.actions[command_id]
        sequence = self.binding(command_id)
        action.setShortcut(QKeySequence(sequence) if sequence else QKeySequence())
        action.setToolTip(self.tooltip(command_id))

    def _load_custom(self) -> dict[str, str]:
        raw = self.settings.value("shortcuts/bindings", "")
        if not raw:
            return {}
        try:
            parsed = json.loads(str(raw))
        except (TypeError, json.JSONDecodeError):
            return {}
        if not isinstance(parsed, dict):
            return {}
        result: dict[str, str] = {}
        for command_id, sequence in parsed.items():
            if isinstance(command_id, str) and isinstance(sequence, str):
                result[command_id] = self._canonical(sequence)
        return result

    def _persist(self) -> None:
        self.settings.set_value("shortcuts/bindings", json.dumps(self.bindings.all_bindings(), sort_keys=True))

    @staticmethod
    def _canonical(sequence: str) -> str:
        if not str(sequence).strip():
            return ""
        key_sequence = QKeySequence(str(sequence))
        return key_sequence.toString(QKeySequence.SequenceFormat.PortableText)


__all__ = ["CommandManager", "ShortcutConflict"]
