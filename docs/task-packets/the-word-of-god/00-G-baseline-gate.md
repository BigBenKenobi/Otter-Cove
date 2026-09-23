# 00-G — Baseline gate

**Authority:** [OC-00](../../../PLAN.md#oc-00). Requires 00-A and the common gate.

- [ ] 00.1: Main, PR state/head and selected integration commit are identified.
- [ ] 00.2: R2 runtime controls and its nested-JSON correction are present; current
  canonical documentation and unrelated work are preserved.
- [ ] 00.3: Fresh combined-baseline suite and offscreen smoke pass without skips.
  Historical 73/74-test results have not been relabelled as a new run.
- [ ] 00.4: OC-01–04 known defects are recorded, without treating baseline success
  as proof those defects are absent.
- [ ] 00.5: Original-reference availability and remaining native gates are explicit.
- [ ] 00.6: Run index, STATUS and acceptance ledger point to actual baseline evidence.

If a required item fails: BLOCKED, return to 00-A. Missing native/reference evidence
alone may be recorded pending. If all pass: record PASSED and continue to 01-A.
