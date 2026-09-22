# Otter Cove — PySide6 GUI concept

GUI-first PySide6 desktop application concept for Otter Cove on Fedora 44. External model/network integrations remain behind service boundaries while the desktop GUI and local application behavior are developed.

## Returning to the project

Read README → [STATUS](STATUS.md) → [PLAN](PLAN.md) →
[ARCHITECTURE](docs/ARCHITECTURE.md) → the relevant record in
[ACCEPTANCE](docs/ACCEPTANCE.md). [DECISIONS](docs/DECISIONS.md) records settled
choices; [TESTING](docs/TESTING.md) gives commands and the validation matrix.
Reviews and archived plans are historical, not alternate instructions.

## Current build

Start with [STATUS.md](STATUS.md) for current progress and the next action.
[PLAN.md](PLAN.md) is the sole implementation/acceptance plan; [ROADMAP.md](ROADMAP.md) summarizes sequence.

Work follows the numbered acceptance plan. Phase A has completed target acceptance for **01 — Application shell** and **53 — Shared states and feedback**. A remote implementation batch now also advances **39, 32, 33, 47, 35, 36, 38, 34, 37 and 50** so their Fedora checks can be run together rather than one build at a time.

### Application shell

- `main.py` is startup/bootstrap only.
- `MainWindow` owns preferences, local data services, theme state, shell state, workspace and floating-window manager.
- `core/routes.py` is the canonical route registry used by the sidebar and shell dispatcher.
- `core/shell_state.py` owns current shell-route state independently of feature widgets.
- All registered routes resolve to a real component or an explicitly labelled unavailable scaffold.
- Floating tools overlay the chat workspace, so opening Theme/Email/etc. does not replace the current chat or composer draft.
- The composer retains its 720px reference width when space allows and contracts for the documented 1100px minimum shell width.
- Restored top-level geometry is recovered into the current screen's available bounds.

### Floating tool windows

- Opening an already-open tool focuses/raises the existing instance instead of creating a duplicate.
- Opening a minimized tool restores it in one action.
- Closing hides the tool while retaining its local widget state for reopen.
- Normal and minimized geometries persist separately; collapsing a tool cannot overwrite its full-size restore geometry.
- Drag/resize commits and host-resize recovery keep titlebars and resize grips reachable.
- Recovered geometry is persisted so display-size changes do not recreate invalid layouts on restart.


### Remote Phase A batch

- Theme customization now persists semantic overrides, exposes More Colors, supports deterministic harmony preview/apply, and fixes dark scroll-viewport styling.
- Named custom themes persist and import/export through versioned atomic JSON, including typography, density and background-effect settings.
- Font size and density are centralized; Frosted uses a documented translucent fallback rather than claiming compositor blur.
- Background effects now have an independent persisted color and separate user-pause / visibility / application-suspension state.
- Settings now has live **Appearance** and **Shortcuts** pages. Appearance controls composer width, welcome/Nobody visibility, decorative glyph mode, status summary, composer actions and sidebar entries without deleting session/draft state.
- Stable command IDs and persistent rebinding/conflict detection cover New Chat, Search, Theme, Settings, Nobody, Tools and TTS demo. Favourite/Delete IDs are present but intentionally disabled with reasons until session management arrives.
- Peek remains visual-only: tool body fades while its titlebar stays usable.
- `scripts/fedora_phase_a_check.sh` gathers target runtime context, runs the complete suite and prints one combined manual checklist.

### Local data architecture

- `QSettings` is reserved for preferences and geometry.
- Local content uses versioned SQLite (`core/data/`).
- Stable IDs and repositories exist for sessions/messages, models, documents, Brain items, notes, tasks and Gallery metadata.
- Widgets consume UI-facing services; `ChatSurface` talks to `SessionService` instead of SQL/repositories directly.
- Nobody/incognito sessions are memory-only and excluded from ordinary SQLite and JSON exports.
- Credential-like fields are rejected from ordinary local stores. There is deliberately no plaintext credential repository.
- Schema changes use atomic migrations and include a v1 migration fixture.
- JSON export is written atomically; reset/import use SQLite transactions and return explicit affected/excluded-data reports.
- Corrupt/unavailable stores report recovery options and are never silently deleted/replaced.

