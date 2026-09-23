# Pilot run record — OC-03

- Run/date/operator/model/reasoning: 23 September 2026 / Codex / GPT-5 / inherited
- Implementation branch/worktree: `terra/word-of-god-pilot-2026-09-23`
- Tested implementation commit: `91e56408755fecc01ef25d8294029b2b18d8d414`
- Disposable profile location: fresh `mktemp` data/settings profiles
- Packets completed / current packet / next action: 03-A, 03-B, 03-G / 04-A / read OC-04 packet and PLAN task
- Gate result: PASSED

## Decisions and scope

Imports now prepare validated JSON once into `PreparedImport`, including exact per-table counts. Applying reparses/revalidates those immutable bytes without reopening the source path, so confirmation cannot be raced by replacement/deletion of the file. The shell prepares before confirmation and displays all validated counts.

## Criteria and evidence

| Criterion ID | Test name or inspection | Command and exit | Log/artifact | Result |
|---|---|---|---|---|
| 03.1–03.4 | `test_import_contract_rejects_incomplete_future_and_broken_snapshots`; existing malformed nested JSON GUI regression | focused/full unittest; exit 0 | [full-suite-gate.log](03/full-suite-gate.log) | PASS |
| 03.5 | `test_atomic_export_reset_and_import_preserve_stable_ids` | full suite; exit 0 | [full-suite-gate.log](03/full-suite-gate.log) | PASS |
| 03.6 | `test_prepared_import_applies_validated_bytes_after_source_changes` | focused/full unittest; exit 0 | [full-suite-gate.log](03/full-suite-gate.log) | PASS |
| 03.7–03.8 | existing rollback and OC-01/02 tests | full suite; exit 0 | [full-suite-gate.log](03/full-suite-gate.log) | PASS |
| Common gate | 81 tests / zero skips / zero expected failures; offscreen smoke | CHECKS blocks; exit 0 / 0 | [full-suite-gate.log](03/full-suite-gate.log), [smoke-gate.log](03/smoke-gate.log) | PASS |

- Before-fix reproduction and observed failure: import validated only after the confirmation flow and reopened the selected path, allowing changed contents to differ from confirmed contents.
- After-fix focused check: replacing the source after `prepare_import` still restores the original confirmed stable ID.
- Full-suite tests / failures / errors / skips / expected failures / exit: 81 / 0 / 0 / 0 / 0 / 0.
- Offscreen smoke result and exit: pass / 0; not native acceptance.
- Source changes after testing: evidence documentation only.

## Acceptance limits and blockers

Native/reference/reviewer acceptance remains pending and non-blocking for Pilot gates.

## Handoff / resume

- Next packet and prerequisite evidence: `04-A`, unlocked by this record.
- Exact next command or inspection: read `04-A-structured-policy.md` and OC-04 PLAN task.
- Uncommitted changes and purpose: OC-03 evidence/index/status changes only.
