from __future__ import annotations

import unittest

from core.routes import DEFAULT_ROUTE_REGISTRY, RouteRegistry, RouteSpec
from core.shell_state import ShellState


class RouteRegistryTests(unittest.TestCase):
    def test_default_registry_has_unique_resolvable_exposed_routes(self) -> None:
        keys = DEFAULT_ROUTE_REGISTRY.exposed_keys()
        self.assertEqual(len(keys), len(set(keys)))
        self.assertGreater(len(keys), 0)
        for key in keys:
            spec = DEFAULT_ROUTE_REGISTRY.require(key)
            self.assertEqual(spec.key, key)
            self.assertIn(spec.kind, {"command", "tool", "theme"})
            self.assertTrue(spec.title)
            if spec.kind == "tool" and not spec.available:
                self.assertTrue(spec.description, f"Unavailable route {key} must explain its scaffold state")

    def test_sidebar_routes_are_all_registered(self) -> None:
        sidebar = DEFAULT_ROUTE_REGISTRY.sidebar_routes()
        self.assertIn("new_chat", [route.key for route in sidebar])
        self.assertIn("theme", [route.key for route in sidebar])
        for route in sidebar:
            self.assertIs(DEFAULT_ROUTE_REGISTRY.get(route.key), route)

    def test_registry_rejects_duplicate_routes(self) -> None:
        route = RouteSpec("duplicate", "Duplicate", "tool")
        with self.assertRaises(ValueError):
            RouteRegistry((route, route))

    def test_shell_state_tracks_active_and_last_tool_routes(self) -> None:
        state = ShellState()
        state.activate("new_chat", is_tool=False)
        state.activate("email", is_tool=True)
        state.activate("theme", is_tool=True)
        self.assertEqual(state.active_route, "theme")
        self.assertEqual(state.last_tool_route, "theme")
        self.assertEqual(state.route_history[-3:], ["new_chat", "email", "theme"])


if __name__ == "__main__":
    unittest.main()
