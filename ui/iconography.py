from __future__ import annotations

from PySide6.QtCore import Property, QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPalette, QPen
from PySide6.QtWidgets import QWidget


class LineIcon(QWidget):
    """Small resolution-independent line icon painted by Qt.

    This avoids using assorted Unicode glyphs as icons. Those glyphs have wildly
    different optical sizes and baselines across fonts/desktops, which made the
    sidebar look uneven on Fedora.  All icons here share one canvas and stroke.
    """

    def __init__(self, kind: str, size: int = 22, parent=None, *, follow_parent: bool = False) -> None:
        super().__init__(parent)
        self.kind = kind
        self._icon_color = QColor("#ffffff")
        self.follow_parent = follow_parent
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

    def get_icon_color(self) -> QColor:
        return QColor(self._icon_color)

    def set_icon_color(self, value) -> None:
        color = QColor(value)
        if color.isValid() and color != self._icon_color:
            self._icon_color = color
            self.update()

    iconColor = Property(QColor, get_icon_color, set_icon_color)

    def _color(self) -> QColor:
        if self.follow_parent and self.parentWidget() is not None:
            return self.parentWidget().palette().color(QPalette.ButtonText)
        return self._icon_color

    def paintEvent(self, event) -> None:
        del event
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        side = min(self.width(), self.height())
        # 18 logical units keeps each pictogram on the same optical canvas.
        scale = side / 24.0
        p.translate((self.width() - side) / 2.0, (self.height() - side) / 2.0)
        p.scale(scale, scale)
        pen = QPen(self._color(), 1.85, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        self._draw(p)

    def _draw(self, p: QPainter) -> None:
        k = self.kind
        if k == "new_chat":
            p.drawLine(QPointF(12, 5), QPointF(12, 19))
            p.drawLine(QPointF(5, 12), QPointF(19, 12))
        elif k == "search":
            p.drawEllipse(QRectF(5, 5, 10, 10))
            p.drawLine(QPointF(14.5, 14.5), QPointF(19, 19))
        elif k == "email":
            r = QRectF(4, 6.5, 16, 11)
            p.drawRoundedRect(r, 1.2, 1.2)
            p.drawLine(QPointF(4.8, 7.5), QPointF(12, 13))
            p.drawLine(QPointF(19.2, 7.5), QPointF(12, 13))
        elif k == "tools":
            # Compact wrench silhouette.
            p.drawLine(QPointF(7, 17), QPointF(16.4, 7.6))
            p.drawEllipse(QRectF(5.2, 15.2, 3.6, 3.6))
            p.drawLine(QPointF(15.1, 6.2), QPointF(18.4, 5.2))
            p.drawLine(QPointF(16.4, 7.6), QPointF(18.8, 9.8))
        elif k == "brain":
            # Node/network metaphor reads cleanly at 16 px and matches the app's
            # Brain concept better than a tiny Unicode dot.
            p.drawEllipse(QRectF(5, 9, 4, 4))
            p.drawEllipse(QRectF(10, 5, 4, 4))
            p.drawEllipse(QRectF(15, 10, 4, 4))
            p.drawEllipse(QRectF(9, 15, 4, 4))
            p.drawLine(QPointF(8.5, 10), QPointF(11.2, 8))
            p.drawLine(QPointF(13.6, 8.5), QPointF(16, 10.5))
            p.drawLine(QPointF(16, 13.5), QPointF(12.5, 16))
            p.drawLine(QPointF(9.5, 15.5), QPointF(8, 13))
        elif k == "calendar":
            p.drawRoundedRect(QRectF(5, 6.5, 14, 13), 1.3, 1.3)
            p.drawLine(QPointF(5, 10), QPointF(19, 10))
            p.drawLine(QPointF(9, 4.8), QPointF(9, 8))
            p.drawLine(QPointF(15, 4.8), QPointF(15, 8))
        elif k == "compare":
            p.drawRoundedRect(QRectF(4.5, 6, 6.5, 12), 1, 1)
            p.drawRoundedRect(QRectF(13, 6, 6.5, 12), 1, 1)
            p.drawLine(QPointF(8, 9), QPointF(8, 15))
            p.drawLine(QPointF(16, 9), QPointF(16, 15))
        elif k == "cookbook":
            path = QPainterPath(QPointF(12, 7))
            path.lineTo(9, 5.5)
            path.lineTo(5, 5.5)
            path.lineTo(5, 18)
            path.lineTo(9.4, 18)
            path.lineTo(12, 19)
            p.drawPath(path)
            path2 = QPainterPath(QPointF(12, 7))
            path2.lineTo(15, 5.5)
            path2.lineTo(19, 5.5)
            path2.lineTo(19, 18)
            path2.lineTo(14.6, 18)
            path2.lineTo(12, 19)
            p.drawPath(path2)
            p.drawLine(QPointF(12, 7), QPointF(12, 19))
        elif k == "research":
            p.drawEllipse(QRectF(5, 5, 13, 13))
            p.drawEllipse(QRectF(9.2, 9.2, 4.6, 4.6))
            p.drawLine(QPointF(15.7, 15.7), QPointF(19, 19))
        elif k == "gallery":
            p.drawRoundedRect(QRectF(4.5, 5.5, 15, 13), 1.3, 1.3)
            p.drawEllipse(QRectF(8, 8, 2.5, 2.5))
            path = QPainterPath(QPointF(6, 16.5))
            path.lineTo(10.3, 12.4)
            path.lineTo(13.2, 15)
            path.lineTo(15.5, 12.8)
            path.lineTo(18, 16.5)
            p.drawPath(path)
        elif k == "library":
            p.drawRoundedRect(QRectF(5, 5.5, 3.5, 13), .7, .7)
            p.drawRoundedRect(QRectF(10.2, 4.5, 3.5, 14), .7, .7)
            p.drawRoundedRect(QRectF(15.4, 6.5, 3.5, 12), .7, .7)
        elif k == "notes":
            p.drawRoundedRect(QRectF(5.5, 4.5, 13, 15), 1, 1)
            p.drawLine(QPointF(8.5, 9), QPointF(15.5, 9))
            p.drawLine(QPointF(8.5, 12.5), QPointF(15.5, 12.5))
            p.drawLine(QPointF(8.5, 16), QPointF(13.5, 16))
        elif k == "tasks":
            p.drawRoundedRect(QRectF(5, 5, 14, 14), 1.5, 1.5)
            path = QPainterPath(QPointF(8, 12))
            path.lineTo(10.7, 14.6)
            path.lineTo(16.5, 8.8)
            p.drawPath(path)
        elif k == "theme":
            p.drawEllipse(QRectF(8, 8, 8, 8))
            for a, b in [((12, 4.5), (12, 6.5)), ((12, 17.5), (12, 19.5)),
                         ((4.5, 12), (6.5, 12)), ((17.5, 12), (19.5, 12)),
                         ((6.7, 6.7), (8.1, 8.1)), ((15.9, 15.9), (17.3, 17.3)),
                         ((17.3, 6.7), (15.9, 8.1)), ((8.1, 15.9), (6.7, 17.3))]:
                p.drawLine(QPointF(*a), QPointF(*b))
        elif k == "shell":
            p.drawLine(QPointF(6.5, 8), QPointF(10.5, 12))
            p.drawLine(QPointF(10.5, 12), QPointF(6.5, 16))
            p.drawLine(QPointF(12.5, 16), QPointF(18, 16))
        elif k == "send":
            p.drawLine(QPointF(5, 12), QPointF(18.5, 12))
            p.drawLine(QPointF(14.2, 7.7), QPointF(18.5, 12))
            p.drawLine(QPointF(18.5, 12), QPointF(14.2, 16.3))
        else:
            p.drawEllipse(QRectF(8, 8, 8, 8))
