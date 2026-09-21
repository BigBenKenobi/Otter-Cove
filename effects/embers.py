from __future__ import annotations

from dataclasses import dataclass
import math

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QPainter, QBrush

from .base import BackgroundEffect


@dataclass
class Ember:
    x: float; y: float; size: float; rise: float; drift: float; phase: float; alpha: int


class EmbersEffect(BackgroundEffect):
    name = "Embers"

    def __init__(self, seed: int = 81427):
        super().__init__(seed); self.embers: list[Ember] = []

    def _ember(self, anywhere=True):
        return Ember(self.rng.uniform(0, self.width), self.rng.uniform(0, self.height) if anywhere else self.height + self.rng.uniform(4, 35), self.rng.uniform(1.3, 3.0), self.rng.uniform(8, 22), self.rng.uniform(2, 8), self.rng.uniform(0, math.tau), self.rng.randint(24, 58))

    def reset(self, width: int, height: int) -> None:
        super().reset(width, height); self.embers = [self._ember() for _ in range(self.count(44, 10))]

    def set_settings(self, settings) -> None:
        super().set_settings(settings)
        if self.embers: self.reset(self.width, self.height)

    def update(self, dt: float) -> None:
        for i, e in enumerate(self.embers):
            e.phase += dt * 1.2 * self.settings.speed
            e.y -= e.rise * dt * self.settings.speed
            e.x += math.sin(e.phase) * e.drift * dt * self.settings.speed
            if e.y < -20: self.embers[i] = self._ember(False)

    def paint(self, painter: QPainter, rect: QRectF, accent: QColor) -> None:
        painter.setPen(Qt.NoPen)
        scale = self.settings.size
        for e in self.embers:
            c = QColor(accent); c.setAlpha(e.alpha)
            painter.setBrush(QBrush(c)); painter.save(); painter.translate(e.x, e.y); painter.rotate(math.sin(e.phase) * 30); painter.drawEllipse(QRectF(-e.size * .5 * scale, -e.size * 1.4 * scale, e.size * scale, e.size * 2.8 * scale)); painter.restore()
