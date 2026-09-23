# Improve the current Otter Cove implementation

Date: 23 September 2026

Status: proposed, documentation only

Scope: improve and complete existing desktop, chat, preferences and local-data behavior

## Objective and authority

Make the existing application dependable before expanding its feature surface.
Keep PySide6, the modular desktop architecture, the local service/repository
boundaries, and the current GUI-first direction. Model configuration and execution
remain deferred.

`PLAN.md` remains the canonical requirements and acceptance plan. This proposal
breaks improvements to the reviewed implementation into independently reviewable
tasks. It does not mark any canonical criterion accepted, supersede the plans in
[PR #8](https://github.com/BigBenKenobi/Otter-Cove/pull/8), or authorize merging
other PRs. Where a task improves part of a larger feature step, accept only that
part. Complete feature modules and release scope still follow `PLAN.md`.

The supporting [review and reproduction record](../reviews/2026-09-23-current-implementation.md)
distinguishes reproduced defects, source observations and pending native evidence.

## Reviewed baseline

| Source | Exact revision | Review result |
|---|---|---|
| `main` | `6aa802219f4130ac4732039bda01b0a870934cfe` | 73 tests passed, no skips; additional probes found gaps |
| PR #6, R2 local data recovery | `a560b5d7c7d88fc6d941e0d5da8542c9ac7d64c3` | 74 tests passed, no skips; offscreen smoke passed; additional defects remain |
| PR #8, existing non-model plans | `531aaa38fe61fac867f8238744c5c6fce08aca18` | Read the inventory and Foundation, Sessions and Composer plans; documentation only |

Verification used Python 3.12.14 and PySide6/Qt 6.11.2 in a Linux container with
the offscreen Qt platform. It provides no new Fedora/Wayland, native-dialog,
screen-reader, display-scaling or reference-machine performance acceptance.

### What is already useful

- Bootstrap and composition are separated; routes, commands, themes and shell
  state have identifiable owners.
- Floating tools preserve the mounted chat and have geometry, minimize, reopen
  and Peek behavior.
- SQLite repositories, migrations and UI-facing services exist. Nobody sessions
  are stored in memory; normal messages persist.
- Failed-send retry and normal/private draft isolation have regression coverage.
- Theme presets, customization, harmony, named bundles, effect controls,
  Appearance and shortcut editing work to a substantial extent.
- Shared feedback, deterministic states and a useful automated suite exist.

Most other product routes are explicitly unavailable scaffolds. Documents, Brain,
Notes, Tasks and Gallery have storage records but do not yet have working feature
workspaces. This improvement pass must not count those records as completed tools.

## Priority and execution order

**P0**: protect data and correct the R2 contract before landing its recovery UI.

**P1**: fix current reliability and usability gaps before the next feature increment.

**P2**: finish maintainability, reproducibility and scoped desktop release evidence.

Each row is a separate task/PR where practical. A large task should be split at
the service/UI boundary without weakening its exit criteria.

| ID | Priority | Task | Depends on |
|---|---|---|---|
| OC-00 | First | Reconcile baseline and current documentation | — |
| OC-01 | P0 | Prevent exports overwriting application storage | OC-00 |
| OC-02 | P0 | Preserve excluded Nobody state during import/reset | OC-00 |
| OC-03 | P0 | Enforce a complete, typed import contract | OC-00 |
| OC-04 | P0 | Enforce credential rules at existing storage boundaries | OC-03 |
| OC-05 | P1 | Make expected storage/read failures recoverable | OC-03 |
| OC-06 | P1 | Recover invalid preferences and report save failures | OC-00 |
| OC-07 | P1 | Bound local-data work and keep the GUI responsive | OC-01–05 |
| OC-08 | P1 | Harden theme file handling and saved-theme state | OC-01, OC-06 |
| OC-09 | P1 | Correct empty-session restoration | OC-05 |
| OC-10 | P1 | Make current session/private lifecycle explicit | OC-02, OC-09 |
| OC-11 | P1 | Make the existing composer usable for long drafts | OC-10 |
| OC-12 | P1 | Render existing message text safely and accessibly | OC-05, OC-09 |
| OC-13 | P1 | Finish shell and floating-tool interaction | OC-06 |
| OC-14 | P1 | Align navigation and commands with actual capabilities | OC-10, OC-13 |
| OC-15 | P1 | Complete keyboard, focus and responsive layout checks | OC-08, OC-11–14 |
| OC-16 | P1 | Finish theme and appearance consistency | OC-08, OC-15 |
| OC-17 | P1 | Verify animation lifecycle and measure performance | OC-06, OC-13, OC-16 |
| OC-18 | P1 | Bound feedback and retain usable error details | OC-05, OC-15 |
| OC-19 | P1 | Complete shutdown and retained-resource cleanup | OC-07, OC-10, OC-17–18 |
| OC-20 | P2 | Consolidate ownership and document changed boundaries | Throughout; close after OC-19 |
| OC-21 | P2 | Add reproducible CI and truthful validation output | Start after OC-00; close after fixes |
| OC-22 | P2 | Repair packaging and provide a Fedora launch path | OC-19–21 |
| OC-23 | P2 | Complete scoped native acceptance and closeout | OC-01–22 |

Run OC-01–04 as the first implementation batch. Then land the remaining fixes
in small groups; do not hold an urgent data fix for all visual checks. Native
checks can start early, but final acceptance must use the corrected revision.

## Task plans

### OC-00 — Reconcile the baseline and documentation

**Evidence:** `main` still names R2 as the next implementation; PR #6 contains it.
PR #8 already proposes detailed non-model work. README, architecture/testing notes
and the end of PLAN contain stale test counts or pre-Git/R1 statements.

**Work**

1. Recheck the heads of `main`, #6 and #8 before implementation. Review #6 with the
   new findings below; record the selected base and eventual replacement/fix SHA.
2. Reconcile `STATUS.md`, README, ROADMAP and current-check text in PLAN. Preserve
   dated historical evidence, clearly labelling its original source/environment.
3. Keep #8's detailed plans as the source for their later feature increments.
   Link this proposal as the current-implementation hardening work.
4. Locate the original visual references. `docs/reference/` is absent from this
   checkout despite being named in the documentation. Restore supplied originals
   or identify their real accessible location; record a blocked parity check if
   unavailable. Do not manufacture replacement reference images.

**Accept when:** one source baseline, one current next action, correct test scope,
and explicit reference availability are documented. No feature completion changes
are inferred from documentation edits. **Maps to:** PLAN governance, 01, 55.

### OC-01 — Protect storage from export destinations

**Evidence:** `LocalDataService.export_json(data.store.path)` replaces the live
SQLite file with JSON. Atomic replacement protects an ordinary destination from
partial writes, but does not make that destination safe.

**Work**

1. Validate destinations before creating directories or temporary files. Reject
   the active database, its WAL/SHM files, and application preferences. Apply the
   same protected-target policy to theme export where the shell knows these paths.
2. Resolve symlinks and compare existing file identities where applicable so an
   alternate path cannot bypass protection. Do not depend on a dialog extension.
3. Return a typed, readable error. Keep current export atomicity for valid targets;
   ensure failure leaves an existing destination and the active store intact.

**Accept when:** direct, alias/symlink and sidecar targets are rejected before
mutation; the database reopens with its original records; normal export succeeds.
Use disposable stores for every destructive-path test. **Maps to:** 37, 54.

### OC-02 — Preserve the state excluded by import/reset

**Evidence:** PR #6 says Nobody is outside reset/import, then calls
`ChatSurface.reset_chat()`, which disposes the private session and its draft.

**Work**

1. Give durable-data replacement its own chat refresh operation. Preserve live
   Nobody messages, drafts and mode because the existing confirmation excludes
   them. Do not reuse New Chat's private-session disposal operation.
2. Invalidate IDs, message views and cached drafts belonging to deleted durable
   records. Restore an appropriate imported normal session or a truthful empty
   normal view without changing a currently active private view.
3. Protect pending normal drafts through an explicit confirmation/preservation
   policy. Keep affected/excluded reports consistent across service, dialog and UI.
4. Ensure failed and cancelled operations leave all views and draft state intact.

**Accept when:** UI-level tests cover reset and import in normal and private mode,
including a live private message/draft and stale normal IDs. Excluded private
state survives; a later explicit New Chat still disposes it. **Maps to:** 06, 54.

### OC-03 — Validate complete import snapshots before replacement

**Evidence:** both reviewed code revisions accept future `schema_version=999`,
missing table collections and null IDs. PR #6 normalizes malformed nested JSON,
but a session title array still raises `AttributeError`.

**Work**

1. Define supported export/schema combinations and normalize supported older
   snapshots explicitly. Require all tables for a full replacement snapshot;
   empty tables must be present as lists. A deliberately partial import needs a
   separate format/mode rather than silently treating absence as deletion.
2. Validate field types, nonempty stable IDs, relationships, ordinal uniqueness,
   allowed roles/states, booleans, timestamps and finite numeric ranges. Reject
   missing/null identity values instead of generating new IDs during restore.
3. Decode and validate nested metadata/config/tag structures before mutation,
   with table/row/field errors. Reuse repository/service validation for direct
   writes so accepted records have the same meaning through either entry point.
4. Preserve #6's JSON-decoding fix. Wrap expected malformed values in
   `DataValidationError`; keep transaction rollback as the final safety net.
5. Preview counts and replacement scope before confirmation. Import the exact
   validated snapshot so a file changing after preview cannot change the operation.

**Accept when:** malformed, incomplete, future-schema and duplicate/reference
fixtures reject with visible errors and unchanged prior data; supported exports
round-trip IDs, timestamps, order and fields exactly. **Maps to:** 54.

### OC-04 — Enforce the existing credential-storage contract

**Evidence:** a synthetic user/password URL and credential query survive the
existing `ModelService.create()` path into SQLite and JSON export. The generic
policy inspects keys, not credentials embedded in URL values; export also sees
nested metadata as serialized JSON strings.

**Work**

1. For existing structured endpoint/config fields, reject parsed URL userinfo and
   credential-bearing query parameters before storage or import. Validate both
   service and lower-level write paths used by import.
2. Inspect decoded structured metadata/config during export as a final guard.
   An unsafe existing record should block export with a field-level remediation
   message that does not echo its secret. Do not silently delete stored records.
3. Replace overly broad key-substring decisions with a documented structured-field
   policy that still rejects credentials but permits legitimate numeric settings
   such as token limits. Keep ordinary document/message text semantics explicit;
   this task is not a general secret detector or content scrubber.
4. Use synthetic credentials and test create, import and export, including nested
   structured values. Carry these requirements into the later model plan.

**Accept when:** credential-bearing structured records cannot enter or leave the
ordinary store, while legitimate non-secret settings remain usable. This is a
repair to existing persistence; no model UI, probes or provider are added.
**Maps to:** 54; future 40–44 reuse the boundary.

### OC-05 — Make expected storage and read failures recoverable

**Evidence:** non-UTF-8 local-data input escapes as `UnicodeDecodeError` even in
#6. Repository reads often issue SQL without translating errors, whereas chat
handlers expect `DataStoreError`. `get_session()` is outside the render try block.

**Work**

1. Translate decoding failures at the file boundary and expected SQLite failures
   at the repository/store boundary. Preserve causes for diagnosis without
   exposing content or credentials in user messages.
2. Guard session lookup and message reads as one operation. Preserve the current
   draft and distinguish load failure from a genuinely empty conversation.
3. Defer initial session loading until the shell's error consumer is connected,
   or return initialization issues for the shell to present after construction.
4. Validate corrupt decoded row metadata instead of allowing later `.get()` or
   conversion failures. Never silently replace the database on a read failure.

**Accept when:** unreadable/invalid-encoding imports, closed/locked stores and
corrupt row metadata produce actionable feedback; no expected exception escapes a
Qt handler, draft vanishes or failed load is presented as empty success.
**Maps to:** 03, 10, 53, 54.

### OC-06 — Recover invalid preferences and report persistence failures

**Evidence:** stored effect quality `inf` causes `OverflowError` during
`MainWindow` construction. Runtime effect setters enforce minimums but no upper
bounds. QSettings exposes status, but shell save flows do not report it.

**Work**

1. Centralize effect defaults and finite ranges; reuse them for saved preferences,
   runtime changes and theme bundles. Reject/recover NaN, infinity, excessive
   values and invalid colors before effects allocate particles.
2. Validate saved booleans/enums/shortcut data consistently. Recover per field to a
   documented default and report a concise warning after the UI is available.
3. Check QSettings sync/status at persistence boundaries. Present an unsaved state
   and recovery path instead of reporting successful saving after an access error.

**Accept when:** invalid settings cannot crash startup or cause unbounded particle
allocation; recovered values are visible; simulated write errors do not claim
durability. Restart tests cover supported extremes. **Maps to:** 35–37, 47, 50, 54.

### OC-07 — Bound data operations and avoid GUI stalls

**Evidence:** import/export/read work is synchronous in Qt handlers; imports read
the complete file, and SQLite's busy timeout is five seconds. Actual large-data
latency has not been measured in this review.

**Work**

1. Measure a representative populated store, large supported import and held
   writer lock. Set documented file/record limits based on supported use cases.
2. Keep operations exceeding PLAN's 100 ms GUI-blocking budget off the event
   loop. Use a serialized worker with its own SQLite connection; never share the
   current connection across threads or allow concurrent destructive operations.
3. Use a consistent read transaction for multi-table snapshots. Carry a validated
   import snapshot from preview to apply; bound memory or stream where justified.
4. Expose busy/progress/failure states, block duplicate actions, and define the
   cancellation boundary before commit. Ignore stale UI completions safely.

**Accept when:** the UI remains responsive during supported I/O and a lock wait;
cancel/retry/shutdown cannot partially import or export; limits give useful errors.
Do not add a job framework beyond the measured requirement. **Maps to:** 53, 54.

### OC-08 — Harden theme interchange and saved-theme state

**Evidence:** non-UTF-8 theme files raise an uncaught `UnicodeDecodeError`.
The atomic writer creates the directory outside its error conversion, and assigns
the temporary cleanup path only after writing/flushing succeeds. Boolean fields
use truthiness, so a string such as `"false"` is interpreted as true.

**Work**

1. Validate strict bundle types and supported versions. Convert encoding,
   directory, write, flush and replace failures to `ThemeBundleError`.
2. Track the temporary file as soon as it exists and clean it on every failure.
   Keep target bytes, active theme and saved catalog unchanged after rejection.
3. Confirm a selected saved theme has consistent edit/restart semantics for
   typography, effect settings and overrides. Document whether edits are a working
   override or explicitly require re-saving; make the UI match that decision.
4. Verify save/replace/import cancellation and duplicate handling; use typed
   duplicate errors rather than matching exception text where practical.

**Accept when:** invalid encoding/types and injected write failures give readable
feedback without leftovers or mutation; named theme round-trips and subsequent
edits match the documented behavior. **Maps to:** 33–37.

### OC-09 — Correct restored empty-session presentation

**Evidence:** an existing zero-message session restores with the hero hidden.
Startup unconditionally switches to the message view; the normal render path
already checks message count. Failed first sends can leave such an empty session.

**Work**

1. Use one rendering path for startup and session transitions. A successfully
   loaded zero-message session displays the configured welcome/empty state.
2. Restore its ID/title while retaining correct normal/private indicators.
3. Keep first-send failure/retry behavior and avoid creating a second session or
   clearing the draft when message persistence fails.

**Accept when:** fresh, restored empty, populated and failed-first-send fixtures
show the correct view; the first accepted message transitions once. **Maps to:** 03, 04, 10.

### OC-10 — Make the current private-session lifecycle explicit

**Evidence:** mode switching and draft isolation exist. The Nobody button lives
inside the hero, which hides after sending, while status summaries can be hidden.
The header retains a private label, but a persistent mouse-accessible transition
control and message-bearing transition choice still need completion.

**Work**

1. Provide a persistent, keyboard-accessible session privacy indicator/control
   outside the empty hero. Its meaning must remain visible even if optional status
   summaries or the welcome area are hidden.
2. Apply PLAN's explicit transition choice after messages exist. Switching to a
   separate normal/private session must never silently convert private content.
3. Keep New Chat's documented discard semantics clear; purge private records and
   drafts on explicit private close and application teardown. Remove cached
   durable drafts when their records are deleted/replaced.
4. Reuse the state ownership in PR #8's Sessions plan. Keep unsent drafts transient
   across process restart unless the canonical scope is intentionally changed.

**Accept when:** normal/private transitions are usable with pointer and keyboard
after messages exist; repeated transitions, New Chat and reset/import preserve or
dispose exactly the intended records. No private content reaches ordinary data,
export, diagnostics or future persistent search. **Maps to:** 03, 06, 47.

### OC-11 — Improve the existing composer for long drafts

**Evidence:** the composer is fixed at 96 px, the editor is capped at 42 px and
its scrollbar is always hidden. Its placeholder still says “Message Odysseus…”.

**Work**

1. Grow the editor to a documented maximum, then enable scrolling. Derive layout
   from typography/density and available workspace height; keep send/mode controls
   reachable with a long multiline paste.
2. Preserve the 720 px reference width when space permits, full-width preference
   and the 1100×680 supported minimum. Fix fixed spacers where they obstruct this.
3. Retain Enter/newline, Ctrl+Enter/send, whitespace rejection, exact draft/mode
   retention on failure and one-time clearing after success.
4. Correct branding and make local storage behavior and unavailable model selection
   clear. Do not enable unsupported Web/Shell/model behavior.

**Accept when:** long text, Unicode, multiline paste and keyboard editing work at
minimum size and Large/Roomy; existing failed-send tests remain valid. Canonical
step 04 stays Partial until the future request/attachment contract exists.
**Maps to:** 04, 35, 47.

### OC-12 — Make existing message rendering explicit and safe

**Evidence:** local messages are passed directly to `QLabel` with default
`AutoText`; text format, copy policy and keyboard selection are not explicit.
This is a rendering trust-boundary observation, not evidence of script execution.

**Work**

1. Render existing user text as literal plain text, including HTML-looking input.
   Set format deliberately for user-supplied titles and feedback too. Introduce
   sanitized rich content only through the separate renderer contract in #8.
2. Add keyboard selection/copy and visible role/time presentation without deriving
   state from widget text. Keep stored content unchanged by presentation.
3. Verify long unbroken text, code-like text, bidirectional text and a 200-message
   fixture. Preserve reading position; scroll only while following the end.
4. Make rebuild/reopen ordering deterministic and avoid accumulating deleted
   message widgets or losing the draft during a view refresh.

**Accept when:** markup displays literally, no user text triggers resource loading,
copy returns the intended displayed content, and the 200-message fixture stays
usable within PLAN's interaction target. Sensitive spans, status fixtures and
streaming are later SC-plan work; do not claim them complete. **Maps to:** 10, 53.

### OC-13 — Finish shell and floating-tool behavior

**Evidence:** the framework already has substantial tests. Native drag, focus,
Peek and display-change evidence remain pending.

**Work**

1. Reuse the existing manager; verify singleton open/focus, close/reopen state,
   minimized restoration and independent normal/minimized geometry.
2. Test all implemented resize affordances and pointer dragging with overlapping
   tools, minimum shell size, host resize and changed display bounds.
3. Preserve the active chat/draft and ensure titlebar, close and resize controls
   remain reachable. Define sensible behavior when the desktop provides fewer
   logical pixels than the documented minimum, especially at 200% scaling.
4. Repeat ten tools' lifecycle and twenty theme/session changes, recording widget,
   signal and timer growth. Fix reproduced leaks or unreachable controls only.

**Accept when:** existing automation passes and native pointer/focus evidence
confirms the framework's contracts on supported desktops. **Maps to:** 01, 38, 39.

### OC-14 — Align sidebar, commands and actual capability

**Evidence:** registries exist, but the sidebar constructs from the default route
registry while `MainWindow` accepts an injected registry. Commands use
window-wide shortcuts; ordinary text-editor conflicts need native verification.

**Work**

1. Pass one route registry through the shell/sidebar/Appearance consumers. Make
   available/scaffold state and active state agree after open, hide and close.
2. Verify rapid collapse/expand settles at the requested width and persists;
   keep Settings and New Chat accessible when optional navigation is hidden.
3. Audit command contexts and rebinding against ordinary editing keys. Reject or
   explicitly scope conflicts instead of silently hijacking typing/copy/undo.
4. Keep command labels/tooltips synchronized and feature commands unavailable
   until their consumers exist. No completion credit for a scaffold route.

**Accept when:** custom-registry, rapid-toggle, restart and disabled-command tests
pass; native keyboard checks preserve expected editing behavior. **Maps to:** 02, 47, 50.

### OC-15 — Complete accessibility and responsive layouts

**Evidence:** some names, focus handling and announcements exist; the full native
matrix remains unverified.

**Work**

1. Audit icon-only controls, labels, tab order, focus visibility, activation,
   Escape, dialog focus return and keyboard access to important errors.
2. Check Home/chat, Theme, Settings, floating titlebars, menus and confirmations at
   Small/Default/Large × Compact/Comfortable/Roomy and minimum/default/maximized
   sizes. Use long theme names, titles and error messages.
3. Verify native accessibility announcements and readable focus/selection/disabled
   states in light and dark themes. Add scroll containers or adaptive sizing
   where needed rather than shrinking text or clipping controls.

**Accept when:** primary flows are possible without a mouse and no primary control
is clipped/unreachable in the supported matrix. Record native checks separately
from offscreen geometry assertions. **Maps to:** 01, 02, 35, 47, 50, 53, 55.

### OC-16 — Finish theme and appearance consistency

**Work**

1. Check all 16 presets on mounted and newly opened surfaces. Review Light,
   Copper, Ocean and Forest in matched states against available originals.
2. Verify every semantic token and More Colors control, picker cancel, preset
   reset semantics, neutral-input harmony preview/apply/reset and live updates.
3. Verify all currently implemented Appearance toggles preserve session/draft
   state and restart correctly. Keep Sensitive blur unavailable until step 48 has
   a renderer/copy policy; Web/Shell visibility activation follows #8's utilities.
4. Check Frosted's documented translucent fallback for legibility. Consolidate
   literal styling only where it defeats semantic tokens or live typography.

**Accept when:** native visual/restart checks meet the selected requirements and
intentional reference differences are recorded. Steps with deferred consumers
remain Partial. **Maps to:** 32–35, 37, 47.

### OC-17 — Validate animation lifecycle and performance

**Work**

1. Reuse #6's paint/frame instrumentation. Check ten effects, resize/switch,
   control synchronization, Solid's stopped timer and user Pause independently of
   visibility, application inactivity and minimized state.
2. Run a native sweep to identify expensive effects. Record the required
   60-second 1720×900 Balanced trace, including Leaves for comparison and the
   slowest observed effect, with GPU/driver/scale/Qt/source identity.
3. Target approximately 60 FPS and p95 frame interval ≤33 ms. Distinguish update,
   paint, timer interval and actual presentation evidence. Do not present the
   offscreen smoke or a short instrumentation check as performance acceptance.
4. Profile only failures; optimize particle work/repaints or add an explicit,
   tested lower-quality fallback. Verify Peek through lifecycle and theme changes.

**Accept when:** the measured native target or documented accepted fallback holds,
Pause is preserved, Peek remains visual-only, and hidden/closed states stop work.
**Maps to:** 36, 38, 55.

### OC-18 — Bound feedback and improve retained error details

**Evidence:** feedback appends history without an automatic bound and stacks every
toast vertically. The important-issue menu resolves an item when activated,
instead of opening a separate readable detail view.

**Work**

1. Limit visible toasts and queue/coalesce repeated messages. Bound ordinary
   history with a documented policy while retaining unresolved important issues.
2. Provide an accessible detail view with separate resolve/dismiss controls.
   Long recovery instructions should remain readable after a toast expires.
3. Ensure repeated failures do not obscure the composer or steal focus; make
   notification lifetime and cancellation belong to a clear QObject owner.

**Accept when:** a burst of failures stays within host bounds, details remain
available, dismissal differs from resolution, and retained memory is bounded by
the documented policy. **Maps to:** 53.

### OC-19 — Complete shutdown and resource cleanup

**Evidence:** the shell stops the background and closes SQLite; private collections
live in `SessionService`, while feedback/shared-state work uses delayed callbacks.
The whole lifecycle needs a single explicit close contract.

**Work**

1. Give services/controllers an idempotent close/dispose path. Purge private
   session/draft state on close without relying only on process termination.
2. Cancel/settle pending operations before closing their database connections;
   prevent delayed callbacks from updating destroyed widgets or closed stores.
3. Commit geometry/preferences with visible failure handling and keep ownership
   of injected services explicit for tests and callers.

**Accept when:** closing during feedback/demo/data work produces no late writes,
duplicate completion or unexpected process; a second close is safe; reopening
uses valid persisted state and no private content. **Maps to:** 06, 39, 53–55.

### OC-20 — Consolidate ownership and meet documentation requirements

**Work**

1. Keep `main.py` as bootstrap, `app.py` as composition, UI free of SQL/provider
   calls, and existing local services in `core/data/`.
2. During the above fixes, extract cohesive local-data-operation or presentation
   coordination only where it reduces duplicated state/error handling in the now
   large composition root. Avoid a broad rewrite or unused abstraction layer.
3. Reuse typed validators, error types and shared registries. Avoid exposing new
   repository internals through widget code.
4. Apply AGENTS.md's module/class/function/lifecycle documentation standard to
   every materially modified code file. Review accuracy after implementation.

**Accept when:** each changed boundary has one owner and clear data/error/lifecycle
contracts; relevant tests pass after documentation changes. This is part of each
task's definition of done, with a final consistency pass. **Maps to:** architecture contracts.

### OC-21 — Make verification reproducible and truthful

**Evidence:** no `.github` workflow is tracked. The smoke prints “native” even
when explicitly run offscreen; unit tests can skip Qt cases when PySide6 is absent.

**Work**

1. Add CI for the supported Python/Qt combinations, isolated full unittest suite,
   offscreen smoke and installed-package smoke. Make missing required Qt coverage
   fail the release gate instead of treating a skipped suite as complete.
2. Report the actual Qt platform, source SHA, environment and skips. The native
   runner must reject accidental offscreen execution; offscreen output must say
   offscreen. A printed checklist is not a passed manual check.
3. Document one reproducible development environment and dependency-update policy.
   Confirm the declared minimum Python/Qt versions or revise them based on tests.
4. Retain concise logs for failures and accepted runs. Keep tests isolated from
   personal SQLite/QSettings and use targeted no-network/no-process guards for
   simulated operations as those consumers are introduced.

**Accept when:** a clean checkout can reproduce all automated gates, missing Qt
fails appropriately, and platform labels cannot imply unperformed native checks.
**Maps to:** 53–55 and TESTING.

### OC-22 — Repair packaging and provide a desktop launch path

**Evidence:** the built wheel contains `app.py` and `main.py` but no `core`, `ui`
or `effects`; importing it away from the checkout fails with missing `core`.

**Work**

1. Configure package discovery to include required packages and future runtime
   assets, excluding tests/reference media unless deliberately shipped.
2. Add an executable entry point and verify install/import/start from a fresh
   environment whose working directory is outside the source tree.
3. Provide a Fedora desktop entry/icon/install-uninstall procedure with a stable
   application ID and working directory-independent paths. Avoid requiring a
   terminal or a hardcoded developer checkout path.
4. State the supported Python/Qt/platform range and retain normal XDG data paths.
   An uninstall must not silently remove user content.

**Accept when:** wheel/sdist contents are checked, an isolated installed build
starts, and native Fedora launcher/startup/error behavior is recorded.
**Maps to:** 01, scoped 55.

### OC-23 — Complete native acceptance and close out the selected scope

**Work**

1. Run #8's FD-6/FD-7 desktop/evidence procedure against the final corrected
   revision: KDE Wayland and GNOME Wayland, 100/150/200% scaling, supported sizes,
   keyboard/pointer/clipboard and native dialogs. Explicitly revise support if a
   platform is excluded; do not mark an unrun cell passed.
2. Include startup corrupt/unavailable-store recovery, all import/export/reset
   outcomes, theme/file dialogs, focus return, display changes, long drafts,
   private transitions, Peek and shutdown.
3. Retain a manifest, automated logs, actual native checklist outcomes,
   performance output and matched-reference captures under `docs/acceptance/`.
4. Update PLAN checkboxes, STATUS, ROADMAP and CHANGELOG only from evidence.
   Record remaining partial steps and deferred feature IDs. Tagging/releasing is
   a separate action after the intended acceptance and user direction.

**Accept when:** the current implementation has no unresolved P0/P1 defect in the
selected scope, automated gates pass with no skips, native results identify the
tested source, and unsupported/deferred behavior is explicit. This is foundation
and existing-chat acceptance, not completion of all 55 product steps.

## Later feature work: reuse the existing plans

After this pass, extend useful local behavior in the order already proposed in
PR #8. These are new feature increments and are not prerequisites for fixing the
current application:

| Next increment | Existing plan / boundary |
|---|---|
| Session browser, rename/favourite/archive/delete, local history search, safe rich/status/sensitive-span rendering | PR #8: `docs/planning/sessions-local-conversation-plan.md`; reuse OC-09–12 rather than rebuild them |
| Composer popover, transient attachments/workspace selection and optional simulated actions | PR #8: `docs/planning/local-composer-utilities-plan.md`; keep model request work deferred |
| Documents and Library | Expand the inventory into its own plan when selected; connect search and composer through stable service contracts |
| Brain, productivity tools, Gallery/editor, demo identity | Separate selected milestones from the eight-area inventory; storage tables and scaffolds do not establish feature completion |

Model registry/selector/defaults, Ollama/API integration, live online services and
AI processing remain deferred. Closed PR #7 requires a future rebase/review; it
is not a dependency for this plan.

## Implementation handoff and definition of done

For each task, supply its OC ID, current source SHA, listed files/boundaries, the
reproduction or acceptance gap, dependencies and exit conditions to the
implementation agent. Finish one task or coherent batch before expanding scope.

- Add a focused regression for each reproduced defect; use existing coverage for
  behavior already proven rather than duplicating implementation-shaped tests.
- Use disposable local data and synthetic values. Preserve IDs and migration
  compatibility. Keep private content and credentials out of diagnostics.
- Run focused checks, then the relevant full gate at the integration boundary.
  Run native checks only where that platform is actually available.
- Review explanatory documentation under AGENTS.md and update current status.
- Report exactly what changed, what was run, and what remains unverified.
- Do not close broader PLAN steps whose attachment, Library, model or other
  consumer-dependent criteria remain outstanding.
