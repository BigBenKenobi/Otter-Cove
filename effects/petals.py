from __future__ import annotations

from dataclasses import dataclass
import math

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QPainter, QBrush

from .base import BackgroundEffect


@dataclass
class Petal:
    x: float; y: float; size: float; fall: float; phase: float; spin: float; angle: float; alpha: int


class PetalsEffect(BackgroundEffect):
    name = "Petals"

    def __init__(self, seed: int = 81427):
        super().__init__(seed); self.petals: list[Petal] = []

    def _petal(self, anywhere=True):
        return Petal(self.rng.uniform(-10, self.width + 10), self.rng.uniform(-10, self.height + 10) if anywhere else self.rng.uniform(-35, -5), self.rng.uniform(2.5, 5.0), self.rng.uniform(7, 17), self.rng.uniform(0, math.tau), self.rng.uniform(-28, 28), self.rng.uniform(0, 180), self.rng.randint(26, 62))

    def reset(self, width: int, height: int) -> None:
        super().reset(width, height); self.petals = [self._petal() for _ in range(self.count(38, 10))]

    def set_settings(self, settings) -> None:
        super().set_settings(settings)
        if self.petals: self.reset(self.width, self.height)

    def update(self, dt: float) -> None:
        for i, p in enumerate(self.petals):
            p.phase += dt * .8 * self.settings.speed; p.y += p.fall * dt * self.settings.speed; p.x += math.sin(p.phase) * 5 * dt * self.settings.speed; p.angle += p.spin * dt * self.settings.speed
            if p.y > self.height + 20: self.petals[i] = self._petal(False)

    def paint(self, painter: QPainter, rect: QRectF, accent: QColor) -> None:
        painter.setPen(Qt.NoPen)
        scale = self.settings.size
        for p in self.petals:
            c = QColor(accent); c.setAlpha(p.alpha); painter.setBrush(QBrush(c)); painter.save(); painter.translate(p.x, p.y); painter.rotate(p.angle); painter.drawEllipse(QRectF(-p.size * .55 * scale, -p.size * 1.35 * scale, p.size * 1.1 * scale, p.size * 2.7 * scale)); painter.restore()
