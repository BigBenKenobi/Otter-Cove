from __future__ import annotations

from dataclasses import dataclass
import math

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPen, QBrush

from .base import BackgroundEffect


@dataclass
class Star:
    x: float; y: float; dx: float; dy: float; phase: float


class ConstellationsEffect(BackgroundEffect):
    name = "Constellations"

    def __init__(self, seed: int = 81427): super().__init__(seed); self.stars: list[Star] = []

    def reset(self, width: int, height: int) -> None:
        super().reset(width, height); self.stars = [Star(self.rng.uniform(0, self.width), self.rng.uniform(0, self.height), self.rng.uniform(-4, 4), self.rng.uniform(-3, 3), self.rng.uniform(0, math.tau)) for _ in range(self.count(30, 12))]

    def set_settings(self, settings) -> None:
        super().set_settings(settings)
        if self.stars: self.reset(self.width, self.height)

    def update(self, dt: float) -> None:
        for s in self.stars:
            s.x = self.wrap(s.x + s.dx * dt * self.settings.speed, self.width, 6); s.y = self.wrap(s.y + s.dy * dt * self.settings.speed, self.height, 6); s.phase += dt * self.settings.speed

    def paint(self, painter: QPainter, rect: QRectF, accent: QColor) -> None:
        link = QColor(accent); link.setAlpha(18); painter.setPen(QPen(link, .6)); limit = 150.0
        for i, a in enumerate(self.stars):
            for b in self.stars[i+1:i+7]:
                dx, dy = a.x-b.x, a.y-b.y; d2 = dx*dx + dy*dy
                if d2 < limit*limit: painter.drawLine(QPointF(a.x, a.y), QPointF(b.x, b.y))
        painter.setPen(Qt.NoPen)
        for s in self.stars:
            c = QColor(accent); c.setAlpha(int(34 + 24*(.5+.5*math.sin(s.phase)))); painter.setBrush(QBrush(c)); r = 1.25 * self.settings.size; painter.drawEllipse(QPointF(s.x, s.y), r, r)
