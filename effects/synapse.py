from __future__ import annotations

from dataclasses import dataclass
import math

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPen, QBrush

from .base import BackgroundEffect


@dataclass
class Node:
    x: float; y: float; phase: float; drift: float


class SynapseEffect(BackgroundEffect):
    name = "Synapse"

    def __init__(self, seed: int = 81427): super().__init__(seed); self.nodes: list[Node] = []; self.links: list[tuple[int,int]] = []

    def reset(self, width: int, height: int) -> None:
        super().reset(width, height)
        n = self.count(22, 10); self.nodes = [Node(self.rng.uniform(0,self.width), self.rng.uniform(0,self.height), self.rng.uniform(0,math.tau), self.rng.uniform(.6,1.4)) for _ in range(n)]
        self.links = []
        for i in range(n):
            choices = [j for j in range(max(0,i-3), min(n,i+4)) if j != i]
            if choices: self.links.append((i, self.rng.choice(choices)))

    def set_settings(self, settings) -> None:
        super().set_settings(settings)
        if self.nodes: self.reset(self.width, self.height)

    def update(self, dt: float) -> None:
        for n in self.nodes: n.phase += dt * n.drift * self.settings.speed

    def paint(self, painter: QPainter, rect: QRectF, accent: QColor) -> None:
        line = QColor(accent); line.setAlpha(24); painter.setPen(QPen(line, .7))
        for a,b in self.links:
            na, nb = self.nodes[a], self.nodes[b]; painter.drawLine(QPointF(na.x,na.y), QPointF(nb.x,nb.y))
        painter.setPen(Qt.NoPen)
        for n in self.nodes:
            c = QColor(accent); c.setAlpha(int(35 + 38*(.5+.5*math.sin(n.phase)))); painter.setBrush(QBrush(c)); r=(1.1+1.0*(.5+.5*math.sin(n.phase))) * self.settings.size; painter.drawEllipse(QPointF(n.x,n.y),r,r)
