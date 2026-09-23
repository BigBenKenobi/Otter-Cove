# Pilot run record — OC-02

- Run/date/operator/model/reasoning: 23 September 2026 / Codex / GPT-5 / inherited
- Implementation branch/worktree: `terra/word-of-god-pilot-2026-09-23`
- Main SHA / R2 candidate SHA / integration commit: `ada8b99` / `a560b5d` / `fb41db8`
- Tested implementation commit: `af2ac00ceda0eb121892f1ecd32bc3ee60ffd419`
- Disposable profile location: fresh `mktemp` data/settings profiles
- Packets completed / current packet / next action: 02-A and 02-G / 03-A / read OC-03 packet and PLAN task
- Gate result: PASSED

## Decisions and scope

Durable replacement uses `ChatSurface.refresh_after_durable_replacement`, not New Chat. It preserves the whole Nobody aggregate and pending normal draft, discards drafts tied to replaced persistent IDs, and chooses the latest imported persistent session only when normal mode is active. A second confirmation explicitly warns when a concrete persistent draft will be discarded; cancellation changes nothing.

## Criteria and evidence

| Criterion ID | Test name or inspection | Command and exit | Log/artifact | Result |
|---|---|---|---|---|
| 02.1–02.3 | `test_reset_preserves_live_nobody_session_and_draft`; `test_import_preserves_private_view_and_drops_replaced_durable_draft` | Qt focused suite; exit 0 | [full-suite-gate.log](02/full-suite-gate.log) | PASS |
| 02.4–02.5 | `test_replacement_draft_confirmation_and_cancel_preserve_state` | Qt focused suite; exit 0 | [full-suite-gate.log](02/full-suite-gate.log) | PASS |
| 02.6 | Existing `test_new_chat_disposes_private_session_and_clears_pending_draft` | full suite; exit 0 | [full-suite-gate.log](02/full-suite-gate.log) | PASS |
| Common gate | 79 tests / zero skips / zero expected failures; offscreen smoke | CHECKS blocks; exit 0 / 0 | [full-suite-gate.log](02/full-suite-gate.log), [smoke-gate.log](02/smoke-gate.log) | PASS |

- Before-fix reproduction and observed failure: R2 called `reset_chat()` after successful replacement, disposing the excluded Nobody session and draft.
- After-fix focused check: real settings handlers retain private identity/message/draft/mode; switching to normal then selects imported durable content.
- Full-suite tests / failures / errors / skips / expected failures / exit: 79 / 0 / 0 / 0 / 0 / 0.
- Offscreen smoke result and exit: pass / 0; not native acceptance.
- Source changes after testing: evidence documentation only.

## Acceptance limits and blockers

Native/reference/reviewer acceptance remains pending and does not block Pilot data gates.

## Handoff / resume

- Next packet and prerequisite evidence: `03-A`, unlocked by this record.
- Exact next command or inspection: read `03-A-import-contract.md` and OC-03 PLAN task.
- Uncommitted changes and purpose: OC-02 evidence/index/status changes only.
