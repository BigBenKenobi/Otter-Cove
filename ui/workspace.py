from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from core.data import SessionService
from core.theme import Theme
from .background import BackgroundCanvas
from .chat import ChatSurface


class Workspace(QWidget):
    """Layered host: animated background, chat surface, then floating tool windows."""

    resized = Signal()

    def __init__(self, theme: Theme, sessions: SessionService, parent=None) -> None:
        super().__init__(parent)
        self.background = BackgroundCanvas(theme, self)
        self.chat = ChatSurface(sessions, self)
        self.background.lower()
        self.chat.raise_()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        rect = self.rect()
        self.background.setGeometry(rect)
        self.chat.setGeometry(rect)
        self.resized.emit()
