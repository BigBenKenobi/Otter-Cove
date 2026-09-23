# Operating guide

Read this once at the start and again after a context reset. Read only the current
packet, its linked PLAN task, and relevant source/tests while working; the whole
feature catalogue need not be loaded into every context window.

## Execution rules

1. Follow the README sequence serially. The canonical plan allows some parallel
   dependencies, but this pilot deliberately uses one predictable sequence.
2. Use a dedicated implementation branch/worktree. Preserve user changes. Never
   force-push, reset somebody else's work, merge PR #6, or edit the packet criteria
   to make implementation pass. Incorporating R2 code into the private work branch
   is preparation, not permission to land it on main.
3. For each behavioral fix, add a focused regression and demonstrate its failure
   against the preceding implementation, then demonstrate the corrected behavior.
   An equivalent reproducible before/after probe is acceptable when practical;
   record exactly what ran. Never deliberately run destructive probes on real data.
4. Prefer the smallest coherent change. Qt stays in presentation/composition;
   core validation and repositories must remain usable without Qt. Keep normal
   atomic exports, SQLite transactions and the existing service boundaries.
5. Apply AGENTS documentation requirements to every materially changed code file,
   class, significant method and lifecycle boundary. Run checks after final code
   and comment edits. Tests must assert behavior, including preservation on failure.
6. Update task evidence and the run index after each packet. Implementation packets
   can advance within their task after their stated checks; only its G packet can
   unlock the following task. No independent-task bypass is permitted in this pilot.

## Permitted decisions and stop conditions

Choose helper names, module placement, test organization and small refactors needed
for a packet. Record decisions affecting persisted data or user-visible behavior.
Use synthetic fixtures. Do not add dependencies, a schema migration, background
job architecture, model configuration UI, providers, or unrelated cleanup unless
an existing canonical requirement makes it unavoidable; otherwise report the need
as a blocker for scope review. Existing project dependencies may be installed into
an isolated environment without changing project dependency declarations.

Repair in-scope test failures autonomously. If two attempted fixes fail in the same
way, stop making speculative edits: inspect the cause and record a revised diagnosis.
Continue if a concrete in-scope repair is evident; otherwise mark BLOCKED with the
smallest question or missing capability. Missing Qt, inaccessible required source,
contradictory requirements, or an unexplained baseline regression cannot be waived.

Missing reference originals and native Fedora access do not block this data-safety
pilot. Record them as pending acceptance. They still block any claim to native,
visual-parity or full feature acceptance. Do not fabricate replacements.

## State and gates

Create `docs/acceptance/evidence/<date>-word-of-god-pilot/` for synthetic logs and
records, using a suffix if a run already exists. Create an `index.md` containing
base/candidate/branch, packet statuses, links to task records, current packet,
next command, blockers and native acceptance status. Copy the supplied template
into one record per task. Keep draft secrets/personal data out of evidence.

| Gate result | Meaning and next action |
|---|---|
| PASSED | Every required automated/inspection criterion has evidence; next packet permitted |
| BLOCKED | A required criterion failed or cannot be checked; remain on this task |
| IMPLEMENTATION COMPLETE — ACCEPTANCE PENDING | FINAL only: code gates pass but native/reference/reviewer acceptance remains; stop and hand off |

An unchecked item, missing log, skipped required test or unsupported “looks right”
claim is not PASSED. Keep native pending items separate from required pilot gate
items so they cannot either disappear or deadlock unrelated data corrections.

Each G packet requires the common gate in CHECKS plus every task-specific item.
Record the implementation commit **before** running final tests. Logs may be
committed afterward in an evidence-only commit: identify the tested code commit,
and verify that no executable/configuration changes followed it. If they did,
rerun affected evidence. A change to shared validation in OC-04 must rerun earlier
import and UI regressions; FINAL reruns the complete suite on the combined code.

## Scope limits

Repair OC-00–04 only. Existing R2 instrumentation may be carried forward unchanged
as candidate code, but do not develop performance work. Do not implement OC-05–23,
SC/CU work, packaging, CI or a general secret scanner. Do not mark feature 54 fully
accepted or erase historical/native caveats because this pilot passes. PLAN owns
requirements; STATUS and the acceptance ledger own current truthful state.
