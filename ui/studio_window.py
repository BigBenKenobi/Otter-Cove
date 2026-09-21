from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QPoint, QRect, QSize, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from core.settings import AppSettings


_QT_MAX = 16777215


class ResizeGrip(QFrame):
    """Bottom-right resize handle for an ordinary child widget."""

    def __init__(self, owner: "StudioWindow") -> None:
        super().__init__(owner)
        self.owner = owner
        self.setObjectName("StudioResizeGrip")
        self.setFixedSize(16, 16)
        self.setCursor(Qt.SizeFDiagCursor)
        self.setToolTip("Resize window")
        self._press_global: QPoint | None = None
        self._start_size: QSize | None = None

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and not self.owner.is_minimized():
            self._press_global = event.globalPosition().toPoint()
            self._start_size = self.owner.size()
            self.owner.activate()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._press_global is not None and self._start_size is not None and event.buttons() & Qt.LeftButton:
            delta = event.globalPosition().toPoint() - self._press_global
            parent = self.owner.parentWidget()
            max_width = _QT_MAX if parent is None else max(self.owner.minimumWidth(), parent.width() - self.owner.x() - 8)
            max_height = _QT_MAX if parent is None else max(self.owner.minimumHeight(), parent.height() - self.owner.y() - 8)
            width = min(max_width, max(self.owner.minimumWidth(), self._start_size.width() + delta.x()))
            height = min(max_height, max(self.owner.minimumHeight(), self._start_size.height() + delta.y()))
            self.owner.resize(width, height)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if self._press_global is not None:
            self.owner.commit_geometry()
        self._press_global = None
        self._start_size = None
        super().mouseReleaseEvent(event)


class StudioTitleBar(QFrame):
    """Drag surface for an embedded StudioWindow."""

    def __init__(self, owner: "StudioWindow", title: str, icon: str = "◎") -> None:
        super().__init__(owner)
        self.owner = owner
        self.setObjectName("StudioWindowTitlebar")
        self.setCursor(Qt.OpenHandCursor)
        self._drag_origin: QPoint | None = None
        self._window_origin: QPoint | None = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 8, 7)
        layout.setSpacing(6)

        self.title_label = QLabel(f"{icon}  {title}".strip())
        self.title_label.setObjectName("StudioWindowTitle")
        layout.addWidget(self.title_label)
        layout.addStretch()

        self.peek_button = QPushButton("◉ Peek")
        self.peek_button.setObjectName("StudioPeekButton")
        self.peek_button.setCheckable(True)
        self.peek_button.setCursor(Qt.PointingHandCursor)
        self.peek_button.setToolTip("Temporarily fade the tool body to inspect the workspace")
        self.peek_button.toggled.connect(owner.set_peeked)
        layout.addWidget(self.peek_button)
        layout.addStretch()

        self.minimize_button = QToolButton()
        self.minimize_button.setObjectName("StudioTitleButton")
        self.minimize_button.setText("−")
        self.minimize_button.setCursor(Qt.PointingHandCursor)
        self.minimize_button.setToolTip("Minimize")
        self.minimize_button.clicked.connect(owner.toggle_minimized)
        layout.addWidget(self.minimize_button)

        self.close_button = QToolButton()
        self.close_button.setObjectName("StudioTitleButton")
        self.close_button.setText("×")
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.close_button.setToolTip("Close")
        self.close_button.clicked.connect(owner.request_close)
        layout.addWidget(self.close_button)

    def set_title(self, title: str, icon: str = "◎") -> None:
        self.title_label.setText(f"{icon}  {title}".strip())

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._drag_origin = event.globalPosition().toPoint()
            self._window_origin = self.owner.pos()
            self.owner.activate()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._drag_origin is not None and self._window_origin is not None and event.buttons() & Qt.LeftButton:
            delta = event.globalPosition().toPoint() - self._drag_origin
            self.owner.move_bounded(self._window_origin + delta)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if self._drag_origin is not None:
            self.owner.commit_geometry()
        self._drag_origin = None
        self._window_origin = None
        self.setCursor(Qt.OpenHandCursor)
        super().mouseReleaseEvent(event)


