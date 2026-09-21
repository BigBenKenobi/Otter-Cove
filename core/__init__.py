"""Core services.

Data services intentionally remain importable without Qt so migrations and
persistence tests can run headlessly. Qt-backed settings/theme objects are loaded
lazily when the GUI imports them.
"""

from .data import AppDataServices, DataStoreError, LocalDataService, SessionService
from .demo_states import DemoOutcome, DemoRequest, DemoScenario, DemoStatus, DeterministicDemoAdapter
from .routes import DEFAULT_ROUTE_REGISTRY, RouteRegistry, RouteSpec
from .shell_state import ShellState

__all__ = [
    "AppSettings",
    "AppDataServices",
    "DataStoreError",
    "LocalDataService",
    "SessionService",
    "RouteSpec",
    "RouteRegistry",
    "DEFAULT_ROUTE_REGISTRY",
    "ShellState",
    "DemoScenario",
    "DemoStatus",
    "DemoRequest",
    "DemoOutcome",
    "DeterministicDemoAdapter",
    "Theme",
    "ThemeManager",
    "THEMES",
]


def __getattr__(name: str):
    if name == "AppSettings":
        from .settings import AppSettings
        return AppSettings
    if name in {"Theme", "ThemeManager", "THEMES"}:
        from .theme import THEMES, Theme, ThemeManager
        return {"Theme": Theme, "ThemeManager": ThemeManager, "THEMES": THEMES}[name]
    raise AttributeError(name)
