from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ShellState:
    """Small, UI-framework-independent state owned by MainWindow.

    Feature modules keep their own domain state.  The shell only tracks routing
    and which tool has most recently been focused, avoiding route state hidden in
    individual widgets.
    """

    active_route: str = "new_chat"
    last_tool_route: str | None = None
    route_history: list[str] = field(default_factory=list)

    def activate(self, route: str, *, is_tool: bool = False) -> None:
        self.active_route = route
        if is_tool:
            self.last_tool_route = route
        if not self.route_history or self.route_history[-1] != route:
            self.route_history.append(route)
            if len(self.route_history) > 32:
                del self.route_history[:-32]
