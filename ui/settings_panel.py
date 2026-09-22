"""Reusable Settings window pages for appearance and keyboard commands.

The panel edits declarative preferences and command bindings supplied by the
application shell. Controls whose runtime consumers do not exist yet remain
visible but disabled with an explicit reason, so stored future configuration is
not presented as working protection, search, or shell functionality.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QKeySequenceEdit,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from core.command_registry import CommandSpec
from core.routes import RouteSpec
from .theme_panel import Section


class SettingsPanel(QFrame):
    """Phase-A settings surface for Appearance and keyboard bindings."""

    appearanceChanged = Signal(dict)
    sidebarVisibilityChanged = Signal(str, bool)
    resetAppearanceRequested = Signal()
    shortcutChangeRequested = Signal(str, str)
    shortcutClearRequested = Signal(str)
    shortcutResetRequested = Signal(str)
    shortcutResetAllRequested = Signal()

    def __init__(
        self,
        appearance: Mapping[str, object],
        sidebar_routes: Sequence[RouteSpec],
        command_specs: Sequence[CommandSpec],
        bindings: Mapping[str, str],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("SettingsPanel")
        self.command_specs = tuple(command_specs)
        self._binding_edits: dict[str, QKeySequenceEdit] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        tabs = QFrame()
        tabs.setObjectName("TabBar")
        tab_layout = QHBoxLayout(tabs)
        tab_layout.setContentsMargins(10, 0, 10, 0)
        self.appearance_tab = QPushButton("Appearance")
        self.shortcuts_tab = QPushButton("Shortcuts")
        group = QButtonGroup(self)
        group.setExclusive(True)
        for button in (self.appearance_tab, self.shortcuts_tab):
            button.setObjectName("TabButton")
            button.setCheckable(True)
            button.setCursor(Qt.PointingHandCursor)
            group.addButton(button)
            tab_layout.addWidget(button)
        self.appearance_tab.setChecked(True)
        tab_layout.addStretch()
        root.addWidget(tabs)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_appearance(appearance, sidebar_routes))
        self.stack.addWidget(self._build_shortcuts(bindings))
        root.addWidget(self.stack, 1)
        self.appearance_tab.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.shortcuts_tab.clicked.connect(lambda: self.stack.setCurrentIndex(1))

    def _scroll_page(self) -> tuple[QScrollArea, QWidget, QVBoxLayout]:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        host = QWidget()
        host.setObjectName("ThemeScrollHost")
        layout = QVBoxLayout(host)
        layout.setContentsMargins(12, 12, 12, 14)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(host)
        return scroll, host, layout

    def _build_appearance(self, appearance: Mapping[str, object], sidebar_routes: Sequence[RouteSpec]) -> QScrollArea:
        """Build live appearance controls and label unavailable capabilities."""

        scroll, _host, root = self._scroll_page()

        chat = Section("Chat & composer", "◌")
        grid = QGridLayout()
        checks = [
            ("Full-width composer", "full_width", "Allow the composer to use the available chat width."),
            ("Show welcome", "show_welcome", "Show the Otter Cove welcome copy on an empty chat."),
            ("Show Nobody", "show_nobody", "Show the ephemeral Nobody control. Hiding it does not change an active session."),
            ("Session storage status", "show_status_summaries", "Show whether the selected session uses persistent or memory-only storage."),
            ("Sensitive-span blur", "sensitive_blur", "Preference used by explicitly marked demo spans; general secret detection is not implied."),
            ("Web Search action", "show_web_search", "Show Web Search beneath the composer."),
            ("Shell action", "show_shell", "Show Shell access beneath the composer."),
        ]
        unavailable = {
            "sensitive_blur": "Unavailable until sensitive-span rendering is implemented; this setting does not currently protect content.",
            "show_web_search": "Unavailable until a web-search action exists; conversation Search is a separate feature.",
            "show_shell": "Unavailable until the composer has a bounded shell action; no command execution is connected.",
        }
        self.appearance_checks: dict[str, QCheckBox] = {}
        for row, (label, key, tooltip) in enumerate(checks):
            reason = unavailable.get(key)
            checkbox = QCheckBox(f"{label} (unavailable)" if reason else label)
            checkbox.setChecked(bool(appearance.get(key, False)))
            checkbox.setToolTip(reason or tooltip)
            checkbox.setAccessibleName(f"{label}, unavailable" if reason else label)
            checkbox.setEnabled(reason is None)
            checkbox.toggled.connect(lambda value, k=key: self.appearanceChanged.emit({k: bool(value)}))
            self.appearance_checks[key] = checkbox
            grid.addWidget(checkbox, row, 0, 1, 2)

        grid.addWidget(QLabel("Emoji presentation"), len(checks), 0)
        self.emoji_combo = QComboBox()
        self.emoji_combo.addItems(["Native", "Minimal"])
        self.emoji_combo.setCurrentText(str(appearance.get("emoji_mode", "Native")))
        self.emoji_combo.setToolTip("Native keeps decorative symbols; Minimal removes optional decorative glyphs.")
        self.emoji_combo.currentTextChanged.connect(lambda value: self.appearanceChanged.emit({"emoji_mode": value}))
        grid.addWidget(self.emoji_combo, len(checks), 1)
        chat.layout.addLayout(grid)
        root.addWidget(chat)

        sidebar = Section("Sidebar entries", "☰")
        vis = appearance.get("sidebar_visible", {})
        vis = vis if isinstance(vis, Mapping) else {}
        self.sidebar_checks: dict[str, QCheckBox] = {}
        sidebar_grid = QGridLayout()
        for index, route in enumerate(sidebar_routes):
            checkbox = QCheckBox(route.title)
            checkbox.setChecked(bool(vis.get(route.key, True)))
            checkbox.setToolTip(f"Show {route.title} in the sidebar. Stable shortcuts remain available where defined.")
            checkbox.toggled.connect(lambda value, key=route.key: self.sidebarVisibilityChanged.emit(key, bool(value)))
            self.sidebar_checks[route.key] = checkbox
            sidebar_grid.addWidget(checkbox, index // 2, index % 2)
        sidebar.layout.addLayout(sidebar_grid)
        root.addWidget(sidebar)

        note = QLabel("Settings and New Chat keep stable keyboard commands even when navigation surfaces are hidden.")
        note.setObjectName("FeatureMuted")
        note.setWordWrap(True)
        root.addWidget(note)

        reset = QPushButton("Reset appearance defaults")
        reset.setObjectName("OutlineButton")
        reset.setCursor(Qt.PointingHandCursor)
        reset.clicked.connect(self.resetAppearanceRequested.emit)
        root.addWidget(reset, alignment=Qt.AlignLeft)
        root.addStretch()
        return scroll

    def _build_shortcuts(self, bindings: Mapping[str, str]) -> QScrollArea:
        scroll, _host, root = self._scroll_page()
        section = Section("Keyboard commands", "⌨")
        grid = QGridLayout()
        grid.setColumnStretch(1, 1)
        for row, spec in enumerate(self.command_specs):
            label = QLabel(spec.label)
            label.setToolTip(spec.command_id)
            grid.addWidget(label, row, 0)
            editor = QKeySequenceEdit(QKeySequence(str(bindings.get(spec.command_id, spec.default_binding))))
            editor.setAccessibleName(f"Shortcut for {spec.label}")
            editor.setEnabled(spec.enabled)
            if not spec.enabled:
                editor.setToolTip(spec.disabled_reason)
            editor.editingFinished.connect(
                lambda cid=spec.command_id, control=editor: self.shortcutChangeRequested.emit(
                    cid, control.keySequence().toString(QKeySequence.SequenceFormat.PortableText)
                )
            )
            self._binding_edits[spec.command_id] = editor
            grid.addWidget(editor, row, 1)

            clear = QPushButton("Clear")
            clear.setObjectName("MiniButton")
            clear.setCursor(Qt.PointingHandCursor)
            clear.setEnabled(spec.enabled)
            clear.clicked.connect(lambda _checked=False, cid=spec.command_id: self.shortcutClearRequested.emit(cid))
            grid.addWidget(clear, row, 2)
            reset = QPushButton("Reset")
            reset.setObjectName("MiniButton")
            reset.setCursor(Qt.PointingHandCursor)
            reset.setEnabled(spec.enabled)
            reset.clicked.connect(lambda _checked=False, cid=spec.command_id: self.shortcutResetRequested.emit(cid))
            grid.addWidget(reset, row, 3)
            if not spec.enabled:
                label.setText(f"{spec.label} · unavailable")
                label.setToolTip(f"{spec.command_id} — {spec.disabled_reason}")
        section.layout.addLayout(grid)
        root.addWidget(section)

        reset_all = QPushButton("Reset all shortcuts")
        reset_all.setObjectName("OutlineButton")
        reset_all.setCursor(Qt.PointingHandCursor)
        reset_all.clicked.connect(self.shortcutResetAllRequested.emit)
        root.addWidget(reset_all, alignment=Qt.AlignLeft)
        root.addStretch()
        return scroll

    def refresh_appearance(self, appearance: Mapping[str, object]) -> None:
        for key, checkbox in self.appearance_checks.items():
            previous = checkbox.blockSignals(True)
            checkbox.setChecked(bool(appearance.get(key, False)))
            checkbox.blockSignals(previous)
        previous = self.emoji_combo.blockSignals(True)
        self.emoji_combo.setCurrentText(str(appearance.get("emoji_mode", "Native")))
        self.emoji_combo.blockSignals(previous)
        visibility = appearance.get("sidebar_visible", {})
        visibility = visibility if isinstance(visibility, Mapping) else {}
        for route, checkbox in self.sidebar_checks.items():
            previous = checkbox.blockSignals(True)
            checkbox.setChecked(bool(visibility.get(route, True)))
            checkbox.blockSignals(previous)

    def refresh_shortcuts(self, bindings: Mapping[str, str]) -> None:
        for command_id, editor in self._binding_edits.items():
            previous = editor.blockSignals(True)
            editor.setKeySequence(QKeySequence(str(bindings.get(command_id, ""))))
            editor.blockSignals(previous)
