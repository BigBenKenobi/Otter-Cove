# Testing

Run commands from the repository root. Tests use temporary storage; do not
point fixtures at a personal profile. See [ACCEPTANCE](ACCEPTANCE.md) for evidence.

## Automated commands

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m unittest discover -s tests -v
```

For an explicitly offscreen run and smoke check:

```bash
PYTHONDONTWRITEBYTECODE=1 QT_QPA_PLATFORM=offscreen PYTHONPATH=. python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 QT_QPA_PLATFORM=offscreen PYTHONPATH=. python3 scripts/fedora_gui_smoke.py --offscreen
```

Missing PySide6 may skip Qt tests; a run with skips does not establish full suite
coverage. The current tests themselves default Qt to offscreen. Running the suite
in a Wayland desktop therefore does not by itself test native pointer interaction.

## Fedora desktop run

```bash
./scripts/fedora_phase_a_check.sh
```

Run in the intended desktop session without an inherited `QT_QPA_PLATFORM=offscreen`.
The script records context, executes the suite and GUI smoke, and prints manual
checks. Printing that checklist does not pass it. Inspect actual Qt platform and
record each manual result. [FEDORA_CHECKLIST](FEDORA_CHECKLIST.md) describes the
functional pass; PLAN.md owns requirements and numerical targets.

| Environment | Automated evidence | Native/manual status |
|---|---|---|
| Fedora 44 KDE edition, Python 3.14.7, Qt/PySide6 6.11.2, offscreen | 65/65 plus smoke pass, 21 September | Not applicable to native acceptance |
| Fedora 44 KDE Wayland | Historical native-smoke report exists; no fresh native run in consolidation | Current pointer/dialog/Peek/shortcut/scaling checks pending |
| Fedora 44 GNOME Wayland | No recorded current run | Pending, or explicitly revise release support |
| 100%, 150%, 200% scaling | No current matrix evidence | Pending on supported desktops |

## Evidence and tagging

Record command, environment, Qt platform, skips, result and source commit/hash.
Store curated output/captures in `docs/acceptance/evidence/<run>/`; keep original
references in `docs/reference/`. [Current automated record](acceptance/2026-09-21-offscreen.md)
includes a source manifest because this workspace is not a Git repository.

Once Git is initialized with a committed baseline, run the intended milestone
checks against a clean checkout and record its SHA before tagging:

```bash
git status --short
git rev-parse HEAD
# After the intended checks pass and their evidence identifies this commit:
git tag -a phase-a-automated-pass -m "Phase A automated suite and native smoke verified; see acceptance evidence"
```

Do not use that message for an offscreen-only run. Use a separately named offscreen
tag if that is the scope verified. Never move an existing milestone tag to a new
commit. No commit or tag was created during this documentation consolidation.
