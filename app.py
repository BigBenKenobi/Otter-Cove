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
    """Stark Studio application shell.

    The shell owns persistent app state and services. Feature windows are children
    of the workspace and talk through signals rather than reaching into one another.
    """

    def __init__(
        self,
        data_services: AppDataServices | None = None,
        settings: AppSettings | None = None,
        route_registry: RouteRegistry = DEFAULT_ROUTE_REGISTRY,
    ) -> None:
        super().__init__()
        self.setWindowTitle("Stark Studio — PySide6 concept")
        self.setMinimumSize(1100, 680)

        self.settings = settings or AppSettings()
        self.data = data_services or AppDataServices.open()
        self.route_registry = route_registry
        self.shell_state = ShellState()
        self.appearance = AppearancePreferences(
            self.settings, tuple(route.key for route in self.route_registry.sidebar_routes())
        )
        self.theme_manager = ThemeManager(self.settings, self)
        self.theme_manager.apply_saved_typography()

        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = Sidebar(self.settings.bool("appearance/sidebar_collapsed", False))
        self.sidebar.navigationRequested.connect(self._route)
        self.sidebar.collapsedChanged.connect(lambda value: self.settings.set_value("appearance/sidebar_collapsed", value))
        layout.addWidget(self.sidebar)

        self.workspace = Workspace(self.theme_manager.theme, self.data.sessions)
        layout.addWidget(self.workspace, 1)

        self.feedback = FeedbackManager(self.workspace)
        self.window_manager = StudioWindowManager(self.workspace, self.settings)
        self.workspace.resized.connect(self.window_manager.keep_in_bounds)
        self.workspace.chat.actionRequested.connect(self._route)
        self.workspace.chat.storageError.connect(self._show_storage_error)
        self._apply_appearance_snapshot()

        self.effect_name = str(self.settings.value("appearance/effect/name", "Leaves"))
        if self.effect_name not in self.workspace.background.available_effects():
            self.effect_name = "Leaves"
        self.effect_color = str(self.settings.value("appearance/effect/color", self.theme_manager.theme.accent))
        self.effect_speed = self.settings.float("appearance/effect/speed", 1.0)
        self.effect_intensity = self.settings.float("appearance/effect/intensity", 1.0)
        self.effect_quality = self.settings.float("appearance/effect/quality", 1.0)
        self.effect_size = self.settings.float("appearance/effect/size", 1.0)
        self.effect_paused = self.settings.bool("appearance/effect/paused", False)

        # A selected saved theme owns its bundled effect settings on restart.
        saved_bundle = self.theme_manager.selected_saved_bundle()
        if saved_bundle is not None:
            self._load_effect_values(saved_bundle["effect"], persist=False)
        self._apply_effect_state()

        self.theme_manager.themeChanged.connect(self._on_theme_changed)
        self.theme_manager.typographyChanged.connect(lambda _family, _size: self._apply_styles())
        self.theme_manager.layoutChanged.connect(lambda _density, _frosted: self._apply_styles())
        self.theme_manager.themeBundleApplied.connect(self._apply_saved_theme_bundle)
        self._apply_styles()
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
        self.command_manager.bindingsChanged.connect(self._on_bindings_changed)
        self._on_bindings_changed()
        if self.command_manager.load_warning:
            self.feedback.error(
                "Shortcut settings recovered",
                self.command_manager.load_warning,
                important=True,
            )

        app = QApplication.instance()
        if app is not None:
            app.applicationStateChanged.connect(lambda _state: self._sync_animation_suspension())

        geometry = self.settings.main_geometry()
        if geometry is not None and self.restoreGeometry(geometry):
            # Clamp once the application event loop has a screen/available geometry.
            QTimer.singleShot(0, self._ensure_main_window_visible)
        else:
            self.resize(1720, 900)
            QTimer.singleShot(0, self._ensure_main_window_visible)
        QTimer.singleShot(0, self._sync_animation_suspension)

    def _show_storage_error(self, message: str) -> None:
        self.feedback.error("Stark Studio local data", message, important=True)

    def _route(self, route: str) -> None:
        spec = self.route_registry.get(route)
        if spec is None:
            self.sidebar.set_active(None)
            self.shell_state.activate(route, is_tool=True)
            self._open_feature(route, unknown=True)
            return

        self.shell_state.activate(route, is_tool=spec.kind in {"tool", "theme"})
        self.sidebar.set_active(route if route in self.sidebar.buttons else None)

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
        def factory() -> ThemePanel:
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
            panel.themeSelected.connect(self._select_theme)
            panel.customChanged.connect(self.theme_manager.customize)
            panel.resetCustomRequested.connect(self.theme_manager.reset_customizations)
            panel.typographyChanged.connect(self._apply_typography_changes)
            panel.layoutChanged.connect(self._apply_layout_changes)
            panel.effectChanged.connect(self.set_effect)
            panel.effectSettingsChanged.connect(self.apply_effect_settings)
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
        def factory() -> SettingsPanel:
            panel = SettingsPanel(
                self.appearance.snapshot(),
                self.route_registry.sidebar_routes(),
                self.command_manager.specs,
                self.command_manager.bindings.all_bindings(),
            )
            panel.appearanceChanged.connect(self._apply_appearance_changes)
            panel.sidebarVisibilityChanged.connect(self._set_sidebar_visibility)
            panel.resetAppearanceRequested.connect(self._reset_appearance)
            panel.shortcutChangeRequested.connect(self._rebind_shortcut)
            panel.shortcutClearRequested.connect(self._clear_shortcut)
            panel.shortcutResetRequested.connect(self._reset_shortcut)
            panel.shortcutResetAllRequested.connect(self._reset_all_shortcuts)
            return panel

        self.window_manager.open_window(
            "settings",
            "Settings",
            factory,
            icon="⚙",
            default_rect=QRect(90, 46, 680, 720),
        )

    def _apply_appearance_changes(self, changes: dict) -> None:
        for key, value in changes.items():
            try:
                self.appearance.set(key, value)
            except (KeyError, ValueError) as exc:
                self.feedback.error("Appearance setting rejected", str(exc), important=False)
        self._apply_appearance_snapshot()

    def _set_sidebar_visibility(self, route: str, visible: bool) -> None:
        try:
            self.appearance.set_sidebar_visible(route, visible)
        except KeyError:
            return
        self.sidebar.set_route_visible(route, visible)

    def _apply_appearance_snapshot(self) -> None:
        snapshot = self.appearance.snapshot()
        if hasattr(self, "workspace"):
            self.workspace.chat.apply_appearance(snapshot)
        if hasattr(self, "sidebar"):
            visibility = snapshot.get("sidebar_visible", {})
            for route, visible in visibility.items():
                self.sidebar.set_route_visible(route, bool(visible))

    def _reset_appearance(self) -> None:
        self.appearance.reset()
        self._apply_appearance_snapshot()
        panel = self._settings_panel()
        if panel is not None:
            panel.refresh_appearance(self.appearance.snapshot())
        self.feedback.success("Appearance reset", "Appearance preferences were restored to their documented defaults.")

    def _toggle_nobody(self) -> None:
        button = self.workspace.chat.nobody
        button.setChecked(not button.isChecked())
        state = "on" if button.isChecked() else "off"
        self.feedback.info("Nobody mode", f"Nobody mode is {state} for the next/local session transition.", timeout_ms=2400)

    def _tts_demo(self) -> None:
        self.feedback.info("TTS demo", "Text-to-speech is a local GUI demo action in this milestone; no speech service was called.")

    def _rebind_shortcut(self, command_id: str, sequence: str) -> None:
        try:
            self.command_manager.rebind(command_id, sequence)
        except (ShortcutConflict, KeyError) as exc:
            self.feedback.error("Shortcut conflict", str(exc), important=False)
            self._refresh_settings_shortcuts()

    def _clear_shortcut(self, command_id: str) -> None:
        try:
            self.command_manager.clear(command_id)
        except KeyError as exc:
            self.feedback.error("Shortcut not changed", str(exc), important=False)

    def _reset_shortcut(self, command_id: str) -> None:
        try:
            self.command_manager.reset(command_id)
        except (ShortcutConflict, KeyError) as exc:
            self.feedback.error("Shortcut not reset", str(exc), important=False)
            self._refresh_settings_shortcuts()

    def _reset_all_shortcuts(self) -> None:
        try:
            self.command_manager.reset_all()
        except ShortcutConflict as exc:
            self.feedback.error("Shortcuts not reset", str(exc), important=False)

    def _on_bindings_changed(self) -> None:
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
        panel = self._settings_panel()
        if panel is not None and hasattr(self, "command_manager"):
            panel.refresh_shortcuts(self.command_manager.bindings.all_bindings())

    def _settings_panel(self) -> SettingsPanel | None:
        settings_window = self.window_manager.windows.get("settings")
        if settings_window is None:
            return None
        content = settings_window.content_widget()
        return content if isinstance(content, SettingsPanel) else None

    def _open_feature(self, route: str, *, unknown: bool = False) -> None:
        spec = self.route_registry.get(route)
        title = spec.title if spec is not None else f"Unavailable route: {route}"
        icon = spec.icon if spec is not None else "?"
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
        is_builtin = key in THEMES
        self.theme_manager.select(key)
        # Built-in preset selection has a defined reset behavior: palette overrides
        # are cleared and the effect color returns to that preset's accent.
        if is_builtin:
            self.apply_effect_settings({"color": self.theme_manager.theme.accent})

    def _apply_typography_changes(self, changes: dict) -> None:
        self.theme_manager.set_typography(changes.get("font"), changes.get("size"))

    def _apply_layout_changes(self, changes: dict) -> None:
        self.theme_manager.set_layout(changes.get("density"), changes.get("frosted"))

    def _on_theme_changed(self, theme: Theme) -> None:
        self.workspace.background.set_theme(theme)
        panel = self._theme_panel()
        if panel is not None:
            panel.set_theme(self.theme_manager.theme_key, theme)
        self._apply_styles()

    def _apply_styles(self) -> None:
        self.setStyleSheet(self.theme_manager.stylesheet())

    def set_effect(self, effect: str) -> None:
        if effect not in self.workspace.background.available_effects():
            return
        self.effect_name = effect
        self.settings.set_value("appearance/effect/name", effect)
        self.workspace.background.set_effect(effect)

    def apply_effect_settings(self, changes: dict) -> None:
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
        panel = self._theme_panel()
        if panel is not None:
            panel.set_effect_settings(self._effect_payload())

    def _apply_effect_state(self) -> None:
        self.workspace.background.set_effect(self.effect_name)
        self.workspace.background.set_effect_color(self.effect_color)
        self.workspace.background.set_effect_speed(self.effect_speed)
        self.workspace.background.set_effect_intensity(self.effect_intensity)
        self.workspace.background.set_effect_quality(self.effect_quality)
        self.workspace.background.set_effect_size(self.effect_size)
        self.workspace.background.set_effect_paused(self.effect_paused)

    def _effect_payload(self) -> dict:
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
        self.effect_name = str(effect.get("name", self.effect_name))
        self.effect_color = str(effect.get("color", self.effect_color))
        self.effect_speed = float(effect.get("speed", self.effect_speed))
        self.effect_intensity = float(effect.get("intensity", self.effect_intensity))
        self.effect_quality = float(effect.get("quality", self.effect_quality))
        self.effect_size = float(effect.get("size", self.effect_size))
        self.effect_paused = bool(effect.get("paused", self.effect_paused))
        if persist:
            self.settings.set_value("appearance/effect/name", self.effect_name)
            self.settings.set_value("appearance/effect/color", self.effect_color)
            self.settings.set_value("appearance/effect/speed", self.effect_speed)
            self.settings.set_value("appearance/effect/intensity", self.effect_intensity)
            self.settings.set_value("appearance/effect/quality", self.effect_quality)
            self.settings.set_value("appearance/effect/size", self.effect_size)
            self.settings.set_value("appearance/effect/paused", self.effect_paused)

    def _apply_saved_theme_bundle(self, bundle: dict) -> None:
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
        try:
            key = self.theme_manager.save_current(name, self._effect_payload(), replace=False)
        except ThemeBundleError as exc:
            if "already exists" not in str(exc):
                self.feedback.error("Theme not saved", str(exc), important=True)
                return
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
        panel = self._theme_panel()
        if panel is not None:
            panel.add_saved_theme(key, self.theme_manager.catalog()[key])
        self.feedback.success("Theme saved", f"{name} is now available under Saved Themes.")

    def _import_theme(self) -> None:
        path, _selected = QFileDialog.getOpenFileName(
            self,
            "Import Stark Studio theme",
            "",
            "Stark Studio Theme (*.json *.starktheme);;JSON (*.json);;All files (*)",
        )
        if not path:
            return
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
        panel = self._theme_panel()
        name = panel.theme_name.text().strip() if panel is not None else self.theme_manager.theme.name
        if not name:
            name = self.theme_manager.theme.name
        path, _selected = QFileDialog.getSaveFileName(
            self,
            "Export Stark Studio theme",
            f"{name}.starktheme.json",
            "Stark Studio Theme (*.json);;All files (*)",
        )
        if not path:
            return
        try:
            bundle = self.theme_manager.bundle_for_current(self._effect_payload(), name=name)
            save_theme_bundle_atomic(path, bundle)
        except ThemeBundleError as exc:
            self.feedback.error("Theme export failed", str(exc), important=True)
            return
        self.feedback.success("Theme exported", f"Saved {Path(path).name}.")

    def _theme_panel(self) -> ThemePanel | None:
        theme_window = self.window_manager.windows.get("theme")
        if theme_window is None:
            return None
        content = theme_window.content_widget()
        return content if isinstance(content, ThemePanel) else None

    def _sync_animation_suspension(self) -> None:
        app = QApplication.instance()
        inactive = app is not None and app.applicationState() != Qt.ApplicationState.ApplicationActive
        suspended = (not self.isVisible()) or self.isMinimized() or inactive
        self.workspace.background.set_effect_suspended(suspended)

    def _ensure_main_window_visible(self) -> None:
        """Recover saved geometry that no longer fits the current display."""
        screen = self.screen() or QApplication.primaryScreen()
        if screen is None:
            return
        available = screen.availableGeometry()
        width = min(max(self.minimumWidth(), self.width()), available.width())
        height = min(max(self.minimumHeight(), self.height()), available.height())
        self.resize(width, height)
        frame = self.frameGeometry()
        x = min(max(frame.x(), available.left()), max(available.left(), available.right() - frame.width() + 1))
        y = min(max(frame.y(), available.top()), max(available.top(), available.bottom() - frame.height() + 1))
        self.move(x, y)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        QTimer.singleShot(0, self._sync_animation_suspension)

    def hideEvent(self, event) -> None:
        self.workspace.background.set_effect_suspended(True)
        super().hideEvent(event)

    def changeEvent(self, event) -> None:
        super().changeEvent(event)
        QTimer.singleShot(0, self._sync_animation_suspension)

    def closeEvent(self, event) -> None:
        self.workspace.background.set_effect_suspended(True)
        self.window_manager.save_all()
        self.settings.set_main_geometry(self.saveGeometry())
        self.settings.sync()
        self.data.close()
        super().closeEvent(event)
