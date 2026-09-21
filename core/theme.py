from __future__ import annotations

from dataclasses import dataclass, fields
import json
import re
from typing import Any, Mapping

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication

from .settings import AppSettings
from .theme_logic import (
    DENSITIES,
    FONT_KINDS,
    TEXT_SIZES,
    ThemeBundleError,
    make_theme_bundle,
    normalize_hex_color,
    validate_theme_bundle,
)


@dataclass(frozen=True)
class Theme:
    name: str
    background: str
    panel: str
    sidebar: str
    border: str
    text: str
    muted: str
    accent: str
    input_bg: str
    send_bg: str

    def palette(self) -> dict[str, str]:
        return {field.name: getattr(self, field.name) for field in fields(self) if field.name != "name"}


THEMES: dict[str, Theme] = {
    "original": Theme("Original", "#0f2030", "#0d1b28", "#0b1823", "#225b7b", "#55b8f6", "#326a88", "#44acf3", "#0d1b28", "#164866"),
    "light": Theme("Light", "#f4f1e8", "#fffdf7", "#ece8df", "#c7a789", "#4a3830", "#8a7469", "#c37d5c", "#ffffff", "#d9a585"),
    "midnight": Theme("Midnight", "#111321", "#15192a", "#0e1020", "#3a4165", "#dbe3ff", "#7781a7", "#ff5b69", "#121626", "#51333f"),
    "paper": Theme("Paper", "#f7f5ee", "#ffffff", "#ece9df", "#c9c4b4", "#20231f", "#74786e", "#a6a04f", "#fbfaf5", "#dad6a7"),
    "cyberpunk": Theme("Cyberpunk", "#0d1521", "#101b28", "#0a111b", "#205067", "#dff9ff", "#52bac8", "#f134d0", "#0a1821", "#2a5263"),
    "retrowave": Theme("Retrowave", "#18101f", "#21142a", "#130d19", "#5a315f", "#f4b0d8", "#936080", "#e45276", "#1b1022", "#5b2c4a"),
    "forest": Theme("Forest", "#1d2521", "#19201c", "#151c18", "#345241", "#77d89c", "#567262", "#67cf92", "#171f1b", "#315d43"),
    "ocean": Theme("Ocean", "#0e2230", "#0d1d29", "#0b1721", "#1c617a", "#5ec8f7", "#3a748d", "#58bbef", "#0b1b25", "#1c5670"),
    "ume": Theme("Ume", "#2a2030", "#251b2b", "#211824", "#694d67", "#f0add1", "#a47190", "#f49bc9", "#241a28", "#69405d"),
    "copper": Theme("Copper", "#1d1612", "#19120f", "#17110f", "#6c4425", "#efbd8a", "#8c6b50", "#e27d4e", "#17110f", "#6c4129"),
    "terminal": Theme("Terminal", "#07110d", "#09140f", "#06100b", "#1c5b3a", "#4cff86", "#269e52", "#18e665", "#06110c", "#155c31"),
    "organs": Theme("Organs", "#211718", "#1d1415", "#1a1213", "#67343a", "#e8a7aa", "#925f64", "#d44c57", "#1c1314", "#663139"),
    "lavender": Theme("Lavender", "#181722", "#1d1b28", "#15141e", "#50456d", "#d6c7f8", "#8676ab", "#8a65cb", "#181622", "#554070"),
    "gpt": Theme("GPT", "#1f2422", "#1b201e", "#171b19", "#53615b", "#dce7e2", "#85908b", "#9da8a3", "#191d1b", "#4e5a55"),
    "claude": Theme("Claude", "#25201c", "#211c18", "#1d1916", "#624d41", "#f1c6aa", "#9c7b69", "#e58255", "#1f1a17", "#6e4633"),
    "cute": Theme("Cute", "#251d26", "#211820", "#1e161d", "#704359", "#ffdbe8", "#a17086", "#ef739d", "#211820", "#753d56"),
}


