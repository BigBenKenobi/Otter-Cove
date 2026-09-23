# Testing

Run from the repository root with disposable SQLite/QSettings. The
[shared gate](../PLAN.md#shared-acceptance-gate) owns fixtures, targets and acceptance;
[ACCEPTANCE](ACCEPTANCE.md) indexes actual evidence.

## Automated commands

```bash
PYTHONDONTWRITEBYTECODE=1 QT_QPA_PLATFORM=offscreen PYTHONPATH=. python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 QT_QPA_PLATFORM=offscreen PYTHONPATH=. python3 scripts/fedora_gui_smoke.py --offscreen
```

Missing PySide6 may currently skip Qt tests. A run with skips does not satisfy the
full-suite gate. Tests themselves default Qt to offscreen, so launching them from
Wayland does not establish native pointer interaction. OC-21 adds enforced
coverage/platform reporting; do not claim those runner fixes already exist.

The smoke currently prints “native” even when run offscreen. Record the actual
platform and invocation rather than copying that label as an acceptance claim.

## Latest recorded source checks

| Source/environment | Recorded result | Limit |
|---|---|---|
| Main `6aa8022`; Ubuntu 24.04.3, Python 3.12.14, PySide6/Qt 6.11.2 | 73 tests, no skips, PASS on 23 September | Offscreen; additional probes found defects |
| PR #6 `a560b5d`; same environment | 74 tests, no skips, and offscreen smoke PASS | Separate implementation branch; not merged or native-accepted |
| Historical 21 September Fedora/KDE, Python 3.14.7, Qt 6.11.2 | 65 tests plus offscreen smoke PASS | Historical source manifest, not a new baseline |

See the [23 September review](reviews/2026-09-23-current-implementation.md) and
[historical evidence](acceptance/2026-09-21-offscreen.md). The documentation
replacement adds no runtime acceptance claim.

## Native Fedora run

```bash
./scripts/fedora_phase_a_check.sh
```

Use the intended KDE/GNOME Wayland session without inherited
`QT_QPA_PLATFORM=offscreen`. Record the actual Qt platform, desktop, display scale,
GPU/driver and source. The runner's current output/checklist is supplemental;
execute [FEDORA_CHECKLIST](FEDORA_CHECKLIST.md) and PLAN's selected native cells.
Printing a checklist is not passing it.

Native KDE/GNOME interaction, 100/150/200% scaling and animation performance remain
pending. The measurement helper in PR #6 becomes available only after that
corrected implementation lands; do not assume it exists on current main.

## Packaging and documentation checks

OC-22 requires building/installing away from the checkout so source-directory
imports cannot conceal missing packages. The reviewed wheel failed that check;
a successful build alone is insufficient. OC-21 adds the corresponding CI gate.

For documentation-only changes, verify local links/anchors, task/dependency
coverage, preservation of catalogue requirements and `git diff --check`. Inspect
the changed paths to confirm no runtime code changed. Do not rerun runtime suites
merely to relabel existing evidence with a documentation commit.

## Evidence and tagging

Record commands, full source SHA, environment/platform, skips and actual outcomes.
Store curated logs/captures in `docs/acceptance/evidence/<date>-<area>/`, with a
short linked acceptance record. Original references are intended for
`docs/reference/` but are absent from the reviewed checkout; OC-00 tracks recovery.

The repository is initialized and tracks GitHub. The old pre-Git source manifest
is historical context, not a description of today's checkout. Before an intended
milestone acceptance, record clean status and the tested commit:

```bash
git status --short
git rev-parse HEAD
```

Only tag an evidenced revision under the intended release direction. The tag's
name/message must match native versus offscreen scope; never move an existing
milestone tag. This plan consolidation does not create a release tag.
