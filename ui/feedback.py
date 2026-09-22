from __future__ import annotations

from dataclasses import dataclass
from itertools import count

from PySide6.QtCore import QEvent, QObject, Qt, QTimer, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMenu, QPushButton, QVBoxLayout, QWidget

from .shared_states import announce_status


@dataclass(frozen=True, slots=True)
class FeedbackEntry:
    entry_id: int
    level: str
    title: str
    message: str
    important: bool = False


class ToastWidget(QFrame):
    dismissed = Signal(int)

    def __init__(self, entry: FeedbackEntry, parent=None) -> None:
        super().__init__(parent)
        self.entry = entry
        self.setObjectName("Toast")
        self.setProperty("toastLevel", entry.level)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAccessibleName(entry.title)
        self.setAccessibleDescription(entry.message)
        self.setMinimumWidth(280)
        self.setMaximumWidth(370)

        root = QHBoxLayout(self)
        root.setContentsMargins(12, 10, 8, 10)
        root.setSpacing(10)

        body = QVBoxLayout()
        body.setSpacing(2)
        title = QLabel(entry.title)
        title.setObjectName("ToastTitle")
        title.setWordWrap(True)
        body.addWidget(title)
        message = QLabel(entry.message)
        message.setObjectName("ToastMessage")
        message.setWordWrap(True)
        body.addWidget(message)
        root.addLayout(body, 1)

        close = QPushButton("×")
        close.setObjectName("ToastClose")
        close.setCursor(Qt.PointingHandCursor)
        close.setFocusPolicy(Qt.NoFocus)
        close.setAccessibleName("Dismiss notification")
        close.clicked.connect(lambda: self.dismissed.emit(entry.entry_id))
        root.addWidget(close, 0, Qt.AlignTop)

    def announce(self) -> None:
        announce_status(
            self,
            f"{self.entry.title}. {self.entry.message}",
            assertive=self.entry.level == "error",
        )


class FeedbackManager(QObject):
    """Non-modal toast stack plus persistent history for important errors."""

    importantErrorsChanged = Signal(int)

    def __init__(self, host: QWidget) -> None:
        super().__init__(host)
        self.host = host
        self._ids = count(1)
        self._toasts: dict[int, ToastWidget] = {}
        self._history: list[FeedbackEntry] = []
        self._important: dict[int, FeedbackEntry] = {}
        host.installEventFilter(self)

        self.issue_button = QPushButton(host)
        self.issue_button.setObjectName("IssueIndicator")
        self.issue_button.setCursor(Qt.PointingHandCursor)
        self.issue_button.setFocusPolicy(Qt.StrongFocus)
        self.issue_button.setAccessibleName("Open important issues")
        self.issue_button.clicked.connect(self._show_issue_menu)
        self.issue_button.hide()

    @property
    def history(self) -> tuple[FeedbackEntry, ...]:
        return tuple(self._history)

    def important_errors(self) -> tuple[FeedbackEntry, ...]:
        return tuple(self._important.values())

    def info(self, title: str, message: str, *, timeout_ms: int = 4200) -> FeedbackEntry:
        return self.show("info", title, message, timeout_ms=timeout_ms)

    def success(self, title: str, message: str, *, timeout_ms: int = 3200) -> FeedbackEntry:
        return self.show("success", title, message, timeout_ms=timeout_ms)

    def error(
        self,
        title: str,
        message: str,
        *,
        important: bool = True,
        timeout_ms: int = 7000,
    ) -> FeedbackEntry:
        return self.show("error", title, message, important=important, timeout_ms=timeout_ms)

    def show(
        self,
        level: str,
        title: str,
        message: str,
        *,
        important: bool = False,
        timeout_ms: int = 4200,
    ) -> FeedbackEntry:
        entry = FeedbackEntry(next(self._ids), level, title.strip(), message.strip(), bool(important))
        self._history.append(entry)
        if entry.important:
            self._important[entry.entry_id] = entry
            self._sync_issue_button()

        toast = ToastWidget(entry, self.host)
        toast.dismissed.connect(self.dismiss)
        self._toasts[entry.entry_id] = toast
        toast.adjustSize()
        toast.show()
        toast.raise_()
        self._relayout()
        QTimer.singleShot(0, toast.announce)
        if timeout_ms > 0:
            QTimer.singleShot(timeout_ms, lambda eid=entry.entry_id: self.dismiss(eid))
        return entry

    def dismiss(self, entry_id: int) -> None:
        toast = self._toasts.pop(entry_id, None)
        if toast is None:
            return
        toast.hide()
        toast.deleteLater()
        self._relayout()
        # Important history deliberately remains until explicitly resolved.

    def resolve(self, entry_id: int) -> None:
        self.dismiss(entry_id)
        if self._important.pop(entry_id, None) is not None:
            self._sync_issue_button()

    def clear_resolved_history(self) -> None:
        important_ids = set(self._important)
        self._history = [entry for entry in self._history if entry.entry_id in important_ids]

    def eventFilter(self, watched, event) -> bool:
        if watched is self.host and event.type() in {QEvent.Resize, QEvent.Show}:
            QTimer.singleShot(0, self._relayout)
        return super().eventFilter(watched, event)

    def _sync_issue_button(self) -> None:
        count_issues = len(self._important)
        if count_issues:
            suffix = "issue" if count_issues == 1 else "issues"
            self.issue_button.setText(f"!  {count_issues} {suffix}")
            self.issue_button.setAccessibleDescription(
                f"{count_issues} important Otter Cove {suffix} remain available."
            )
            self.issue_button.adjustSize()
            self.issue_button.show()
            self.issue_button.raise_()
        else:
            self.issue_button.hide()
        self.importantErrorsChanged.emit(count_issues)
        self._relayout()

    def _show_issue_menu(self) -> None:
        menu = QMenu(self.issue_button)
        menu.setObjectName("IssueMenu")
        if not self._important:
            action = menu.addAction("No important issues")
            action.setEnabled(False)
        else:
            for entry in self._important.values():
                action = menu.addAction(f"{entry.title}: {entry.message}")
                action.setToolTip(entry.message)
                action.triggered.connect(lambda _checked=False, eid=entry.entry_id: self.resolve(eid))
            menu.addSeparator()
            clear = menu.addAction("Resolve all")
            clear.triggered.connect(self._resolve_all)
        menu.exec(self.issue_button.mapToGlobal(self.issue_button.rect().bottomRight()))

    def _resolve_all(self) -> None:
        for entry_id in tuple(self._important):
            self.resolve(entry_id)

    def _relayout(self) -> None:
        margin = 16
        gap = 8
        y = margin
        available_width = max(280, self.host.width() - margin * 2)
        for toast in list(self._toasts.values()):
            toast.setMaximumWidth(min(370, available_width))
            toast.adjustSize()
            x = max(margin, self.host.width() - toast.width() - margin)
            toast.move(x, y)
            toast.raise_()
            y += toast.height() + gap

        if self.issue_button.isVisible():
            self.issue_button.adjustSize()
            x = max(margin, self.host.width() - self.issue_button.width() - margin)
            y_button = max(margin, self.host.height() - self.issue_button.height() - margin)
            self.issue_button.move(x, y_button)
            self.issue_button.raise_()
