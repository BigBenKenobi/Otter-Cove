# Current implementation review — 23 September 2026

Status: planning evidence, not release acceptance

Implementation plan: [24 improvement tasks](../planning/current-implementation-improvement-plan.md)

## Sources and method

| Source | Revision |
|---|---|
| `main` | `6aa802219f4130ac4732039bda01b0a870934cfe` |
| [PR #6: local data recovery](https://github.com/BigBenKenobi/Otter-Cove/pull/6) | `a560b5d7c7d88fc6d941e0d5da8542c9ac7d64c3` |
| [PR #8: first three non-model plans](https://github.com/BigBenKenobi/Otter-Cove/pull/8) | `531aaa38fe61fac867f8238744c5c6fce08aca18` |

Read repository guidance, README/STATUS/ROADMAP, canonical PLAN, architecture and
decision records, testing/evidence documentation, the #8 inventory and plans,
application/bootstrap code, chat, settings, themes, sidebar, commands, floating
tools, feedback/states, effect management and local-data implementation/tests.
Reviewed #6's changes against `main` rather than assuming its behavior was merged.

Environment: Ubuntu 24.04.3 LTS container, Linux 6.18.44 x86_64, Python 3.12.14,
PySide6 and Qt 6.11.2, `QT_QPA_PLATFORM=offscreen`. Dependencies were installed in
a temporary review directory; data, preferences, build output and probes used
disposable paths. No application implementation was changed for this review.

## Checks executed

| Check | Source | Result |
|---|---|---|
| Full `unittest` discovery | `main` | 73 tests, no skips, PASS |
| Full `unittest` discovery | PR #6 | 74 tests, no skips, PASS |
| `scripts/fedora_gui_smoke.py --offscreen` | PR #6 | PASS; supplementary offscreen only |
| Import/credential/theme probes below | Both | Reproduced the listed validation gaps |
| UI reset with a live private message and draft | PR #6 | Excluded private state was discarded |
| Export-to-active-database probe | `main` | Database path replaced with JSON |
| Invalid saved effect setting | `main` | `inf` quality raised `OverflowError` during construction |
| Restore a saved zero-message session | `main` | Empty hero incorrectly hidden |
| Build wheel and import outside checkout | `main` | Build succeeded; runtime import failed: missing `core` |

Commands, with PySide6 available in the selected Python environment:

```bash
PYTHONDONTWRITEBYTECODE=1 QT_QPA_PLATFORM=offscreen PYTHONPATH=. python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 QT_QPA_PLATFORM=offscreen PYTHONPATH=. python3 scripts/fedora_gui_smoke.py --offscreen
python3 -m pip wheel --no-deps --no-build-isolation --wheel-dir /tmp/otter-review-wheel .
```

The smoke prints `Phase A native GUI smoke: PASS` even with `--offscreen`. Its
actual platform in this run was offscreen; correcting that misleading label is
OC-21. No native desktop, screenshot parity or performance target was accepted.

## Reproduced findings

### F01 — Export can overwrite the active SQLite file

**Confirmed on:** `main`; the same destination behavior remains in #6.

**Location:** `core/data/services.py`, `LocalDataService.export_json`.

**Plan:** OC-01, P0.

Using a disposable store, `data.local_data.export_json(data.store.path)` succeeds.
The database path's bytes then start with `{`, not the SQLite header. The writer
checks no protected application path before `os.replace`. A JSON dialog filter is
not a service-level safeguard. The probe did not target personal data.

### F02 — Reset discards the private state its confirmation excludes

**Confirmed on:** PR #6.

**Location:** `app.py`, `_reset_local_data` and `_import_local_data`;
`ui/chat.py`, `reset_chat`.

**Plan:** OC-02, P0.

Created a Nobody message, retained its ID, typed an unsent private draft, and
confirmed reset through a patched modal answer. After reset:

```text
PR6 reset preserves excluded Nobody session: False
PR6 reset preserves excluded Nobody draft: False
```

The UI says Nobody sessions are outside reset, but then invokes New Chat's
private-disposal path. Import uses the same post-operation call by inspection;
the independent import UI case still needs its regression test.

### F03 — Replacement import accepts incomplete or invalid identity envelopes

**Confirmed on:** `main` and PR #6.

**Location:** `LocalDataService._validate_import`, row validation/import methods.

**Plan:** OC-03, P0.

Starting from a valid snapshot, each of these independent mutations was accepted:

- `schema_version=999`.
- `content={}`; absent tables become empty and replacement clears existing content.
- A null session ID, with the message collection cleared for that probe. Repository
  creation substitutes a new ID, violating stable identity restoration.

PR #6 improves required-key presence and nested JSON validation, but does not
fully validate types, complete table presence, supported schema or stable IDs.
The plan explicitly defines a complete-snapshot contract and older-version policy.

### F04 — Malformed values still escape the recovery boundary

**Confirmed on:** `main` and PR #6.

**Location:** `LocalDataService.import_json`, `SessionRepository.create`.

**Plan:** OC-03 and OC-05, P1 except destructive import contract under OC-03.

```text
Invalid UTF-8: UnicodeDecodeError
Session title array: AttributeError
```

The title-array case rolls back its transaction, but the exception type is not
caught by #6's Settings import handler. Invalid UTF-8 fails before row import and
also escapes that handler. The earlier malformed-nested-JSON bug has been fixed
in #6 and must not be reported as still unfixed there.

### F05 — Credential-bearing endpoint reaches ordinary storage and export

**Confirmed on:** `main` and PR #6.

**Location:** `ModelService.create`, `ModelRepository.create`,
`core/data/policy.py`, `LocalDataService.snapshot`.

**Plan:** OC-04, P0.

An existing storage API accepts the synthetic endpoint:

```text
https://synthetic-user:synthetic-pass@example.invalid/?api_key=synthetic
```

The snapshot contains both the synthetic password and credential query. No network
request was made. This finding is about the existing ordinary-store contract;
it does not require resuming deferred model-configuration PR #7.

The policy recursively examines mapping keys but ignores strings, including URL
userinfo/query values and serialized JSON metadata. A repair should inspect
known structured fields without claiming arbitrary free-text secret detection.

### F06 — Theme import lets encoding errors escape

**Confirmed on:** `main` and PR #6.

**Location:** `core/theme_logic.py`, `load_theme_bundle`; `app.py`, `_import_theme`.

**Plan:** OC-08, P1.

A file containing byte `0xff` raises `UnicodeDecodeError`, while the GUI catches
`ThemeBundleError`. Expected malformed-file feedback is bypassed. The writer's
directory/cleanup issues and boolean coercion are additional source observations,
not injected-failure reproductions from this review.

### F07 — Infinite effect preference prevents startup

**Confirmed on:** `main`.

**Location:** `AppSettings.float`, `MainWindow.__init__`, effect settings/count.

**Plan:** OC-06, P1.

Set `appearance/effect/quality` to the string `inf` in a temporary INI and construct
the window. Construction raises `OverflowError` when calculating particle count.
A negative quality is clamped to 0.25, confirming that minimum-only handling is
insufficient. Upper bounds and finite-value checks must precede allocation.

### F08 — Restored empty session shows no empty hero

**Confirmed on:** `main`.

**Location:** `ui/chat.py`, `_restore_latest_session`.

**Plan:** OC-09, P1.

Created a normal session with no messages, constructed and showed the window, and
processed events. `chat.hero.isVisible()` returned false. Startup unconditionally
hides the hero, unlike the general render path's message-count logic. This state
can also arise when session creation succeeds but the first message write fails.

### F09 — Packaged application is missing its runtime packages

**Confirmed on:** wheel built from `main`.

**Location:** `pyproject.toml`, `[tool.setuptools]`.

**Plan:** OC-22, P2 before distribution.

The wheel contains only:

```text
app.py
main.py
otter_cove_pyside6-0.1.0.dist-info/METADATA
otter_cove_pyside6-0.1.0.dist-info/WHEEL
otter_cove_pyside6-0.1.0.dist-info/top_level.txt
otter_cove_pyside6-0.1.0.dist-info/RECORD
```

Importing `main` with the wheel and PySide6 on the Python path, from `/tmp` rather
than the checkout, fails with `ModuleNotFoundError: No module named 'core'`.
Running from the checkout conceals this distribution defect.

## Additional source observations and acceptance gaps

These are scoped tasks, not claims that every listed behavior has failed a test.

| Observation | Follow-up |
|---|---|
| Repository reads issue raw SQL while chat expects typed store errors; initial restore can emit before shell wiring | OC-05: targeted failure/initialization tests |
| Full-file import/export and lock waiting execute synchronously from GUI handlers | OC-07: measure first, then bound/move slow operations |
| Composer/editor use fixed small heights and hide the editor scrollbar; old Odysseus placeholder remains | OC-11: long-draft and branding correction |
| Message labels use default AutoText with user content and mouse-only selection | OC-12: explicit literal-text and copy/keyboard contract; no script-execution claim |
| Nobody control is inside the hidden-after-send hero; header still carries the private label | OC-10: persistent control and explicit transitions |
| Shell accepts an injected route registry; sidebar uses the default registry | OC-14: align consumers |
| Feedback history/toast stack have no automatic bound; selecting an issue resolves it | OC-18: bound queues and separate details from resolution |
| Data close shuts SQLite but does not explicitly dispose all private service collections | OC-19: close/dispose lifecycle |
| Several older modules lack the newer AGENTS.md explanatory standard | OC-20: comply as files are materially modified |
| No CI workflow or runtime assets/desktop launcher tracked; `assets` has only a placeholder | OC-21/22: reproducible verification and install/launch work |
| `docs/reference/` is not tracked in the reviewed checkout | OC-00/23: locate supplied originals before parity acceptance |
| Current docs include old test counts, “no Git/HEAD” statements and resolved R1 defects as open | OC-00: reconcile current sections, preserve dated history |
| Native interaction, accessibility, scaling, dialogs and 60-second reference-machine animation evidence remain pending | OC-13–17/23: execute on the target desktop |

## Safe minimal reproduction for data findings

Run from the checked-out revision with its dependencies installed. This example
uses only a temporary database and synthetic data. It restores the baseline after
each import probe and closes the disposable connection.

```python
import copy
import json
import tempfile
from pathlib import Path
from core.data import AppDataServices

with tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary)
    data = AppDataServices.open(root / "probe.sqlite3")
    try:
        session = data.sessions.create_session("Keep me")
        data.sessions.add_message(session.id, "user", "Baseline message")
        baseline = data.local_data.snapshot()
        source = root / "input.json"
        restore = root / "restore.json"
        restore.write_text(json.dumps(baseline), encoding="utf-8")

        cases = {
            "future schema": lambda p: p.update(schema_version=999),
            "missing tables": lambda p: p.update(content={}),
            "title array": lambda p: p["content"]["sessions"][0].update(title=[]),
            "null ID": lambda p: (
                p["content"]["sessions"][0].update(id=None),
                p["content"].update(messages=[]),
            ),
        }
        for name, mutate in cases.items():
            payload = copy.deepcopy(baseline)
            mutate(payload)
            source.write_text(json.dumps(payload), encoding="utf-8")
            try:
                data.local_data.import_json(source)
                print(name, "ACCEPTED")
            except Exception as error:
                print(name, type(error).__name__)
            data.local_data.import_json(restore)

        source.write_bytes(b"\xff")
        try:
            data.local_data.import_json(source)
        except Exception as error:
            print("invalid UTF-8", type(error).__name__)

        data.models.create(
            "Probe", "local",
            endpoint="https://synthetic-user:synthetic-pass@example.invalid/?api_key=synthetic",
        )
        print("credential URL exported", "synthetic-pass" in json.dumps(data.local_data.snapshot()))

        # Intentionally tests destructive destination validation on this disposable
        # database only. Never substitute an existing personal store here.
        data.local_data.export_json(data.store.path)
        print("database replaced with JSON", data.store.path.read_bytes().startswith(b"{"))
    finally:
        data.close()
```

## Conclusion

The architecture and current tests provide a useful base. Passing suites do not
cover the reproduced boundary cases above. Resolve OC-01–04 before landing R2's
destructive data controls; then fix startup/error handling and current chat/theme
usability, establish reproducible packaging/CI, and complete native acceptance.

This was a repository/code review with targeted executable probes. It was not a
full security audit, a live Fedora UX review, or verification of unimplemented
product workspaces. The 24-task plan records those limits and reuses the existing
non-model plans for later feature development.
