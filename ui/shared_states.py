from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAccessible, QAccessibleAnnouncementEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.demo_states import DemoOutcome, DemoScenario, DemoStatus, DeterministicDemoAdapter


def announce_status(widget: QWidget, message: str, *, assertive: bool = False) -> None:
    """Expose a state change to assistive technologies without moving keyboard focus."""

    if not message:
        return
    widget.setAccessibleDescription(message)
    try:
        event = QAccessibleAnnouncementEvent(widget, message)
        event.setPoliteness(
            QAccessible.AnnouncementPoliteness.Assertive
            if assertive
            else QAccessible.AnnouncementPoliteness.Polite
        )
        QAccessible.updateAccessibility(event)
    except Exception:
        # Accessibility backends can be unavailable in headless/offscreen runs.
        # The accessible name/description remain available to assistive clients.
        pass


class SharedStateCard(QFrame):
    """Base visual for reusable empty/loading/error/success/cancelled states."""

    actionTriggered = None

    def __init__(
        self,
        title: str,
        message: str,
        *,
        icon: str = "·",
        action_label: str | None = None,
        action: Callable[[], None] | None = None,
        secondary_label: str | None = None,
        secondary_action: Callable[[], None] | None = None,
        state_kind: str = "neutral",
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("SharedStateCard")
        self.setProperty("stateKind", state_kind)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAccessibleName(title)
        self.setAccessibleDescription(message)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(9)

        heading_row = QHBoxLayout()
        heading_row.setSpacing(9)
        self.icon_label = QLabel(icon)
        self.icon_label.setObjectName("SharedStateIcon")
        self.icon_label.setAccessibleName("")
        heading_row.addWidget(self.icon_label, 0, Qt.AlignTop)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("SharedStateTitle")
        self.title_label.setWordWrap(True)
        heading_row.addWidget(self.title_label, 1)
        layout.addLayout(heading_row)

        self.message_label = QLabel(message)
        self.message_label.setObjectName("SharedStateMessage")
        self.message_label.setWordWrap(True)
        self.message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.message_label)

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)
        layout.addLayout(self.content_layout)

        button_row = QHBoxLayout()
        button_row.setSpacing(8)
        self.primary_button: QPushButton | None = None
        self.secondary_button: QPushButton | None = None

        if action_label:
            self.primary_button = QPushButton(action_label)
            self.primary_button.setObjectName("StatePrimaryButton")
            self.primary_button.setCursor(Qt.PointingHandCursor)
            self.primary_button.setFocusPolicy(Qt.StrongFocus)
            self.primary_button.setAccessibleName(action_label)
            if action is not None:
                self.primary_button.clicked.connect(action)
            button_row.addWidget(self.primary_button)

        if secondary_label:
            self.secondary_button = QPushButton(secondary_label)
            self.secondary_button.setObjectName("StateSecondaryButton")
            self.secondary_button.setCursor(Qt.PointingHandCursor)
            self.secondary_button.setFocusPolicy(Qt.StrongFocus)
            self.secondary_button.setAccessibleName(secondary_label)
            if secondary_action is not None:
                self.secondary_button.clicked.connect(secondary_action)
            button_row.addWidget(self.secondary_button)

        button_row.addStretch()
        layout.addLayout(button_row)

    def announce(self, *, assertive: bool = False) -> None:
        announce_status(self, f"{self.title_label.text()}. {self.message_label.text()}", assertive=assertive)


class EmptyState(SharedStateCard):
    def __init__(self, title: str, message: str, *, action_label: str | None = None, action=None, parent=None) -> None:
        super().__init__(
            title,
            message,
            icon="○",
            action_label=action_label,
            action=action,
            state_kind="empty",
            parent=parent,
        )


class LoadingState(SharedStateCard):
    def __init__(self, title: str, message: str, *, cancel_label: str = "Cancel", cancel=None, parent=None) -> None:
        super().__init__(
            title,
            message,
            icon="↻",
            action_label=cancel_label,
            action=cancel,
            state_kind="loading",
            parent=parent,
        )
        self.progress = QProgressBar()
        self.progress.setObjectName("StateProgress")
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.progress.setAccessibleName("Loading")
        self.content_layout.addWidget(self.progress)


class ErrorState(SharedStateCard):
    def __init__(
        self,
        title: str,
        message: str,
        *,
        retry_label: str = "Retry",
        retry=None,
        secondary_label: str | None = None,
        secondary_action=None,
        parent=None,
    ) -> None:
        super().__init__(
            title,
            message,
            icon="!",
            action_label=retry_label,
            action=retry,
            secondary_label=secondary_label,
            secondary_action=secondary_action,
            state_kind="error",
            parent=parent,
        )

    def announce(self, *, assertive: bool = True) -> None:
        super().announce(assertive=assertive)


