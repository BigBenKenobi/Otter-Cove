from __future__ import annotations

from collections.abc import Mapping

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QBrush, QPainter
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSlider,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from core.theme import THEMES, Theme
from core.theme_logic import generate_harmony, harmony_to_theme_changes


class SwatchButton(QPushButton):
    selected = Signal(str)

    def __init__(self, key: str, theme: Theme, parent=None) -> None:
        super().__init__(parent)
        self.key = key
        self.theme_data = theme
        self.setObjectName("SwatchButton")
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumSize(112, 52)
        self.clicked.connect(lambda: self.selected.emit(self.key))

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = [self.theme_data.background, self.theme_data.panel, self.theme_data.text, self.theme_data.accent]
        width = self.width()
        x = width / 2 - 24
        for color in colors:
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QRectF(x, 8, 15, 15))
            x += 16
        painter.setPen(QColor(self.theme_data.text))
        font = painter.font()
        # This is the tiny preview label inside a fixed-size swatch; application
        # typography still controls all normal labels and controls.
        font.setPointSizeF(max(7.0, font.pointSizeF() * 0.72))
        painter.setFont(font)
        painter.drawText(QRectF(4, 27, width - 8, 18), Qt.AlignCenter, self.theme_data.name)


class Section(QFrame):
    def __init__(self, title: str, symbol: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Section")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(12, 10, 12, 11)
        self.layout.setSpacing(8)
        label = QLabel(f"{symbol} {title}".strip())
        label.setObjectName("SectionTitle")
        self.layout.addWidget(label)
        rule = QFrame()
        rule.setFrameShape(QFrame.HLine)
        rule.setObjectName("SectionRule")
        self.layout.addWidget(rule)


class ColorDot(QPushButton):
    colorChanged = Signal(str)

    def __init__(self, color: str, parent=None) -> None:
        super().__init__(parent)
        self.color = color
        self.setCursor(Qt.PointingHandCursor)
        self.setAccessibleName("Color picker")
        self.setFixedSize(24, 24)
        self.clicked.connect(self.pick)
        self._refresh()

    def _refresh(self) -> None:
        self.setStyleSheet(
            f"QPushButton {{background:{self.color}; border:1px solid rgba(255,255,255,.22); border-radius:11px;}}"
        )

    def set_color(self, color: str) -> None:
        self.color = color
        self._refresh()

    def pick(self) -> None:
        before = self.color
        color = QColorDialog.getColor(QColor(before), self, "Choose color")
        # QColorDialog returns an invalid color on Cancel. Do not update either the
        # dot or the live theme in that case.
        if color.isValid():
            self.set_color(color.name())
            self.colorChanged.emit(self.color)


class HarmonyStrip(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.colors = ["#ffffff", "#dedede", "#989898", "#6a6a6a", "#444444"]
        self.setFixedHeight(20)
        self.setAccessibleName("Generated color harmony preview")

    def set_colors(self, colors: list[str] | tuple[str, ...]) -> None:
        self.colors = list(colors)
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        if not self.colors:
            return
        part = self.width() / len(self.colors)
        for index, color in enumerate(self.colors):
            painter.fillRect(QRectF(index * part, 0, part + 1, self.height()), QColor(color))


class ThemePanel(QFrame):
    themeSelected = Signal(str)
    customChanged = Signal(dict)
    resetCustomRequested = Signal()
    typographyChanged = Signal(dict)
    layoutChanged = Signal(dict)
    effectChanged = Signal(str)
    effectSettingsChanged = Signal(dict)
    saveThemeRequested = Signal(str)
    importThemeRequested = Signal()
    exportThemeRequested = Signal()

    def __init__(
        self,
        current_key: str,
        theme: Theme,
        *,
        effect: str = "Leaves",
        effect_color: str | None = None,
        speed: float = 1.0,
        intensity: float = 1.0,
        quality: float = 1.0,
        size: float = 1.0,
        paused: bool = False,
        density: str = "Comfortable",
        frosted: bool = False,
        saved_themes: Mapping[str, Theme] | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("ThemePanel")
        self._theme = theme
        self._current_key = current_key
        self._catalog: dict[str, Theme] = dict(THEMES)
        self._catalog.update(dict(saved_themes or {}))
        self._harmony_preview: tuple[str, str, str, str, str] | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        tabs = QFrame()
        tabs.setObjectName("TabBar")
        tb = QHBoxLayout(tabs)
        tb.setContentsMargins(10, 0, 10, 0)
        tb.setSpacing(4)
        self.themes_tab = QPushButton("◎ Themes")
        self.custom_tab = QPushButton("⌕ Customize")
        for button in (self.themes_tab, self.custom_tab):
            button.setCheckable(True)
            button.setCursor(Qt.PointingHandCursor)
            button.setObjectName("TabButton")
        group = QButtonGroup(self)
        group.setExclusive(True)
        group.addButton(self.themes_tab)
        group.addButton(self.custom_tab)
        self.themes_tab.setChecked(True)
        tb.addWidget(self.themes_tab)
        tb.addWidget(self.custom_tab)
        tb.addStretch()
        root.addWidget(tabs)

        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)
        self.stack.addWidget(self._build_themes())
        self.stack.addWidget(
            self._build_customize(
                effect,
                effect_color or theme.accent,
                speed,
                intensity,
                quality,
                size,
                paused,
                density,
                frosted,
            )
        )
        self.themes_tab.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.custom_tab.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.set_theme(current_key, theme)

    def _build_themes(self) -> QWidget:
        page = QWidget()
        page.setObjectName("ThemeScrollHost")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setAlignment(Qt.AlignTop)

        section = Section("Default Themes", "◎")
        grid = QGridLayout()
        grid.setSpacing(7)
        self.swatches: dict[str, SwatchButton] = {}
        for index, (key, theme) in enumerate(THEMES.items()):
            button = self._make_swatch(key, theme)
            grid.addWidget(button, index // 4, index % 4)
        section.layout.addLayout(grid)
        layout.addWidget(section)

        self.saved_section = Section("Saved Themes", "♡")
        self.saved_grid = QGridLayout()
        self.saved_grid.setSpacing(7)
        self.saved_section.layout.addLayout(self.saved_grid)
        layout.addWidget(self.saved_section)
        saved = [(key, theme) for key, theme in self._catalog.items() if key.startswith("custom:")]
        for index, (key, theme) in enumerate(saved):
            self.saved_grid.addWidget(self._make_swatch(key, theme), index // 4, index % 4)
        self.saved_section.setVisible(bool(saved))

        layout.addStretch()
        return page

    def _make_swatch(self, key: str, theme: Theme) -> SwatchButton:
        button = SwatchButton(key, theme)
        button.selected.connect(self._choose_theme)
        self.swatches[key] = button
        return button

    def add_saved_theme(self, key: str, theme: Theme) -> None:
        self._catalog[key] = theme
        if key in self.swatches:
            self.swatches[key].theme_data = theme
            self.swatches[key].update()
            return
        index = self.saved_grid.count()
        self.saved_grid.addWidget(self._make_swatch(key, theme), index // 4, index % 4)
        self.saved_section.show()

    def _build_customize(
        self,
        effect: str,
        effect_color: str,
        speed: float,
        intensity: float,
        quality: float,
        size: float,
        paused: bool,
        density: str,
        frosted: bool,
    ) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setObjectName("ThemeCustomizeScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        host = QWidget()
        host.setObjectName("ThemeScrollHost")
        root = QVBoxLayout(host)
        root.setContentsMargins(9, 9, 9, 12)
        root.setSpacing(9)
        root.setAlignment(Qt.AlignTop)

        colors = Section("Colors", "⌕")
        grid = QGridLayout()
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(6)
        self.color_dots: dict[str, ColorDot] = {}
        primary_keys = [
            ("Background", "background"),
            ("Text", "text"),
            ("Panel", "panel"),
            ("Sidebar", "sidebar"),
            ("Border", "border"),
            ("Accent", "accent"),
        ]
        for index, (label, key) in enumerate(primary_keys):
            column = 0 if index % 2 == 0 else 2
            row = index // 2
            grid.addWidget(QLabel(label), row, column)
            dot = self._make_color_dot(key)
            grid.addWidget(dot, row, column + 1, alignment=Qt.AlignRight)
        colors.layout.addLayout(grid)

        self.more_colors_host = QFrame()
        more_grid = QGridLayout(self.more_colors_host)
        more_grid.setContentsMargins(0, 0, 0, 0)
        more_grid.setHorizontalSpacing(24)
        expanded = [("Muted text", "muted"), ("Input background", "input_bg"), ("Send background", "send_bg")]
        for index, (label, key) in enumerate(expanded):
            column = 0 if index % 2 == 0 else 2
            row = index // 2
            more_grid.addWidget(QLabel(label), row, column)
            more_grid.addWidget(self._make_color_dot(key), row, column + 1, alignment=Qt.AlignRight)
        self._more_colors_expanded = False
        self.more_colors_host.hide()
        colors.layout.addWidget(self.more_colors_host)

        more_row = QHBoxLayout()
        self.more_colors_button = QPushButton("▸ More Colors")
        self.more_colors_button.setObjectName("FlatLineButton")
        self.more_colors_button.setCursor(Qt.PointingHandCursor)
        self.more_colors_button.clicked.connect(self._toggle_more_colors)
        reset_colors = QPushButton("Reset colors")
        reset_colors.setObjectName("OutlineButton")
        reset_colors.setCursor(Qt.PointingHandCursor)
        reset_colors.setToolTip("Discard custom overrides and restore the selected preset")
        reset_colors.clicked.connect(self.resetCustomRequested.emit)
        more_row.addWidget(self.more_colors_button, 1)
        more_row.addWidget(reset_colors)
        colors.layout.addLayout(more_row)
        root.addWidget(colors)

        harmony = Section("Color Harmony", "⌘")
        hgrid = QGridLayout()
        hgrid.setVerticalSpacing(8)
        hgrid.addWidget(QLabel("Accent Color"), 0, 0)
        self.accent_dot = ColorDot(self._theme.accent)
        hgrid.addWidget(self.accent_dot, 1, 0, alignment=Qt.AlignLeft)
        hgrid.addWidget(QLabel("Harmony"), 0, 1)
        self.harmony_combo = QComboBox()
        self.harmony_combo.addItems(["Complementary", "Analogous", "Triadic", "Split Complementary"])
        hgrid.addWidget(self.harmony_combo, 1, 1)
        hgrid.addWidget(QLabel("Mode"), 2, 0)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Light", "Dark"])
        self.mode_combo.setCurrentText("Dark")
        hgrid.addWidget(self.mode_combo, 3, 0)
        generate = QPushButton("Generate")
        generate.setObjectName("OutlineButton")
        generate.setCursor(Qt.PointingHandCursor)
        generate.clicked.connect(self._generate_harmony)
        hgrid.addWidget(generate, 3, 1)
        harmony.layout.addLayout(hgrid)
        self.harmony_strip = HarmonyStrip()
        harmony.layout.addWidget(self.harmony_strip)
        harmony_actions = QHBoxLayout()
        self.harmony_apply = QPushButton("Apply")
        self.harmony_apply.setObjectName("OutlineButton")
        self.harmony_apply.setCursor(Qt.PointingHandCursor)
        self.harmony_apply.setEnabled(False)
        self.harmony_apply.clicked.connect(self._apply_harmony)
        harmony_reset = QPushButton("Reset preview")
        harmony_reset.setObjectName("OutlineButton")
        harmony_reset.setCursor(Qt.PointingHandCursor)
        harmony_reset.clicked.connect(self._reset_harmony_preview)
        harmony_actions.addWidget(self.harmony_apply)
        harmony_actions.addWidget(harmony_reset)
        harmony_actions.addStretch()
        harmony.layout.addLayout(harmony_actions)
        root.addWidget(harmony)

        layout_sec = Section("Font & Layout", "T")
        lgrid = QGridLayout()
        lgrid.setHorizontalSpacing(8)
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Monospace", "Sans Serif", "Serif"])
        self.density_combo = QComboBox()
        self.density_combo.addItems(["Compact", "Comfortable", "Roomy"])
        self.density_combo.setCurrentText(density if density in {"Compact", "Comfortable", "Roomy"} else "Comfortable")
        self.size_combo = QComboBox()
        self.size_combo.addItems(["Small", "Default", "Large"])
        self.size_combo.setCurrentText("Default")
        self.frost_check = QCheckBox("Frosted")
        self.frost_check.setChecked(bool(frosted))
        self.frost_check.setToolTip("Uses translucent in-app surfaces. Native compositor blur is not required for this milestone.")
        for column, (label, widget) in enumerate(
            [("Font", self.font_combo), ("Density", self.density_combo), ("Text size", self.size_combo), ("", self.frost_check)]
        ):
            if label:
                lgrid.addWidget(QLabel(label), 0, column)
            lgrid.addWidget(widget, 1, column)
        layout_sec.layout.addLayout(lgrid)

        effect_row = QHBoxLayout()
        effect_box = QVBoxLayout()
        effect_box.addWidget(QLabel("Background / Effect"))
        self.effect_combo = QComboBox()
        self.effect_combo.addItems(["Solid", "Dots", "Synapse", "Rain", "Constellations", "Perlin Flow", "Petals", "Sparkles", "Embers", "Leaves"])
        available = {self.effect_combo.itemText(i) for i in range(self.effect_combo.count())}
        self.effect_combo.setCurrentText(effect if effect in available else "Leaves")
        effect_box.addWidget(self.effect_combo)
        effect_row.addLayout(effect_box, 1)
        effect_color_box = QVBoxLayout()
        effect_color_box.addWidget(QLabel("Effect color"))
        self.effect_color = ColorDot(effect_color)
        effect_color_box.addWidget(self.effect_color, alignment=Qt.AlignLeft)
        effect_row.addLayout(effect_color_box)
        layout_sec.layout.addLayout(effect_row)

        anim_grid = QGridLayout()
        anim_grid.setHorizontalSpacing(8)
        anim_grid.setVerticalSpacing(5)
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["Slow", "Normal", "Fast"])
        self.speed_combo.setCurrentText(self._speed_label(speed))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Low", "Balanced", "High"])
        self.quality_combo.setCurrentText(self._quality_label(quality))
        self.intensity_slider = QSlider(Qt.Horizontal)
        self.intensity_slider.setRange(25, 180)
        self.intensity_slider.setValue(round(intensity * 100))
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(50, 180)
        self.size_slider.setValue(round(size * 100))
        self.pause_animation = QCheckBox("Pause animation")
        self.pause_animation.setChecked(paused)
        anim_grid.addWidget(QLabel("Speed"), 0, 0)
        anim_grid.addWidget(QLabel("Quality"), 0, 1)
        anim_grid.addWidget(QLabel("Intensity"), 2, 0)
        anim_grid.addWidget(QLabel("Size"), 2, 1)
        anim_grid.addWidget(self.speed_combo, 1, 0)
        anim_grid.addWidget(self.quality_combo, 1, 1)
        anim_grid.addWidget(self.intensity_slider, 3, 0)
        anim_grid.addWidget(self.size_slider, 3, 1)
        anim_grid.addWidget(self.pause_animation, 4, 0, 1, 2)
        layout_sec.layout.addLayout(anim_grid)
        root.addWidget(layout_sec)

        saved = Section("Save / Share", "♡")
        save_row = QHBoxLayout()
        self.theme_name = QLineEdit("My Theme")
        self.theme_name.setAccessibleName("Saved theme name")
        save = QPushButton("Save")
        save.setObjectName("OutlineButton")
        save.setCursor(Qt.PointingHandCursor)
        save.clicked.connect(lambda: self.saveThemeRequested.emit(self.theme_name.text().strip()))
        save_row.addWidget(self.theme_name, 1)
        save_row.addWidget(save)
        saved.layout.addLayout(save_row)
        share_row = QHBoxLayout()
        imp = QPushButton("↑ Import")
        exp = QPushButton("↓ Export")
        for button in (imp, exp):
            button.setObjectName("OutlineButton")
            button.setCursor(Qt.PointingHandCursor)
        imp.clicked.connect(self.importThemeRequested.emit)
        exp.clicked.connect(self.exportThemeRequested.emit)
        share_row.addWidget(imp)
        share_row.addWidget(exp)
        saved.layout.addLayout(share_row)
        root.addWidget(saved)
        root.addStretch()

        self.effect_combo.currentTextChanged.connect(self._effect_selected)
        self.speed_combo.currentTextChanged.connect(self._emit_effect_settings)
        self.quality_combo.currentTextChanged.connect(self._emit_effect_settings)
        self.intensity_slider.valueChanged.connect(self._emit_effect_settings)
        self.size_slider.valueChanged.connect(self._emit_effect_settings)
        self.pause_animation.toggled.connect(self._emit_effect_settings)
        self.effect_color.colorChanged.connect(self._emit_effect_settings)
        self.font_combo.currentTextChanged.connect(lambda value: self.typographyChanged.emit({"font": value}))
        self.size_combo.currentTextChanged.connect(lambda value: self.typographyChanged.emit({"size": value}))
        self.density_combo.currentTextChanged.connect(lambda value: self.layoutChanged.emit({"density": value}))
        self.frost_check.toggled.connect(lambda value: self.layoutChanged.emit({"frosted": bool(value)}))
        self._sync_effect_capabilities()
        scroll.setWidget(host)
        return scroll

    def _make_color_dot(self, key: str) -> ColorDot:
        dot = ColorDot(getattr(self._theme, key))
        dot.setAccessibleName(f"{key.replace('_', ' ').title()} color")
        dot.colorChanged.connect(lambda value, k=key: self.customChanged.emit({k: value}))
        self.color_dots[key] = dot
        return dot

    def _toggle_more_colors(self) -> None:
        # Track expansion independently of effective widget visibility. A widget
        # inside a hidden stacked page reports isVisible() == False even after it
        # has explicitly been set visible, which made toggle state tab-dependent.
        self._more_colors_expanded = not self._more_colors_expanded
        self.more_colors_host.setVisible(self._more_colors_expanded)
        self.more_colors_button.setText(
            "▾ More Colors" if self._more_colors_expanded else "▸ More Colors"
        )

    def set_theme(self, key: str, theme: Theme) -> None:
        self._current_key = key
        self._theme = theme
        self._catalog[key] = theme
        for name, button in getattr(self, "swatches", {}).items():
            button.setChecked(name == key)
        for color_key, dot in getattr(self, "color_dots", {}).items():
            dot.set_color(getattr(theme, color_key))
        if hasattr(self, "accent_dot"):
            self.accent_dot.set_color(theme.accent)
        self._reset_harmony_preview()

    def set_effect_settings(self, changes: Mapping[str, object]) -> None:
        blockers = [
            self.effect_combo.blockSignals(True), self.speed_combo.blockSignals(True), self.quality_combo.blockSignals(True),
            self.intensity_slider.blockSignals(True), self.size_slider.blockSignals(True), self.pause_animation.blockSignals(True),
        ]
        try:
            if "name" in changes:
                self.effect_combo.setCurrentText(str(changes["name"]))
            if "color" in changes:
                self.effect_color.set_color(str(changes["color"]))
            if "speed" in changes:
                self.speed_combo.setCurrentText(self._speed_label(float(changes["speed"])))
            if "quality" in changes:
                self.quality_combo.setCurrentText(self._quality_label(float(changes["quality"])))
            if "intensity" in changes:
                self.intensity_slider.setValue(round(float(changes["intensity"]) * 100))
            if "size" in changes:
                self.size_slider.setValue(round(float(changes["size"]) * 100))
            if "paused" in changes:
                self.pause_animation.setChecked(bool(changes["paused"]))
        finally:
            # blockSignals returns the previous state. Restore each one exactly.
            for widget, previous in zip(
                (self.effect_combo, self.speed_combo, self.quality_combo, self.intensity_slider, self.size_slider, self.pause_animation),
                blockers,
            ):
                widget.blockSignals(previous)
        self._sync_effect_capabilities()

    def _choose_theme(self, key: str) -> None:
        theme = self._catalog.get(key)
        if theme is None:
            return
        self.set_theme(key, theme)
        self.themeSelected.emit(key)

    def _effect_selected(self, value: str) -> None:
        self._sync_effect_capabilities()
        self.effectChanged.emit(value)

    def _sync_effect_capabilities(self) -> None:
        if not hasattr(self, "effect_combo"):
            return
        animated = self.effect_combo.currentText() != "Solid"
        explanation = "Solid has no particle animation, so animation controls are not applicable."
        for widget in (
            self.speed_combo,
            self.quality_combo,
            self.intensity_slider,
            self.size_slider,
            self.pause_animation,
            self.effect_color,
        ):
            widget.setEnabled(animated)
            widget.setToolTip("" if animated else explanation)

    def _emit_effect_settings(self, *_args) -> None:
        speed = {"Slow": 0.55, "Normal": 1.0, "Fast": 1.65}[self.speed_combo.currentText()]
        quality = {"Low": 0.65, "Balanced": 1.0, "High": 1.35}[self.quality_combo.currentText()]
        self.effectSettingsChanged.emit(
            {
                "color": self.effect_color.color,
                "speed": speed,
                "quality": quality,
                "intensity": self.intensity_slider.value() / 100.0,
                "size": self.size_slider.value() / 100.0,
                "paused": self.pause_animation.isChecked(),
            }
        )

    def _generate_harmony(self) -> None:
        self._harmony_preview = generate_harmony(
            self.accent_dot.color,
            self.harmony_combo.currentText(),
            self.mode_combo.currentText(),
        )
        self.harmony_strip.set_colors(self._harmony_preview)
        self.harmony_apply.setEnabled(True)

    def _apply_harmony(self) -> None:
        if self._harmony_preview is None:
            return
        changes = harmony_to_theme_changes(self._harmony_preview, self.mode_combo.currentText())
        self.customChanged.emit(changes)

    def _reset_harmony_preview(self) -> None:
        self._harmony_preview = None
        if hasattr(self, "harmony_strip"):
            self.harmony_strip.set_colors([
                self._theme.background,
                self._theme.panel,
                self._theme.accent,
                self._theme.border,
                self._theme.muted,
            ])
        if hasattr(self, "harmony_apply"):
            self.harmony_apply.setEnabled(False)

    @staticmethod
    def _speed_label(speed: float) -> str:
        if speed < 0.8:
            return "Slow"
        if speed > 1.3:
            return "Fast"
        return "Normal"

    @staticmethod
    def _quality_label(quality: float) -> str:
        if quality < 0.8:
            return "Low"
        if quality > 1.15:
            return "High"
        return "Balanced"
