from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject, QElapsedTimer, QTimer, Qt, Signal
from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QPainter

from .base import BackgroundEffect, EffectSettings
from .solid import SolidEffect
from .dots import DotsEffect
from .rain import RainEffect
from .constellations import ConstellationsEffect
from .synapse import SynapseEffect
from .flow import PerlinFlowEffect
from .petals import PetalsEffect
from .sparkles import SparklesEffect
from .embers import EmbersEffect
from .leaves import LeavesEffect


class BackgroundEffectManager(QObject):
    """Single timing/quality/pause controller for all animated backgrounds."""

    frameRequested = Signal()
    effectChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._registry: dict[str, Callable[[], BackgroundEffect]] = {
            cls.name: cls for cls in (
                SolidEffect, DotsEffect, SynapseEffect, RainEffect,
                ConstellationsEffect, PerlinFlowEffect, PetalsEffect,
                SparklesEffect, EmbersEffect, LeavesEffect,
            )
        }
        self.settings = EffectSettings()
        self._width = 1; self._height = 1
        self._effect: BackgroundEffect = LeavesEffect()
        self._effect.set_settings(self.settings)
        self._effect.reset(self._width, self._height)
        self._paused = False
        self._suspended = False

        self._clock = QElapsedTimer(); self._clock.start()
        self._timer = QTimer(self)
        self._timer.setTimerType(Qt.PreciseTimer)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._tick)
        self._sync_timer()

    @property
    def effect_name(self) -> str: return self._effect.name

    @property
    def available_effects(self) -> tuple[str, ...]: return tuple(self._registry)

    @property
    def paused(self) -> bool: return self._paused

    @property
    def suspended(self) -> bool: return self._suspended

    @property
    def timer_active(self) -> bool: return self._timer.isActive()

    @property
    def animated(self) -> bool: return self._effect.animated

    def set_effect(self, name: str) -> None:
        factory = self._registry.get(name)
        if factory is None or name == self._effect.name: return
        self._effect = factory()
        self._effect.set_settings(self.settings)
        self._effect.reset(self._width, self._height)
        self._clock.restart(); self._sync_timer(); self.frameRequested.emit(); self.effectChanged.emit(name)

    def resize(self, width: int, height: int) -> None:
        width = max(1, width)
        height = max(1, height)
        first_real_size = self._width <= 1 or self._height <= 1
        self._width = width
        self._height = height
        if first_real_size and width > 1 and height > 1:
            self._effect.reset(width, height)
        else:
            self._effect.resize(width, height)

    def reset(self) -> None:
        self._effect.reset(self._width,self._height); self._clock.restart(); self.frameRequested.emit()

    def set_paused(self, paused: bool) -> None:
        self._paused = bool(paused)
        self._clock.restart()
        self._sync_timer()

    def set_suspended(self, suspended: bool) -> None:
        """Temporarily stop rendering while the canvas is hidden.

        This is separate from the user's pause setting, so showing the canvas
        again never accidentally unpauses an effect they explicitly paused.
        """
        self._suspended = bool(suspended)
        self._clock.restart()
        self._sync_timer()

    def set_speed(self, speed: float) -> None:
        self.settings.speed=max(.05,float(speed)); self._effect.set_settings(self.settings)

    def set_intensity(self, intensity: float) -> None:
        self.settings.intensity=max(.05,float(intensity)); self._effect.set_settings(self.settings); self.frameRequested.emit()

    def set_quality(self, quality: float) -> None:
        self.settings.quality=max(.25,float(quality)); self._effect.set_settings(self.settings); self.frameRequested.emit()

    def set_size(self, size: float) -> None:
        self.settings.size=max(.25,float(size)); self._effect.set_settings(self.settings); self.frameRequested.emit()

    def paint(self, painter: QPainter, rect: QRectF, accent: QColor) -> None:
        self._effect.paint(painter, rect, accent)

    def _sync_timer(self) -> None:
        should_run = self._effect.animated and not self._paused and not self._suspended
        if should_run and not self._timer.isActive(): self._timer.start()
        elif not should_run and self._timer.isActive(): self._timer.stop()

    def _tick(self) -> None:
        # Cap dt after stalls/window drags so particles never teleport across screen.
        dt = min(0.05, max(0.0, self._clock.restart() / 1000.0))
        if dt <= 0.0: return
        self._effect.update(dt)
        self.frameRequested.emit()
