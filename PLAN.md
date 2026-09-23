# Otter Cove — implementation and acceptance plan

Updated 23 September 2026. Target: Fedora 44, PySide6 / Qt Widgets.

**This is the single replacement plan.** It consolidates the former root plan,
PR #8's Foundation/Sessions/Composer plans and PR #9's 24 improvement tasks.
The earlier proposals are superseded. All 55 original feature IDs, deliverables,
dependency declarations and acceptance checkboxes are retained in the catalogue
below. Historical observations and repeated execution instructions have been
removed from that catalogue; current status belongs in STATUS and the ledger.

**Next:** establish OC-00's implementation baseline, then complete **OC-01–04**
before landing PR #6's data-management UI. Model configuration/execution remains
deferred. This documentation change does not implement the planned fixes.

## Navigation and document ownership

- [Current baseline](#current-baseline)
- [Execution order](#execution-order)
- [Cross-area completion boundaries](#cross-area-completion-boundaries)
- [Existing implementation tasks: OC-00–23](#existing-implementation-tasks)
- [Sessions and conversation: SC-1–6](#sessions-and-local-conversation)
- [Composer utilities: CU-0–6](#local-composer-utilities)
- [Shared acceptance gate](#shared-acceptance-gate)
- [Feature catalogue: 01–55](#feature-steps-and-acceptance-conditions)
- [Superseded-plan mapping](#superseded-plan-mapping)

| Document | Role |
|---|---|
| `PLAN.md` | Sole current scope, execution tasks, dependencies and acceptance requirements |
| [STATUS.md](STATUS.md) | Current implementation state, exact evidence and next action |
| [ROADMAP.md](ROADMAP.md) | Short summary of the execution order in this plan |
| [docs/ACCEPTANCE.md](docs/ACCEPTANCE.md) | Feature state/evidence index; not another requirements list |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [DECISIONS](docs/DECISIONS.md), [AGENTS](AGENTS.md) | Boundaries, settled choices and mandatory engineering documentation |
| [docs/TESTING.md](docs/TESTING.md), [FEDORA_CHECKLIST](docs/FEDORA_CHECKLIST.md) | Commands and native test procedure supporting this plan |
| `docs/reviews/`, `docs/acceptance/`, `docs/archive/` | Dated findings/evidence/history; never alternative current instructions |
| [docs/planning/](docs/planning/README.md) | Compatibility pointers to this replacement; no active standalone proposals |
| [The word of God](docs/task-packets/the-word-of-god/README.md) | Subordinate Terra execution packets for the OC-00–04 pilot; no new scope or implementation claim |

## Current baseline

| Source reviewed | Revision | Actual evidence |
|---|---|---|
| Application on `main` before documentation consolidation | `6aa802219f4130ac4732039bda01b0a870934cfe` | 73 tests passed, no skips |
| Open R2 implementation PR #6 | `a560b5d7c7d88fc6d941e0d5da8542c9ac7d64c3` | 74 tests passed, no skips; offscreen smoke passed; additional defects remain |
| Former non-model proposals, PR #8 | `531aaa38fe61fac867f8238744c5c6fce08aca18` | Documentation source absorbed into this replacement |
| Former improvement proposal, initial PR #9 | `3240dcb37e287cbb6d059c86b940bbd86da6b8d0` | Documentation source absorbed into this replacement |

The 23 September code review used Ubuntu 24.04.3, Python 3.12.14 and PySide6/Qt
6.11.2 with `QT_QPA_PLATFORM=offscreen`. It provides no native Fedora/Wayland
acceptance. The [review record](docs/reviews/2026-09-23-current-implementation.md)
contains reproduced failures and safe reproduction instructions. The earlier
65-test Fedora offscreen result is dated historical evidence.

The shell, floating tools, local data services, normal/private draft isolation,
failed-send retry, themes, effects, Appearance, shortcuts and shared states are
substantially implemented. Steps 01/53 retain earlier scoped acceptance. Most
other workspaces remain unavailable scaffolds; domain records alone do not make
Documents, Brain, Notes, Tasks or Gallery implemented product tools.

Immediate findings: export can overwrite active storage; R2 reset discards an
excluded Nobody session; incomplete/future-schema/null-ID imports are accepted;
credential-bearing endpoint values reach storage/export. Further tasks cover
uncaught read/validation errors, invalid effect preferences, empty-session
restoration, theme errors and incomplete packaging. None is fixed by this plan.

## Scope and completion rules

1. Keep the existing architecture. Qt presentation consumes local services;
   repositories own SQL. `main.py` remains bootstrap, `app.py` composition, and
   external adapters belong behind service boundaries.
2. The selected direction is useful local GUI behavior without model work. Use
   labelled deterministic fixtures only where the feature criteria allow them.
   No inference, real search, shell/agent execution, mail delivery, authentication,
   CalDAV synchronization or AI image processing is implied by a demo.
3. Preserve stable IDs, transactional migrations, atomic valid exports and
   memory-only Nobody data. Structured credentials never belong in ordinary
   SQLite/QSettings/export/logs; OC-04 repairs that existing boundary.
4. Run tests/demo flows with disposable local data. Add focused regressions for
   reproduced defects and reuse existing coverage for stable behavior.
5. A visible control either works or explains its unavailability. Tables,
   scaffolds, documentation and unrelated passing tests never establish Done.
6. A feature is Done only after its criteria, applicable dependency gates and
   shared acceptance requirements have actual evidence. Record accepted subsets
   while leaving broader steps Partial. Never lower thresholds to obtain a pass.
7. Preserve dated evidence. Report source revision, runtime, Qt platform, skips,
   actions and outcomes. Offscreen checks do not substitute for native evidence.
8. Every materially modified code file meets AGENTS.md's explanatory standard;
   review documentation accuracy and run relevant checks after comments are added.

Status meanings: **Not started/scaffold** = no dedicated workflow;
**Data/preference foundation** = records/settings without the feature;
**Partial** = implementation remains; **Implemented, acceptance pending** =
remaining native/visual/performance gates; **Scoped accepted** = only the named
historical or current subset; **Done** = all applicable criteria evidenced.

## Execution order

This order replaces the former R1–R6 and model-first A–G sequence. Feature
`Depends on` declarations remain integration/completion gates. They do not prevent
independent local work on a named subset; they do prevent claiming unsupported
full completion. The task dependencies below govern actual coding order.

| Area / order | Work | Exit and later boundary |
|---|---|---|
| 1a. Protect current data | OC-00, then OC-01–04; review corrected R2 implementation | Safe destinations, truthful reset/import scope, validated snapshots and credential rules |
| 1b. Complete existing foundation and chat | OC-05–22 using their dependency table; OC-20 is continuous, OC-21 can begin early | Current UI reliable, maintainable and reproducible |
| 1c. Foundation desktop acceptance | OC-23 using the shared gate | Native evidence for the selected foundation; not all 55 features |
| 2. Sessions and local conversation | SC-1; CU-0/CU-1 shared popover before SC-2; SC-2–6 | Session CRUD/browser, privacy integration, safe fixtures, local history search, sensitive/status presentation |
| 3. Local composer utilities | CU-2–6 after session draft contracts; reuse CU-0/CU-1 | Local selections and labelled Web/Shell simulations; no attachment consumption claim |
| 4. Documents and Library | 28 → 27 → complete 11's Library provider and 07's Documents picker | Local text/Markdown editing, unsaved protection, shared stable IDs and search; Prompt gate remains |
| 5. Brain records and controls | 13 → 14 → 15 → 16 | Local memories/skills/import-export and explicitly simulated audit/extraction; recheck private exclusion |
| 6. Local productivity | Define the local/non-AI slice of 44; 31 → 30 → 12 → 45 → 46 → 17, applying each feature's dependency gates | Local tasks/notes, fixture email, simulated reminders, calendar/basic ICS; no live delivery/sync |
| 7. Gallery and conventional editor | 21 → 22 → 23 → 25 → 24 | Local import/albums, document/canvas/layers/history and ordinary editing; AI-labelled controls remain fixtures |
| 8. Demo identity and study | 51 → 52 | Explicitly simulated account/2FA/profile flows and meaningful local Study Mode |
| Every completed area | Shared acceptance gate on the feature changes and affected foundation contracts | Fresh evidence and accurate Partial/Done boundaries |

Areas 1–3 have the execution-ready tasks below. Areas 4–8 retain their full
feature deliverables/criteria in the catalogue; expand the selected area's
implementation packages **inside this plan** before starting it. Do not infer a
complete implementation design for them from their storage tables or recreate
separate competing plans. This replacement preserves their scope without claiming
that the earlier preparation contained detailed task breakdowns for all eight.

### Deferred model and mixed work

| Feature IDs | Boundary |
|---|---|
| 05, 40–42 | Model registry, selector, defaults and probes deferred; closed PR #7 needs future rebase/review |
| 18–20, 43 | Model comparison, model management, research and provider settings deferred |
| 04 | Autosizing/drafts/local storage can improve now; final selected-model/request/attachment contract remains later |
| 09 | Prompt editing/CRUD may be scoped later; full Prompt Studio requires model selection and request consumption |
| 26, 29 | Mask/editor preparation and report presentation may advance later; model inpaint and research-artifact provenance remain gated |
| 44 | Local settings/contact-file work must be scoped separately from model/agent integrations; combined step stays Partial |

No model step is reopened merely to satisfy an incidental dependency of a local
subset. When model work is selected later, update this plan explicitly and retain
the privacy and service boundaries.

## Cross-area completion boundaries

| Step / contract | Can be evidenced now | Gate that remains |
|---|---|---|
| 03 | Empty/restored/new session and responsive sidebar layout | Re-run Notes-dock layout after 30 exists |
| 04 | Editor sizing, text/mode retention and local submission retry | Selected model and accepted attachment/request record |
| 06 | Private disk/export/search exclusion, transitions and disposal | Revalidate with CU attachments and Brain extraction consumers |
| 07 | Popover, file/workspace selection and transient chips | Documents and Prompt must open their actual modules |
| 08 | Complete labelled simulated actions and visibility behavior | Record its local subset; retain unresolved prerequisite integration gates |
| 11 | Persistent conversation history provider | Library metadata/content provider from 27/28 |
| 47 | Existing Appearance behavior | Enable Sensitive blur/status/Web/Shell controls only when their actual consumers pass |
| 50 | Existing commands and editor | Activate Favourite/Delete only after SC workflows are real |
| 55 | Selected foundation or feature-area matrix | Full release requires all selected features; explicitly list deferred IDs |

### Session and draft ownership contract

| Action | Required ownership/result |
|---|---|
| Ordinary persistent session switch | Save outgoing transient draft/view state; load incoming only on success |
| Normal/private switch after messages | Explicit switch-and-retain, new-session or cancel choice; no copying between modes |
| New Chat from a concrete persistent session | Retain its session-owned draft for return and create a blank pending normal slot |
| New Chat from a pending slot | Explicit New Chat discards pending text/selections under its documented UI policy |
| New Chat or Close Nobody | Dispose the private message/draft/status/selection aggregate and return to a valid normal view |
| Durable-data reset/import | Preserve excluded Nobody state; refresh/invalidate affected durable IDs and protect ordinary unsaved drafts explicitly |
| Application close/restart | Dispose all private state; restore durable content only; unsent drafts remain process-local unless scope is explicitly revised |

Do not silently use the New Chat operation to refresh a view after reset/import.
Draft ownership starts in separate pending normal/private slots before a record
ID exists, then follows the concrete session ID. Later attachment state joins
the same aggregate rather than introducing another owner.

## Existing implementation tasks

OC IDs are retained for continuity with the 23 September findings. P0 means data
protection before landing R2; P1 means current reliability/usability before feature
expansion; P2 means maintainability/distribution/evidence before scoped release.

| ID | Priority | Task | Depends on |
|---|---|---|---|
| [OC-00](#oc-00) | First | Reconcile baseline and current documentation | — |
| [OC-01](#oc-01) | P0 | Prevent exports overwriting application storage | [OC-00](#oc-00) |
| [OC-02](#oc-02) | P0 | Preserve excluded Nobody state during import/reset | [OC-00](#oc-00) |
| [OC-03](#oc-03) | P0 | Enforce a complete, typed import contract | [OC-00](#oc-00) |
| [OC-04](#oc-04) | P0 | Enforce credential rules at existing storage boundaries | [OC-03](#oc-03) |
| [OC-05](#oc-05) | P1 | Make expected storage/read failures recoverable | [OC-03](#oc-03) |
| [OC-06](#oc-06) | P1 | Recover invalid preferences and report save failures | [OC-00](#oc-00) |
| [OC-07](#oc-07) | P1 | Bound local-data work and keep the GUI responsive | OC-01–05 |
| [OC-08](#oc-08) | P1 | Harden theme file handling and saved-theme state | OC-01, OC-06 |
| [OC-09](#oc-09) | P1 | Correct empty-session restoration | [OC-05](#oc-05) |
| [OC-10](#oc-10) | P1 | Make current session/private lifecycle explicit | OC-02, OC-09 |
| [OC-11](#oc-11) | P1 | Make the existing composer usable for long drafts | [OC-10](#oc-10) |
| [OC-12](#oc-12) | P1 | Render existing message text safely and accessibly | OC-05, OC-09 |
| [OC-13](#oc-13) | P1 | Finish shell and floating-tool interaction | [OC-06](#oc-06) |
| [OC-14](#oc-14) | P1 | Align navigation and commands with actual capabilities | OC-10, OC-13 |
| [OC-15](#oc-15) | P1 | Complete keyboard, focus and responsive layout checks | OC-08, OC-11–14 |
| [OC-16](#oc-16) | P1 | Finish theme and appearance consistency | OC-08, OC-15 |
| [OC-17](#oc-17) | P1 | Verify animation lifecycle and measure performance | OC-06, OC-13, OC-16 |
| [OC-18](#oc-18) | P1 | Bound feedback and retain usable error details | OC-05, OC-15 |
| [OC-19](#oc-19) | P1 | Complete shutdown and retained-resource cleanup | OC-07, OC-10, OC-17–18 |
| [OC-20](#oc-20) | P2 | Consolidate ownership and document changed boundaries | Throughout; close after OC-19 |
| [OC-21](#oc-21) | P2 | Add reproducible CI and truthful validation output | OC-00; CI scaffold can start early |
| [OC-22](#oc-22) | P2 | Repair packaging and provide a Fedora launch path | OC-19–21 |
| [OC-23](#oc-23) | P2 | Complete scoped native acceptance and closeout | OC-01–22 |

<a id="oc-00"></a>

### OC-00 — Establish the implementation baseline

**Current state:** documentation consolidation is complete. Runtime fixes and
reference-media recovery are still pending; this task is not fully accepted.

**Work**

1. Recheck `main` and PR #6 before coding. Review #6 against OC-01–04 and preserve
   its nested-JSON validation fix. Identify the existing base and R2 candidate
   to fix; land that code only after OC-01–04, review and checks.
2. Use isolated SQLite/QSettings, record the exact commit/environment, and run the
   complete automated suite and offscreen smoke without skipped Qt coverage.
3. Locate supplied original visual references. `docs/reference/` is absent from
   the reviewed source. Restore originals or record their real accessible
   location; keep parity checks blocked if unavailable. Do not invent references.
4. Update STATUS and the evidence ledger with the selected source and actual
   results. The historical R1 defects already fixed on main must not be reopened
   merely because an old review still describes them.

**Accept when:** the reviewed base and R2 candidate are identified, with current
checks, known defects, reference availability and remaining native gates explicit.
Baseline identification permits OC-01–04 to begin; it does not claim those fixes
are already complete.
**Maps to:** governance, 01, 54, 55.

<a id="oc-01"></a>

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

<a id="oc-02"></a>

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

<a id="oc-03"></a>

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

<a id="oc-04"></a>

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

<a id="oc-05"></a>

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

<a id="oc-06"></a>

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

<a id="oc-07"></a>

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

<a id="oc-08"></a>

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

<a id="oc-09"></a>

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

<a id="oc-10"></a>

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
4. Reuse the session ownership contract below. Keep unsent drafts transient
   across process restart unless the canonical scope is intentionally changed.

**Accept when:** normal/private transitions are usable with pointer and keyboard
after messages exist; repeated transitions, New Chat and reset/import preserve or
dispose exactly the intended records. No private content reaches ordinary data,
export, diagnostics or future persistent search. **Maps to:** 03, 06, 47.

<a id="oc-11"></a>

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

<a id="oc-12"></a>

### OC-12 — Make existing message rendering explicit and safe

**Evidence:** local messages are passed directly to `QLabel` with default
`AutoText`; text format, copy policy and keyboard selection are not explicit.
This is a rendering trust-boundary observation, not evidence of script execution.

**Work**

1. Render existing user text as literal plain text, including HTML-looking input.
   Set format deliberately for user-supplied titles and feedback too. Introduce
   sanitized rich content only through SC-4 below.
2. Add keyboard selection/copy and visible role/time presentation without deriving
   state from widget text. Keep stored content unchanged by presentation.
3. Verify long unbroken text, code-like text, bidirectional text and a 200-message
   fixture. Preserve reading position; scroll only while following the end.
4. Make rebuild/reopen ordering deterministic and avoid accumulating deleted
   message widgets or losing the draft during a view refresh.

**Accept when:** markup displays literally, no user text triggers resource loading,
copy returns the intended displayed content, and the 200-message fixture stays
usable within PLAN's interaction target. Sensitive spans, status fixtures and
streaming belong to SC-4/SC-6 below; do not claim them complete. **Maps to:** 10, 53.

<a id="oc-13"></a>

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

<a id="oc-14"></a>

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

<a id="oc-15"></a>

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

<a id="oc-16"></a>

### OC-16 — Finish theme and appearance consistency

**Work**

1. Check all 16 presets on mounted and newly opened surfaces. Review Light,
   Copper, Ocean and Forest in matched states against available originals.
2. Verify every semantic token and More Colors control, picker cancel, preset
   reset semantics, neutral-input harmony preview/apply/reset and live updates.
3. Verify all currently implemented Appearance toggles preserve session/draft
   state and restart correctly. Keep Sensitive blur unavailable until step 48 has
   a renderer/copy policy; Web/Shell visibility activation follows CU-5/CU-6.
4. Check Frosted's documented translucent fallback for legibility. Consolidate
   literal styling only where it defeats semantic tokens or live typography.

**Accept when:** native visual/restart checks meet the selected requirements and
intentional reference differences are recorded. Steps with deferred consumers
remain Partial. **Maps to:** 32–35, 37, 47.

<a id="oc-17"></a>

### OC-17 — Validate animation lifecycle and performance

**Work**

1. Reuse PR #6's paint/frame instrumentation after its corrected implementation is integrated. Check ten effects, resize/switch,
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

<a id="oc-18"></a>

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

<a id="oc-19"></a>

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

<a id="oc-20"></a>

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
task's definition of done, with a final consistency pass. **Maps to:** [architecture contracts](docs/ARCHITECTURE.md).

<a id="oc-21"></a>

### OC-21 — Make verification reproducible and truthful

**Evidence:** no `.github` workflow is tracked. The smoke prints “native” even
when explicitly run offscreen; unit tests can skip Qt cases when PySide6 is absent.

**Work**

1. Add CI for the supported Python/Qt combinations, isolated full unittest suite
   and offscreen smoke. OC-22 adds the installed-package check to this pipeline.
   Make missing required Qt coverage
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

<a id="oc-22"></a>

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
5. Add the installed-package smoke to OC-21's CI pipeline. Build and launch from
   outside the checkout so source imports cannot hide omitted runtime packages.

**Accept when:** wheel/sdist contents are checked, an isolated installed build
starts, and native Fedora launcher/startup/error behavior is recorded.
**Maps to:** 01, scoped 55.

<a id="oc-23"></a>

### OC-23 — Complete native acceptance and close out the selected scope

**Work**

1. Run the shared acceptance gate below against the final corrected
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

## Sessions and local conversation

These packages incorporate the former SC plan. Baseline and general privacy,
empty-view, literal-text and native fixes have one owner in OC; the SC packages
extend those contracts into actual session workflows. SC-0 is absorbed by OC-00;
SC-7 is absorbed by the shared gate. No generated response or provider is required.

| Package | Depends on | Deliverable |
|---|---|---|
| SC-1 | Corrected OC baseline, especially OC-03–05/09–10 | Session repository/service CRUD and migration |
| SC-2 | SC-1, CU-1, OC-13–15 | Session browser and commands |
| SC-3 | SC-2, OC-10/19 | Privacy integration across browser/search-ready contracts |
| SC-4 | SC-1–3, OC-12/18–19 | Typed rich/code/tool fixture renderers and deterministic streaming |
| SC-5 | SC-2–4, OC-05/07/14 | Persistent local history search |
| SC-6 | SC-3–5, OC-12/16/18 | Sensitive spans and supplied process/status presentation |

<a id="sc-1"></a>

### SC-1 — Session repository and service lifecycle

**Work:**

1. Extend the existing `SessionRepository`/`SessionService` with create/get/list,
   rename, favourite/unfavourite, archive/restore and delete; widgets never issue
   SQL. Use explicit not-found/validation/store errors and transactional mutation.
2. Add a dedicated favourite query field with an atomic migration if needed;
   preserve IDs/timestamps/messages and extend import/export plus prior-schema
   migration fixtures. Do not hide core sort fields in opaque metadata.
3. Validate blank/overlong titles and documented whitespace normalization. Define
   deterministic ordering by favourite/update time/stable ID, archived filtering,
   and monotonic message ordering. Archive is reversible; delete needs confirmation
   or an explicitly bounded undo policy. Deleting a session removes its messages.
4. Keep Nobody operations memory-only. Archive/favourite must reject private
   records rather than imply persistence. Use one lifecycle contract and return
   copies/immutable records to consumers where appropriate.

**Accept when:** CRUD, ordering, migration, exact import/export, restart,
not-found and injected-write rollback tests pass; no private operation writes
SQLite or export. **Feature IDs:** 10, 54.

<a id="sc-2"></a>

### SC-2 — Session browser and Home integration

**Work:**

1. Use CU-1's shared anchored popover for the chat-title browser. Show title,
   updated time, favourite/storage state and a separate archive view/filter.
2. Provide selection, rename, favourite, archive/restore and confirmed delete by
   keyboard and pointer. Escape/outside click restores trigger focus. Enable
   Favourite/Delete commands only when valid and display current bindings.
3. Use the shared draft/lifecycle contract: save before switching, restore only
   the selected draft, and retain the outgoing view on failed loading. Reuse
   OC-09's empty renderer and OC-10's New Chat behavior.
4. Keep Home/composer centered as the sidebar changes. Preserve a layout assertion
   for the later Notes dock; do not implement a fake dock to close step 03.

**Accept when:** normal, empty, populated, archived, deleted and failed-load
sessions navigate without mixing/losing drafts; commands reflect current state.
Step 03's Notes-dock criterion remains open. **Feature IDs:** 03, 10, 50.

<a id="sc-3"></a>

### SC-3 — Privacy integration for session workflows

**Work:**

1. Integrate OC-10's persistent indicator, explicit transition choice and Close
   Nobody operation into the browser. Reuse its implementation; this package
   verifies newly introduced consumers rather than recreating the mode controller.
2. Ensure persistent browser/history/export providers cannot enumerate private
   collections. Errors, diagnostics and derived snippets must not include private
   content. Restart must restore none of its title/text/draft/status.
3. Exercise pending/live private sessions, switch-and-retain/new/cancel, explicit
   close, New Chat, failed load and durable-data replacement. Define consumer
   tests for later CU attachments and Brain extraction to re-run.

**Accept when:** browser and service integration enforce the lifecycle table by
pointer/keyboard, private data remains excluded, and later-consumer gates are
recorded rather than presumed passed. **Feature IDs:** 06, 10, 54.

<a id="sc-4"></a>

### SC-4 — Safe renderers and deterministic streaming

**Work:**

1. Define validated presentation metadata for role, timestamp, fixture kind,
   language/code, status and later sensitive spans. Render user, assistant
   fixture, system/tool, code and status records through reusable components.
   Keep OC-12's literal user text; sanitize/escape supported rich content, forbid
   embedded resource execution/loading, and label demo provenance clearly.
2. Provide selection/copy/timestamps and accessible roles/names. Treat stored
   message identity/order independently of widget state and provider execution.
3. Add deterministic pending/running/completed/failed/cancelled streaming.
   Separate partial presentation from durable results; only accepted terminal
   fixture output may be persisted. Failure/cancel never creates a completed
   assistant record. Retry uses a new operation ID; stale/duplicate completion
   cannot alter another session or duplicate output.
4. Reuse per-session scroll-follow and expansion state: follow only while the
   user is at the end, never pull them away from earlier messages. Exercise a
   200-message mixed fixture with bounded widget/cache ownership and safe reopen.

**Accept when:** all fixture roles and stream outcomes work without network/model
execution, exact ordering survives restart, and selection/copy/scroll meet the
shared interaction targets. **Feature IDs:** 10, 53.

<a id="sc-5"></a>

### SC-5 — Persistent local history search

**Work:**

1. Add a local search-provider contract over persistent session titles/message
   text through repositories/services. Private collections are structurally
   unavailable. Exclude archived records by default with an explicit filter.
2. Return stable result/source/session/message IDs, safe snippets, timestamps and
   match location. Opening a result selects the right session and highlights or
   scrolls to the match without changing its content/draft.
3. Debounce queries with generation IDs. Cover empty query, searching, results,
   no matches, failure/retry and stale completions after query/session changes.
4. Ctrl+F opens/focuses search; arrows/Enter activate, Escape restores focus.
   Measure 1,000 searchable records against the shared warm-search target; use
   the existing bounded-work pattern if I/O would block the GUI.
5. Define the typed Library-provider extension; connect real Library metadata/
   content when 27/28 exist. Do not insert fake Library results.

**Accept when:** local history search and private exclusion pass service/UI/native
checks; canonical 11 remains Partial until Library integration. **Feature IDs:** 11, 50.

<a id="sc-6"></a>

### SC-6 — Sensitive spans and supplied process/status views

**Work:**

1. Validate explicit non-overlapping, in-bounds sensitive spans with semantic
   labels; reject malformed ranges safely. Use synthetic fixture values only.
2. Conceal marked values by default with intentional accessible reveal/conceal.
   Copy/export defaults to concealed text; original-copy, if supplied, requires
   an explicit clearly explained action. No concealed original reaches tooltips,
   accessibility labels, selection previews or logs. Unmarked text is unchanged;
   the GUI does not claim general secret detection.
3. Define the relationship between presentation export and local-data backup
   explicitly. Backup/import must not bypass the structured-credential policy;
   do not silently corrupt message identity or indices when redacting content.
4. Separate truthful session-storage status from expandable supplied process
   entries. Support pending/running/completed/failed/cancelled with timestamps,
   accessible announcements and adapter/fixture-supplied summaries only. Do not
   invent or label content as hidden model reasoning.
5. Preserve scroll on expand/collapse. Hiding summaries changes presentation,
   not data. Keep private statuses/spans in memory and dispose with their session.
6. Enable the corresponding Appearance controls only after their renderer and
   copy/visibility policy pass; update existing messages live and on restart.

**Accept when:** conceal/reveal/copy/accessibility tests and native checks pass,
status fixtures are truthful, and privacy holds across the new consumers.
**Feature IDs:** 48, 49 and the corresponding portion of 47.

## Local composer utilities

These packages absorb the former CU plan. Build CU-0/CU-1 before SC-2 to avoid
separate session and composer popovers. CU-7's closeout is the shared gate.

| Package | Depends on | Deliverable |
|---|---|---|
| CU-0 | Corrected OC baseline; session ownership contract | Selection/action limits and no-I/O contracts |
| CU-1 | CU-0, OC-13–15 | Shared anchored popup/focus primitive |
| CU-2 | SC-1–3, CU-0, OC-10/19 | Session-owned transient attachment/workspace aggregate |
| CU-3 | CU-1/2, OC-11/15 | Native file/folder selection and accessible chips |
| CU-4 | CU-3 | Typed Documents/Prompt entry contracts; honest unavailable gates |
| CU-5 | CU-0/3, OC-14/16 | Registry-backed composer actions |
| CU-6 | CU-5, SC-4, OC-18/19 | Deterministic Web/Shell simulations |

<a id="cu-0"></a>

### CU-0 — Selection and simulation contracts

**Work:**

1. Define documented maximum attachment count/per-file size, supported types,
   unreadable/stale-file behavior and error policy before UI implementation.
2. Specify an immutable draft-local descriptor: generated ID, display name,
   canonical path, kind/MIME, size, source and availability. Absolute paths and
   content stay transient; no SQLite/QSettings/export/log/search persistence.
3. Workspace selection stores one transient directory descriptor. No recursion,
   indexing, file-content reads, watching, symlink traversal or execution occurs.
4. Define distinct action IDs, order, preference mapping and simulated wording.
   Add targeted test seams that reject network and subprocess calls.
5. Until step 04 can accept attachment descriptors in a submission, attachment-
   bearing Send must explain unavailability and retain the aggregate. It must
   neither silently clear selections nor claim their contents were consumed.

**Accept when:** limits and contracts are concrete and shared, without opening
model request/tokenization/provider work. **Feature IDs:** 07, 08, partial 04.

<a id="cu-1"></a>

### CU-1 — Shared anchored popover

**Work:**

1. Accept an anchor and injected content; contain no business state. Choose
   above/below placement and clamp to workspace bounds as anchor/host/scale moves.
2. Define keyboard/pointer opening, first enabled focus, Tab/Shift+Tab, list arrows,
   Enter/Space, Escape/outside click and trigger-focus return.
3. Keep one active composer popup; replacement/toggling/anchor destruction,
   application deactivation and tool minimize must remove event filters and never
   leave an invisible input blocker. Reuse the primitive for SC-2.
4. Expose accessible name/role/item state and disabled reasons. Test edges/corners,
   resize, focus return, destroyed anchors and repeated lifecycle cycles.

**Accept when:** deterministic geometry/lifecycle checks and native pointer/focus
checks pass; no orphan widget/filter/signal remains. **Feature IDs:** 07, 10.

<a id="cu-2"></a>

### CU-2 — Session-owned selection drafts

**Work:**

1. Extend the existing text/mode aggregate with ordered attachments and optional
   workspace. A presentation-neutral controller owns add/remove/clear/replace/
   mark-unavailable operations; reorder only if exposed.
2. Preserve draft-local identity when filenames duplicate. Detect duplicate
   canonical paths within a draft with a visible explanation.
3. Apply the lifecycle table to concrete/pending normal and private states. A
   later edit cannot be cleared by stale acceptance; failed storage preserves
   text, mode, chips and workspace together.
4. Private close/New Chat/shutdown disposes all references. Durable-data reset/
   import preserves its excluded private aggregate. No selection path/name leaks
   through exports, history, diagnostics or future persistent search.

**Accept when:** switching/failure/stale completion/disposal tests cover all four
pending/live privacy states with no new durable schema for selections.
**Feature IDs:** 06, 07, partial 04.

<a id="cu-3"></a>

### CU-3 — Tool menu, files and workspace selection

**Work:**

1. Add an accessible tool-menu trigger and typed Attach Files, Documents,
   Workspace and Prompt items with truthful enabled/disabled states.
2. Use native multi-file selection; cancellation is a strict no-op. Validate
   readable regular files under CU-0 limits with per-file accepted/rejected
   feedback. Inspect only minimum metadata/type; do not parse contents.
3. Render removable chips with name/type/size/availability and keyboard removal.
   Handle long Unicode names without exposing unnecessary paths; bounded wrapping/
   scrolling must preserve editor, mode and Send at minimum size/Large/Roomy.
4. Workspace uses a directory picker with change/remove and a selected-only,
   not-scanned/executed explanation. Missing/stale paths offer remove/reselect,
   without automatic reads or retry loops.
5. Opening tools, closing the popup or changing routes preserves the aggregate.

**Accept when:** happy/cancel/invalid/oversize/unsupported/unreadable/stale cases
work by pointer and keyboard and selections are never sent/persisted/executed.
**Feature IDs:** 07.

<a id="cu-4"></a>

### CU-4 — Documents and Prompt integration contracts

**Work:**

1. Define a document-picker provider returning stable document IDs/display
   metadata from the shared document service. Do not create a second store.
2. Provide stable Documents and Prompt route/command contracts. Until actual
   modules exist, show precise unavailable reasons; no fake editor/picker counts.
3. Add contract checks so 27/28 and later 09 can enable these entries without
   replacing the popup or draft APIs. Revalidate real module opening at that time.

**Accept when:** integration contracts and honest current states work. Step 07
remains Partial for real Documents/Prompt consumers. **Feature IDs:** 07, 09, 27, 28.

<a id="cu-5"></a>

### CU-5 — Composer action registry

**Work:**

1. Define pure immutable action specs: stable ID, label, icon, order, preference,
   availability/reason and handler key. Reject duplicates/order collisions and
   missing handlers; render buttons/menu items from the registry.
2. Use `composer.web_search_demo` and `composer.shell_demo` distinct from
   `navigation.search` or general Tools. Use canonical handlers where global
   commands are exposed and composer scope for local controls.
3. Recompute visibility live without deleting fixture state; restore documented
   preferences on restart. Unknown actions fail closed with an explanation.

**Accept when:** adding an action needs no layout edit, identity/handler tests
pass, and visibility never implies a real unavailable operation. **Feature IDs:** 08, 47, 50.

<a id="cu-6"></a>

### CU-6 — Deterministic Web and Shell simulations

**Work:**

1. Use dedicated local adapters for loading/success/empty/failure/cancellation.
   Retry uses a new operation ID; stale or duplicate completions are ignored.
2. Web output is fixed fixture results/citations labelled “Simulated — no web
   request was made.” Do not fetch arbitrary URLs. Shell output is fixed fixture
   command/output labelled “Simulated — no command was executed.” Never pass
   user text to a subprocess or terminal.
3. Render in an explicit demo/status surface, not an apparent live assistant
   answer. Cancel/error retains the full draft and important errors remain
   accessible through shared feedback.
4. Guard network/process boundaries in tests. After consumers pass, enable only
   their corresponding Appearance controls with simulated wording; verify
   live/restart/reset behavior and private output disposal.

**Accept when:** every scenario and no-I/O assertion has evidence; no action
implies real execution. Accept the local 08/47 subset and retain broader gates
listed above. **Feature IDs:** 08, 47, 53.

## Shared acceptance gate

One gate replaces FD-6/7, SC-7 and CU-7. Apply it first under OC-23 for the current
foundation and then to the changed feature subset after Sessions, Composer and
later areas. Reuse valid evidence for unchanged contracts; rerun affected native
cells after fixes. Do not repeat all foundation work merely because a new area
starts. One failed cell keeps its criterion open.

### Automated and integration checks

1. Use isolated data/settings and one identified source revision. Run relevant
   focused regressions, the complete Qt-enabled suite without skips, offscreen
   smoke and, once OC-22 exists, installed-package smoke. Record actual platform.
2. Exercise applicable success, empty, invalid, loading, failure, cancellation,
   retry and stale-result behavior. Preserve drafts on failure; reject duplicate
   completion and dangerous data destinations. Restart/migration/import/export
   must preserve supported IDs, order and relationships.
3. After SC, cover fresh/empty/populated/archived/deleted/failed-load sessions,
   normal/private transitions, browser commands, copy/reveal/status and search.
   After CU, cover pending/live normal/private full aggregates, cancelled native
   picks, mixed accepted/rejected files, stale paths and no-I/O simulations.
4. Attachment-bearing Send remains unavailable until its request contract exists;
   no silent clearing/consumption. Private selections/status never enter ordinary
   data, exports, logs or search. Revalidate with each later privacy consumer.
5. Review all materially changed code for AGENTS.md documentation and architectural
   ownership. Resolve defects without weakening assertions or thresholds.

### Required fixture inventory

| Area | Fixtures |
|---|---|
| Foundation/data | Fresh/saved preferences; fresh/populated/corrupt/unavailable stores; valid/invalid/nested-malformed/future/incomplete exports; protected destinations; duplicate/constraint and encoding failures |
| Windows/themes | Two overlapping tools with distinct normal/minimized geometry; all 16 presets and ten effects; paused/Solid; long saved-theme lists; valid/duplicate/malformed/unwritable theme bundles |
| Sessions | Pending/live normal/private; zero-message and 200 mixed messages; archived/deleted/failed-load; explicit sensitive spans and all stream/status outcomes; 1,000 searchable records |
| Composer | Empty/text/file/mixed draft; duplicate filenames and canonical paths; Unicode/long/unsupported/oversized/unreadable/missing/directory-as-file; selected folder with nested/symlink/executable-looking entries to prove no scan/execution |
| Lifecycle | Repeated tool/theme/session transitions; reset/import while private or drafting; close during animation/demo/data work; saved restart; stale callbacks |

### Native desktop matrix

| Dimension | Required evidence for the selected scope |
|---|---|
| Desktop | Fedora 44 KDE Wayland and GNOME Wayland; explicitly scope out unsupported environments instead of claiming an unrun pass |
| Scaling | 100%, 150%, 200%; record actual available logical screen bounds |
| Window/layout | 1100×680, default working size and maximized; Small/Default/Large × Compact/Comfortable/Roomy for affected surfaces |
| Theme | Light, Copper, Ocean, Forest and any preset affected by a defect |
| Input/accessibility | Pointer, keyboard-only traversal, accessible names/status, focus visibility/return, ordinary editing, selection/copy, applicable drag/drop |
| Native dialogs | File/directory/color dialogs, confirmation/cancel, error detail and startup recovery |
| Lifecycle | Minimize/hide/reactivate, display-size change, tool reopen, private close, application shutdown/restart |

Run `scripts/fedora_phase_a_check.sh` from the supported native session. Verify
the actual Qt platform; inherited offscreen must not count as native. Execute the
checklist and record results; merely printing it is not evidence. Inspect original
reference captures at matched theme/sidebar/window/tool state, using Copper/Ocean
detail and Forest home/background. Document intentional native differences.
Missing originals remain a named parity blocker.

### Performance and bounded resource targets

These original PLAN targets are retained:

- After warm-up, local search over 1,000 supported records returns within 300 ms;
  ordinary selection/tab changes respond within 100 ms. Expensive I/O/processing
  shows prompt progress and does not block the GUI event loop for more than 100 ms.
- Conversation fixture: 200 mixed prose/code messages. Later Gallery fixture:
  500 photos with cached thumbnails. Later editor fixture: 2048×2048, five layers.
- Animation: 60-second trace at 1720×900, Balanced quality, approximately 60 FPS
  with p95 frame interval ≤33 ms on a recorded reference machine. Retain Leaves
  plus the slowest-effect trace. Profile failures or ship an explicit tested
  fallback; do not silently lower the threshold.
- Repeat open/close for ten tools and twenty session/theme switches. Widgets,
  timers, jobs, decoded-image caches and history must have documented bounds;
  reaching a bound must not corrupt the current document or draft.

Record measurement method, warm-up, samples, p95 where applicable, hardware,
driver, scale, Qt and source. Offscreen timer measurements are instrumentation
checks, not compositor or native frame-rate acceptance.

### Evidence and closeout

Store curated evidence under `docs/acceptance/evidence/<date>-<area>/`: source/
environment manifest, automated log including skips, actual native checklist,
performance result and needed captures. Maintain short linked acceptance records.
Keep supplied originals separate from generated evidence.

Update this plan's checkboxes only for executed criteria, plus STATUS, ROADMAP,
CHANGELOG and the acceptance ledger. Preserve partial gates for Notes layout,
Library, Prompt, attachments, extraction and model/request consumers. No new
manual acceptance is created by this documentation consolidation.

A release requires every selected feature to meet this gate and its catalogue
criteria, or an explicit revision listing deferred feature IDs and unsupported
environments. All 55 remain the long-term scope; the current non-model milestone
is not a completed full-product release. Tag/publish only the evidenced revision
under the intended release authorization; never move an existing acceptance tag.

## Feature steps and acceptance conditions

The following catalogue is normative. Original feature IDs, dependencies,
deliverables and acceptance checkbox text are preserved. See the execution order
and completion-boundary tables for the selected non-model slices; see STATUS and
the acceptance ledger for actual implementation/evidence. Stale per-feature
review observations are available in the original revision, not repeated here.

### 01. Application shell

Depends on: 54
Deliverable: MainWindow, service/state ownership, route registry and layered workspace; main.py remains an entry point.
Done only when:

- [ ] Application starts with isolated fresh preferences and with saved preferences; opening a tool preserves the current chat and composer draft.
- [ ] Every exposed route resolves to its intended component or an explicitly labelled unavailable state; feature logic is kept out of main.py.
- [ ] Resizing between 1100×680 and 1920×1080 logical pixels leaves navigation and primary controls reachable.

### 02. Collapsible sidebar

Depends on: 1, 47, 50
Deliverable: Expanded and icon-only navigation driven by canonical commands and visibility preferences.
Done only when:

- [ ] Collapse/expand animates without losing active route, tool state or draft; rapid repeated toggles finish at the requested width.
- [ ] Every icon-only action has a tooltip and accessible name; Settings/account remain reachable when collapsed.
- [ ] Active state, optional entries and badges reflect application state; width and visibility restore after restart.

### 03. Home / empty session

Depends on: 10
Deliverable: One session view whose empty state contains brand, welcome text, Nobody control and composer.
Done only when:

- [ ] A session with zero messages displays the welcome state; the first message replaces it with conversation content.
- [ ] New Chat creates a separate empty session and opening an existing session restores its contents; hidden welcome preferences apply immediately.
- [ ] The hero and composer remain centered within the available workspace, including when the sidebar or Notes dock changes width.

### 04. Chat composer

Depends on: 5, 7, 8, 10, 50
Deliverable: Reusable multiline composer with bounded autosizing, model selection, Agent/Chat mode and send state.
Done only when:

- [ ] Input grows to a documented maximum height then scrolls; long text and pasted multiline text do not cover controls.
- [ ] Ctrl+Enter sends, Enter inserts a newline, and empty/whitespace-only submission is rejected; shortcut help matches behavior.
- [ ] Selected model, mode and attachments are included in the local submission record; unavailable selections give an actionable state.
- [ ] A failed persistence/submission operation retains the complete editable draft and attachments, reports the error and supports retry without duplicate messages.
- [ ] Submission clears the accepted draft once; switching sessions restores each draft. Mock responses and cancellation work without network access.

### 05. Model selector

Depends on: 40, 41, 53
Deliverable: Anchored model popover consuming the shared model registry.
Done only when:

- [ ] Empty, loading, available, offline and failed-refresh states can be reached with deterministic fixtures.
- [ ] Selection updates the composer and session state; refresh keeps a valid selection and removal clears an invalid one.
- [ ] Add Model opens the shared configuration flow; keyboard navigation, Escape and outside-click dismissal work.

### 06. Nobody / incognito session

Depends on: 10, 54
Deliverable: Session-level no-history/no-memory mode, visibly distinguished from normal sessions.
Done only when:

- [ ] Creating an incognito session displays a persistent indicator and a tooltip explaining local GUI behavior.
- [ ] Its messages, drafts and attachments are excluded from persisted history, search indexes, memory extraction and diagnostic content; restart does not restore them.
- [ ] Normal/private mode transitions render only the newly active session; indicators and status summaries describe its actual persistence state.
- [ ] Changing mode after messages exist has an explicit transition choice and never silently saves private content; closing the session clears its transient state.

### 07. Composer tool menu and attachments

Depends on: 1, 28, 53
Deliverable: Shared anchored popover primitive, Attach Files, Documents, Workspace and Prompt entry points.
Done only when:

- [ ] Popover repositions within workspace bounds, accepts keyboard input, dismisses on Escape/outside click, and returns focus to its trigger.
- [ ] Native file selection adds removable attachment chips with filename/type; cancellation leaves the draft unchanged and unreadable files show an error.
- [ ] Documents and Prompt open their actual modules; Workspace selects a local context folder and displays that choice without executing files.

### 08. Optional composer actions

Depends on: 7, 47, 50
Deliverable: Command-backed action registry for web search, shell and additional composer tools.
Done only when:

- [ ] Each action has a stable ID, label, icon, enabled state and handler; adding an action does not require composer layout changes.
- [ ] Appearance toggles add/remove the corresponding action immediately and survive restart.
- [ ] Web and shell actions show clearly labelled simulated results in this milestone; cancellation/error states work and no real shell command or search request is executed.

### 09. Prompt Studio

Depends on: 5, 7, 54
Deliverable: Inject, Persona and Group tabs backed by persistent prompt configuration.
Done only when:

- [ ] Prefix/suffix, temperature and token limit validate before apply; invalid numeric values explain the supported range.
- [ ] Personas can be created, selected, edited and deleted; group participants can be added, removed and reordered with sequential/group mode.
- [ ] Applied configuration is visible in the session and used by the mock request builder; closing/reopening and restarting preserve saved definitions while Cancel discards uncommitted edits.

### 10. Sessions and message rendering

Depends on: 1, 53, 54
Deliverable: Local session/message model and reusable user, assistant, system/tool, code and status views.
Done only when:

- [ ] Create, reopen, rename, favourite, archive and delete sessions through the shared model; destructive actions use confirmation or undo.
- [ ] User, assistant, code and tool/status fixtures render with selection, copy, timestamps and consistent state indicators; rich text cannot execute embedded code.
- [ ] Simulated streaming can complete, fail and cancel; scrolling stays at the bottom only while the user is following it and does not jump away from older messages.
- [ ] A 200-message fixture remains usable and persisted normal sessions reopen with correct ordering; storage/rendering are separated from provider execution.

### 11. Search

Depends on: 10, 27, 50
Deliverable: Search overlay using a replaceable local search provider.
Done only when:

- [ ] Search matches session titles and message text plus supported Library metadata/content; results identify their source and open the correct item.
- [ ] Empty query, no matches, searching and provider failure states work; editing queries cannot display stale results.
- [ ] Ctrl+F opens and focuses search, arrows/Enter activate results, Escape restores focus; incognito content is never returned.

### 12. Email

Depends on: 44, 53, 54
Deliverable: Mailbox list/detail, account/filter controls, tags, compose and local draft state.
Done only when:

- [ ] Fixture inbox supports selection, search, account/filter changes, tags and readable message details without losing the selected item unexpectedly.
- [ ] Compose validates recipients and required fields, stores local drafts and preserves them across reopen/restart; discard is explicit.
- [ ] Refresh, loading, empty and failure states are exercisable; Send creates a labelled simulated sent item and never transmits mail.

### 13. Brain — Memories

Depends on: 53, 54
Deliverable: Memory cards and local CRUD with search, sorting, selection and enabled state.
Done only when:

- [ ] Create, edit, delete, enable/disable and select memories; search and sort operate on the same persisted records.
- [ ] Bulk operations affect only selected records; disabled memories are excluded from simulated injection.
- [ ] Tidy previews proposed deduplication/cleanup and requires application of that preview; cancel preserves all entries.

### 14. Brain — Skills

Depends on: 13
Deliverable: Skill records with confidence, tags, instructions and enabled/audit state.
Done only when:

- [ ] Skills can be edited, searched, sorted by confidence and enabled/disabled with persistent results.
- [ ] Mock audit shows pending/running/completed/failed states and a readable result; no actual capability or verification is claimed.
- [ ] Disabled or unapproved skills are excluded from injection; selecting a skill exposes its trigger and instructions.

### 15. Brain — Add / import / export

Depends on: 13, 14
Deliverable: Validated memory and skill forms plus versioned JSON interchange.
Done only when:

- [ ] Manual memory and skill forms validate required title/when/how fields as appropriate and normalize tags.
- [ ] Export then import into an empty store preserves supported fields; duplicate handling offers a clear skip/replace/copy choice.
- [ ] Malformed or unsupported files show a readable error without partial store corruption; cancelling a picker or preview leaves records untouched.

### 16. Brain automation preferences

Depends on: 6, 14, 15
Deliverable: Persistent extraction/approval thresholds and injection limits for the demo pipeline.
Done only when:

- [ ] Auto-extract memory/skills, auto-approve, confidence threshold and injection count have documented defaults, valid ranges and saved values.
- [ ] A deterministic normal-session fixture demonstrates each toggle and threshold, including rejection below threshold and the maximum injection count.
- [ ] Incognito sessions bypass extraction and persistence regardless of preferences; the interface identifies extraction as simulated.

### 17. Calendar

Depends on: 44, 53, 54
Deliverable: Local calendars, month/week/day views, event editing and local .ics import; CalDAV configuration only.
Done only when:

- [ ] Create/rename calendars and create/edit/delete dated, timed and all-day events; calendar visibility updates every view.
- [ ] Navigation handles month/year boundaries and local timezone/DST fixtures without moving events to the wrong date.
- [ ] Import supported basic .ics VEVENTs with preview and duplicate handling; unsupported recurrence or fields are reported rather than silently dropped.
- [ ] Empty calendar, invalid import and mock CalDAV failure states are usable; local events survive restart.

### 18. Model Compare

Depends on: 5, 10, 54
Deliverable: Comparison setup and results using deterministic mock model runners.
Done only when:

- [ ] Two or more model slots accept a prompt and Chat/Agent/Search/Research mode; timeout and cancellation end pending runs visibly.
- [ ] Parallel results, blind identity hiding, reveal and shuffle behave consistently; scoring updates a persistent scoreboard without duplicate votes.
- [ ] Continue uses the selected result as context, Save creates a Library item, and Reset clears the run after protecting unsaved results; all answers are labelled demo output.

### 19. Cookbook

Depends on: 41, 53, 54
Deliverable: Local-model management console with Launch, Download, Dependencies and Settings tabs.
Done only when:

- [ ] Cache fixtures show model identity, location, availability and state; selecting an entry populates the appropriate controls.
- [ ] Download, launch and dependency operations have deterministic progress, cancel, complete and failure states with retry.
- [ ] Configuration persists; all simulated operations are labelled and neither install packages nor download/execute models.

### 20. Deep Research

Depends on: 31, 42, 43
Deliverable: Research setup and local queued jobs producing demo reports.
Done only when:

- [ ] Prompt, rounds, format, engine, endpoint and model validate before a job can be queued.
- [ ] Queue/start/pause where supported/cancel/retry drive explicit job states without duplicate starts; progress survives reopening the view.
- [ ] A completed demo job writes one report to Research Library with its setup and completion metadata; cancellation/failure does not create a completed report.
- [ ] Generated sample text and sample citations are identified as mock content, not real research.

### 21. Gallery — Photos

Depends on: 53, 54
Deliverable: Local image import, thumbnail model/view, tags, filters, favourites and selection.
Done only when:

- [ ] File picker and drag/drop import supported raster formats; corrupt/unsupported files fail individually without losing valid imports.
- [ ] Search, source filter, sorting, favourites and bulk selection update the same metadata store and survive restart.
- [ ] Thumbnails load outside blocking UI work; a 500-image fixture scrolls without full-size decoding on every paint, and missing originals display a recovery state.
- [ ] Import/reference ownership and deletion behavior are explicit; removing a Gallery record never silently deletes the source file.

### 22. Gallery — Albums

Depends on: 21
Deliverable: Album records referencing imported photos.
Done only when:

- [ ] Create, rename and delete albums; add/remove photos by selection or drag/drop and show an accurate count/cover.
- [ ] One photo may belong to multiple albums; deleting an album preserves photos and other album memberships.
- [ ] Empty albums and missing photos are handled; membership and ordering survive restart.

### 23. Gallery editor foundation

Depends on: 21
Deliverable: Dedicated canvas/viewport and editor document architecture; QGraphicsView/Scene or an equivalent custom canvas.
Done only when:

- [ ] Open an imported image, zoom/pan/fit and map pointer positions correctly at multiple zoom levels and display scales.
- [ ] Canvas/document state is separate from tool widgets; an unsaved indicator and save/discard/cancel flow protect work on close or replacement.
- [ ] Save/reopen an editable project and export a flattened PNG with correct dimensions and alpha; failed/cancelled writes retain the document.

### 24. Gallery editing tools

Depends on: 23, 25
Deliverable: Move, Crop, Transform, Brush, Eraser, Clone, Lasso, Wand and Sharpen; adapter UI for AI-labelled tools.
Done only when:

- [ ] Move/crop/transform and brush/eraser/clone operate on the selected editable layer with visible previews and cancel/commit behavior.
- [ ] Lasso and Wand produce visible selections, respect image bounds and constrain applicable edits; Sharpen exposes a preview and strength.
- [ ] Every committed document edit supports undo/redo, including after zoom/pan; cancelled gestures create no history entry.
- [ ] SAM and background removal provide a complete selection/result preview flow using a clearly marked mock adapter; they never imply real AI processing.

### 25. Gallery layers and history

Depends on: 23
Deliverable: Independent layer model with pixel content, visibility, opacity, order, transforms and masks; command-based history.
Done only when:

- [ ] Add/duplicate/remove/reorder layers, rename them, toggle visibility, change opacity and attach/edit masks; rendered output follows the model.
- [ ] Undo/redo restores exact document state for each supported operation; a new edit after undo invalidates the redo branch.
- [ ] Save/reopen retains layer properties and masks; flattened export matches the current composite and transparent areas.
- [ ] History and decoded-image caches have documented bounds; reaching a bound does not corrupt the current document.

### 26. Inpaint workflow

Depends on: 24, 25, 42
Deliverable: Mask editor and preview/apply workflow with replaceable processing adapter.
Done only when:

- [ ] Paint/erase masks, change brush size, invert, clear and hide/show overlay without changing underlying pixels until Apply.
- [ ] Prompt, model, strength, generate/remove/outpaint mode and edge controls validate; outpaint updates canvas dimensions predictably.
- [ ] Mock processing supports progress/cancel/failure and preview/reject/apply; Apply is undoable and preserves other layers.
- [ ] Changing images or masks during a job cannot apply a stale result to the wrong document.

### 27. Library

Depends on: 10, 28, 54
Deliverable: Shared searchable item model for Chats, Documents, Research and Archive.
Done only when:

- [ ] Each tab uses consistent search, sorting, selection and empty/error states and opens the correct underlying item.
- [ ] Archive/restore/delete and bulk actions keep source modules synchronized; tidy previews changes before applying them.
- [ ] Persisted items retain stable IDs and category metadata; incognito sessions are excluded.

### 28. Documents

Depends on: 53, 54
Deliverable: Local plain-text/Markdown document import, editor and viewer.
Done only when:

- [ ] Create/import/open/edit/save supported text and Markdown files with title/content search and source metadata.
- [ ] Unsaved edits prompt save/discard/cancel; external write failure and unsupported encoding produce useful errors without losing editor text.
- [ ] Documents can be selected from the composer and Library; preview rendering does not execute embedded HTML or scripts.

### 29. Research Library

Depends on: 20, 27
Deliverable: Research category backed by completed research job artifacts.
Done only when:

- [ ] Each successful research job appears once with title, report, model/setup and date; incomplete jobs are absent from completed reports.
- [ ] Open/search/archive/restore/export a report through the shared Library operations.
- [ ] Reopening/restarting preserves report content and provenance; mock status stays visible in the viewer and exported document.

### 30. Notes dock

Depends on: 31, 54
Deliverable: Right-side dock with notes, list/grid modes, archive, pin, selection and reminder links.
Done only when:

- [ ] Dock open/close/resize adjusts the available workspace without covering essential composer controls; saved width and view mode restore.
- [ ] Create/edit/search/pin/archive/restore/delete notes in list and grid views; bulk actions use explicit selection.
- [ ] Notes persist and reminder metadata creates/updates one linked local task; deleting either side handles the relationship explicitly.

### 31. Tasks and local scheduler

Depends on: 46, 53, 54
Deliverable: Task state model plus Tasks, Activity, Completed and Add views; safe in-process demo execution.
Done only when:

- [ ] Create/edit scheduled demo tasks with timezone-aware due dates and validated recurrence; search and tab counts match stored states.
- [ ] Pending/running/completed/failed/cancelled transitions and activity records are deterministic; Pause All prevents new starts.
- [ ] Restart handles overdue tasks using a documented catch-up policy and never duplicates completion; paused and cancelled tasks do not run.
- [ ] Execution is limited to local demo handlers while the application is open; UI explains that background execution while closed is outside this milestone.

### 32. Theme presets

Depends on: 1
Deliverable: Sixteen semantic theme definitions consumed consistently by all widgets.
Done only when:

- [ ] Original, Light, Midnight, Paper, Cyberpunk, Retrowave, Forest, Ocean, Ume, Copper, Terminal, Organs, Lavender, GPT, Claude and Cute are selectable.
- [ ] Selecting a theme updates existing and newly opened windows, popovers, menus, scroll viewports and backgrounds immediately.
- [ ] No unstyled white viewport remains in dark themes; text, focus, selection and disabled controls remain readable in light and dark themes, and the selected preset survives restart.

### 33. Theme customization

Depends on: 32, 54
Deliverable: Editable semantic palette with live preview and persistent custom overrides.
Done only when:

- [ ] Background, panel, text, sidebar, border and accent plus the expanded token set update their intended surfaces immediately.
- [ ] More Colors expands real controls; canceling a picker changes nothing and resetting overrides restores the selected preset.
- [ ] Custom colors survive restart and feed new windows; selecting a preset has a defined reset behavior and never leaves stale overrides.

### 34. Colour harmony generator

Depends on: 33
Deliverable: Local deterministic palette generation, preview and explicit application.
Done only when:

- [ ] Complementary, Analogous, Triadic and Split Complementary modes generate valid palettes for both light and dark settings.
- [ ] Neutral/zero-saturation input and repeated generation are handled deterministically; the displayed palette matches the chosen accent and mode.
- [ ] Generate only previews; Apply maps the preview to named theme tokens and Reset/Cancel preserves or restores the prior theme as labelled.

### 35. Fonts, density and frosted surfaces

Depends on: 32, 47
Deliverable: Central typography/spacing tokens and a defined frosted appearance with desktop fallback.
Done only when:

- [ ] Font family, text size and Compact/Comfortable/Roomy density visibly affect intended widgets; hardcoded QSS sizes do not defeat global settings.
- [ ] Long labels and large text remain reachable at the supported minimum window size, including Theme and Settings.
- [ ] Frosted toggle produces the documented appearance or indicates an unsupported fallback; all values restore after restart without sacrificing readability.

### 36. Animated backgrounds

Depends on: 32, 54
Deliverable: Independent effect lifecycle and shared speed, intensity, size, quality, color and pause settings.
Done only when:

- [ ] All ten listed effects render, resize and switch repeatedly without stale paint or exceptions; Solid does not run an animation timer.
- [ ] Each applicable control changes the active effect, stays synchronized on panel reopen and persists; irrelevant controls are disabled with an explanation.
- [ ] Pause freezes updates, hidden/minimized application state suspends animation work, and restoration never overrides the user pause setting.
- [ ] On the recorded reference machine at 1720×900 and Balanced quality, a 60-second trace targets 60 FPS with p95 frame time ≤33 ms; slower effects must be tuned or have an explicit lower-quality fallback.

### 37. Theme save / share

Depends on: 33, 34, 35, 36
Deliverable: Named custom themes with versioned JSON import/export.
Done only when:

- [ ] Save creates or explicitly replaces a named theme and makes it selectable after restart.
- [ ] Export/import round-trip preserves the documented palette, typography, density and effect fields; generated palettes can be saved after application.
- [ ] Invalid colors, unsupported versions, duplicate names and file write failures are handled without altering the current theme; picker cancellation is a no-op.

### 38. Peek mode

Depends on: 39
Deliverable: Temporary visual transparency for tool content while its titlebar stays usable.
Done only when:

- [ ] Peek visibly exposes the workspace through the tool body and restores the exact normal appearance when toggled off.
- [ ] The titlebar remains operable; focus/input behavior is explicitly defined as visual-only Peek for this milestone, without promising click-through.
- [ ] Peek behaves correctly through minimize/restore, theme changes and close/reopen and never leaves a hidden overlay intercepting input.

### 39. Floating tool-window framework

Depends on: 1, 54
Deliverable: Shared window lifecycle, drag, resize, stacking, minimize/restore, close and geometry.
Done only when:

- [ ] Opening an already open tool focuses it; opening a minimized tool restores it and reopening a closed tool retains its intended local state.
- [ ] Drag/resize/raise/minimize/restore work with multiple tools; titlebar and resize controls remain reachable after host resizing.
- [ ] Normal geometry is saved separately from minimized geometry and restored within bounds after restart or display-size change.
- [ ] Closing one tool leaves chat and other tools intact; repeated open/close cycles do not accumulate duplicate widgets, signals or timers.

### 40. Settings — Add Models

Depends on: 1, 53, 54
Deliverable: Settings navigation shell and model configuration forms using a shared registry.
Done only when:

- [ ] All planned Settings sections are navigable with retained edits or an explicit discard choice; the model form supports local endpoint and API-provider records.
- [ ] Name, endpoint, provider and capability fields validate before save; deterministic Test results show testing/success/failure and do not issue real requests.
- [ ] Saving creates one registry entry visible in Added Models and selector; any credential control is session-only/mocked until a secure credential adapter exists.

### 41. Settings — Added Models

Depends on: 40
Deliverable: Shared model list with edit/remove/probe and availability states.
Done only when:

- [ ] Local/API filters show saved registry records; edit and remove update all dependent selectors.
- [ ] Mock probe supports online/offline/testing/error states and retry without freezing the UI.
- [ ] Removing a default or in-use model shows the affected selections and clears/replaces references consistently; no stale ID is submitted.

### 42. Settings — AI Defaults

Depends on: 41
Deliverable: Central capability-based selection for chat, fallbacks, utility, vision, research, images and writing style.
Done only when:

- [ ] Only compatible configured models can be assigned to each role; unsupported roles show a useful empty state.
- [ ] Fallbacks can be ordered without duplicates and model removal invalidates affected defaults visibly.
- [ ] Composer, comparison, research and image mock adapters resolve the same settings; writing style and defaults restore after restart.

### 43. Settings — Search

Depends on: 40, 54
Deliverable: Provider settings plus research limits/timeouts through a replaceable adapter.
Done only when:

- [ ] Provider, result count, endpoint, rounds and timeout fields have documented defaults and enforced valid ranges.
- [ ] Test shows deterministic mock success/failure with actionable feedback; fields and results clearly indicate that no live provider was contacted.
- [ ] Saved settings populate composer search and Deep Research setup consistently and survive restart.

### 44. Settings — Integrations

Depends on: 40
Deliverable: Schema-driven configuration pages for API Service, CalDAV, Claude Agent, Codex Agent, CardDAV, IMAP/SMTP and MCP.
Done only when:

- [ ] Each listed integration has complete add/edit/remove configuration, required-field validation, mock test state and a clear connected-demo/offline distinction.
- [ ] Contacts import previews supported local files and validates records before applying; invalid entries are reported and cancellation leaves the store unchanged.
- [ ] Non-secret configuration persists; secrets never enter QSettings, exported JSON or logs. Real services, agent processes and network authentication are outside this GUI milestone.

### 45. Settings — Email navigation

Depends on: 12, 31, 44
Deliverable: Navigation hub linking Email, mail accounts and related tasks.
Done only when:

- [ ] Each link opens/focuses the correct module and relevant subsection without creating duplicate windows.
- [ ] Account summaries and task counts use shared models and update after edits elsewhere.
- [ ] No-account and no-task states provide working setup/create entry points.

### 46. Settings — Reminders

Depends on: 44, 54
Deliverable: Reminder-provider settings for desktop, email, ntfy and webhook with simulated delivery.
Done only when:

- [ ] Provider forms validate required fields; test actions show labelled mock delivery success/failure and never send a notification externally.
- [ ] Synthesis/persona and public URL preferences persist and are used by the local reminder preview.
- [ ] Browser-notification reference behavior is mapped explicitly to desktop notifications; optional real Fedora notifications are completed under step 55, not implied by a mock test.

### 47. Settings — Appearance

Depends on: 1, 32, 54
Deliverable: Declarative live preferences for chat, composer, sidebar and presentation.
Done only when:

- [ ] Full width, welcome, Nobody visibility, emoji behavior, status summaries, sensitive blur, composer actions and sidebar entries each have a documented default and observable effect.
- [ ] Changes update already open UI immediately and survive restart; hiding controls preserves underlying session content.
- [ ] Settings and New Chat remain accessible through a stable command even if their usual navigation surface is hidden; reset restores documented defaults.

### 48. Sensitive-span presentation

Depends on: 10, 47
Deliverable: Presentation layer for explicitly marked sensitive demo spans; detection remains an adapter concern.
Done only when:

- [ ] Marked emails/tokens/secrets are concealed when enabled and can be intentionally revealed with an accessible control.
- [ ] Copy/export behavior is explicit and defaults to concealed content; original sensitive text is not exposed through tooltips or accessibility labels while concealed.
- [ ] Toggle updates existing messages; unmarked text is unaffected and the UI does not claim general secret detection.

### 49. Process/status presentation

Depends on: 10, 47
Deliverable: Expandable provider-supplied progress summaries and tool status, separate from answer content.
Done only when:

- [ ] Pending/running/completed/failed/cancelled fixtures show clear accessible status and can be expanded/collapsed without disrupting scroll position.
- [ ] Appearance preference shows/hides status summaries without deleting data or changing the main answer.
- [ ] Only supplied summaries and demo status are displayed; the GUI does not invent or claim access to hidden model reasoning.

### 50. Keyboard commands and shortcut editor

Depends on: 1, 54
Deliverable: Canonical QAction/QShortcut command registry plus persistent user bindings.
Done only when:

- [ ] Navigation, new/favourite/delete session, incognito, tools and TTS demo actions have stable command IDs, labels and documented defaults.
- [ ] Rebinding detects conflicts within the applicable scope, supports clear/reset and restores custom bindings after restart.
- [ ] Commands work from intended contexts without stealing ordinary text editing; disabled commands explain why, and menus/tooltips show current bindings.

### 51. Account flows

Depends on: 40, 53
Deliverable: Profile, logout, password change and 2FA visual flows backed by an explicit demo account service.
Done only when:

- [ ] Profile details, change-password validation and 2FA setup/verification/cancel/error states are fully navigable.
- [ ] Logout resets demo account/session presentation according to an explicit keep-local-data choice; unsaved edits are protected.
- [ ] All success states say demo/simulated; no real authentication, password update or 2FA enrollment is claimed or persisted as plaintext credentials.

### 52. Profile / Study Mode area

Depends on: 51
Deliverable: Interactive sidebar account/status/mode entry.
Done only when:

- [ ] Profile control opens Account; mode/status switching visibly updates the sidebar and relevant session presentation.
- [ ] Study Mode has a defined GUI effect and explanatory text instead of a decorative label; saved non-sensitive preference restores.
- [ ] Profile and mode controls remain accessible in collapsed sidebar mode and by keyboard.

### 53. Shared states and feedback

Depends on: 1
Deliverable: Reusable empty, loading, error, retry and toast components plus deterministic demo adapters.
Done only when:

- [ ] Components accept module-specific text/actions while sharing styling, focus behavior and accessible status announcements.
- [ ] Fixtures can explicitly select success, empty, loading, failure and cancellation; retries cannot duplicate requests or apply stale results.
- [ ] Toasts do not steal focus or cover essential controls; important errors remain available after toast dismissal.
- [ ] Every completed feature demonstrates its applicable states using the shared components.

### 54. Persistence and application data

Depends on: None
Deliverable: QSettings for preferences/geometry; versioned SQLite for local content and explicit JSON import/export formats.
Done only when:

- [ ] Define stable IDs and repositories for sessions, models, documents, Brain items, notes, tasks, Gallery metadata and related records; UI accesses repositories through services.
- [ ] Normal content, preferences and geometry round-trip on restart; incognito data and credentials are excluded from ordinary stores.
- [ ] Writes are transactional or atomic; corrupted/unavailable stores report recovery options without silently deleting data, and schema upgrades have fixture-based migration checks.
- [ ] Tests and demo runs use isolated temporary storage, and reset/export/import clearly state which local data is affected.

### 55. Fedora desktop validation and release polish

Depends on: All feature steps selected for the release
Deliverable: Native desktop behavior, accessibility, rendering parity, performance and clean shutdown.
Done only when:

- [ ] Record Fedora version, desktop/session type, Qt/PySide6 version, GPU and display scale; run the acceptance flows under both GNOME Wayland and KDE Wayland, with any unsupported environment explicitly scoped out.
- [ ] Check 100%, 150% and 200% display scaling, minimum/default/maximized layouts, focus/tab order, clipboard, drag/drop and native file dialogs; no unreachable primary control or unreadable text remains.
- [ ] If real local desktop notifications are included, opt-in/test/delivery/failure are verified on each supported desktop; otherwise the release labels them simulated.
- [ ] Closing during background/demo work stops timers/jobs safely and restores valid state on restart; no unintended process remains.
- [ ] Compare matched-state captures against the supplied references; document intentional native differences and verify the performance fixture targets in the acceptance protocol.

## Superseded-plan mapping

The source proposals are preserved in Git history. No copied archive is needed.

| Previous source | Replacement owner |
|---|---|
| [Former root PLAN](https://github.com/BigBenKenobi/Otter-Cove/blob/6aa802219f4130ac4732039bda01b0a870934cfe/PLAN.md) | This plan's feature catalogue and shared gate; old R1–R6/A–G execution order retired |
| [PR #8 inventory and detailed plans](https://github.com/BigBenKenobi/Otter-Cove/tree/531aaa38fe61fac867f8238744c5c6fce08aca18/docs/planning) | Eight-area sequence, session/draft contracts, SC/CU packages and cross-area gates here |
| [Initial PR #9 improvement plan](https://github.com/BigBenKenobi/Otter-Cove/blob/3240dcb37e287cbb6d059c86b940bbd86da6b8d0/docs/planning/current-implementation-improvement-plan.md) | OC-00–23 here; dated review remains evidence |
| FD-0 | OC-00 baseline; OC-01–04 findings now precede R2 landing |
| FD-1 | Relevant OC regressions plus OC-21; no second generic test-building package |
| FD-2 | OC-01–07 and native data checks in the shared gate |
| FD-3 | OC-13–15 and native interaction gate |
| FD-4 | OC-08/15/16 and theme matrix |
| FD-5 | OC-06/17/19 and animation/Peek measurements |
| FD-6/FD-7 | OC-23 and shared native/evidence gate |
| SC-0/SC-7 | OC-00, shared session contracts and shared gate |
| SC-1/SC-2 | Retained here; reuse OC-09 empty state and CU-1 popup |
| SC-3 | Retained as browser/consumer integration of OC-10 privacy behavior |
| SC-4/SC-5/SC-6 | Retained rich/streaming, search, sensitive/status increments, reusing OC fixes |
| CU-0/CU-1 | Retained shared contracts/popup, scheduled before SC-2 |
| CU-2–6 | Retained selection/action increments after session contracts |
| CU-7 | Shared integration/native/evidence gate |

All 24 OC task IDs remain defined. Six unique SC and seven CU packages remain;
the repeated foundation/baseline/closeout packages are mapped above instead of
kept as parallel instructions. Old `docs/planning/*.md` URLs now point here.
