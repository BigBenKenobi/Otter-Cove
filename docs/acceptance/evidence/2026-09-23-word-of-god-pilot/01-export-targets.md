# Pilot run record — OC-01

- Run/date/operator/model/reasoning: 23 September 2026 / Codex / GPT-5 / inherited
- Implementation branch/worktree: `terra/word-of-god-pilot-2026-09-23`
- Main SHA / R2 candidate SHA / integration commit: `ada8b99` / `a560b5d` / `fb41db8`
- Tested implementation commit: `92b83ef134a9f8753c89890a141434ce58fd45cf`
- Disposable profile location: fresh `mktemp -d -t otter-word-of-god-XXXXXX` profiles only
- Packets completed / current packet / next action: 01-A and 01-G / 02-A / read OC-02 packet and PLAN task
- Gate result: PASSED

## Decisions and scope

Added the Qt-independent `core.protected_paths` guard. It resolves lexical and symlink-parent aliases, compares existing identities for hard links, and rejects before either writer creates directories or temporary files. `LocalDataService` always protects its database and absent WAL/SHM names; the shell supplies the owned QSettings path for local-data exports and all four active paths for theme exports. Rejections become `DataValidationError` or `ThemeBundleError`, which existing UI feedback handlers display.

## Criteria and evidence

| Criterion ID | Test name or inspection | Command and exit | Log/artifact | Result |
|---|---|---|---|---|
| 01.1–01.3 | `test_export_rejects_active_store_aliases_and_sidecars_before_mutation`; `test_export_rejects_protected_target_before_creating_parent` | focused unittest; exit 0 | [focused.log](01/focused.log) | PASS |
| 01.2 | Symlink, symlinked parent, and `os.link` hard-link probes in persistence test | focused unittest; exit 0 | [focused.log](01/focused.log) | PASS |
| 01.4 | Existing atomic export/theme round-trip and no-overwrite regressions | full suite; exit 0 | [full-suite-gate.log](01/full-suite-gate.log) | PASS |
| 01.5 | `test_local_data_gui_exports_reports_errors_and_confirms_reset` | focused Qt unittest; exit 0 | [full-suite-gate.log](01/full-suite-gate.log) | PASS |
| Common gate | 76 tests / zero skips / zero expected failures; offscreen smoke | CHECKS blocks; exit 0 / 0 | [full-suite-gate.log](01/full-suite-gate.log), [smoke-gate.log](01/smoke-gate.log) | PASS |

- Before-fix reproduction and observed failure: the reviewed `fb41db8` implementation called `export_json(data.store.path)` without validation; the documented OC-01 probe replaced a disposable SQLite database with JSON. Theme export also created its parent before any policy check.
- After-fix focused check: protected direct, sidecar, symlink, symlink-parent, hard-link, and settings targets raise typed errors while the disposable database and settings bytes remain readable.
- Full-suite tests / failures / errors / skips / expected failures / exit: 76 / 0 / 0 / 0 / 0 / 0.
- Offscreen smoke result and exit: pass / 0; this is not native acceptance.
- Documentation/scope review: only the known active storage target boundary and regressions changed; no general sandbox or TOCTOU redesign.
- Source changes after testing: only evidence documentation follows the tested executable commit.

## Acceptance limits and blockers

Native/reference/reviewer acceptance remains pending and non-blocking for this pilot. No automated gate blocker remains.

## Handoff / resume

- Next packet and prerequisite evidence: `02-A`, unlocked by this passing gate.
- Exact next command or inspection: read `02-A-replacement-lifecycle.md` and OC-02 in `PLAN.md`.
- Uncommitted changes and purpose: OC-01 evidence files/index/status updates only.
- Clarification requests / failed repair attempts / context restarts: none / none / none.
