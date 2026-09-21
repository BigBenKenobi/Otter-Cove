from __future__ import annotations

from dataclasses import dataclass
import math

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QPainter, QPen, QBrush

from .base import BackgroundEffect


@dataclass
class Leaf:
    x: float
    y: float
    size: float
    fall: float
    phase: float
    sway: float
    angle: float
    spin: float
    opacity: int


class LeavesEffect(BackgroundEffect):
    name = "Leaves"

    def __init__(self, seed: int = 81427):
        super().__init__(seed)
        self.leaves: list[Leaf] = []

    def _make_leaf(self, anywhere: bool = True) -> Leaf:
        y = self.rng.uniform(-20, self.height + 20) if anywhere else self.rng.uniform(-42, -8)
        return Leaf(
            x=self.rng.uniform(-12, self.width + 12),
            y=y,
            size=self.rng.uniform(3.3, 6.6),
            fall=self.rng.uniform(8.0, 18.0),
            phase=self.rng.uniform(0.0, math.tau),
            sway=self.rng.uniform(5.0, 16.0),
            angle=self.rng.uniform(-38.0, 38.0),
            spin=self.rng.uniform(-19.0, 19.0),
            opacity=self.rng.randint(24, 58),
        )

    def reset(self, width: int, height: int) -> None:
        super().reset(width, height)
        self.leaves = [self._make_leaf(True) for _ in range(self.count(44, 10))]

    def _sync_count(self) -> None:
        target = self.count(44, 10)
        while len(self.leaves) < target:
            self.leaves.append(self._make_leaf(True))
        if len(self.leaves) > target:
            del self.leaves[target:]

    def set_settings(self, settings) -> None:
        super().set_settings(settings)
        if self.leaves:
            self._sync_count()

    def update(self, dt: float) -> None:
        speed = self.settings.speed
        for i, leaf in enumerate(self.leaves):
            leaf.phase += dt * (0.45 + leaf.fall * 0.018) * speed
            leaf.y += leaf.fall * dt * speed
            leaf.x += math.sin(leaf.phase) * leaf.sway * dt * 0.30 * speed
            leaf.angle += leaf.spin * dt * speed
            if leaf.y > self.height + 24 or leaf.x < -40 or leaf.x > self.width + 40:
                self.leaves[i] = self._make_leaf(False)

    def paint(self, painter: QPainter, rect: QRectF, accent: QColor) -> None:
        scale = self.settings.size
        for leaf in self.leaves:
            c = QColor(accent)
            c.setAlpha(leaf.opacity)
            painter.save()
            painter.translate(leaf.x, leaf.y)
            painter.rotate(leaf.angle + math.sin(leaf.phase) * 12.0)
            painter.setPen(QPen(c, max(0.55, leaf.size * 0.13 * scale)))
            painter.setBrush(QBrush(c))
            path_rect = QRectF(-leaf.size * 0.43 * scale, -leaf.size * scale, leaf.size * 0.86 * scale, leaf.size * 2.0 * scale)
            painter.drawEllipse(path_rect)
            stem = QColor(c)
            stem.setAlpha(min(75, leaf.opacity + 10))
            painter.setPen(QPen(stem, 0.7))
            painter.drawLine(0, int(-leaf.size * 0.65 * scale), 0, int(leaf.size * 0.78 * scale))
            painter.restore()