class ThemeManager(QObject):
    """Single source of truth for semantic palette and presentation settings."""

    themeChanged = Signal(object)
    typographyChanged = Signal(str, int)
    layoutChanged = Signal(str, bool)
    themeBundleApplied = Signal(object)
    savedThemesChanged = Signal(object)

    def __init__(self, settings: AppSettings, parent=None) -> None:
        super().__init__(parent)
        self.settings = settings
        self._saved_themes = self._load_saved_themes()

        stored_key = str(settings.value("appearance/theme", "forest"))
        if stored_key == "GPT":
            stored_key = "gpt"
        self.theme_key = stored_key if self._has_theme(stored_key) else "forest"
        self._base_theme = self._theme_for_key(self.theme_key)
        self._custom = self._load_custom_overrides()
        self._theme = self._apply_overrides(self._base_theme, self._custom)

        self.font_kind = str(settings.value("appearance/font", "Monospace"))
        if self.font_kind not in FONT_KINDS:
            self.font_kind = "Monospace"
        self.text_size = str(settings.value("appearance/text_size", "Default"))
        if self.text_size not in TEXT_SIZES:
            self.text_size = "Default"
        self.density = str(settings.value("appearance/density", "Comfortable"))
        if self.density not in DENSITIES:
            self.density = "Comfortable"
        self.frosted = settings.bool("appearance/frosted", False)

        # Saved themes carry their presentation settings. Apply those values at
        # construction time so restart restores the whole named theme, not only colors.
        bundle = self._saved_themes.get(self.theme_key)
        if bundle is not None:
            typography = bundle["typography"]
            self.font_kind = typography["font"]
            self.text_size = typography["text_size"]
            self.density = typography["density"]
            self.frosted = bool(typography["frosted"])

    @property
    def theme(self) -> Theme:
        return self._theme

    @property
    def custom_overrides(self) -> dict[str, str]:
        return dict(self._custom)

    def catalog(self) -> dict[str, Theme]:
        result = dict(THEMES)
        for key, bundle in self._saved_themes.items():
            result[key] = self._theme_from_bundle(bundle)
        return result

    def saved_themes(self) -> dict[str, dict[str, Any]]:
        return {key: dict(value) for key, value in self._saved_themes.items()}

    def selected_saved_bundle(self) -> dict[str, Any] | None:
        bundle = self._saved_themes.get(self.theme_key)
        return dict(bundle) if bundle is not None else None

    def select(self, key: str) -> None:
        if not self._has_theme(key):
            return
        self.theme_key = key
        self._base_theme = self._theme_for_key(key)
        self._custom.clear()
        self.settings.remove("appearance/theme_overrides")
        self._theme = self._base_theme
        self.settings.set_value("appearance/theme", key)

        bundle = self._saved_themes.get(key)
        if bundle is not None:
            typography = bundle["typography"]
            self.set_typography(typography["font"], typography["text_size"])
            self.set_layout(typography["density"], bool(typography["frosted"]))

        self.themeChanged.emit(self._theme)
        if bundle is not None:
            self.themeBundleApplied.emit(dict(bundle))

    def customize(self, changes: Mapping[str, str]) -> None:
        allowed = {field.name for field in fields(Theme) if field.name != "name"}
        changed = False
        for key, value in changes.items():
            if key not in allowed:
                continue
            try:
                normalized = normalize_hex_color(value)
            except ThemeBundleError:
                continue
            if self._custom.get(key) != normalized:
                self._custom[key] = normalized
                changed = True
        if not changed:
            return
        self._theme = self._apply_overrides(self._base_theme, self._custom)
        self._persist_custom_overrides()
        self.themeChanged.emit(self._theme)

    def reset_customizations(self) -> None:
        if not self._custom:
            return
        self._custom.clear()
        self.settings.remove("appearance/theme_overrides")
        self._theme = self._base_theme
        self.themeChanged.emit(self._theme)

    def set_typography(self, font_kind: str | None = None, text_size: str | None = None) -> None:
        if font_kind in FONT_KINDS:
            self.font_kind = str(font_kind)
            self.settings.set_value("appearance/font", self.font_kind)
        if text_size in TEXT_SIZES:
            self.text_size = str(text_size)
            self.settings.set_value("appearance/text_size", self.text_size)
        family, point_size = self._font_spec()
        app = QApplication.instance()
        if app is not None:
            app.setFont(QFont(family, point_size))
        self.typographyChanged.emit(family, point_size)

    def set_layout(self, density: str | None = None, frosted: bool | None = None) -> None:
        if density in DENSITIES:
            self.density = str(density)
            self.settings.set_value("appearance/density", self.density)
        if frosted is not None:
            self.frosted = bool(frosted)
            self.settings.set_value("appearance/frosted", self.frosted)
        self.layoutChanged.emit(self.density, self.frosted)

    def apply_saved_typography(self) -> None:
        family, point_size = self._font_spec()
        app = QApplication.instance()
        if app is not None:
            app.setFont(QFont(family, point_size))

    def save_current(self, name: str, effect: Mapping[str, Any], *, replace: bool = False) -> str:
        name = str(name).strip()
        if not name:
            raise ThemeBundleError("Theme name is required")
        builtin_names = {theme.name.casefold() for theme in THEMES.values()}
        if name.casefold() in builtin_names:
            raise ThemeBundleError("A built-in theme already uses that name")

        existing_key = self._saved_key_for_name(name)
        if existing_key is not None and not replace:
            raise ThemeBundleError("A saved theme with that name already exists")
        key = existing_key or self._allocate_saved_key(name)
        bundle = make_theme_bundle(
            name,
            self._theme.palette(),
            font=self.font_kind,
            text_size=self.text_size,
            density=self.density,
            frosted=self.frosted,
            effect=effect,
        )
        self._saved_themes[key] = bundle
        self._persist_saved_themes()
        self.savedThemesChanged.emit(self.saved_themes())
        return key

    def import_bundle(self, bundle: Mapping[str, Any], *, replace: bool = False) -> str:
        normalized = validate_theme_bundle(bundle)
        name = normalized["name"]
        builtin_names = {theme.name.casefold() for theme in THEMES.values()}
        if name.casefold() in builtin_names:
            raise ThemeBundleError("Imported theme name conflicts with a built-in theme")
        existing_key = self._saved_key_for_name(name)
        if existing_key is not None and not replace:
            raise ThemeBundleError("A saved theme with that name already exists")
        key = existing_key or self._allocate_saved_key(name)
        self._saved_themes[key] = normalized
        self._persist_saved_themes()
        self.savedThemesChanged.emit(self.saved_themes())
        return key

    def bundle_for_current(self, effect: Mapping[str, Any], *, name: str | None = None) -> dict[str, Any]:
        display_name = name or self._theme.name
        return make_theme_bundle(
            display_name,
            self._theme.palette(),
            font=self.font_kind,
            text_size=self.text_size,
            density=self.density,
            frosted=self.frosted,
            effect=effect,
        )

    def _font_spec(self) -> tuple[str, int]:
        if self.font_kind == "Sans Serif":
            family = QFontDatabase.systemFont(QFontDatabase.GeneralFont).family()
        elif self.font_kind == "Serif":
            family = "serif"
        else:
            family = QFontDatabase.systemFont(QFontDatabase.FixedFont).family()
        size = {"Small": 9, "Default": 10, "Large": 12}.get(self.text_size, 10)
        return family, size

    def stylesheet(self) -> str:
        t = self._theme
        base = {"Small": 9, "Default": 10, "Large": 12}.get(self.text_size, 10)
        density = {"Compact": 0.82, "Comfortable": 1.0, "Roomy": 1.18}.get(self.density, 1.0)
        nav_height = round(32 * density)
        button_vpad = max(3, round(5 * density))
        section_pad = max(7, round(10 * density))
        panel_surface = self._css_rgba(t.panel, 214) if self.frosted else t.panel
        input_surface = self._css_rgba(t.input_bg, 220) if self.frosted else t.input_bg
        title_size = round(base * 3.0)
        hero_sub = max(base + 2, round(base * 1.25))
        dialog_title = max(base + 4, round(base * 1.5))
        section_title = max(base + 2, round(base * 1.25))
        feature_title = max(base + 8, round(base * 2.0))
        return f"""
        QWidget {{ color: {t.text}; font-size: {base}pt; }}
        QWidget:disabled {{ color: {t.muted}; }}
        #Sidebar {{ background: {t.sidebar}; border-right: 1px solid {t.border}; }}
        #Brand {{ color:{t.text}; font-size:{max(base + 5, 15)}pt; font-weight:700; }}
        #MenuButton {{ background:transparent; border:0; color:{t.muted}; font-size:{max(base + 6, 16)}pt; padding:2px; }}
        #NavButton {{ background:transparent; border:0; border-radius:6px; color:{t.text}; text-align:left; padding:0; min-height:{nav_height}px; }}
        #NavButton:hover {{ color:{t.accent}; background:{panel_surface}; }}
        #NavButton:checked {{ color:{t.accent}; background:{panel_surface}; }}
        #NavGlyph {{ qproperty-iconColor:{t.accent}; }}
        #NavText {{ color:{t.text}; }}
        #Avatar {{ background:{panel_surface}; border:1px solid {t.border}; border-radius:10px; min-width:20px; max-width:20px; min-height:20px; max-height:20px; }}
        #Avatar:hover, #SidebarSettingsButton:hover {{ color:{t.accent}; border-color:{t.accent}; }}
        #ChatSurface {{ background:transparent; }}
        #ChatHeader {{ color:{t.muted}; }}
        #HeroTitle {{ color:{t.accent}; font-size:{title_size}pt; font-weight:700; letter-spacing:2px; }}
        #HeroSub {{ color:{t.muted}; font-size:{hero_sub}pt; }}
        #HeroHint {{ color:{t.muted}; font-size:{max(base + 1, 10)}pt; }}
        #NobodyButton {{ background:transparent; border:1px solid {t.border}; color:{t.muted}; border-radius:13px; padding:{button_vpad}px 9px; }}
        #NobodyButton:hover {{ color:{t.accent}; border-color:{t.accent}; background:{panel_surface}; }}
        #PromptBox {{ background:{input_surface}; border:1px solid {t.border}; border-radius:15px; }}
        #PromptEditor {{ background:transparent; border:0; color:{t.text}; selection-background-color:{t.accent}; selection-color:{t.background}; }}
        #MessageArea, #MessageHost {{ background:transparent; border:0; }}
        #ModelButton {{ background:transparent; border:0; color:{t.text}; padding:2px 4px; }}
        #ModelButton:hover {{ color:{t.accent}; }}
        #PromptIcon {{ background:{panel_surface}; border:1px solid {t.border}; border-radius:9px; min-width:36px; max-width:36px; min-height:36px; max-height:36px; }}
        #PromptIcon:hover {{ background:{t.background}; border-color:{t.accent}; color:{t.accent}; }}
        #ModeToggle {{ border:1px solid {t.border}; border-radius:12px; background:{panel_surface}; }}
        #ModeButton {{ background:transparent; border:0; border-radius:9px; padding:4px 10px; color:{t.muted}; }}
        #ModeButton:hover {{ background:{t.background}; color:{t.accent}; }}
        #ModeButton:checked {{ background:{t.border}; color:{t.text}; }}
        #SendButton {{ background:{t.send_bg}; border:1px solid {t.border}; border-radius:9px; color:{t.text}; min-width:34px; max-width:34px; min-height:34px; max-height:34px; }}
        #SendButton:hover {{ background:{t.accent}; border-color:{t.accent}; color:{t.background}; }}
        #LocalMessage {{ background:{panel_surface}; border:1px solid {t.border}; border-radius:10px; padding:9px 12px; }}
        #StudioWindow {{ background:{panel_surface}; border:1px solid {t.border}; border-radius:10px; }}
        #StudioWindowBody {{ background:transparent; }}
        #StudioWindowTitlebar {{ background:{panel_surface}; border-bottom:1px solid {t.border}; border-top-left-radius:10px; border-top-right-radius:10px; }}
        #StudioWindowTitle {{ color:{t.accent}; font-size:{max(base + 4, 14)}pt; font-weight:700; }}
        #StudioTitleButton, #StudioPeekButton {{ background:transparent; border:0; color:{t.text}; padding:3px 6px; }}
        #StudioPeekButton {{ border:1px solid {t.border}; border-radius:10px; padding:3px 9px; }}
        #StudioPeekButton:checked {{ color:{t.accent}; border-color:{t.accent}; }}
        #ThemePanel {{ background:transparent; border:0; }}
        #ThemeScrollHost {{ background:transparent; }}
        #DialogTitle {{ color:{t.accent}; font-size:{dialog_title}pt; font-weight:700; }}
        #TabBar {{ background:{panel_surface}; border-bottom:1px solid {t.border}; }}
        #TabButton {{ background:transparent; border:0; padding:9px 8px; color:{t.text}; }}
        #TabButton:checked {{ border-bottom:2px solid {t.accent}; color:{t.accent}; }}
        #MiniButton, #OutlineButton {{ background:transparent; border:1px solid {t.border}; border-radius:8px; padding:{button_vpad}px 10px; color:{t.text}; }}
        #MiniButton:hover, #OutlineButton:hover {{ border-color:{t.accent}; color:{t.accent}; }}
        #Section {{ background:{panel_surface}; border:1px solid {t.border}; border-radius:8px; }}
        #SectionTitle {{ font-size:{section_title}pt; font-weight:700; color:{t.text}; }}
        #SectionRule {{ color:{t.border}; background:{t.border}; max-height:1px; }}
        #SwatchButton {{ background:{panel_surface}; border:1px solid {t.border}; border-radius:8px; }}
        #SwatchButton:checked {{ border:2px solid {t.accent}; }}
        #FlatLineButton {{ text-align:left; background:transparent; border:1px solid {t.border}; border-radius:5px; padding:{button_vpad}px; color:{t.text}; }}
        #FeaturePlaceholder {{ background:transparent; }}
        #FeatureTitle {{ color:{t.accent}; font-size:{feature_title}pt; font-weight:700; }}
        #FeatureMuted {{ color:{t.muted}; }}
        #StatusChip {{ background:{t.background}; border:1px solid {t.border}; border-radius:10px; padding:4px 8px; color:{t.muted}; }}
        #SharedStateCard {{ background:{t.background}; border:1px solid {t.border}; border-radius:10px; }}
        #SharedStateCard[stateKind="error"] {{ border-color:{t.accent}; }}
        #SharedStateIcon {{ color:{t.accent}; font-size:{max(base + 7, 17)}pt; font-weight:700; min-width:18px; }}
        #SharedStateTitle {{ color:{t.text}; font-size:{max(base + 3, 13)}pt; font-weight:700; }}
        #SharedStateMessage {{ color:{t.muted}; }}
        #StatePrimaryButton, #StateSecondaryButton {{ border:1px solid {t.border}; border-radius:8px; padding:6px 11px; color:{t.text}; }}
        #StatePrimaryButton {{ background:{panel_surface}; }}
        #StateSecondaryButton {{ background:transparent; }}
        #StatePrimaryButton:hover, #StateSecondaryButton:hover {{ border-color:{t.accent}; color:{t.accent}; }}
        #StatePrimaryButton:focus, #StateSecondaryButton:focus {{ border:2px solid {t.accent}; }}
        #StateProgress {{ background:{panel_surface}; border:1px solid {t.border}; border-radius:4px; min-height:7px; max-height:7px; text-align:center; }}
        #StateProgress::chunk {{ background:{t.accent}; border-radius:3px; }}
        #Toast {{ background:{panel_surface}; border:1px solid {t.border}; border-radius:10px; }}
        #Toast[toastLevel="error"] {{ border-color:{t.accent}; }}
        #ToastTitle {{ color:{t.text}; font-weight:700; }}
        #ToastMessage {{ color:{t.muted}; }}
        #ToastClose {{ background:transparent; border:0; color:{t.muted}; min-width:22px; max-width:22px; min-height:22px; max-height:22px; }}
        #ToastClose:hover {{ color:{t.accent}; }}
        #IssueIndicator {{ background:{panel_surface}; border:1px solid {t.accent}; border-radius:11px; padding:5px 9px; color:{t.accent}; }}
        #IssueIndicator:hover {{ background:{t.background}; }}
        #IssueMenu {{ background:{panel_surface}; color:{t.text}; border:1px solid {t.border}; }}
        QComboBox, QLineEdit {{ background:{panel_surface}; border:1px solid {t.border}; border-radius:5px; padding:{button_vpad}px 8px; color:{t.text}; selection-background-color:{t.accent}; selection-color:{t.background}; }}
        QComboBox QAbstractItemView {{ background:{t.panel}; color:{t.text}; selection-background-color:{t.accent}; selection-color:{t.background}; border:1px solid {t.border}; }}
        QAbstractScrollArea, QScrollArea {{ background:transparent; border:0; }}
        QAbstractScrollArea::viewport {{ background:transparent; }}
        QScrollBar:vertical {{ background:{panel_surface}; width:11px; margin:2px; }}
        QScrollBar::handle:vertical {{ background:{t.accent}; min-height:34px; border-radius:4px; }}
        QToolButton {{ background:transparent; border:0; color:{t.text}; font-size:{max(base + 5, 15)}pt; }}
        QCheckBox {{ spacing:6px; }}
        QCheckBox::indicator {{ width:24px; height:14px; border-radius:7px; background:{t.muted}; }}
        QCheckBox::indicator:checked {{ background:{t.accent}; }}
        QSlider::groove:horizontal {{ height:3px; background:{t.border}; border-radius:1px; }}
        QSlider::sub-page:horizontal {{ background:{t.accent}; border-radius:1px; }}
        QSlider::handle:horizontal {{ background:{t.text}; border:1px solid {t.border}; width:11px; margin:-5px 0; border-radius:6px; }}
        """

    def _has_theme(self, key: str) -> bool:
        return key in THEMES or key in self._saved_themes

    def _theme_for_key(self, key: str) -> Theme:
        if key in THEMES:
            return THEMES[key]
        return self._theme_from_bundle(self._saved_themes[key])

    @staticmethod
    def _theme_from_bundle(bundle: Mapping[str, Any]) -> Theme:
        palette = bundle["palette"]
        palette_fields = (field.name for field in fields(Theme) if field.name != "name")
        return Theme(str(bundle["name"]), **{key: palette[key] for key in palette_fields})

    @staticmethod
    def _apply_overrides(base: Theme, overrides: Mapping[str, str]) -> Theme:
        values = base.palette()
        values.update({key: value for key, value in overrides.items() if key in values})
        return Theme(base.name, **values)

    def _load_custom_overrides(self) -> dict[str, str]:
        raw = self.settings.value("appearance/theme_overrides", "")
        if not raw:
            return {}
        try:
            parsed = json.loads(str(raw))
        except (TypeError, json.JSONDecodeError):
            return {}
        if not isinstance(parsed, dict):
            return {}
        allowed = self._base_theme.palette()
        result: dict[str, str] = {}
        for key, value in parsed.items():
            if key not in allowed:
                continue
            try:
                result[key] = normalize_hex_color(str(value))
            except ThemeBundleError:
                continue
        return result

    def _persist_custom_overrides(self) -> None:
        self.settings.set_value("appearance/theme_overrides", json.dumps(self._custom, sort_keys=True))

    def _load_saved_themes(self) -> dict[str, dict[str, Any]]:
        raw = self.settings.value("appearance/saved_themes", "")
        if not raw:
            return {}
        try:
            parsed = json.loads(str(raw))
        except (TypeError, json.JSONDecodeError):
            return {}
        if not isinstance(parsed, dict):
            return {}
        result: dict[str, dict[str, Any]] = {}
        for key, bundle in parsed.items():
            if not str(key).startswith("custom:"):
                continue
            try:
                result[str(key)] = validate_theme_bundle(bundle)
            except ThemeBundleError:
                continue
        return result

    def _persist_saved_themes(self) -> None:
        self.settings.set_value("appearance/saved_themes", json.dumps(self._saved_themes, sort_keys=True))

    def _saved_key_for_name(self, name: str) -> str | None:
        folded = name.casefold()
        for key, bundle in self._saved_themes.items():
            if str(bundle.get("name", "")).casefold() == folded:
                return key
        return None

    def _allocate_saved_key(self, name: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-") or "theme"
        candidate = f"custom:{slug}"
        index = 2
        while candidate in self._saved_themes:
            candidate = f"custom:{slug}-{index}"
            index += 1
        return candidate

    @staticmethod
    def _css_rgba(color: str, alpha: int) -> str:
        color = normalize_hex_color(color)
        red = int(color[1:3], 16)
        green = int(color[3:5], 16)
        blue = int(color[5:7], 16)
        return f"rgba({red}, {green}, {blue}, {max(0, min(255, alpha))})"
