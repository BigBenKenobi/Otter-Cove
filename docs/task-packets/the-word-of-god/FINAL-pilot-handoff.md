# FINAL — Pilot handoff and stop

**Requires:** every task gate 00-G through 04-G PASSED. This is the final packet of
Pilot 1, not authorization to start the next section of PLAN.

1. Review the complete diff against the selected base. Confirm R2 integration is
   explained, OC-01–04 requirements are covered, AGENTS documentation is complete,
   no personal fixtures/secrets are committed, and no unrelated feature work slipped
   in. Preserve the original 55-feature catalogue and existing acceptance history.
2. Commit final implementation edits, then run CHECKS again on the combined source.
   Review every task's specific regression coverage, especially OC-04 changes to
   import behavior. Earlier passes do not excuse a final combined failure.
3. Update STATUS and the acceptance ledger with exact code SHA and evidence links.
   Distinguish implemented pilot behavior from native acceptance. Do not mark all
   of feature 54, Foundation, or R2 native acceptance complete. Reference parity,
   Fedora interaction/scaling and performance remain separate PLAN requirements.
4. Where native Fedora is available, perform the selected local-data interaction
   checks using a disposable profile: export rejection/normal save, validated
   preview/cancel/import, reset with private state and draft confirmation, readable
   error dialogs and focus recovery. Record actual platform/display/scale and
   source. This scoped check does not substitute for the entire native matrix.
   Otherwise record exactly which native checks remain pending and why.
5. Create a final handoff record with task/gate table, code and evidence commits,
   tests/counts/skips, residual risks, native/reviewer pending items, and proposed
   PR title/body. Keep the implementation local until the owner asks to publish;
   do not merge/change PR #6, tag or release. Explain how a later PR would contain
   the R2 candidate plus fixes so reviewers do not land the old uncorrected PR.
6. Add the pilot evaluation: autonomous completions, intervention requests, failed
   gates repaired, scope surprises, context resets and ambiguous packet wording.
   Provide factual observations useful for revising the next packet section.

**Final outcome:** if every automated/inspection gate passes but native/reference
or reviewer acceptance remains, report **IMPLEMENTATION COMPLETE — ACCEPTANCE
PENDING** and list the remaining evidence. If a required code gate fails, report
**BLOCKED**. Report **PASSED** only for the explicitly evidenced pilot scope;
never imply full application acceptance.

**STOP HERE. Do not start OC-05 or any later task.** Hand control back to the owner
with the branch, commits, evidence paths and pilot evaluation.
