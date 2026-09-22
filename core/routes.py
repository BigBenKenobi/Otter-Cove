from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator


@dataclass(frozen=True, slots=True)
class RouteSpec:
    """Declarative description of a route exposed by the Otter Cove shell.

    The registry deliberately contains metadata only.  Widgets and backend logic
    remain outside this module so route validation can run without Qt.
    """

    key: str
    title: str
    kind: str
    icon: str = "◇"
    sidebar: bool = False
    available: bool = False
    description: str = ""

    def validate(self) -> None:
        if not self.key or any(char.isspace() for char in self.key):
            raise ValueError(f"Invalid route key: {self.key!r}")
        if self.kind not in {"command", "tool", "theme"}:
            raise ValueError(f"Unsupported route kind {self.kind!r} for {self.key!r}")
        if not self.title.strip():
            raise ValueError(f"Route {self.key!r} has no title")


class RouteRegistry:
    def __init__(self, routes: Iterable[RouteSpec]) -> None:
        self._routes: dict[str, RouteSpec] = {}
        self._order: list[str] = []
        for route in routes:
            route.validate()
            if route.key in self._routes:
                raise ValueError(f"Duplicate route: {route.key}")
            self._routes[route.key] = route
            self._order.append(route.key)

    def __contains__(self, key: str) -> bool:
        return key in self._routes

    def __iter__(self) -> Iterator[RouteSpec]:
        for key in self._order:
            yield self._routes[key]

    def get(self, key: str) -> RouteSpec | None:
        return self._routes.get(key)

    def require(self, key: str) -> RouteSpec:
        try:
            return self._routes[key]
        except KeyError as exc:
            raise KeyError(f"Unknown Otter Cove route: {key}") from exc

    def sidebar_routes(self) -> tuple[RouteSpec, ...]:
        return tuple(route for route in self if route.sidebar)

    def exposed_keys(self) -> tuple[str, ...]:
        return tuple(self._order)


DEFAULT_ROUTE_REGISTRY = RouteRegistry(
    (
        RouteSpec("new_chat", "New Chat", "command", "+", True, True, "Create a new local chat session."),
        RouteSpec("search", "Search", "tool", "⌕", True, False, "Conversation and library search. Searchable history arrives with the dedicated search milestone."),
        RouteSpec("email", "Email", "tool", "✉", True, False, "Inbox, message viewer, compose flow, accounts, filters and task integration. Local demo data first; mail adapters later."),
        RouteSpec("tools", "Tools", "tool", "⌁", True, False, "Composer tools and integration launchers will live here behind a common action registry."),
        RouteSpec("brain", "Brain", "tool", "◉", True, False, "Memories, Skills and Add flows with shared cards, search, confidence state and local persistence."),
        RouteSpec("calendar", "Calendar", "tool", "▣", True, False, "Local calendar shell, .ics import, month/week/day views and a provider adapter for CalDAV later."),
        RouteSpec("compare", "Model Compare", "tool", "▥", True, False, "Blind/parallel comparison workspace with model slots, reveal state and a local deterministic demo runner."),
        RouteSpec("cookbook", "Cookbook", "tool", "◫", True, False, "Local model/package management UI: cached models, launch/download state, dependencies and settings."),
        RouteSpec("research", "Deep Research", "tool", "⌾", True, False, "Research setup, rounds, format, provider/model choices, queued jobs and result documents."),
        RouteSpec("gallery", "Gallery", "tool", "▧", True, False, "Photos/albums first, then the canvas/layers editor as its own subsystem."),
        RouteSpec("library", "Library", "tool", "▤", True, False, "Chats, Documents, Research and Archive on a shared searchable item model."),
        RouteSpec("notes", "Notes", "tool", "⌑", True, False, "Dockable notes/reminders with list/grid views, archive state and local persistence."),
        RouteSpec("tasks", "Tasks", "tool", "▣", True, False, "Tasks, activity, completed jobs and scheduled actions using a local scheduler model."),
        RouteSpec("theme", "Theme", "theme", "◎", True, True, "Theme presets, customization and animated background controls."),
        RouteSpec("settings", "Settings", "tool", "⚙", False, True, "Appearance and shortcut editing are active in Phase A; model/default/search/integration sections follow in later Settings milestones."),
        RouteSpec("account", "Account", "tool", "A", False, False, "Profile, Study Mode and account flows. This is unavailable until the dedicated account milestone."),
        RouteSpec("model_selector", "Models", "tool", "◉", False, False, "Model registry with selected model, refresh, add and online/offline states."),
    )
)
