from __future__ import annotations

from dataclasses import dataclass
import math

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QBrush

from .base import BackgroundEffect


@dataclass
class Dot:
    x: float
    y: float
    r: float
    phase: float
    dx: float
    dy: float


class DotsEffect(BackgroundEffect):
    name = "Dots"

    def __init__(self, seed: int = 81427):
        super().__init__(seed); self.dots: list[Dot] = []

    def reset(self, width: int, height: int) -> None:
        super().reset(width, height)
        self.dots = [Dot(self.rng.uniform(0, self.width), self.rng.uniform(0, self.height), self.rng.uniform(.8, 1.8), self.rng.uniform(0, 6.28), self.rng.uniform(-3, 3), self.rng.uniform(-2, 2)) for _ in range(self.count(76, 18))]

    def set_settings(self, settings) -> None:
        super().set_settings(settings)
        if self.dots:
            self.reset(self.width, self.height)

    def update(self, dt: float) -> None:
        for d in self.dots:
            d.phase += dt * .7 * self.settings.speed
            d.x = self.wrap(d.x + d.dx * dt * self.settings.speed, self.width, 4)
            d.y = self.wrap(d.y + d.dy * dt * self.settings.speed, self.height, 4)

    def paint(self, painter: QPainter, rect: QRectF, accent: QColor) -> None:
        painter.setPen(Qt.NoPen)
        for d in self.dots:
            c = QColor(accent); c.setAlpha(int(28 + 18 * (0.5 + 0.5 * math.sin(d.phase))))
            painter.setBrush(QBrush(c)); r = d.r * self.settings.size; painter.drawEllipse(QPointF(d.x, d.y), r, r)
