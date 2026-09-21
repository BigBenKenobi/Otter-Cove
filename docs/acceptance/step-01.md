# Step 01 — Application shell acceptance record

Plan deliverable: **MainWindow, service/state ownership, route registry and layered workspace; `main.py` remains an entry point.**

Status: **Done for the current GUI milestone.**

## Implemented

- Declarative, Qt-independent route registry in `core/routes.py`.
- Sidebar navigation generated from the canonical route registry.
- Shell-owned route state in `core/shell_state.py`.
- `MainWindow` owns application services, preferences, theme state, workspace and child-window management; `main.py` remains bootstrap only.
- Registered routes resolve to their real component or an explicitly labelled unavailable scaffold; unknown routes are labelled unavailable rather than silently misrouted.
- Floating tools preserve the chat surface, session identity and composer draft.
- Responsive composer behavior covers the documented 1100×680 minimum and 1920×1080 reference size.
- Saved main-window geometry is clamped into the current display's available geometry after restore.

## Fedora acceptance evidence

On 2026-09-21 the user ran:

```bash
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

on the Fedora target with PySide6 installed. All **26/26** tests in that build passed, including all four `ShellQtAcceptanceTests`:

- `test_every_registered_route_resolves_to_command_or_window`
- `test_minimum_and_reference_sizes_keep_primary_controls_reachable`
- `test_opening_tool_preserves_session_and_composer_draft`
- `test_saved_preferences_restore_sidebar_and_geometry`

This satisfies the current Step 01 automated acceptance. Final GNOME/KDE multi-scale release validation remains separately governed by Step 55.
