from __future__ import annotations

from dataclasses import dataclass
import random

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QPainter


@dataclass
class EffectSettings:
    """Shared runtime settings applied uniformly to every background effect."""

    speed: float = 1.0
    intensity: float = 1.0
    quality: float = 1.0
    size: float = 1.0


class BackgroundEffect:
    """Base contract for an Otter Cove animated background effect.

    Effects own their particles/state.  The manager owns timing.  This keeps the
    main window and canvas completely unaware of effect-specific behaviour.
    """

    name = "Base"
    animated = True

    def __init__(self, seed: int = 81427):
        self.seed = seed
        self.rng = random.Random(seed)
        self.width = 1
        self.height = 1
        self.settings = EffectSettings()

    def set_settings(self, settings: EffectSettings) -> None:
        self.settings = settings

    def reset(self, width: int, height: int) -> None:
        self.width = max(1, width)
        self.height = max(1, height)
        self.rng.seed(self.seed)

    def resize(self, width: int, height: int) -> None:
        self.width = max(1, width)
        self.height = max(1, height)

    def update(self, dt: float) -> None:
        """Advance state by dt seconds. Override in animated effects."""

    def paint(self, painter: QPainter, rect: QRectF, accent: QColor) -> None:
        """Draw the effect. Override in every concrete effect."""

    def count(self, base: int, minimum: int = 1) -> int:
        factor = max(0.05, self.settings.intensity) * max(0.25, self.settings.quality)
        return max(minimum, int(base * factor))

    @staticmethod
    def alpha(color: QColor, value: int) -> QColor:
        c = QColor(color)
        c.setAlpha(max(0, min(255, value)))
        return c

    @staticmethod
    def wrap(value: float, maximum: float, margin: float = 0.0) -> float:
        span = maximum + margin * 2.0
        if span <= 0:
            return 0.0
        return ((value + margin) % span) - margin