class CancelledState(SharedStateCard):
    def __init__(self, title: str, message: str, *, retry_label: str = "Try again", retry=None, parent=None) -> None:
        super().__init__(
            title,
            message,
            icon="×",
            action_label=retry_label,
            action=retry,
            state_kind="cancelled",
            parent=parent,
        )


class SuccessState(SharedStateCard):
    def __init__(self, title: str, message: str, *, action_label: str | None = None, action=None, parent=None) -> None:
        super().__init__(
            title,
            message,
            icon="✓",
            action_label=action_label,
            action=action,
            state_kind="success",
            parent=parent,
        )


class StateHost(QWidget):
    """Own one shared state card at a time and preserves focus outside state changes."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("StateHost")
        self._current: QWidget | None = None
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

    @property
    def current(self) -> QWidget | None:
        return self._current

    def set_state(self, widget: QWidget, *, announce: bool = True, assertive: bool = False) -> None:
        previous = self._current
        if previous is not None:
            self._layout.removeWidget(previous)
            previous.deleteLater()
        self._current = widget
        widget.setParent(self)
        self._layout.addWidget(widget)
        if announce and hasattr(widget, "announce"):
            QTimer.singleShot(0, lambda w=widget, a=assertive: w.announce(assertive=a))


class DemoStateHost(StateHost):
    """Qt presentation wrapper around DeterministicDemoAdapter.

    A completion callback always carries its request id. If a retry or new fixture
    has already started, the adapter reports STALE and the callback is ignored.
    """

    def __init__(self, module_title: str, *, feedback=None, parent=None) -> None:
        super().__init__(parent)
        self.module_title = module_title
        self.feedback = feedback
        self.adapter = DeterministicDemoAdapter()
        self._scenario = DemoScenario.SUCCESS
        self._completion_delay_ms = 420

    def run(self, scenario: str | DemoScenario) -> int:
        self._scenario = DemoScenario.parse(scenario)
        request = self.adapter.begin(self._scenario)
        self._show_loading(request.request_id)
        if self._scenario is DemoScenario.LOADING:
            return request.request_id
        QTimer.singleShot(self._completion_delay_ms, lambda rid=request.request_id: self.finish(rid))
        return request.request_id

    def retry(self) -> int:
        request = self.adapter.retry(self._scenario)
        self._show_loading(request.request_id)
        if self._scenario is not DemoScenario.LOADING:
            QTimer.singleShot(self._completion_delay_ms, lambda rid=request.request_id: self.finish(rid))
        return request.request_id

    def cancel_active(self) -> None:
        request_id = self.adapter.active_request_id
        if request_id is None:
            return
        self._apply_outcome(self.adapter.cancel(request_id))

    def finish(self, request_id: int) -> DemoOutcome:
        outcome = self.adapter.complete(request_id)
        if outcome.status is not DemoStatus.STALE:
            self._apply_outcome(outcome)
        return outcome

    def _show_loading(self, request_id: int) -> None:
        state = LoadingState(
            f"Loading {self.module_title}",
            f"Demo request {request_id} is in progress. Starting another request will supersede this one.",
            cancel=self.cancel_active,
        )
        self.set_state(state)

    def _apply_outcome(self, outcome: DemoOutcome) -> None:
        if outcome.status is DemoStatus.LOADING:
            return
        if outcome.status is DemoStatus.SUCCESS:
            state = SuccessState(
                f"{self.module_title} loaded",
                outcome.message,
                action_label="Run again",
                action=self.retry,
            )
            self.set_state(state)
            if self.feedback is not None:
                self.feedback.success(self.module_title, "Demo state loaded successfully.")
            return
        if outcome.status is DemoStatus.EMPTY:
            state = EmptyState(
                f"No {self.module_title.lower()} items yet",
                outcome.message,
                action_label="Retry demo",
                action=self.retry,
            )
            self.set_state(state)
            return
        if outcome.status is DemoStatus.FAILURE:
            state = ErrorState(
                f"Couldn’t load {self.module_title}",
                outcome.message,
                retry=self.retry,
            )
            self.set_state(state, assertive=True)
            if self.feedback is not None:
                self.feedback.error(
                    self.module_title,
                    outcome.message,
                    important=True,
                )
            return
        if outcome.status is DemoStatus.CANCELLED:
            state = CancelledState(
                f"{self.module_title} request cancelled",
                outcome.message,
                retry=self.retry,
            )
            self.set_state(state)