class StudioWindow(QFrame):
    """Reusable movable/resizable inner window used by Stark Studio tools.

    Close is intentionally a hide operation owned by ``StudioWindowManager`` so
    the content widget and its unsaved/local UI state survive close/reopen cycles.
    Normal and minimized geometries are tracked independently; collapsing a tool
    can therefore never overwrite its full-size restore geometry.
    """

    closeRequested = Signal()
    normalGeometryCommitted = Signal(object)
    minimizedGeometryCommitted = Signal(object)
    minimizedChanged = Signal(bool)
    peekChanged = Signal(bool)
    activated = Signal()

    def __init__(self, title: str, icon: str = "◎", parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("StudioWindow")
        self.setMinimumSize(360, 240)
        self.setFocusPolicy(Qt.StrongFocus)
        self._minimized = False
        self._peeked = False
        self._normal_geometry = QRect(0, 0, 570, 720)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.titlebar = StudioTitleBar(self, title, icon)
        root.addWidget(self.titlebar)

        self.body = QFrame()
        self.body.setObjectName("StudioWindowBody")
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(0)
        root.addWidget(self.body, 1)

        self.grip = ResizeGrip(self)
        self.grip.raise_()

    def set_content(self, widget: QWidget) -> None:
        while self.body_layout.count():
            item = self.body_layout.takeAt(0)
            old = item.widget()
            if old is not None:
                old.setParent(None)
        self.body_layout.addWidget(widget)

    def content_widget(self) -> QWidget | None:
        if not self.body_layout.count():
            return None
        return self.body_layout.itemAt(0).widget()

    def set_title(self, title: str, icon: str = "◎") -> None:
        self.titlebar.set_title(title, icon)

    def is_minimized(self) -> bool:
        return self._minimized

    def is_peeked(self) -> bool:
        return self._peeked

    def normal_geometry(self) -> QRect:
        return QRect(self._normal_geometry)

    def set_normal_geometry(self, rect: QRect) -> None:
        """Restore a persisted full-size geometry without entering minimized state."""
        rect = QRect(rect)
        rect.setWidth(max(self.minimumWidth(), rect.width()))
        rect.setHeight(max(self.minimumHeight(), rect.height()))
        self._normal_geometry = rect
        if not self._minimized:
            self.setGeometry(rect)

    def activate(self) -> None:
        self.raise_()
        self.setFocus(Qt.OtherFocusReason)
        self.activated.emit()

    def request_close(self) -> None:
        self.commit_geometry()
        self.closeRequested.emit()

    def toggle_minimized(self) -> None:
        self.set_minimized(not self._minimized)

    def set_minimized(self, minimized: bool) -> None:
        minimized = bool(minimized)
        if minimized == self._minimized:
            return

        if minimized:
            # Capture the full geometry before fixed-height collapse can generate a
            # resize event. This is the critical restore geometry.
            self._normal_geometry = QRect(self.geometry())
            self.normalGeometryCommitted.emit(QRect(self._normal_geometry))
            self._minimized = True
            self.body.hide()
            self.grip.hide()
            self.setFixedHeight(self.titlebar.sizeHint().height() + 2)
            self.titlebar.minimize_button.setText("□")
            self.titlebar.minimize_button.setToolTip("Restore")
            self.ensure_in_bounds()
            self.minimizedGeometryCommitted.emit(QRect(self.geometry()))
        else:
            # Release the fixed height while the minimized flag is still true, so
            # the transient resize cannot overwrite _normal_geometry.
            self.setMaximumHeight(_QT_MAX)
            self.setMinimumHeight(240)
            self._minimized = False
            restore = QRect(self._normal_geometry)
            # If the minimized bar was dragged, its current position is the most
            # intuitive restore position while the full-size dimensions remain.
            restore.moveTopLeft(self.pos())
            self._normal_geometry = restore
            self.setGeometry(restore)
            self.body.show()
            self.grip.show()
            self.titlebar.minimize_button.setText("−")
            self.titlebar.minimize_button.setToolTip("Minimize")
            self.ensure_in_bounds()
            self.normalGeometryCommitted.emit(QRect(self._normal_geometry))

        self.minimizedChanged.emit(minimized)

    def set_peeked(self, peeked: bool) -> None:
        peeked = bool(peeked)
        self._peeked = peeked
        if self.titlebar.peek_button.isChecked() != peeked:
            previous = self.titlebar.peek_button.blockSignals(True)
            self.titlebar.peek_button.setChecked(peeked)
            self.titlebar.peek_button.blockSignals(previous)
        effect = self.body.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(self.body)
            self.body.setGraphicsEffect(effect)
        effect.setOpacity(0.18 if self._peeked else 1.0)
        self.titlebar.peek_button.setAccessibleDescription(
            "Peek is on. Tool content is visually faded; the titlebar remains interactive."
            if self._peeked
            else "Peek is off. Tool content is fully visible."
        )
        self.peekChanged.emit(self._peeked)

    def move_bounded(self, point: QPoint) -> None:
        parent = self.parentWidget()
        if parent is None:
            self.move(point)
            return
        margin = 8
        max_x = max(margin, parent.width() - self.width() - margin)
        max_y = max(margin, parent.height() - self.height() - margin)
        x = min(max(point.x(), margin), max_x)
        y = min(max(point.y(), margin), max_y)
        self.move(x, y)

    def ensure_in_bounds(self) -> None:
        """Keep the complete titlebar and resize affordance reachable in the host."""
        parent = self.parentWidget()
        if parent is None:
            return
        margin = 8
        max_width = max(self.minimumWidth(), parent.width() - margin * 2)
        width = min(self.width(), max_width)

        if self._minimized:
            # Fixed height is retained; only the width may need recovery.
            if width != self.width():
                self.resize(width, self.height())
        else:
            max_height = max(self.minimumHeight(), parent.height() - margin * 2)
            height = min(self.height(), max_height)
            if width != self.width() or height != self.height():
                self.resize(width, height)

        self.move_bounded(self.pos())
        if not self._minimized:
            self._normal_geometry = QRect(self.geometry())

    def commit_geometry(self) -> None:
        """Commit the stable geometry after user drag/resize/state transitions."""
        if self._minimized:
            # Preserve the current bar position in both records, but never its
            # collapsed height in the normal geometry record.
            self._normal_geometry.moveTopLeft(self.pos())
            self.normalGeometryCommitted.emit(QRect(self._normal_geometry))
            self.minimizedGeometryCommitted.emit(QRect(self.geometry()))
        else:
            self._normal_geometry = QRect(self.geometry())
            self.normalGeometryCommitted.emit(QRect(self._normal_geometry))

    def moveEvent(self, event) -> None:
        super().moveEvent(event)
        if self._minimized:
            self._normal_geometry.moveTopLeft(self.pos())
        else:
            self._normal_geometry = QRect(self.geometry())

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.grip.move(max(0, self.width() - self.grip.width() - 2), max(0, self.height() - self.grip.height() - 2))
        self.grip.raise_()
        if not self._minimized:
            self._normal_geometry = QRect(self.geometry())

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.activate()
        super().mousePressEvent(event)


class StudioWindowManager:
    """Owns embedded tool windows and persists their lifecycle/geometry."""

    def __init__(self, host: QWidget, settings: AppSettings) -> None:
        self.host = host
        self.settings = settings
        self.windows: dict[str, StudioWindow] = {}

    def _save_normal(self, key: str, rect: QRect) -> None:
        self.settings.set_window_normal_rect(key, rect)

    def _save_minimized(self, key: str, rect: QRect) -> None:
        self.settings.set_window_minimized_rect(key, rect)

    def open_window(
        self,
        key: str,
        title: str,
        factory: Callable[[], QWidget],
        *,
        icon: str = "◎",
        default_rect: QRect | None = None,
    ) -> StudioWindow:
        existing = self.windows.get(key)
        if existing is not None:
            # Route activation doubles as restore: a minimized tool should never
            # require a second click before its body becomes usable again.
            if existing.is_minimized():
                existing.set_minimized(False)
            existing.show()
            existing.ensure_in_bounds()
            existing.commit_geometry()
            existing.activate()
            return existing

        fallback = default_rect or QRect(44, 28, 570, 720)
        window = StudioWindow(title, icon, self.host)
        window.set_content(factory())
        window.set_normal_geometry(self.settings.window_normal_rect(key, fallback))
        window.closeRequested.connect(lambda k=key: self.hide_window(k))
        window.normalGeometryCommitted.connect(lambda geometry, k=key: self._save_normal(k, geometry))
        window.minimizedGeometryCommitted.connect(lambda geometry, k=key: self._save_minimized(k, geometry))
        self.windows[key] = window
        window.show()
        window.ensure_in_bounds()
        window.activate()
        # Persist any bounds recovery immediately so a changed display size does
        # not produce the same invalid geometry on the next restart.
        window.commit_geometry()
        return window

    def hide_window(self, key: str) -> None:
        window = self.windows.get(key)
        if window is None:
            return
        window.commit_geometry()
        self.settings.sync()
        window.hide()

    def toggle_window(
        self,
        key: str,
        title: str,
        factory: Callable[[], QWidget],
        *,
        icon: str = "◎",
        default_rect: QRect | None = None,
    ) -> StudioWindow | None:
        window = self.windows.get(key)
        if window is not None and window.isVisible():
            self.hide_window(key)
            return None
        return self.open_window(key, title, factory, icon=icon, default_rect=default_rect)

    def keep_in_bounds(self) -> None:
        for window in self.windows.values():
            if window.isVisible():
                window.ensure_in_bounds()
                window.commit_geometry()

    def save_all(self) -> None:
        for window in self.windows.values():
            window.commit_geometry()
        self.settings.sync()