Default Fedora data location is `$XDG_DATA_HOME/otter-cove/otter-cove.sqlite3`, or `~/.local/share/otter-cove/otter-cove.sqlite3` when `XDG_DATA_HOME` is unset. For an isolated demo run, set `OTTER_COVE_DATA_DIR` to a temporary directory.

## Clone and start

Clone the public repository, then run all commands from its root. The following
uses Git's default checkout directory; a differently named clone works the same
way as long as commands are run from that repository root.

```bash
git clone https://github.com/BigBenKenobi/Otter-Cove.git
cd Otter-Cove
```

## Project structure

```text
Otter-Cove/                   default directory created by `git clone`
  README.md
  PLAN.md
  ROADMAP.md
  STATUS.md
  CHANGELOG.md
  pyproject.toml
  requirements.txt
  main.py
  app.py
  core/
    routes.py             canonical shell route registry
    shell_state.py        shell-owned routing state
    settings.py
    theme.py
    theme_logic.py
    appearance.py
    command_registry.py
    command_manager.py
    data/
      database.py
      migrations.py
      ids.py
      models.py
      policy.py
      repositories.py
      services.py
  ui/
    workspace.py          background + chat + floating tools
    background.py
    sidebar.py            generated from the route registry
    chat.py
    studio_window.py      persistent floating-tool lifecycle/geometry
    theme_panel.py
    settings_panel.py
    shared_states.py
    feedback.py
    placeholders.py       explicit unavailable-route state
  effects/
    ...
  services/
  assets/
  tests/
    fixtures/schema_v1.sql
    test_persistence.py
    test_routes.py
    test_shell_qt.py
    test_shared_states_qt.py
    test_studio_window_qt.py
    test_theme_logic.py
    test_theme_qt.py
    test_effects_qt.py
    test_peek_qt.py
    test_appearance_commands.py
    test_settings_commands_qt.py
  scripts/
    fedora_phase_a_check.sh
  docs/
    ARCHITECTURE.md
    ACCEPTANCE.md
    TESTING.md
    DECISIONS.md
    acceptance/
    reference/
      screenshots/
      videos/
    reviews/
```

Project governance and evidence are documented in [PLAN.md](PLAN.md), [STATUS.md](STATUS.md), [CHANGELOG.md](CHANGELOG.md), and the [`docs/`](docs/) tree. All acceptance records now live under [`docs/acceptance/`](docs/acceptance/); original visual references live once under [`docs/reference/`](docs/reference/).

## Fedora 44

```bash
sudo dnf install python3-pyside6
# Run from the repository root after cloning (for example, `Otter-Cove/`).
python3 main.py
```

For an isolated acceptance run:

```bash
DEMO_DIR="$(mktemp -d)"
OTTER_COVE_DATA_DIR="$DEMO_DIR/data" \
OTTER_COVE_SETTINGS_PATH="$DEMO_DIR/settings.ini" python3 main.py
```

## Tests

```bash
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

The latest recorded GUI review passed **65/65 tests without skips** with PySide6
on Fedora using the offscreen platform, plus the offscreen GUI smoke check.
This does not replace native desktop/manual acceptance. See [STATUS.md](STATUS.md)
for the evidence boundary and current gaps. For native verification, run:

```bash
./scripts/fedora_phase_a_check.sh
```

The script runs the same suite and prints the deferred native/manual checklist.

## Shared state fixtures (Step 53)

For development/acceptance, an unfinished feature window can be forced into a deterministic shared state:

```bash
OTTER_COVE_DEMO_SCENARIO=failure python3 main.py
```

Valid values are `success`, `empty`, `loading`, `failure`, and `cancellation`. To expose an interactive fixture selector inside unfinished feature windows, set `OTTER_COVE_SHOW_STATE_FIXTURES=1`.
