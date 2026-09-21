from __future__ import annotations

from dataclasses import dataclass
import math

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QPainter, QPen

from .base import BackgroundEffect


@dataclass
class Sparkle:
    x: float; y: float; size: float; phase: float; rate: float


class SparklesEffect(BackgroundEffect):
    name = "Sparkles"

    def __init__(self, seed: int = 81427): super().__init__(seed); self.sparkles: list[Sparkle] = []

    def reset(self, width: int, height: int) -> None:
        super().reset(width, height); self.sparkles = [Sparkle(self.rng.uniform(0, self.width), self.rng.uniform(0, self.height), self.rng.uniform(2, 4.5), self.rng.uniform(0, math.tau), self.rng.uniform(.7, 2.1)) for _ in range(self.count(34, 9))]

    def set_settings(self, settings) -> None:
        super().set_settings(settings)
        if self.sparkles: self.reset(self.width, self.height)

    def update(self, dt: float) -> None:
        for s in self.sparkles: s.phase += dt * s.rate * self.settings.speed

    def paint(self, painter: QPainter, rect: QRectF, accent: QColor) -> None:
        for s in self.sparkles:
            glow = .5 + .5 * math.sin(s.phase); c = QColor(accent); c.setAlpha(int(20 + 65 * glow)); painter.setPen(QPen(c, .8)); r = s.size * (.65 + .55 * glow) * self.settings.size; painter.drawLine(int(s.x-r), int(s.y), int(s.x+r), int(s.y)); painter.drawLine(int(s.x), int(s.y-r), int(s.x), int(s.y+r))
