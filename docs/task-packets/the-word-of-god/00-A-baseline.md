# 00-A — Establish the implementation baseline

**Authority:** [OC-00](../../../PLAN.md#oc-00). **Prerequisite:** operating guide read.
**Outcome:** an isolated, reproducible R2 candidate with current documentation.

Read AGENTS, STATUS, docs/ACCEPTANCE.md, docs/TESTING.md and the dated review linked
from the README. Inspect git status, main and PR #6 live state before changing code.
The preparation SHAs in README are anchors, not permission to overwrite newer work.

1. Create a new `terra/word-of-god-pilot-<date>` branch/worktree from current main.
   Bring these task-packet documents into that worktree if still only on the docs
   branch. Preserve the authoritative PLAN and unrelated user work.
2. Fetch/review PR #6. If unchanged, its baseline-relative changes comprise seven
   runtime/test/script files: `app.py`, `core/data/services.py`,
   `scripts/fedora_phase_a_check.sh`, `scripts/measure_background.py`,
   `tests/test_settings_commands_qt.py`, `ui/background.py`, `ui/settings_panel.py`.
   It also changes five existing documentation files. Inspect the actual diff;
   do not assume this list remains current.
3. Incorporate the reviewed R2 runtime changes into the implementation branch.
   A scoped patch from runtime baseline `6aa8022` to the pinned PR head is suitable
   if main still has that runtime. Apply with context checking; do not restore
   whole old files over newer changes. Alternatively perform a normal local merge
   and resolve conflicts deliberately. Keep the consolidated PLAN and current
   packet guides; reconcile useful R2 evidence without reverting documentation.
   Preserve the malformed nested-JSON recovery regression. Record source SHAs,
   included/excluded paths and why. Carry existing instrumentation unchanged.
4. If main or PR #6 advanced, review the new delta first. Already-fixed criteria
   still need evidence; do not reintroduce old code. If PR #6 was merged, use main
   and verify its functionality. If inaccessible and the exact candidate is not
   locally verifiable, stop with a source blocker.
5. Commit this integration separately. Run CHECKS with isolated profiles against
   the chosen combined baseline. Diagnose any newly failing existing test before
   advancing. Known OC-01–04 defects are the work queue, not a demand to fix them
   inside OC-00. Preserve the baseline test log before introducing regressions.
6. Locate original reference media in accessible project sources; record actual
   paths or absence. Do not replace missing originals with invented mockups. Update
   STATUS/ledger with baseline evidence and native/reference limits.

**Development check:** R2 controls exist, its nested-JSON regression passes, full
suite and offscreen smoke run without skips. Record the still-open four findings.
**Next:** 00-G. Do not land R2 or start fixes before that gate.
