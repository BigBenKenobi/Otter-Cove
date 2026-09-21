# Automated baseline — 21 September 2026

State: **Automated pass for the existing suite and smoke assertions only.**
This is not acceptance of every condition in PLAN.md or native desktop validation.

- Fedora 44 KDE edition; Python 3.14.7; PySide6/Qt 6.11.2.
- Platform forced to `offscreen`; normal application state untouched.
- `PYTHONDONTWRITEBYTECODE=1 QT_QPA_PLATFORM=offscreen PYTHONPATH=. python3 -m unittest discover -s tests -v`: **65/65 passed, zero skips**, 0.612 seconds.
- `PYTHONDONTWRITEBYTECODE=1 QT_QPA_PLATFORM=offscreen PYTHONPATH=. python3 scripts/fedora_gui_smoke.py --offscreen`: **PASS**. Its printed “native” label does not describe this invocation.
- Git commit/tag unavailable: `git rev-parse` reports no repository. This is a passing automated source snapshot, not a fully accepted release.

Evidence: [test output](evidence/2026-09-21-offscreen/unittest.log),
[smoke output](evidence/2026-09-21-offscreen/smoke.log),
[source SHA-256 manifest](evidence/2026-09-21-offscreen/source-manifest.json).
The manifest covers Python, shell, SQL and TOML files. Known GUI-review defects
remain open; see PLAN.md and STATUS.md. No application code changed in this pass.
