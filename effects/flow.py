from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPen

from .base import BackgroundEffect


class PerlinFlowEffect(BackgroundEffect):
    name = "Perlin Flow"

    def __init__(self, seed: int = 81427): super().__init__(seed); self.time = 0.0

    def reset(self, width: int, height: int) -> None: super().reset(width, height); self.time = 0.0

    def update(self, dt: float) -> None: self.time += dt * self.settings.speed

    def paint(self, painter: QPainter, rect: QRectF, accent: QColor) -> None:
        c = QColor(accent); c.setAlpha(32); painter.setPen(QPen(c, .65))
        scale = max(.5, self.settings.quality); rows = max(6, int(11*scale)); cols = max(9, int(17*scale))
        for row in range(rows):
            y=(row+1)*self.height/(rows+1)
            for col in range(cols):
                x=(col+1)*self.width/(cols+1); ang=math.sin(col*.68 + row*.51 + self.time*.8)*1.9 + math.cos(row*.23-self.time*.4)*.45; length=10.0 * self.settings.size
                painter.drawLine(QPointF(x,y), QPointF(x+length*math.cos(ang), y+length*math.sin(ang)))
