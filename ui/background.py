from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget

from core.theme import Theme
from effects import BackgroundEffectManager


class BackgroundCanvas(QWidget):
    """Theme-aware paint surface backed by the reusable effect manager."""

    def __init__(self, theme: Theme, parent=None) -> None:
        super().__init__(parent)
        self.theme = theme
        self.effect_color = QColor(theme.accent)
        self.effects = BackgroundEffectManager(self)
        self.effects.frameRequested.connect(self.update)
        self.setAttribute(Qt.WA_OpaquePaintEvent, True)
        self._hidden_suspended = True
        self._external_suspended = False

    @property
    def effect(self) -> str:
        return self.effects.effect_name

    def available_effects(self) -> tuple[str, ...]:
        return self.effects.available_effects

    def set_theme(self, theme: Theme) -> None:
        self.theme = theme
        self.update()

    def set_effect(self, effect: str) -> None:
        self.effects.set_effect(effect)

    def set_effect_color(self, color: str) -> None:
        candidate = QColor(color)
        if not candidate.isValid():
            return
        self.effect_color = candidate
        self.update()

    def set_effect_suspended(self, suspended: bool) -> None:
        """External lifecycle suspension, independent from widget visibility."""
        self._external_suspended = bool(suspended)
        self._sync_suspension()

    def set_effect_speed(self, speed: float) -> None:
        self.effects.set_speed(speed)

    def set_effect_intensity(self, intensity: float) -> None:
        self.effects.set_intensity(intensity)

    def set_effect_quality(self, quality: float) -> None:
        self.effects.set_quality(quality)

    def set_effect_size(self, size: float) -> None:
        self.effects.set_size(size)

    def set_effect_paused(self, paused: bool) -> None:
        self.effects.set_paused(paused)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        size = event.size()
        self.effects.resize(size.width(), size.height())

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.effects.resize(self.width(), self.height())
        self._hidden_suspended = False
        self._sync_suspension()

    def hideEvent(self, event) -> None:
        self._hidden_suspended = True
        self._sync_suspension()
        super().hideEvent(event)

    def _sync_suspension(self) -> None:
        self.effects.set_suspended(self._hidden_suspended or self._external_suspended)

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.fillRect(self.rect(), QColor(self.theme.background))
        self.effects.paint(painter, QRectF(self.rect()), self.effect_color)
