# The word of God

Pilot 1 · Protect current data · OC-00–OC-04 · Designed for Terra (Medium)

These are execution guides for [PLAN](../../../PLAN.md), not a replacement for
it. The name is the owner's chosen title; it creates no instruction precedence.
User instructions, applicable AGENTS rules and the canonical plan still govern.
Version 1 was prepared on 23 September 2026. **Implementation has not started.**

## End goal

Produce a review-ready implementation branch containing the existing R2 controls
and the OC-01–04 corrections, with reproducible regression evidence. Preserve
current architecture, private state and valid local data. Stop after the pilot
handoff. Do not merge, release, start OC-05 or build model features.

Start with [START-HERE](START-HERE.md), then follow the
[operating guide](OPERATING-GUIDE.md). Each task's final packet is its gate.
The larger import and credential tasks have two implementation packets each.

| Order | Packet | Required result before advancing |
|---|---|---|
| 1 | [00-A: Baseline](00-A-baseline.md) | Reviewed R2 candidate on isolated branch; fresh baseline |
| 2 | [00-G: Baseline gate](00-G-baseline-gate.md) | Base, defects and acceptance limits evidenced |
| 3 | [01-A: Export targets](01-A-export-targets.md) | Local-data and theme exports protect active storage |
| 4 | [01-G: Export gate](01-G-export-gate.md) | Alias, sidecar and normal-export checks pass |
| 5 | [02-A: Replacement lifecycle](02-A-replacement-lifecycle.md) | Durable replacement preserves excluded private state |
| 6 | [02-G: Lifecycle gate](02-G-lifecycle-gate.md) | Import/reset, mode, draft and cancellation matrix passes |
| 7 | [03-A: Import contract](03-A-import-contract.md) | Typed, complete snapshots and shared field validation |
| 8 | [03-B: Preview and apply](03-B-preview-and-apply.md) | Confirmation applies exactly the previewed snapshot |
| 9 | [03-G: Import gate](03-G-import-gate.md) | Invalid data cannot replace storage; exact round trip |
| 10 | [04-A: Structured policy](04-A-structured-policy.md) | Existing write paths reject structured credentials |
| 11 | [04-B: Export guard](04-B-export-guard.md) | Legacy unsafe structured records cannot be exported |
| 12 | [04-G: Credential gate](04-G-credential-gate.md) | Negative and legitimate-value controls pass |
| 13 | [FINAL: Pilot handoff](FINAL-pilot-handoff.md) | Combined evidence, honest status and hard stop |

Use [CHECKS](CHECKS.md) for runnable checks and copy
[RUN-RECORD-TEMPLATE](RUN-RECORD-TEMPLATE.md) for each task's evidence. The gates
are mandatory execution rules supported by actual tests, not an installed agent
scheduler or protected GitHub check. A coding model could disregard prose;
mechanical branch enforcement/CI belongs to OC-21 and is not claimed here.

## Source anchors

- Main at preparation: `1c5be2824838a9cc347af32960d94ac104ac027a`.
- Runtime baseline: `6aa802219f4130ac4732039bda01b0a870934cfe`.
- Open [PR #6](https://github.com/BigBenKenobi/Otter-Cove/pull/6):
  `a560b5d7c7d88fc6d941e0d5da8542c9ac7d64c3`.
- [Dated review](../../reviews/2026-09-23-current-implementation.md) supplies
  observations, not fresh acceptance. Recheck source before implementation.

## How we will evaluate this pilot

The handoff must report packets completed without intervention, clarification
requests, gate failures and repairs, unexpected scope changes, and any instructions
that were ambiguous. Record approximate time/context restarts when available;
do not invent telemetry. We will use that evidence before writing later sections.
