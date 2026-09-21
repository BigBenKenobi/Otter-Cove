from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class DemoScenario(str, Enum):
    """Deterministic fixture scenarios used to exercise shared UI states."""

    SUCCESS = "success"
    EMPTY = "empty"
    LOADING = "loading"
    FAILURE = "failure"
    CANCELLATION = "cancellation"

    @classmethod
    def parse(cls, value: str | "DemoScenario") -> "DemoScenario":
        if isinstance(value, cls):
            return value
        normalized = str(value).strip().lower()
        return cls(normalized)


class DemoStatus(str, Enum):
    LOADING = "loading"
    SUCCESS = "success"
    EMPTY = "empty"
    FAILURE = "failure"
    CANCELLED = "cancelled"
    STALE = "stale"


@dataclass(frozen=True, slots=True)
class DemoRequest:
    request_id: int
    scenario: DemoScenario


@dataclass(frozen=True, slots=True)
class DemoOutcome:
    request_id: int
    status: DemoStatus
    title: str
    message: str
    payload: Any = None
    stale: bool = False


class DeterministicDemoAdapter:
    """Small request-token state machine for GUI-only demo flows.

    Starting a new request supersedes the previous request. Completing a superseded
    request returns STALE, so delayed timers cannot overwrite a newer result.
    Retrying always allocates a fresh request id and therefore cannot duplicate the
    original request.
    """

    def __init__(self) -> None:
        self._next_request_id = 1
        self._active: DemoRequest | None = None
        self._last_scenario = DemoScenario.SUCCESS

    @property
    def active_request(self) -> DemoRequest | None:
        return self._active

    @property
    def active_request_id(self) -> int | None:
        return None if self._active is None else self._active.request_id

    @property
    def last_scenario(self) -> DemoScenario:
        return self._last_scenario

    def begin(self, scenario: str | DemoScenario) -> DemoRequest:
        parsed = DemoScenario.parse(scenario)
        request = DemoRequest(self._next_request_id, parsed)
        self._next_request_id += 1
        self._active = request
        self._last_scenario = parsed
        return request

    def retry(self, scenario: str | DemoScenario | None = None) -> DemoRequest:
        return self.begin(self._last_scenario if scenario is None else scenario)

    def cancel(self, request_id: int) -> DemoOutcome:
        if self._active is None or self._active.request_id != request_id:
            return self._stale(request_id)
        self._active = None
        return DemoOutcome(
            request_id,
            DemoStatus.CANCELLED,
            "Cancelled",
            "The demo request was cancelled. No result was applied.",
        )

    def complete(self, request_id: int) -> DemoOutcome:
        request = self._active
        if request is None or request.request_id != request_id:
            return self._stale(request_id)

        scenario = request.scenario
        if scenario is DemoScenario.LOADING:
            # Explicit loading fixtures stay pending until cancelled or superseded.
            return DemoOutcome(
                request_id,
                DemoStatus.LOADING,
                "Loading",
                "This deterministic fixture remains in the loading state.",
            )

        self._active = None
        if scenario is DemoScenario.SUCCESS:
            return DemoOutcome(
                request_id,
                DemoStatus.SUCCESS,
                "Loaded",
                "The deterministic demo request completed successfully.",
                payload={"fixture": "success", "request_id": request_id},
            )
        if scenario is DemoScenario.EMPTY:
            return DemoOutcome(
                request_id,
                DemoStatus.EMPTY,
                "Nothing here yet",
                "The request completed successfully but returned no items.",
                payload=[],
            )
        if scenario is DemoScenario.FAILURE:
            return DemoOutcome(
                request_id,
                DemoStatus.FAILURE,
                "Couldn’t load this view",
                "The deterministic fixture returned a recoverable demo error.",
            )
        if scenario is DemoScenario.CANCELLATION:
            return DemoOutcome(
                request_id,
                DemoStatus.CANCELLED,
                "Cancelled",
                "The deterministic fixture cancelled before applying a result.",
            )
        raise AssertionError(f"Unhandled demo scenario: {scenario}")

    @staticmethod
    def _stale(request_id: int) -> DemoOutcome:
        return DemoOutcome(
            request_id,
            DemoStatus.STALE,
            "Stale result ignored",
            "A newer request already owns this view, so this result was not applied.",
            stale=True,
        )
