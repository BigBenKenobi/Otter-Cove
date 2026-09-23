# Pilot run record — OC-00

- Run/date/operator/model/reasoning: 23 September 2026 / Codex / GPT-5 / inherited
- Implementation branch/worktree: `terra/word-of-god-pilot-2026-09-23` in the repository checkout
- Main SHA / R2 candidate SHA / integration commit: `ada8b9992786006af57e34631096c3a195108a55` / `a560b5d7c7d88fc6d941e0d5da8542c9ac7d64c3` / `fb41db85e8108ea0606b329da7c83b0e8d7967b3`
- Tested implementation commit: `fb41db85e8108ea0606b329da7c83b0e8d7967b3`
- Evidence-only follow-up commit, if any: pending
- Python / PySide6 / Qt / OS / Qt platform: Python 3.14.7 / PySide6 6.11.2 / Qt 6.11.2 / Fedora 44 / offscreen
- Disposable profile location (no personal data): `/tmp/otter-word-of-god-SYerWQ` for environment capture; separate fresh `mktemp` profiles for gate suite and smoke
- Packets completed / current packet / next action: 00-A and 00-G / 01-A / inspect the OC-01 export boundary
- Gate result: PASSED

## Decisions and scope

Created the isolated branch from current `main` after a fresh `git fetch`. PR #6 had not advanced from its recorded head. Applied only its seven runtime/test/script paths from runtime baseline `6aa8022` to the candidate: `app.py`, `core/data/services.py`, `scripts/fedora_phase_a_check.sh`, `scripts/measure_background.py`, `tests/test_settings_commands_qt.py`, `ui/background.py`, and `ui/settings_panel.py`. Excluded PR #6's five documentation paths because current `main` contains the consolidated current plan and Pilot packet documentation. The scoped patch applied cleanly and was committed separately as `fb41db8`.

The reviewed R2 controls, including the malformed nested-JSON import regression in `test_local_data_gui_exports_reports_errors_and_confirms_reset`, are present. The open OC-01–04 findings remain intentionally unfixed: export accepts the active store path; R2 refresh disposes excluded Nobody state; import accepts incomplete/future/null-ID envelopes; and credential-bearing structured endpoint values reach ordinary storage/export.

`find` located no original image media in the checkout. Repository documentation and `.gitignore` identify `docs/reference/` as the intended location and record it as absent, so no replacement was invented.

## Criteria and evidence

| Criterion ID | Test name or inspection | Command and exit | Log/artifact | Result |
|---|---|---|---|---|
| 00.1–00.2 | Fresh remote/source and scoped-diff inspection | `git fetch origin --prune`; `git diff 6aa8022 a560b5d -- <seven paths>`; exit 0 | this record; integration commit `fb41db8` | PASS |
| 00.3 / common full suite | 74 discovered tests, no skips or expected failures | CHECKS full-suite block; exit 0 | [full-suite-gate.log](00/full-suite-gate.log) | PASS |
| 00.3 / common smoke | Disposable offscreen GUI smoke | `python3 scripts/fedora_gui_smoke.py --offscreen`; exit 0 | [smoke-gate.log](00/smoke-gate.log) | PASS (offscreen only) |
| 00.4 | Dated review and current source inspection | `sed`/`rg` review and R2 diff; exit 0 | this record; [review](../../../reviews/2026-09-23-current-implementation.md) | PASS |
| 00.5 | Reference-media availability inspection | `find . -type f` for raster/vector media; exit 0 | this record | PENDING, non-blocking |
| 00.6 | Run index and current status/ledger update | documentation inspection; exit 0 | [index.md](index.md), [STATUS](../../../../STATUS.md), [ledger](../../../ACCEPTANCE.md) | PASS |

- Before-fix reproduction and observed failure: OC-00 introduced no fix. The dated review records all four known open defects and R2's existing nested-JSON correction.
- After-fix focused check: not applicable to baseline reconciliation; the integrated R2 GUI regression passed in the full suite.
- Full-suite tests / failures / errors / skips / expected failures / exit: 74 / 0 / 0 / 0 / 0 / 0.
- Offscreen smoke result and exit: pass / 0. The script's printed “native” label is not a native acceptance claim.
- Documentation/scope review: seven runtime/test/script paths were integrated; five stale PR documentation paths were excluded. Current PLAN and task packets are preserved.
- Source changes after testing and which checks were rerun: evidence documentation follows the tested executable commit only; no runtime or configuration change followed the gate run.

## Acceptance limits and blockers

Native Fedora interaction, scaling, accessibility, dialog and animation acceptance remain pending; offscreen smoke cannot substitute for them. Original reference media is absent from the checkout (`docs/reference/` is ignored), so reference-parity acceptance remains pending. Neither item blocks the OC-01–04 data-safety pilot under the operating guide. Reviewer acceptance remains pending.

## Handoff / resume

- Next packet and prerequisite evidence: `01-A`; OC-00 passed with this record and the run index.
- Exact next command or inspection: `sed -n '1,260p' docs/task-packets/the-word-of-god/01-A-export-targets.md` followed by the OC-01 PLAN task.
- Uncommitted changes and purpose: evidence files plus status/ledger updates, to be committed as evidence-only work.
- Clarification requests / failed repair attempts / context restarts: none / none / none.
- Instruction ambiguities and suggested improvements for the next pilot version: the supplied full-suite block must be run verbatim to capture skip/expected-failure counts; initial ordinary discovery was retained as baseline context and then superseded by the required gate block.
