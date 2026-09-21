from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QPainter, QPen

from .base import BackgroundEffect


@dataclass
class Drop:
    x: float
    y: float
    length: float
    speed: float
    opacity: int


class RainEffect(BackgroundEffect):
    name = "Rain"

    def __init__(self, seed: int = 81427):
        super().__init__(seed)
        self.drops: list[Drop] = []

    def _drop(self, anywhere=True) -> Drop:
        return Drop(
            self.rng.uniform(0, self.width),
            self.rng.uniform(0, self.height) if anywhere else self.rng.uniform(-90, -8),
            self.rng.uniform(9, 28),
            self.rng.uniform(70, 165),
            self.rng.randint(25, 70),
        )

    def reset(self, width: int, height: int) -> None:
        super().reset(width, height)
        self.drops = [self._drop(True) for _ in range(self.count(58, 14))]

    def set_settings(self, settings) -> None:
        super().set_settings(settings)
        if not self.drops:
            return
        target = self.count(58, 14)
        while len(self.drops) < target:
            self.drops.append(self._drop(True))
        del self.drops[target:]

    def update(self, dt: float) -> None:
        for i, d in enumerate(self.drops):
            d.y += d.speed * dt * self.settings.speed
            d.x += d.speed * 0.035 * dt * self.settings.speed
            if d.y > self.height + d.length:
                self.drops[i] = self._drop(False)

    def paint(self, painter: QPainter, rect: QRectF, accent: QColor) -> None:
        for d in self.drops:
            c = QColor(accent); c.setAlpha(d.opacity)
            scale = self.settings.size
            painter.setPen(QPen(c, max(0.55, 0.8 * scale)))
            painter.drawLine(int(d.x), int(d.y), int(d.x + 1.5 * scale), int(d.y + d.length * scale))
