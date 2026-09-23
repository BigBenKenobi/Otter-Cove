# Common verification and gate

Run from the implementation checkout root in Bash. Read docs/TESTING.md as well.
Use the Python interpreter with the project's existing dependencies installed.
Do not copy the preparation environment's temporary dependency path as a requirement.
Tests added by this pilot must also create their own disposable databases/settings.

## Isolated environment

Run this once per shell; retain its printed location for logs. A resumed shell
must create a fresh disposable profile, not fall back to your normal one.

```bash
export OTTER_PILOT_TMP="$(mktemp -d -t otter-word-of-god-XXXXXX)"
export OTTER_COVE_DATA_DIR="$OTTER_PILOT_TMP/data"
export OTTER_COVE_SETTINGS_PATH="$OTTER_PILOT_TMP/settings.ini"
export QT_QPA_PLATFORM=offscreen
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=.
printf '%s\n' "$OTTER_PILOT_TMP"
python3 -c 'import sys, platform, PySide6; from PySide6.QtCore import qVersion; from PySide6.QtWidgets import QApplication; a=QApplication([]); print(sys.version); print(platform.platform()); print("PySide6", PySide6.__version__, "Qt", qVersion(), "platform", a.platformName())'
git rev-parse HEAD
git status --short
```

If setup/import fails, fix the environment or mark BLOCKED. Do not count Qt-skipped
runs as coverage. Before full validation, commit the implementation locally and
ensure no uncommitted runtime/config changes remain. Evidence documents may still
be in progress. Log the source SHA and setup output in the task record.

## Focused development

For the touched test file, substitute its actual filename:

```bash
python3 -m unittest discover -s tests -p 'test_persistence.py' -v
```

Read the result and record it, including failures during regression development.
For each packet, choose the relevant existing/new files; a filename is not itself
a test requirement. Existing suites include persistence, settings commands,
shell, appearance commands and theme logic. Never delete or skip a failing test
just to satisfy a gate.

## Full suite: nonzero exit on any skip or unexpected success

Run this exact block for every G packet and FINAL. The program exits unsuccessfully
if discovery is empty, any test fails, or any test is skipped/expected-failing.
That is a local test gate, not CI enforcement of packet progression.

```bash
python3 - <<'PYTEST' > "$OTTER_PILOT_TMP/full-suite.log" 2>&1
import sys
import unittest
suite = unittest.defaultTestLoader.discover('tests')
result = unittest.TextTestRunner(verbosity=2).run(suite)
print('PILOT COUNTS', result.testsRun, 'skips', len(result.skipped),
      'expected failures', len(result.expectedFailures))
sys.exit(0 if result.testsRun > 0 and result.wasSuccessful()
         and not result.skipped and not result.expectedFailures else 1)
PYTEST
OTTER_SUITE_RC=$?
cat "$OTTER_PILOT_TMP/full-suite.log"
printf 'Full suite exit: %s\n' "$OTTER_SUITE_RC"
test "$OTTER_SUITE_RC" -eq 0
```

A later successful shell command cannot override the recorded test exit. Retain
this run's log before another task overwrites it. The historical 73/74 counts are
observations, not a fixed target; explain removed coverage and require new defect
regressions. An unchanged old suite passing does not prove the new criteria.

```bash
python3 scripts/fedora_gui_smoke.py --offscreen > "$OTTER_PILOT_TMP/smoke.log" 2>&1
OTTER_SMOKE_RC=$?
cat "$OTTER_PILOT_TMP/smoke.log"
printf 'Smoke exit: %s\n' "$OTTER_SMOKE_RC"
git diff --check
OTTER_DIFF_RC=$?
test "$OTTER_SMOKE_RC" -eq 0 && test "$OTTER_DIFF_RC" -eq 0
```

The smoke's current “native” wording is inaccurate for this command. Record
**offscreen**. Preserve both exit statuses and copy logs to the run's task evidence
folder. A failed suite or smoke means BLOCKED, even if the other command succeeds.

## Required common gate checklist

- [ ] Every task-specific criterion links to a named test or inspection result.
- [ ] Final full suite and smoke exit 0; zero skips/expected failures; counts recorded.
- [ ] Regression evidence shows the original defect and corrected behavior.
- [ ] Disposable fixtures used; database/preferences preservation checked where relevant.
- [ ] Changes comply with AGENTS, architecture and packet scope; diff reviewed.
- [ ] Tested code SHA, environment, commands, logs and remaining limits recorded.
- [ ] No subsequent runtime/config change invalidates these results.
- [ ] STATUS/ledger distinguish pilot implementation from native/full acceptance.

OC-00 has no new fix to demonstrate: its regression-evidence item means recording
known defects and existing candidate regression coverage, not fixing OC-01–04 early.
