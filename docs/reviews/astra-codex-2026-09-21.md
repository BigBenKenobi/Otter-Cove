# Astra Codex review — 21 September 2026

Historical review, incorporated into [PLAN.md](../../PLAN.md). Consult the current
plan/status for priorities; findings below describe the reviewed build, not future
fix status. Prior layout-normalization note is retained at the end.

Scope: source inspection, 65-test offscreen run, smoke check, rendered GUI and
isolated session/error probes. It did not establish native desktop acceptance.

## PROGRESS ASSESSMENT

Shared foundations are substantially implemented and automated regression is
green. Settings now has real Appearance and Shortcuts pages. Theme work now
includes persistent customization, expanded colors, harmony Apply/Reset, density,
typography, effect controls and named theme import/export. The dark Customize
viewport defect is resolved in the observed render. Floating-window lifecycle and
geometry have dedicated passing checks. Sidebar/composer line icons are present;
Settings/profile entry points remain reachable when collapsed.

Persistence now includes SQLite repositories/services, migrations and local JSON
operations. Chat writes normal messages and restores the latest stored session;
Nobody records are kept out of SQLite/export. This is meaningful implementation,
but not complete session management or incognito UX.

Most product workspaces remain unavailable scaffolds: Search, Email, Tools,
Brain, Calendar, Compare, Cookbook, Research, Gallery, Library, Notes, Tasks,
Account and Models. Data tables/services for several domains do not count as
finished GUI modules. Settings has no model/default/search/integration pages yet.

## PRIORITY FINDINGS — FIX IN A LATER IMPLEMENTATION PASS

P1 — Failed send loses draft (04/10/54)
Reproduction: inject DataStoreError from SessionService.add_message, type a
message, submit. Actual: the editor becomes empty even though storage failed.
Cause: PromptBox.submit clears before the receiving handler accepts the write.
Required outcome: retain/recover draft, mode and attachments; show an error;
retry creates one accepted message. Add a focused failure-and-retry check.

P1 — Mode transition mixes session views (06/10/49)
Reproduction: submit normal text; invoke Toggle Nobody; submit private text.
Actual: separate normal/private records exist, but both labels remain in the
same message view. Status text stays "Local GUI session · persistent storage".
The probe verified only the normal text in the normal session's stored messages;
this observation is not evidence of a private-message disk leak.
Required outcome: explicit transition, one active session view, truthful persistent
indicator/status, and no implicit copying of content between modes.

P1 — Transient session disposal and draft ownership incomplete (03/06/10)
Reproduction: create a private session, then New Chat. The service still retains
one private session; separately, New Chat retains a previously typed draft.
Required outcome: a deliberate close/switch policy, disposal of closed private
records, and session-scoped drafts with explicit unsaved-edit handling.

P2 — Large-text Nobody control clips (02/04/35)
Observed: 1100×680, Sans Serif, Large, Roomy; fixed 82-pixel Nobody button truncates
its label. The problem remains visible with the sidebar collapsed.
Required outcome: content/font-aware sizing; inspect all similarly fixed controls
at supported text sizes/densities. Scrolling long panels is acceptable; clipped
control labels or unreachable actions are not.

P2 — Preferences ahead of actual functionality (47/48/49)
Sensitive blur is a stored widget property, not a sensitive-span renderer. Status
summary is a static label, not process presentation. Web Search routes to the
conversation Search scaffold. Clearly explain/disable unavailable behavior until
its actual consumer is implemented; do not imply protection or a working tool.

No fixes were applied in this review. Passing the existing suite does not resolve
these separately reproduced gaps.


## Earlier layout-normalization note


## Scope

Project-structure normalization for the PySide6 application.

## Result

The repository now has designated locations for project metadata, services, packaged assets, architecture and testing documentation, acceptance evidence, reference media, and review notes. Existing source and root-level acceptance records were preserved.
