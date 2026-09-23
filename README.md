# Otter Cove

A GUI-first PySide6 desktop application for Fedora 44. Development currently
focuses on reliable local behavior; model configuration and execution are deferred.

## Start here

Read [STATUS](STATUS.md) for the current state and next action, then
[PLAN](PLAN.md) for the single replacement implementation and acceptance plan.
It combines the earlier 55-feature plan, non-model work plans and 24 improvement
tasks. [ROADMAP](ROADMAP.md) is a short sequence summary.

**Next work:** establish the OC-00 implementation baseline, then OC-01–04's
data-protection fixes before landing the R2 data-management UI in PR #6.
The detailed [review](docs/reviews/2026-09-23-current-implementation.md) records
the reproduced issues. The replacement plan itself changes no application code.

## What is implemented

- Application shell and explicit available/unavailable routes.
- Floating tools that preserve the mounted chat/draft, with geometry recovery,
  minimize/restore, reopen and visual-only Peek.
- SQLite repositories/services and migrations; normal local message storage,
  memory-only Nobody sessions, isolated drafts and failed-send retry.
- Sixteen theme presets, customization/harmony, typography/density, named themes
  and animated-background controls.
- Appearance and shortcut settings, plus shared feedback and deterministic states.

Most other product workspaces are still scaffolds. Data tables are not completed
feature modules. Local-data protection, theme/input failure handling, startup,
packaging and native validation gaps remain in PLAN; passing tests do not close
those findings. In particular, the structured-credential and atomic-export
contracts need the targeted OC fixes before being treated as fully safe.

## Clone and run on Fedora

```bash
git clone https://github.com/BigBenKenobi/Otter-Cove.git
cd Otter-Cove
sudo dnf install python3-pyside6
python3 main.py
```

Run from the repository root. Source launch is the current documented path;
OC-22 repairs the incomplete wheel and adds an installed desktop launcher.

For a disposable profile:

```bash
DEMO_DIR="$(mktemp -d)"
OTTER_COVE_DATA_DIR="$DEMO_DIR/data" \
OTTER_COVE_SETTINGS_PATH="$DEMO_DIR/settings.ini" python3 main.py
```

Normal content lives at `$XDG_DATA_HOME/otter-cove/otter-cove.sqlite3`, or
`~/.local/share/otter-cove/otter-cove.sqlite3` when XDG_DATA_HOME is unset.
QSettings stores preferences/geometry separately. Nobody records are process-local.

## Code and documentation map

| Path | Responsibility |
|---|---|
| `main.py` | Qt bootstrap and startup recovery presentation |
| `app.py` | Composition, shared service ownership and routing |
| `core/` | Routes/commands, state, preferences and semantic themes |
| `core/data/` | SQLite migrations, records, repositories, validation and local services |
| `ui/` | Chat, sidebar, settings/theme panels, floating tools and shared feedback |
| `effects/` | Background effects and timing/lifecycle manager |
| `services/` | Reserved external-adapter boundary |
| `assets/` | Runtime assets; currently only a placeholder |
| `tests/`, `scripts/` | Regression suite and desktop smoke/check commands |
| `docs/acceptance/`, `docs/reviews/` | Dated evidence and findings |
| `docs/planning/` | Compatibility pointers to PLAN; no parallel active plans |

Follow [AGENTS](AGENTS.md), [ARCHITECTURE](docs/ARCHITECTURE.md) and
[DECISIONS](docs/DECISIONS.md) when implementing a task. Original visual references
are intended for `docs/reference/`, but are absent from the reviewed checkout.
OC-00 tracks locating them; reference-parity acceptance remains pending.

## Verification

```bash
PYTHONDONTWRITEBYTECODE=1 QT_QPA_PLATFORM=offscreen PYTHONPATH=. python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 QT_QPA_PLATFORM=offscreen PYTHONPATH=. python3 scripts/fedora_gui_smoke.py --offscreen
```

The 23 September review passed 73 tests on main and 74 on the separate PR #6
revision, without skips, using Ubuntu/Python 3.12.14/PySide6 6.11.2 offscreen.
PR #6's offscreen smoke also passed. These are source-specific automated results,
not native Fedora acceptance. See [TESTING](docs/TESTING.md) and the
[acceptance ledger](docs/ACCEPTANCE.md).

For native Fedora checks, run `./scripts/fedora_phase_a_check.sh` in the intended
desktop session, verify the actual Qt platform, and execute the
[manual checklist](docs/FEDORA_CHECKLIST.md). The runner's current “native” output
label is not proof of the platform; OC-21 addresses that issue.

## Development state fixtures

An unfinished feature window can use a deterministic scenario:

```bash
OTTER_COVE_DEMO_SCENARIO=failure python3 main.py
```

Available scenarios: `success`, `empty`, `loading`, `failure`, `cancellation`.
Set `OTTER_COVE_SHOW_STATE_FIXTURES=1` to expose their selector. Fixtures do not
mean the scaffold's product workflow or any external operation is implemented.
