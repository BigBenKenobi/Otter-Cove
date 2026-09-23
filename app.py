"""Compose and coordinate Otter Cove's top-level Qt application shell.

``main.py`` creates :class:`MainWindow`; this module then connects the durable
settings/data layer, shared shell state, route/command registries, and visual
widgets.  It deliberately contains orchestration rather than feature-specific
business logic.  Widgets communicate outward through signals, while this shell
translates those signals into route changes, persisted preferences, feedback,
or floating-window lifecycle operations.

The principal data flows are:

* QSettings/SQLite -> managers and widgets while the shell is constructed;
* user interactions -> Qt signals -> the methods below -> managers/services;
* manager signals -> widget refreshes and stylesheet/background updates; and
* close events -> geometry/preferences/data-service cleanup before Qt exits.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QRect, QTimer, Qt
from PySide6.QtWidgets import QApplication, QFileDialog, QHBoxLayout, QMainWindow, QMessageBox, QWidget

from core import (
    AppDataServices, AppSettings, DEFAULT_ROUTE_REGISTRY, RouteRegistry, ShellState,
    Theme, ThemeManager,
)
from core.appearance import AppearancePreferences
from core.command_manager import CommandManager, ShortcutConflict
from core.data import DataStoreError, DataValidationError
from core.theme import THEMES
from core.theme_logic import ThemeBundleError, load_theme_bundle, save_theme_bundle_atomic
from ui.feedback import FeedbackManager
from ui.placeholders import FeaturePlaceholder
from ui.sidebar import Sidebar
from ui.settings_panel import SettingsPanel
from ui.studio_window import StudioWindowManager
from ui.theme_panel import ThemePanel
from ui.workspace import Workspace


class MainWindow(QMainWindow):
    """Top-level owner and composition root for one running Otter Cove shell.

    ``main.main`` creates this window after Qt has initialized.  The window owns
    the long-lived settings wrapper, SQLite-facing services, route state, theme
    manager, command actions, workspace, and embedded floating-window manager.
    Individual tools remain children of ``workspace`` and do not call one another
    directly; their signals return here so routing and persistence stay centralized.

    Constructor injection is primarily useful for tests: callers may provide an
    isolated data service, settings instance, or route registry.  Normal desktop
    startup lets this class open the default local services and registry itself.

    Important owned state is intentionally split by lifecycle:

    * ``settings`` and ``data`` are durable infrastructure, closed/flushed during
      :meth:`closeEvent` rather than by individual panels;
    * ``shell_state``, ``appearance``, ``theme_manager``, and effect fields are
      canonical shell state that outlives a hidden/reopened floating tool; and
    * ``sidebar``, ``workspace``, ``feedback``, and ``window_manager`` are the
      presentation layer that projects that state into the running Qt widget tree.

    This division prevents hidden panels from becoming an accidental source of
    truth and makes it possible to restore presentation settings before a panel is
    opened for the first time.
    """

    def __init__(
        self,
        data_services: AppDataServices | None = None,
        settings: AppSettings | None = None,
        route_registry: RouteRegistry = DEFAULT_ROUTE_REGISTRY,
    ) -> None:
        """Build the shell, restore persisted presentation state, and wire signals.

        Initialization intentionally happens in dependency order.  Persistent
        services and state models come first; visual components consume those
        objects next; signal connections are made before deferred geometry and
        animation work is scheduled.  The ``QTimer`` calls defer screen-dependent
        recovery until the Qt event loop can report valid display geometry.
        """
        super().__init__()
        self.setWindowTitle("Otter Cove — PySide6 concept")
        self.setMinimumSize(1100, 680)

        # These objects outlive every feature panel.  SQLite content and QSettings
        # preferences have different storage responsibilities, so they are exposed
        # separately rather than making presentation code speak to the database.
        self.settings = settings or AppSettings()
        self.data = data_services or AppDataServices.open()
        self.route_registry = route_registry
        self.shell_state = ShellState()

        # Appearance preferences stay Qt-free in their model.  Passing only the
        # registry's sidebar route keys prevents a stale setting from inventing a
        # navigation item that the current application version does not expose.
        self.appearance = AppearancePreferences(
            self.settings, tuple(route.key for route in self.route_registry.sidebar_routes())
        )

        # ThemeManager is the single semantic-color/typography authority.  Apply
        # its saved application font before child widgets calculate their layouts.
        self.theme_manager = ThemeManager(self.settings, self)
        self.theme_manager.apply_saved_typography()

        # The central horizontal layout establishes the persistent shell: a
        # navigation sidebar on the left and a workspace that owns the chat,
        # background canvas, and overlay tool windows on the right.
        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Navigation begins at the sidebar, but it does not choose widgets itself.
        # Its route signal joins chat action links and QAction shortcuts at _route,
        # which keeps all navigation semantics in one dispatcher.
        self.sidebar = Sidebar(self.settings.bool("appearance/sidebar_collapsed", False))
        self.sidebar.navigationRequested.connect(self._route)
        # Collapse is a shell-chrome preference, not the appearance model's per
        # route visibility state, so it persists directly to its dedicated key.
        self.sidebar.collapsedChanged.connect(lambda value: self.settings.set_value("appearance/sidebar_collapsed", value))
        layout.addWidget(self.sidebar)

        # Workspace receives the theme and session service, then exposes only
        # widget-level signals to its parent.  In particular, MainWindow never
        # reaches through it to perform storage work after construction.
        self.workspace = Workspace(self.theme_manager.theme, self.data.sessions)
        layout.addWidget(self.workspace, 1)

        # Feedback is rendered over the workspace, while StudioWindowManager makes
        # feature panels child overlays.  This keeps the chat/draft mounted while
        # users open tools, instead of treating navigation as page replacement.
        self.feedback = FeedbackManager(self.workspace)
        self.window_manager = StudioWindowManager(self.workspace, self.settings)
        # Overlay tools are positioned in workspace coordinates.  Host resize can
        # invalidate persisted positions, so every workspace resize asks the window
        # manager to clamp visible children before their titlebars become stranded.
        self.workspace.resized.connect(self.window_manager.keep_in_bounds)
        # Chat actions reuse route metadata, and low-level storage exceptions cross
        # the chat-to-shell boundary as a user-displayable message rather than a
        # database exception that a presentation widget would need to interpret.
        self.workspace.chat.actionRequested.connect(self._route)
        self.workspace.chat.storageError.connect(self._show_storage_error)
        self._apply_appearance_snapshot()

        # Effect preferences are stored independently because a saved theme can
        # bundle them, while users may also adjust the active effect without
        # changing a theme.  Validate the saved effect name against this runtime's
        # manager so removed/unknown effect implementations fail safely to Leaves.
        self.effect_name = str(self.settings.value("appearance/effect/name", "Leaves"))
        if self.effect_name not in self.workspace.background.available_effects():
            self.effect_name = "Leaves"
        self.effect_color = str(self.settings.value("appearance/effect/color", self.theme_manager.theme.accent))
        self.effect_speed = self.settings.float("appearance/effect/speed", 1.0)
        self.effect_intensity = self.settings.float("appearance/effect/intensity", 1.0)
        self.effect_quality = self.settings.float("appearance/effect/quality", 1.0)
        self.effect_size = self.settings.float("appearance/effect/size", 1.0)
        self.effect_paused = self.settings.bool("appearance/effect/paused", False)

        # A selected saved theme owns its bundled effect settings on restart, so
        # it intentionally supersedes the standalone effect preference values.
        saved_bundle = self.theme_manager.selected_saved_bundle()
        if saved_bundle is not None:
            self._load_effect_values(saved_bundle["effect"], persist=False)
        self._apply_effect_state()

        # Theme signals are deliberately separated by concern.  A palette change
        # updates the canvas and theme selector; typography/layout changes only
        # require stylesheet regeneration; a named bundle additionally carries its
        # own effect payload and must be reconciled with standalone effect settings.
        self.theme_manager.themeChanged.connect(self._on_theme_changed)
        self.theme_manager.typographyChanged.connect(lambda _family, _size: self._apply_styles())
        self.theme_manager.layoutChanged.connect(lambda _density, _frosted: self._apply_styles())
        self.theme_manager.themeBundleApplied.connect(self._apply_saved_theme_bundle)
        self._apply_styles()

        # CommandManager turns pure registry bindings into window-scoped Qt
        # actions.  The small handler map is the boundary from stable command IDs
        # to shell behavior; panels receive command metadata, not arbitrary calls.
        self.command_manager = CommandManager(
            self,
            self.settings,
            {
                "navigation.new_chat": lambda: self._route("new_chat"),
                "navigation.search": lambda: self._route("search"),
                "navigation.theme": lambda: self._route("theme"),
                "navigation.settings": lambda: self._route("settings"),
                "session.incognito": self._toggle_nobody,
                "tools.open": lambda: self._route("tools"),
                "speech.tts": self._tts_demo,
            },
            self,
        )
        # The manager installs actual QAction shortcuts.  This signal handles the
        # second half of the contract: all visible hints must describe the same
        # bindings that Qt will now recognize.
        self.command_manager.bindingsChanged.connect(self._on_bindings_changed)
        self._on_bindings_changed()
        if self.command_manager.load_warning:
            self.feedback.error(
                "Shortcut settings recovered",
                self.command_manager.load_warning,
                important=True,
            )

        # Qt reports application activation separately from this window's own
        # visibility/minimized state.  Both feed animation suspension to avoid
        # spending timer/paint work when the shell cannot be meaningfully viewed.
        app = QApplication.instance()
        if app is not None:
            app.applicationStateChanged.connect(lambda _state: self._sync_animation_suspension())

        # Restored geometry may reference a monitor that no longer exists.  Restore
        # first, then clamp on the next event-loop turn once screen bounds exist.
        geometry = self.settings.main_geometry()
        if geometry is not None and self.restoreGeometry(geometry):
            # Clamp once the application event loop has a screen/available geometry.
            QTimer.singleShot(0, self._ensure_main_window_visible)
        else:
            self.resize(1720, 900)
            QTimer.singleShot(0, self._ensure_main_window_visible)
        QTimer.singleShot(0, self._sync_animation_suspension)

    def _show_storage_error(self, message: str) -> None:
        """Surface a recoverable chat persistence failure through shared feedback.

        The chat widget detects the low-level failure but delegates presentation to
        the shell so important feedback uses the same accessible, persistent path
        as failures triggered by other feature panels.
        """
        self.feedback.error("Otter Cove local data", message, important=True)

    def _route(self, route: str) -> None:
        """Dispatch a route key from navigation, chat actions, or keyboard commands.

        Registered routes carry a kind that determines whether the activation
        resets chat state, opens a singleton floating tool, or displays an
        explicitly unavailable scaffold.  Unknown keys are still recorded in
        ``ShellState`` and rendered as unavailable rather than being silently
        ignored, which makes missing integrations visible during development.
        """
        spec = self.route_registry.get(route)
        if spec is None:
            # Unknown keys have no sidebar definition or kind.  Treat them like an
            # unavailable tool so state/history remains inspectable and developers
            # see an explicit scaffold rather than a dead navigation path.
            self.sidebar.set_active(None)
            self.shell_state.activate(route, is_tool=True)
            self._open_feature(route, unknown=True)
            return

        # ShellState is deliberately independent of the sidebar: a route can come
        # from a chat action or shortcut even when its sidebar button is hidden.
        self.shell_state.activate(route, is_tool=spec.kind in {"tool", "theme"})
        self.sidebar.set_active(route if route in self.sidebar.buttons else None)

        # Route kinds form a small control-flow protocol owned by RouteRegistry:
        # command routes act immediately and do not open a window; theme/settings
        # routes map to implemented singleton panels; all other registered routes
        # currently receive a clearly labelled placeholder panel.
        if spec.kind == "command":
            if route == "new_chat":
                self.workspace.chat.reset_chat()
            return
        if spec.kind == "theme":
            self._open_theme()
            return
        if route == "settings":
            self._open_settings()
            return
        self._open_feature(route)

    def _open_theme(self) -> None:
        """Open or focus the singleton theme tool and connect its editing signals.

        The factory is evaluated only on the first open by ``StudioWindowManager``.
        Reopening the same key therefore preserves unsaved panel-local UI state,
        while manager-owned theme/effect values remain the canonical application
        state.  The panel is populated from that canonical state at construction.
        """
        def factory() -> ThemePanel:
            """Create ThemePanel from canonical manager/effect state on first open.

            ``StudioWindowManager`` caches the result after this call.  The catalog
            is filtered so the panel can render built-ins and separately identify
            saved bundles, while font controls are set after construction because
            their current values live in ``ThemeManager``, not panel-local state.
            """
            # ``catalog`` includes built-ins plus saved themes.  ThemePanel's saved
            # section expects only custom keys, so preserve that category boundary.
            catalog = self.theme_manager.catalog()
            saved = {key: value for key, value in catalog.items() if key.startswith("custom:")}
            panel = ThemePanel(
                self.theme_manager.theme_key,
                self.theme_manager.theme,
                effect=self.effect_name,
                effect_color=self.effect_color,
                speed=self.effect_speed,
                intensity=self.effect_intensity,
                quality=self.effect_quality,
                size=self.effect_size,
                paused=self.effect_paused,
                density=self.theme_manager.density,
                frosted=self.theme_manager.frosted,
                saved_themes=saved,
            )
            panel.font_combo.setCurrentText(self.theme_manager.font_kind)
            panel.size_combo.setCurrentText(self.theme_manager.text_size)
            # ThemePanel emits intent; it never persists or applies semantic
            # changes itself.  These connections return each change to its owner.
            # Palette selection and palette customization take distinct paths:
            # selecting may reset overrides/apply a bundle, while customization
            # changes only allowed semantic color tokens in the active manager.
            panel.themeSelected.connect(self._select_theme)
            panel.customChanged.connect(self.theme_manager.customize)
            panel.resetCustomRequested.connect(self.theme_manager.reset_customizations)
            # Presentation/effect controls use partial change dictionaries.  Their
            # shell handlers merge those patches with stored state before sending a
            # complete snapshot back to the panel when needed.
            panel.typographyChanged.connect(self._apply_typography_changes)
            panel.layoutChanged.connect(self._apply_layout_changes)
            panel.effectChanged.connect(self.set_effect)
            panel.effectSettingsChanged.connect(self.apply_effect_settings)
            # File and saved-catalog operations belong here because they need both
            # dialog/feedback UI and ThemeManager's persistence/validation policy.
            panel.saveThemeRequested.connect(self._save_named_theme)
            panel.importThemeRequested.connect(self._import_theme)
            panel.exportThemeRequested.connect(self._export_theme)
            return panel

        self.window_manager.open_window(
            "theme",
            "Theme",
            factory,
            icon="◎",
            default_rect=QRect(44, 28, 570, 810),
        )

    def _open_settings(self) -> None:
        """Open or focus Settings with a snapshot of shell-owned preferences.

        The panel is a view/editor rather than a second preference store.  It gets
        a current appearance snapshot, valid sidebar routes, and command registry
        metadata, then reports requested mutations through the connected signals.
        """
        def factory() -> SettingsPanel:
            """Create the Settings editor using snapshots, registries, and bindings.

            Settings receives copies of current values and static metadata instead
            of references to mutable shell internals.  Its emitted edit requests
            therefore remain the only route for changing durable appearance and
            shortcut state; subsequent manager notifications refresh an open panel.
            """
            # These inputs describe what can be changed at this application version:
            # current preference values, legal sidebar routes, command specs, and
            # the persisted/effective shortcut map respectively.
            panel = SettingsPanel(
                self.appearance.snapshot(),
                self.route_registry.sidebar_routes(),
                self.command_manager.specs,
                self.command_manager.bindings.all_bindings(),
                str(self.data.store.path),
                self.data.store.schema_version(),
            )
            # Signals are grouped by ownership: appearance model mutations, sidebar
            # visibility mutations, then command-manager shortcut mutations.
            panel.appearanceChanged.connect(self._apply_appearance_changes)
            panel.sidebarVisibilityChanged.connect(self._set_sidebar_visibility)
            panel.resetAppearanceRequested.connect(self._reset_appearance)
            panel.shortcutChangeRequested.connect(self._rebind_shortcut)
            panel.shortcutClearRequested.connect(self._clear_shortcut)
            panel.shortcutResetRequested.connect(self._reset_shortcut)
            panel.shortcutResetAllRequested.connect(self._reset_all_shortcuts)
            panel.dataExportRequested.connect(self._export_local_data)
            panel.dataImportRequested.connect(self._import_local_data)
            panel.dataResetRequested.connect(self._reset_local_data)
            return panel

        self.window_manager.open_window(
            "settings",
            "Settings",
            factory,
            icon="⚙",
            default_rect=QRect(90, 46, 680, 720),
        )

    def _data_operation_message(self, operation: str, report) -> str:
        """Format service-owned affected/excluded details for feedback and Settings."""

        affected_total = sum(report.counts.values())
        affected = ", ".join(report.affected)
        excluded = ", ".join(report.excluded)
        path = f"\nFile: {report.path}" if report.path else ""
        return (
            f"{operation} completed for {affected_total} records."
            f"{path}\nAffected: {affected}.\nExcluded: {excluded}."
        )

    def _show_data_operation_result(self, message: str, *, failed: bool = False) -> None:
        """Keep the reusable Settings panel synchronized with operation feedback."""

        panel = self._settings_panel()
        if panel is not None:
            panel.show_data_result(message, failed=failed)
        if failed:
            self.feedback.error("Local data operation failed", message, important=True)
        else:
            self.feedback.success("Local data updated", message)

    def _export_local_data(self) -> None:
        """Choose a JSON destination and atomically export supported local content."""

        path, _selected = QFileDialog.getSaveFileName(
            self, "Export Otter Cove local data", "otter-cove-data.json", "JSON (*.json)"
        )
        if not path:
            return
        try:
            report = self.data.local_data.export_json(path, additional_protected_paths=(self.settings.path,))
        except (DataStoreError, DataValidationError, OSError) as exc:
            self._show_data_operation_result(str(exc), failed=True)
            return
        self._show_data_operation_result(self._data_operation_message("Export", report))

    def _import_local_data(self) -> None:
        """Validate and transactionally replace local content after confirmation."""

        path, _selected = QFileDialog.getOpenFileName(
            self, "Import Otter Cove local data", "", "JSON (*.json)"
        )
        if not path:
            return
        answer = QMessageBox.question(
            self,
            "Replace local content?",
            "Import replaces sessions/messages, models, documents, Brain items, notes, tasks and Gallery metadata. "
            "Credentials, Nobody sessions, preferences and window geometry are not imported.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        try:
            report = self.data.local_data.import_json(path, replace=True)
        except (DataStoreError, DataValidationError, OSError) as exc:
            self._show_data_operation_result(str(exc), failed=True)
            return
        self.workspace.chat.refresh_after_durable_replacement()
        self._show_data_operation_result(self._data_operation_message("Import", report))

    def _reset_local_data(self) -> None:
        """Delete supported local content transactionally after explicit confirmation."""

        answer = QMessageBox.warning(
            self,
            "Reset local content?",
            "This deletes local sessions/messages, models, documents, Brain items, notes, tasks and Gallery metadata. "
            "Credentials, Nobody sessions, preferences and window geometry are outside this reset.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        try:
            report = self.data.local_data.reset_local_content()
        except DataStoreError as exc:
            self._show_data_operation_result(exc.user_message(), failed=True)
            return
        self.workspace.chat.refresh_after_durable_replacement()
        self._show_data_operation_result(self._data_operation_message("Reset", report))

    def _apply_appearance_changes(self, changes: dict) -> None:
        """Validate a Settings appearance delta, persist accepted values, and redraw.

        A panel may submit several values at once.  Each is validated independently
        so an invalid key/value produces feedback without discarding unrelated
        valid changes from the same interaction.  The resulting model snapshot is
        then pushed to widgets that consume appearance preferences.
        """
        # Apply the delta before taking a replacement snapshot.  Widgets therefore
        # never observe a mixed old/new collection of independently persisted keys.
        for key, value in changes.items():
            try:
                self.appearance.set(key, value)
            except (KeyError, ValueError) as exc:
                self.feedback.error("Appearance setting rejected", str(exc), important=False)
        self._apply_appearance_snapshot()

    def _set_sidebar_visibility(self, route: str, visible: bool) -> None:
        """Persist one registered sidebar item's visibility and update its button.

        A ``KeyError`` means a stale/invalid panel request.  It is intentionally
        ignored here because the model has not changed and the visual shell has no
        meaningful item to update.
        """
        try:
            self.appearance.set_sidebar_visible(route, visible)
        except KeyError:
            return
        self.sidebar.set_route_visible(route, visible)

    def _apply_appearance_snapshot(self) -> None:
        """Propagate the model's complete appearance state to mounted UI consumers.

        The ``hasattr`` guards allow the same helper to be used safely during
        construction, before every visual child has been assigned.  Sidebar
        visibility is applied item-by-item because the sidebar owns its buttons.
        """
        snapshot = self.appearance.snapshot()
        if hasattr(self, "workspace"):
            self.workspace.chat.apply_appearance(snapshot)
        if hasattr(self, "sidebar"):
            visibility = snapshot.get("sidebar_visible", {})
            for route, visible in visibility.items():
                self.sidebar.set_route_visible(route, bool(visible))

    def _reset_appearance(self) -> None:
        """Restore documented appearance defaults, refresh Settings if it is open.

        Reset changes both the durable model and the already-mounted chat/sidebar.
        The optional panel refresh is necessary because it owns editor controls that
        do not automatically subscribe to individual appearance-model fields.
        """
        self.appearance.reset()
        self._apply_appearance_snapshot()
        panel = self._settings_panel()
        if panel is not None:
            panel.refresh_appearance(self.appearance.snapshot())
        self.feedback.success("Appearance reset", "Appearance preferences were restored to their documented defaults.")

    def _toggle_nobody(self) -> None:
        """Switch the active chat view through its existing Nobody control.

        The button remains the owner of its checked state; its normal Qt signal
        path saves the outgoing session draft and renders the selected privacy
        mode. The shell only supplies confirmation of the completed transition.
        """
        button = self.workspace.chat.nobody
        button.setChecked(not button.isChecked())
        state = "on" if button.isChecked() else "off"
        policy = "memory-only session" if button.isChecked() else "persistent session"
        self.feedback.info("Nobody mode", f"Nobody mode is {state}; showing the {policy} view.", timeout_ms=2400)

    def _tts_demo(self) -> None:
        """Report the intentionally local, non-provider TTS demo command action."""
        self.feedback.info("TTS demo", "Text-to-speech is a local GUI demo action in this milestone; no speech service was called.")

    def _rebind_shortcut(self, command_id: str, sequence: str) -> None:
        """Apply one requested key binding, restoring the panel on conflict/error.

        ``CommandManager`` validates command IDs and prevents duplicate shortcuts.
        When it rejects the request, settings were not changed; refreshing the
        open panel returns its editor to the manager's still-authoritative binding.
        """
        try:
            self.command_manager.rebind(command_id, sequence)
        except (ShortcutConflict, KeyError) as exc:
            self.feedback.error("Shortcut conflict", str(exc), important=False)
            self._refresh_settings_shortcuts()

    def _clear_shortcut(self, command_id: str) -> None:
        """Remove a command binding while retaining the command's metadata/action.

        A cleared binding disables only keyboard activation; the corresponding menu
        or widget action remains available.  Unknown command IDs are rejected by
        the registry and shown as non-blocking feedback without modifying settings.
        """
        try:
            self.command_manager.clear(command_id)
        except KeyError as exc:
            self.feedback.error("Shortcut not changed", str(exc), important=False)

    def _reset_shortcut(self, command_id: str) -> None:
        """Restore one command's documented default binding when it is conflict-free.

        A stored custom sequence might occupy a default sequence, so reset can use
        the same conflict path as rebind.  In that case no shortcut is changed and
        the panel is rehydrated from the manager's current effective bindings.
        """
        try:
            self.command_manager.reset(command_id)
        except (ShortcutConflict, KeyError) as exc:
            self.feedback.error("Shortcut not reset", str(exc), important=False)
            self._refresh_settings_shortcuts()

    def _reset_all_shortcuts(self) -> None:
        """Restore every command binding, reporting a registry-level conflict if any.

        The manager performs the operation as one registry update, allowing this
        shell method to avoid independently mutating actions or settings entries.
        The normal ``bindingsChanged`` signal updates all visible shortcut hints.
        """
        try:
            self.command_manager.reset_all()
        except ShortcutConflict as exc:
            self.feedback.error("Shortcuts not reset", str(exc), important=False)

    def _on_bindings_changed(self) -> None:
        """Refresh every mounted shortcut affordance after a manager mutation.

        Qt actions already receive the new key sequences inside ``CommandManager``.
        This shell additionally updates sidebar/chat tooltips and the optional
        Settings panel so visible explanatory text never advertises an old binding.
        """
        # Only sidebar routes with visible buttons need a tooltip update.  Commands
        # such as Tools or TTS may be QAction-only in this milestone, so the mapping
        # is intentionally narrower than the full command registry.
        self._refresh_settings_shortcuts()
        mapping = {
            "new_chat": "navigation.new_chat",
            "search": "navigation.search",
            "theme": "navigation.theme",
        }
        for route, command_id in mapping.items():
            button = self.sidebar.buttons.get(route)
            if button is not None:
                button.set_command_tooltip(self.command_manager.tooltip(command_id))
        self.sidebar.settings_button.setToolTip(self.command_manager.tooltip("navigation.settings"))
        self.workspace.chat.nobody.setToolTip(
            self.command_manager.tooltip("session.incognito")
            + "\nNobody sessions are ephemeral and are not written to local history."
        )

    def _refresh_settings_shortcuts(self) -> None:
        """Push the full persisted binding map to Settings only while it is mounted."""
        panel = self._settings_panel()
        if panel is not None and hasattr(self, "command_manager"):
            panel.refresh_shortcuts(self.command_manager.bindings.all_bindings())

    def _settings_panel(self) -> SettingsPanel | None:
        """Return the live Settings content if its reusable floating window exists.

        WindowManager retains hidden windows for stateful reopen, so checking the
        manager mapping is preferable to constructing a replacement just to update
        data.  The ``isinstance`` check documents the assumed content contract.
        """
        settings_window = self.window_manager.windows.get("settings")
        if settings_window is None:
            return None
        content = settings_window.content_widget()
        return content if isinstance(content, SettingsPanel) else None

    def _open_feature(self, route: str, *, unknown: bool = False) -> None:
        """Display a registered or unknown route as an overlay feature placeholder.

        Incomplete routes intentionally remain navigable so the app can distinguish
        unavailable functionality from a failed click.  A deterministic position
        derived from the route index offsets separate placeholders slightly without
        requiring per-route geometry defaults.  Unknown keys use a namespaced
        window key to avoid colliding with a future registered route of that name.
        """
        # Registered placeholder titles/icons come from the same registry that
        # produced the request.  Unknown routes get a diagnostic title and neutral
        # icon, avoiding a false claim that a real feature has been opened.
        spec = self.route_registry.get(route)
        title = spec.title if spec is not None else f"Unavailable route: {route}"
        icon = spec.icon if spec is not None else "?"
        # The predictable stagger prevents a stack of placeholders from looking as
        # if only one opened, while still allowing the manager to restore any later
        # user-positioned geometry from QSettings.
        keys = self.route_registry.exposed_keys()
        index = keys.index(route) if route in keys else 0
        x = 72 + (index % 4) * 26
        y = 54 + (index % 5) * 24
        key = route if not unknown else f"unavailable:{route}"
        self.window_manager.open_window(
            key,
            title,
            lambda r=route: FeaturePlaceholder(r, registry=self.route_registry, feedback=self.feedback),
            icon=icon,
            default_rect=QRect(x, y, 520, 390),
        )

    def _select_theme(self, key: str) -> None:
        """Select a catalog theme and reset effect color for built-in presets.

        Saved themes carry their own complete effect bundle and emit a follow-up
        ``themeBundleApplied`` signal from ``ThemeManager``.  Built-ins have no
        bundled effect, so selecting one explicitly makes its accent the effect
        color and clears the visual carry-over from the previous palette.
        """
        is_builtin = key in THEMES
        self.theme_manager.select(key)
        # Built-in preset selection has a defined reset behavior: palette overrides
        # are cleared and the effect color returns to that preset's accent.
        if is_builtin:
            self.apply_effect_settings({"color": self.theme_manager.theme.accent})

    def _apply_typography_changes(self, changes: dict) -> None:
        """Forward optional font/size fields from ThemePanel to ThemeManager.

        Missing keys are meaningful: ThemePanel can update only one control, and
        the manager retains the other current value while recalculating the
        application font and publishing its typography signal.
        """
        self.theme_manager.set_typography(changes.get("font"), changes.get("size"))

    def _apply_layout_changes(self, changes: dict) -> None:
        """Forward optional density/frosted fields from ThemePanel to ThemeManager.

        Like typography, layout is centralized in the manager so an emitted change
        reaches existing widgets through a stylesheet update rather than requiring
        each panel to persist or interpret density/frosted preferences itself.
        """
        self.theme_manager.set_layout(changes.get("density"), changes.get("frosted"))

    def _on_theme_changed(self, theme: Theme) -> None:
        """Apply an emitted semantic palette to live visual consumers.

        The background takes the structured ``Theme`` for painting; the main window
        applies the manager-generated stylesheet for regular widgets.  Updating an
        open panel keeps its preview/selection synchronized after indirect changes.
        """
        self.workspace.background.set_theme(theme)
        panel = self._theme_panel()
        if panel is not None:
            panel.set_theme(self.theme_manager.theme_key, theme)
        self._apply_styles()

    def _apply_styles(self) -> None:
        """Install the stylesheet generated from the current semantic theme state."""
        self.setStyleSheet(self.theme_manager.stylesheet())

    def set_effect(self, effect: str) -> None:
        """Select a supported background effect, then persist and activate it.

        Runtime availability is checked against the effect manager instead of a
        hard-coded list, protecting startup/panel signals from a name unsupported
        by this build.  Invalid requests make no state or preference changes.
        """
        if effect not in self.workspace.background.available_effects():
            return
        self.effect_name = effect
        self.settings.set_value("appearance/effect/name", effect)
        self.workspace.background.set_effect(effect)

    def apply_effect_settings(self, changes: dict) -> None:
        """Merge effect-control changes into shell state, canvas state, and QSettings.

        ThemePanel sends partial dictionaries; each supplied field is independently
        mirrored to the background canvas and its stable settings key.  Once all
        updates have been applied, an open panel receives the complete payload so
        interdependent controls reflect the canonical values rather than only the
        field that originated the signal.
        """
        # Each accepted field follows the same three-way synchronization contract:
        # shell field (for bundles and future panel construction), live canvas (for
        # immediate feedback), then QSettings (for restart).  Values are converted
        # here because ThemePanel emits UI values while BackgroundCanvas accepts the
        # normalized primitive types used by its effect manager.
        if "color" in changes:
            self.effect_color = str(changes["color"])
            self.workspace.background.set_effect_color(self.effect_color)
            self.settings.set_value("appearance/effect/color", self.effect_color)
        if "speed" in changes:
            self.effect_speed = float(changes["speed"])
            self.workspace.background.set_effect_speed(self.effect_speed)
            self.settings.set_value("appearance/effect/speed", self.effect_speed)
        if "intensity" in changes:
            self.effect_intensity = float(changes["intensity"])
            self.workspace.background.set_effect_intensity(self.effect_intensity)
            self.settings.set_value("appearance/effect/intensity", self.effect_intensity)
        if "quality" in changes:
            self.effect_quality = float(changes["quality"])
            self.workspace.background.set_effect_quality(self.effect_quality)
            self.settings.set_value("appearance/effect/quality", self.effect_quality)
        if "size" in changes:
            self.effect_size = float(changes["size"])
            self.workspace.background.set_effect_size(self.effect_size)
            self.settings.set_value("appearance/effect/size", self.effect_size)
        if "paused" in changes:
            self.effect_paused = bool(changes["paused"])
            self.workspace.background.set_effect_paused(self.effect_paused)
            self.settings.set_value("appearance/effect/paused", self.effect_paused)
        # A hidden ThemePanel retains its own controls, so only a currently created
        # panel needs a full rehydration after a partial update from one control.
        panel = self._theme_panel()
        if panel is not None:
            panel.set_effect_settings(self._effect_payload())

    def _apply_effect_state(self) -> None:
        """Push the complete stored effect state to the background canvas.

        This is used after startup and saved-theme application, where individual
        setters would otherwise repeat panel synchronization and preference writes.
        """
        self.workspace.background.set_effect(self.effect_name)
        self.workspace.background.set_effect_color(self.effect_color)
        self.workspace.background.set_effect_speed(self.effect_speed)
        self.workspace.background.set_effect_intensity(self.effect_intensity)
        self.workspace.background.set_effect_quality(self.effect_quality)
        self.workspace.background.set_effect_size(self.effect_size)
        self.workspace.background.set_effect_paused(self.effect_paused)

    def _effect_payload(self) -> dict:
        """Return the serializable effect portion of a named theme bundle.

        The dictionary shape matches the theme-bundle validator and is also the
        single source for returning the current values to ThemePanel.
        """
        return {
            "name": self.effect_name,
            "color": self.effect_color,
            "speed": self.effect_speed,
            "intensity": self.effect_intensity,
            "quality": self.effect_quality,
            "size": self.effect_size,
            "paused": self.effect_paused,
        }

    def _load_effect_values(self, effect: dict, *, persist: bool) -> None:
        """Copy a bundle's effect mapping into shell fields, optionally into QSettings.

        Bundle validation happens before this method is reached.  Defaults preserve
        existing values if a caller supplies a partial mapping; ``persist=False``
        is important at startup because an already-selected bundle should override
        runtime state without rewriting every preference during construction.
        """
        # Keep assignment separate from canvas application.  Callers can choose the
        # ordering: startup loads fields before one batched canvas update, whereas
        # saved-theme selection persists first and then activates the full bundle.
        self.effect_name = str(effect.get("name", self.effect_name))
        self.effect_color = str(effect.get("color", self.effect_color))
        self.effect_speed = float(effect.get("speed", self.effect_speed))
        self.effect_intensity = float(effect.get("intensity", self.effect_intensity))
        self.effect_quality = float(effect.get("quality", self.effect_quality))
        self.effect_size = float(effect.get("size", self.effect_size))
        self.effect_paused = bool(effect.get("paused", self.effect_paused))
        if persist:
            # A newly selected saved theme becomes the active restart baseline as
            # well as the source for the current canvas; persistence intentionally
            # mirrors every effect field, not merely the palette-derived color.
            self.settings.set_value("appearance/effect/name", self.effect_name)
            self.settings.set_value("appearance/effect/color", self.effect_color)
            self.settings.set_value("appearance/effect/speed", self.effect_speed)
            self.settings.set_value("appearance/effect/intensity", self.effect_intensity)
            self.settings.set_value("appearance/effect/quality", self.effect_quality)
            self.settings.set_value("appearance/effect/size", self.effect_size)
            self.settings.set_value("appearance/effect/paused", self.effect_paused)

    def _apply_saved_theme_bundle(self, bundle: dict) -> None:
        """Finish applying a selected saved theme beyond its palette/typography.

        ``ThemeManager.select`` handles palette and presentation values, then emits
        the normalized bundle.  This complementary handler installs its effect
        values, persists them as the active independent values, and brings any
        already-open ThemePanel controls in line with the selected bundle.
        """
        # Signal order matters: ThemeManager has already emitted palette/layout
        # updates by the time this handler receives the bundle.  This method fills
        # in the remaining effect portion instead of reapplying color state itself.
        self._load_effect_values(bundle["effect"], persist=True)
        self._apply_effect_state()
        panel = self._theme_panel()
        if panel is not None:
            panel.font_combo.setCurrentText(self.theme_manager.font_kind)
            panel.size_combo.setCurrentText(self.theme_manager.text_size)
            panel.density_combo.setCurrentText(self.theme_manager.density)
            panel.frost_check.setChecked(self.theme_manager.frosted)
            panel.set_effect_settings(bundle["effect"])

    def _save_named_theme(self, name: str) -> None:
        """Persist the current palette/presentation/effect state under ``name``.

        Name collision is a normal user decision rather than an automatic overwrite:
        the first manager call rejects an existing name, then this shell asks for
        explicit confirmation before retrying with replacement enabled.  Other
        validation/persistence errors become important feedback and leave the panel
        and current active theme unchanged.
        """
        try:
            key = self.theme_manager.save_current(name, self._effect_payload(), replace=False)
        except ThemeBundleError as exc:
            if "already exists" not in str(exc):
                self.feedback.error("Theme not saved", str(exc), important=True)
                return
            # The manager purposefully does not overwrite on its first call.  Keep
            # replacement authorization at the UI boundary, where a user can make
            # the destructive choice with the conflicting name in context.
            answer = QMessageBox.question(
                self,
                "Replace saved theme?",
                f"A saved theme named {name!r} already exists. Replace it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
            try:
                key = self.theme_manager.save_current(name, self._effect_payload(), replace=True)
            except ThemeBundleError as replace_exc:
                self.feedback.error("Theme not saved", str(replace_exc), important=True)
                return
        # Saving a bundle does not select it.  It is added to an open panel's saved
        # catalog immediately, while the current active palette remains untouched.
        panel = self._theme_panel()
        if panel is not None:
            panel.add_saved_theme(key, self.theme_manager.catalog()[key])
        self.feedback.success("Theme saved", f"{name} is now available under Saved Themes.")

    def _import_theme(self) -> None:
        """Choose, validate, and add a theme file without selecting it automatically.

        File parsing/validation is performed before ``ThemeManager`` mutates its
        saved catalog.  A successful import only makes the new entry available in
        ThemePanel; this protects the user's current palette from an accidental
        visual switch caused merely by opening a file.
        """
        # Cancel returns an empty path and intentionally produces neither feedback
        # nor state changes; it is an expected non-error dialog outcome.
        path, _selected = QFileDialog.getOpenFileName(
            self,
            "Import Otter Cove theme",
            "",
            "Otter Cove Theme (*.json *.ottercove);;JSON (*.json);;All files (*)",
        )
        if not path:
            return
        # Loading validates the external JSON before ThemeManager allocates a saved
        # key or writes preferences, so malformed/unreadable files leave the catalog
        # intact and get an important, durable feedback message.
        try:
            bundle = load_theme_bundle(path)
            key = self.theme_manager.import_bundle(bundle, replace=False)
        except ThemeBundleError as exc:
            self.feedback.error("Theme import failed", str(exc), important=True)
            return
        panel = self._theme_panel()
        if panel is not None:
            panel.add_saved_theme(key, self.theme_manager.catalog()[key])
        self.feedback.success("Theme imported", f"{bundle['name']} was imported without changing the current theme.")

    def _export_theme(self) -> None:
        """Ask for a destination and atomically serialize the current theme bundle.

        The panel's name field, when mounted and nonblank, becomes the exported
        display name; otherwise the active semantic theme name is used.  The helper
        validates and writes through a temporary file/replace operation, while this
        method limits filesystem-specific feedback to the shell UI.
        """
        # Prefer a user-entered pending name without requiring the panel to be
        # saved first; fall back to the semantic theme name when no editor exists.
        panel = self._theme_panel()
        name = panel.theme_name.text().strip() if panel is not None else self.theme_manager.theme.name
        if not name:
            name = self.theme_manager.theme.name
        # As with import, cancellation is a normal no-op.  The default filename
        # offers a recognizable extension while the filter controls file selection.
        path, _selected = QFileDialog.getSaveFileName(
            self,
            "Export Otter Cove theme",
            f"{name}.ottercove.json",
            "Otter Cove Theme (*.json);;All files (*)",
        )
        if not path:
            return
        # Bundle construction validates the in-memory payload and the writer uses
        # an atomic replacement strategy.  A failure reports to feedback rather
        # than leaving the currently active theme or panel state partially changed.
        try:
            bundle = self.theme_manager.bundle_for_current(self._effect_payload(), name=name)
            store_path = self.data.store.path
            save_theme_bundle_atomic(
                path,
                bundle,
                protected_paths=(
                    store_path,
                    store_path.with_name(f"{store_path.name}-wal"),
                    store_path.with_name(f"{store_path.name}-shm"),
                    self.settings.path,
                ),
            )
        except ThemeBundleError as exc:
            self.feedback.error("Theme export failed", str(exc), important=True)
            return
        self.feedback.success("Theme exported", f"Saved {Path(path).name}.")

    def _theme_panel(self) -> ThemePanel | None:
        """Return the reusable ThemePanel content when its floating window exists."""
        theme_window = self.window_manager.windows.get("theme")
        if theme_window is None:
            return None
        content = theme_window.content_widget()
        return content if isinstance(content, ThemePanel) else None

    def _sync_animation_suspension(self) -> None:
        """Combine window and application activity into external effect suspension.

        BackgroundCanvas separately tracks whether it is hidden.  This method adds
        top-level visibility, minimized state, and Qt application activation so the
        effect manager can stop timing work whenever the shell is not usable, while
        preserving the user's independent pause preference.
        """
        # No QApplication is possible in narrowly constructed tests; in that case
        # only the window-local visibility/minimized parts participate in the value.
        app = QApplication.instance()
        inactive = app is not None and app.applicationState() != Qt.ApplicationState.ApplicationActive
        suspended = (not self.isVisible()) or self.isMinimized() or inactive
        self.workspace.background.set_effect_suspended(suspended)

    def _ensure_main_window_visible(self) -> None:
        """Recover saved geometry that no longer fits the current available screen.

        Window dimensions are clamped between the application minimum and the
        screen's available rectangle.  The position calculation then keeps the
        whole frame on that rectangle, covering unplugged-monitor and resolution
        change cases without discarding the user's otherwise valid geometry.
        """
        screen = self.screen() or QApplication.primaryScreen()
        if screen is None:
            return
        # ``availableGeometry`` excludes desktop-reserved areas such as panels, so
        # recovery does not place controls behind a taskbar/dock after resolution
        # or monitor topology changes.
        available = screen.availableGeometry()
        width = min(max(self.minimumWidth(), self.width()), available.width())
        height = min(max(self.minimumHeight(), self.height()), available.height())
        self.resize(width, height)
        frame = self.frameGeometry()
        x = min(max(frame.x(), available.left()), max(available.left(), available.right() - frame.width() + 1))
        y = min(max(frame.y(), available.top()), max(available.top(), available.bottom() - frame.height() + 1))
        self.move(x, y)

    def showEvent(self, event) -> None:
        """Re-evaluate effect suspension after Qt makes the shell visible."""
        super().showEvent(event)
        # Defer until the visibility transition has settled; querying immediately
        # during this event can still reflect the previous effective state.
        QTimer.singleShot(0, self._sync_animation_suspension)

    def hideEvent(self, event) -> None:
        """Immediately suspend effect timing while the top-level shell is hidden."""
        self.workspace.background.set_effect_suspended(True)
        super().hideEvent(event)

    def changeEvent(self, event) -> None:
        """Re-evaluate animation state after Qt changes window/application state."""
        super().changeEvent(event)
        # Minimize/restore and activation changes funnel through this deferred
        # synchronization path; BackgroundCanvas combines it with user pause state.
        QTimer.singleShot(0, self._sync_animation_suspension)

    def closeEvent(self, event) -> None:
        """Persist recoverable shell state and close local data before Qt teardown.

        Effects are stopped first.  Floating-window geometry, main-window geometry,
        and QSettings are then committed before the SQLite-facing service container
        closes its resources.  ``super`` receives the event last so Qt only proceeds
        with normal close processing after this shell-owned cleanup has run.
        """
        self.workspace.background.set_effect_suspended(True)
        self.window_manager.save_all()
        self.settings.set_main_geometry(self.saveGeometry())
        self.settings.sync()
        self.data.close()
        super().closeEvent(event)
