# STARK STUDIO — CURRENT GUI PLAN AND IMPLEMENTATION INSTRUCTIONS

Progress review: 21 September 2026 (supersedes the earlier same-day baseline)
Target: Fedora 44 desktop, PySide6 / Qt Widgets
Authoritative current plan: PLAN.md in stark_studio_pyside6/

## DOCUMENT OWNERSHIP AND PROVENANCE

This is the sole current implementation and acceptance plan. It adopts the
21 September GUI progress review formerly stored in the workspace-root Plan.
The application directory is now stark_studio_pyside6 (formerly Current Build).
All application-relative paths below refer to this directory unless stated otherwise.

- PLAN.md owns scope, feature IDs, dependencies and acceptance conditions.
- ROADMAP.md summarizes execution order and points to the next work package.
- STATUS.md is the short return-to-project handoff: current state, latest evidence,
  known gaps and next action. It does not redefine acceptance requirements.
- docs/acceptance/ holds dated evidence, including consolidated historical records.
- docs/archive/ holds retired snapshots, never current implementation instructions.

Update PLAN.md when requirements or acceptance baselines change; update STATUS.md
when progress/evidence/next action changes; update ROADMAP.md only when sequence
changes. Link to detailed criteria instead of copying them into other documents.
The older PLAN.txt is archived. The former PLAN.md stub is superseded, and the
workspace-root Plan is moved here, leaving no second active plan.
This consolidation changes documentation only; it does not fix the findings below.

The original 55 IDs and acceptance criteria are retained. Each feature now has a
current observation and a next implementation instruction. Existing working
foundations should be extended, not rewritten. No total completion percentage is
assigned: these steps differ greatly in size, and passing tests cover only the
implemented slice, not all planned workflows.

## CHECKS EXECUTED THIS REVIEW

Environment: Fedora Linux 44 (KDE Plasma Desktop Edition); Python 3.14.7;
PySide6 6.11.2 / Qt 6.11.2. Execution platform: offscreen.

Commands were run before directory renaming; run from stark_studio_pyside6 now:
  PYTHONDONTWRITEBYTECODE=1 QT_QPA_PLATFORM=offscreen PYTHONPATH=. \
    python3 -m unittest discover -s tests -v
Result: 65 tests run, 65 passed, no skips or failures (0.608 seconds).

  PYTHONDONTWRITEBYTECODE=1 QT_QPA_PLATFORM=offscreen PYTHONPATH=. \
    python3 scripts/fedora_gui_smoke.py --offscreen
Result: PASS. The script prints "native GUI smoke", but this invocation was
explicitly offscreen and must not be reported as a new native desktop pass.
Coverage includes tool reuse/minimized restore, Peek lifecycle, all presets and
effect switching, appearance/draft preservation, bounds and theme restart.

Additional temporary probes used isolated SQLite and QSettings files, without
changing production data or source. Inspected rendered Home, Theme Customize,
Settings Appearance/Shortcuts, collapsed sidebar and Large/Roomy layout. Captured
Home explicitly at 1720×900; initial captures were clamped by the offscreen screen
to 1100×800, and minimum-size captures were 1100×680. Captures are not native
window-manager or fractional-scale evidence.

Temporary evidence (not permanent project deliverables):
- /tmp/stark-progress-tests.log
- /tmp/stark-progress-smoke.log
- /tmp/stark-progress-home-1720.png
- /tmp/stark-progress-custom.png
- /tmp/stark-progress-settings.png and /tmp/stark-progress-shortcuts.png
- /tmp/stark-progress-minimum-large.png and /tmp/stark-progress-collapsed.png
- /tmp/stark-progress-inspect.py (probe source)
- /tmp/stark-progress-before.json (130-file Current Build hash inventory)
Inventory digest: 87c070c48455e396714eb468e815e43830d86cda4e50140c76ef6ed7d1d25469
These paths are temporary; rerun and archive evidence during a later authorized
acceptance pass. The observations and results are recorded here for durability.

Previously recorded evidence in docs/acceptance/step-01.md and step-53.md reports a
prior 26/26 target run and scoped acceptance for shell/shared states. Preserve
those records as prior evidence. The later 64/65 More Colors test failure noted
in docs/FEDORA_CHECKLIST is not reproduced: its corrected test passes in this run.

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

## SCOPE AND COMPLETION RULES

The milestone remains a working local GUI: real local files, editing, persistence,
themes and desktop interactions. External inference, search, email delivery,
CalDAV, authentication, agent execution and AI image operations use visibly
labelled deterministic demo adapters. Real backend integration is separate work.

Status meanings:
- Accepted baseline: scoped earlier acceptance plus current regression evidence;
  preserve it, while retaining shared release obligations under 55.
- Implemented; acceptance pending: substantial behavior and passing checks exist;
  listed native/visual/performance conditions still block full completion.
- Partial: behavior exists but known implementation work remains.
- Data foundation / Preference / UI only: infrastructure or controls exist without
  the complete feature behavior.
- Scaffold: unavailable placeholder route only, even if it demonstrates states.
- Not started: no dedicated implementation found.
- Done: all step conditions plus common gates have executed evidence. Never infer
  Done from a visible button, a table or a passing unrelated test suite.

Common gates for every step:
1. Visible controls work or explain why unavailable; mock operations are labelled.
2. Exercise applicable happy/empty/invalid/loading/error/cancel/retry states.
3. Persistent state passes close/reopen AND restart; private data obeys its policy.
4. Keyboard focus/names, themes, 1100×680 minimum size and scaling are usable.
5. State belongs to models/services and shared commands; avoid competing stores.
6. Record build, environment, actions, fixtures and actual results; unresolved
   conditions remain open. Offscreen is supplementary to native desktop evidence.
7. Use focused behavioral tests for new state/error logic and manual visual checks
   for appearance. Do not weaken assertions or lower thresholds just to pass.

## NEXT WORK PACKAGES

R1. Correct the four reproduced session/layout findings above. Extend the current
    tests with failure/retry, normal/private transitions, private disposal and
    session-draft ownership. Inspect large-text controls visually. Exit: each
    reproduction now satisfies its stated outcome and the existing 65 still pass.
R2. Finish foundation acceptance, without rebuilding implemented controls. Verify
    real drag/resize, dialogs, theme/shortcut restart, focus and display scaling;
    add local-data management/recovery UI under 54. Measure animation under 36.
    Exit: distinguish any remaining implementation defects from desktop evidence.
R3. Add model configuration and capability defaults (40/41/42), then selector (05)
    and shared popover/composer contracts (07/08/04). Keep unavailable integrations
    labelled; use the existing Settings window and SQLite services.
R4. Complete session UX and documents (10/03/06/28), Prompt (09), Library/Search
    (27/11), and sensitive/process rendering (48/49). Session integrity fixes in
    R1 do not require waiting for the entire feature to be complete.
R5. Build the remaining personal/research/Gallery modules in the dependency order
    below; reuse working state, feedback, command, theme and data foundations.
R6. Complete step 55 release checks. Do not turn the native checklist into a claim
    of successful execution merely because an offscreen smoke run passes.

## FEATURE DEPENDENCIES AND MILESTONE ORDER

Retained from the accepted plan; foundation entries already implemented need
verification/targeted completion, not a fresh implementation. Each feature's
Depends on line is a full-completion gate, not a prohibition on independent work.

A: 54, 01, 53, 39, 32, 33, 47, 35, 36, 38, 34, 37, 50.
B: 40, 41, 42, 43, 44, 46, 02, 51, 52.
C: 10, 03, 06, 28, 07, 08, 05, 04, 09, 27, 11, 48, 49.
D: 13, 14, 15, 16, 31, 30, 12, 45, 17.
E: 18, 19, 20, 29, 21, 22.
F: 23, 25, 24, 26.
G: 55 and regression of all release-selected features.

A exit: reliable shared services/windows, complete foundation flows and evidence.
B exit: model/settings records update consumers, persist and handle invalid state.
C exit: session privacy/drafts, local documents, prompts and search work end to end.
D exit: personal workspaces retain consistent local state and simulated jobs.
E exit: comparison/research artifacts and Gallery metadata are consistent.
F exit: image project round-trip, composition/history and mock result application.
G exit: documented native matrix, reference comparison and performance targets.

Original screenshots and screencasts are stored once under docs/reference/ and
remain the appearance/interaction target.
This pass reuses the earlier reference review; it is not a new exhaustive
pixel-parity audit. Use original full-resolution reference files for comparison.

## FEATURE STEPS AND ACCEPTANCE CONDITIONS


### 01. Application shell

Baseline: Accepted baseline; regression suite passes
Current check: Shell owns services, route state, feedback, themes and commands. Existing step-01 acceptance records a prior 26/26 run; the current 65-test suite also passes. Keep that scoped acceptance; do not reinterpret it as full desktop release validation.
Next implementation instruction: Preserve the shell and route contracts. Extend factories for real modules; do not rebuild the shell. Maintain draft preservation while opening tools.
Depends on: 54
Deliverable: MainWindow, service/state ownership, route registry and layered workspace; main.py remains an entry point.
Done only when:

- [ ] Application starts with isolated fresh preferences and with saved preferences; opening a tool preserves the current chat and composer draft.
- [ ] Every exposed route resolves to its intended component or an explicitly labelled unavailable state; feature logic is kept out of main.py.
- [ ] Resizing between 1100×680 and 1920×1080 logical pixels leaves navigation and primary controls reachable.

### 02. Collapsible sidebar

Baseline: Partial
Current check: Sidebar uses painted line icons, active state, collapse animation and visibility preferences. Profile and Settings remain visible when collapsed; the old hidden-Settings defect is resolved in source and rendered capture.
Next implementation instruction: Validate rapid toggles, keyboard focus, route badges and all typography/density combinations. Account currently opens an unavailable scaffold, not a complete profile flow.
Depends on: 1, 47, 50
Deliverable: Expanded and icon-only navigation driven by canonical commands and visibility preferences.
Done only when:

- [ ] Collapse/expand animates without losing active route, tool state or draft; rapid repeated toggles finish at the requested width.
- [ ] Every icon-only action has a tooltip and accessible name; Settings/account remain reachable when collapsed.
- [ ] Active state, optional entries and badges reflect application state; width and visibility restore after restart.

### 03. Home / empty session

Baseline: Partial
Current check: Empty hero, welcome preferences and first-message transition exist. Latest persistent session is restored at startup. New Chat resets the session pointer and message widgets but retains the old composer draft.
Next implementation instruction: Define session-scoped drafts and deliberate New Chat behavior. Cover switching existing sessions and zero-message restored sessions, not only the first-send path.
Depends on: 10
Deliverable: One session view whose empty state contains brand, welcome text, Nobody control and composer.
Done only when:

- [ ] A session with zero messages displays the welcome state; the first message replaces it with conversation content.
- [ ] New Chat creates a separate empty session and opening an existing session restores its contents; hidden welcome preferences apply immediately.
- [ ] The hero and composer remain centered within the available workspace, including when the sidebar or Notes dock changes width.

### 04. Chat composer

Baseline: Partial
Current check: Composer width adapts and Full-width works; height remains fixed at 96 with a 42-pixel editor limit. Submission only saves local user messages. Injected add_message failure clears the draft before reporting failure.
Next implementation instruction: First clear input only after successful acceptance and preserve attachments/mode on failure. Then implement bounded autosizing, model/request records, cancellation and per-session drafts.
Depends on: 5, 7, 8, 10, 50
Deliverable: Reusable multiline composer with bounded autosizing, model selection, Agent/Chat mode and send state.
Done only when:

- [ ] Input grows to a documented maximum height then scrolls; long text and pasted multiline text do not cover controls.
- [ ] Ctrl+Enter sends, Enter inserts a newline, and empty/whitespace-only submission is rejected; shortcut help matches behavior.
- [ ] Selected model, mode and attachments are included in the local submission record; unavailable selections give an actionable state.
- [ ] A failed persistence/submission operation retains the complete editable draft and attachments, reports the error and supports retry without duplicate messages.
- [ ] Submission clears the accepted draft once; switching sessions restores each draft. Mock responses and cancellation work without network access.

### 05. Model selector

Baseline: Scaffold
Current check: Select model opens FeaturePlaceholder; repository support exists but there is no user-facing registry/selector flow.
Next implementation instruction: Build model configuration under 40/41, then a shared anchored selector backed by those records.
Depends on: 40, 41, 53
Deliverable: Anchored model popover consuming the shared model registry.
Done only when:

- [ ] Empty, loading, available, offline and failed-refresh states can be reached with deterministic fixtures.
- [ ] Selection updates the composer and session state; refresh keeps a valid selection and removal clears an invalid one.
- [ ] Add Model opens the shared configuration flow; keyboard navigation, Escape and outside-click dismissal work.

### 06. Nobody / incognito session

Baseline: Partial
Current check: SessionService keeps incognito records in memory and excludes them from SQLite/export. A normal-to-Nobody transition creates a different session but leaves both sessions' message labels on screen. The status summary still says persistent storage. New Chat leaves the former incognito record retained in the service.
Next implementation instruction: Add explicit mode-transition handling, render only the active session, update visible status from session state, and dispose transient records when the session is closed. Re-test both directions and restart; do not claim a disk leak from the observed view-mixing issue.
Depends on: 10, 54
Deliverable: Session-level no-history/no-memory mode, visibly distinguished from normal sessions.
Done only when:

- [ ] Creating an incognito session displays a persistent indicator and a tooltip explaining local GUI behavior.
- [ ] Its messages, drafts and attachments are excluded from persisted history, search indexes, memory extraction and diagnostic content; restart does not restore them.
- [ ] Normal/private mode transitions render only the newly active session; indicators and status summaries describe its actual persistence state.
- [ ] Changing mode after messages exist has an explicit transition choice and never silently saves private content; closing the session clears its transient state.

### 07. Composer tool menu and attachments

Baseline: Not started
Current check: No attachment menu, file chips, Documents/Workspace picker or Prompt entry exists.
Next implementation instruction: Create one popover/focus primitive and use the document service rather than a parallel store.
Depends on: 1, 28, 53
Deliverable: Shared anchored popover primitive, Attach Files, Documents, Workspace and Prompt entry points.
Done only when:

- [ ] Popover repositions within workspace bounds, accepts keyboard input, dismisses on Escape/outside click, and returns focus to its trigger.
- [ ] Native file selection adds removable attachment chips with filename/type; cancellation leaves the draft unchanged and unreadable files show an error.
- [ ] Documents and Prompt open their actual modules; Workspace selects a local context folder and displays that choice without executing files.

### 08. Optional composer actions

Baseline: Partial
Current check: Appearance toggles directly show/hide Web Search and Shell buttons; clicks route to Search/Tools scaffolds. Canonical app commands exist, but there is no composer action registry.
Next implementation instruction: Introduce the composer registry and connect labelled mock actions. Distinguish web search from conversation search; the current web-labelled button routes to conversation Search.
Depends on: 7, 47, 50
Deliverable: Command-backed action registry for web search, shell and additional composer tools.
Done only when:

- [ ] Each action has a stable ID, label, icon, enabled state and handler; adding an action does not require composer layout changes.
- [ ] Appearance toggles add/remove the corresponding action immediately and survive restart.
- [ ] Web and shell actions show clearly labelled simulated results in this milestone; cancellation/error states work and no real shell command or search request is executed.

### 09. Prompt Studio

Baseline: Not started
Current check: Prompt Studio has no dedicated view or route in the current registry.
Next implementation instruction: Implement Inject/Persona/Group against persistent configuration once model and popover contracts exist.
Depends on: 5, 7, 54
Deliverable: Inject, Persona and Group tabs backed by persistent prompt configuration.
Done only when:

- [ ] Prefix/suffix, temperature and token limit validate before apply; invalid numeric values explain the supported range.
- [ ] Personas can be created, selected, edited and deleted; group participants can be added, removed and reordered with sequential/group mode.
- [ ] Applied configuration is visible in the session and used by the mock request builder; closing/reopening and restarting preserve saved definitions while Cancel discards uncommitted edits.

### 10. Sessions and message rendering

Baseline: Partial
Current check: Persistent session/message repositories and SessionService now drive local user cards and latest-session restoration. No session browser, rename/favourite/delete flow, streaming or rich message types exist.
Next implementation instruction: Fix mixed-session rendering and draft ownership first, then add session selection/CRUD and richer renderers. Wire disabled favourite/delete commands only when the underlying flows work.
Depends on: 1, 53, 54
Deliverable: Local session/message model and reusable user, assistant, system/tool, code and status views.
Done only when:

- [ ] Create, reopen, rename, favourite, archive and delete sessions through the shared model; destructive actions use confirmation or undo.
- [ ] User, assistant, code and tool/status fixtures render with selection, copy, timestamps and consistent state indicators; rich text cannot execute embedded code.
- [ ] Simulated streaming can complete, fail and cancel; scrolling stays at the bottom only while the user is following it and does not jump away from older messages.
- [ ] A 200-message fixture remains usable and persisted normal sessions reopen with correct ordering; storage/rendering are separated from provider execution.

### 11. Search

Baseline: Scaffold
Current check: Search opens a generic unavailable tool with shared demo-state controls; no local query provider is wired.
Next implementation instruction: Implement history/Library search over shared records and keep incognito records out of its source.
Depends on: 10, 27, 50
Deliverable: Search overlay using a replaceable local search provider.
Done only when:

- [ ] Search matches session titles and message text plus supported Library metadata/content; results identify their source and open the correct item.
- [ ] Empty query, no matches, searching and provider failure states work; editing queries cannot display stale results.
- [ ] Ctrl+F opens and focuses search, arrows/Enter activate results, Escape restores focus; incognito content is never returned.

### 12. Email

Baseline: Scaffold
Current check: Email still uses FeaturePlaceholder; state-demo buttons are not mailbox behavior.
Next implementation instruction: Implement local fixtures, list/detail and draft/compose flows after shared integration contracts.
Depends on: 44, 53, 54
Deliverable: Mailbox list/detail, account/filter controls, tags, compose and local draft state.
Done only when:

- [ ] Fixture inbox supports selection, search, account/filter changes, tags and readable message details without losing the selected item unexpectedly.
- [ ] Compose validates recipients and required fields, stores local drafts and preserves them across reopen/restart; discard is explicit.
- [ ] Refresh, loading, empty and failure states are exercisable; Send creates a labelled simulated sent item and never transmits mail.

### 13. Brain — Memories

Baseline: Scaffold with data foundation
Current check: Brain route is a placeholder; generic Brain records have repository/service support.
Next implementation instruction: Build memory cards and domain operations over the existing store; do not count table existence as UI completion.
Depends on: 53, 54
Deliverable: Memory cards and local CRUD with search, sorting, selection and enabled state.
Done only when:

- [ ] Create, edit, delete, enable/disable and select memories; search and sort operate on the same persisted records.
- [ ] Bulk operations affect only selected records; disabled memories are excluded from simulated injection.
- [ ] Tidy previews proposed deduplication/cleanup and requires application of that preview; cancel preserves all entries.

### 14. Brain — Skills

Baseline: Scaffold with data foundation
Current check: Brain has no Skills tab or audit flow; Brain records can represent domain content.
Next implementation instruction: Add skill validation, approval/injection rules and deterministic audit UI on the shared Brain service.
Depends on: 13
Deliverable: Skill records with confidence, tags, instructions and enabled/audit state.
Done only when:

- [ ] Skills can be edited, searched, sorted by confidence and enabled/disabled with persistent results.
- [ ] Mock audit shows pending/running/completed/failed states and a readable result; no actual capability or verification is claimed.
- [ ] Disabled or unapproved skills are excluded from injection; selecting a skill exposes its trigger and instructions.

### 15. Brain — Add / import / export

Baseline: Not started
Current check: Whole-store JSON import/export exists, but no Brain-specific form or import/export GUI exists.
Next implementation instruction: Build focused forms and preview/duplicate handling. Whole-store replacement is not a substitute for skill/memory import.
Depends on: 13, 14
Deliverable: Validated memory and skill forms plus versioned JSON interchange.
Done only when:

- [ ] Manual memory and skill forms validate required title/when/how fields as appropriate and normalize tags.
- [ ] Export then import into an empty store preserves supported fields; duplicate handling offers a clear skip/replace/copy choice.
- [ ] Malformed or unsupported files show a readable error without partial store corruption; cancelling a picker or preview leaves records untouched.

### 16. Brain automation preferences

Baseline: Not started
Current check: No Brain automation settings or extraction pipeline UI is present.
Next implementation instruction: Implement after memory/skill records and incognito transitions are reliable.
Depends on: 6, 14, 15
Deliverable: Persistent extraction/approval thresholds and injection limits for the demo pipeline.
Done only when:

- [ ] Auto-extract memory/skills, auto-approve, confidence threshold and injection count have documented defaults, valid ranges and saved values.
- [ ] A deterministic normal-session fixture demonstrates each toggle and threshold, including rejection below threshold and the maximum injection count.
- [ ] Incognito sessions bypass extraction and persistence regardless of preferences; the interface identifies extraction as simulated.

### 17. Calendar

Baseline: Scaffold
Current check: Calendar route is a placeholder; no calendar/event repository or import/view UI is exposed.
Next implementation instruction: Add calendar domain model and supported .ics scope before views; retain mocked CalDAV boundary.
Depends on: 44, 53, 54
Deliverable: Local calendars, month/week/day views, event editing and local .ics import; CalDAV configuration only.
Done only when:

- [ ] Create/rename calendars and create/edit/delete dated, timed and all-day events; calendar visibility updates every view.
- [ ] Navigation handles month/year boundaries and local timezone/DST fixtures without moving events to the wrong date.
- [ ] Import supported basic .ics VEVENTs with preview and duplicate handling; unsupported recurrence or fields are reported rather than silently dropped.
- [ ] Empty calendar, invalid import and mock CalDAV failure states are usable; local events survive restart.

### 18. Model Compare

Baseline: Scaffold
Current check: Model Compare remains a generic tool scaffold.
Next implementation instruction: Use shared model registry and deterministic runners; save results through Library contracts.
Depends on: 5, 10, 54
Deliverable: Comparison setup and results using deterministic mock model runners.
Done only when:

- [ ] Two or more model slots accept a prompt and Chat/Agent/Search/Research mode; timeout and cancellation end pending runs visibly.
- [ ] Parallel results, blind identity hiding, reveal and shuffle behave consistently; scoring updates a persistent scoreboard without duplicate votes.
- [ ] Continue uses the selected result as context, Save creates a Library item, and Reset clears the run after protecting unsaved results; all answers are labelled demo output.

### 19. Cookbook

Baseline: Scaffold
Current check: Cookbook remains a generic tool scaffold.
Next implementation instruction: Build cache/status/configuration UI with explicitly simulated launch/download/dependency operations.
Depends on: 41, 53, 54
Deliverable: Local-model management console with Launch, Download, Dependencies and Settings tabs.
Done only when:

- [ ] Cache fixtures show model identity, location, availability and state; selecting an entry populates the appropriate controls.
- [ ] Download, launch and dependency operations have deterministic progress, cancel, complete and failure states with retry.
- [ ] Configuration persists; all simulated operations are labelled and neither install packages nor download/execute models.

### 20. Deep Research

Baseline: Scaffold
Current check: Deep Research remains a generic tool scaffold.
Next implementation instruction: Use the task/job model and shared search/model defaults; persist one artifact per completed job.
Depends on: 31, 42, 43
Deliverable: Research setup and local queued jobs producing demo reports.
Done only when:

- [ ] Prompt, rounds, format, engine, endpoint and model validate before a job can be queued.
- [ ] Queue/start/pause where supported/cancel/retry drive explicit job states without duplicate starts; progress survives reopening the view.
- [ ] A completed demo job writes one report to Research Library with its setup and completion metadata; cancellation/failure does not create a completed report.
- [ ] Generated sample text and sample citations are identified as mock content, not real research.

### 21. Gallery — Photos

Baseline: Scaffold with data foundation
Current check: Gallery metadata repository/service exists; Gallery still opens a placeholder.
Next implementation instruction: Implement safe local import and cached thumbnails before albums/editor work.
Depends on: 53, 54
Deliverable: Local image import, thumbnail model/view, tags, filters, favourites and selection.
Done only when:

- [ ] File picker and drag/drop import supported raster formats; corrupt/unsupported files fail individually without losing valid imports.
- [ ] Search, source filter, sorting, favourites and bulk selection update the same metadata store and survive restart.
- [ ] Thumbnails load outside blocking UI work; a 500-image fixture scrolls without full-size decoding on every paint, and missing originals display a recovery state.
- [ ] Import/reference ownership and deletion behavior are explicit; removing a Gallery record never silently deletes the source file.

### 22. Gallery — Albums

Baseline: Not started
Current check: No album view or membership model is implemented.
Next implementation instruction: Add album/photo relationships after the Photos model is usable.
Depends on: 21
Deliverable: Album records referencing imported photos.
Done only when:

- [ ] Create, rename and delete albums; add/remove photos by selection or drag/drop and show an accurate count/cover.
- [ ] One photo may belong to multiple albums; deleting an album preserves photos and other album memberships.
- [ ] Empty albums and missing photos are handled; membership and ordering survive restart.

### 23. Gallery editor foundation

Baseline: Not started
Current check: No editor document, viewport or save/export UI exists.
Next implementation instruction: Establish document ownership and coordinate mapping before tools.
Depends on: 21
Deliverable: Dedicated canvas/viewport and editor document architecture; QGraphicsView/Scene or an equivalent custom canvas.
Done only when:

- [ ] Open an imported image, zoom/pan/fit and map pointer positions correctly at multiple zoom levels and display scales.
- [ ] Canvas/document state is separate from tool widgets; an unsaved indicator and save/discard/cancel flow protect work on close or replacement.
- [ ] Save/reopen an editable project and export a flattened PNG with correct dimensions and alpha; failed/cancelled writes retain the document.

### 24. Gallery editing tools

Baseline: Not started
Current check: No editing tool implementation exists.
Next implementation instruction: Implement ordinary edits through the layer/history model, then labelled mock AI flows.
Depends on: 23, 25
Deliverable: Move, Crop, Transform, Brush, Eraser, Clone, Lasso, Wand and Sharpen; adapter UI for AI-labelled tools.
Done only when:

- [ ] Move/crop/transform and brush/eraser/clone operate on the selected editable layer with visible previews and cancel/commit behavior.
- [ ] Lasso and Wand produce visible selections, respect image bounds and constrain applicable edits; Sharpen exposes a preview and strength.
- [ ] Every committed document edit supports undo/redo, including after zoom/pan; cancelled gestures create no history entry.
- [ ] SAM and background removal provide a complete selection/result preview flow using a clearly marked mock adapter; they never imply real AI processing.

### 25. Gallery layers and history

Baseline: Not started
Current check: No layer/mask/history subsystem exists.
Next implementation instruction: Define serializable layers and reversible commands before adding tools.
Depends on: 23
Deliverable: Independent layer model with pixel content, visibility, opacity, order, transforms and masks; command-based history.
Done only when:

- [ ] Add/duplicate/remove/reorder layers, rename them, toggle visibility, change opacity and attach/edit masks; rendered output follows the model.
- [ ] Undo/redo restores exact document state for each supported operation; a new edit after undo invalidates the redo branch.
- [ ] Save/reopen retains layer properties and masks; flattened export matches the current composite and transparent areas.
- [ ] History and decoded-image caches have documented bounds; reaching a bound does not corrupt the current document.

### 26. Inpaint workflow

Baseline: Not started
Current check: No mask/inpaint workflow exists.
Next implementation instruction: Build on the editor command model; reject stale processing results.
Depends on: 24, 25, 42
Deliverable: Mask editor and preview/apply workflow with replaceable processing adapter.
Done only when:

- [ ] Paint/erase masks, change brush size, invert, clear and hide/show overlay without changing underlying pixels until Apply.
- [ ] Prompt, model, strength, generate/remove/outpaint mode and edge controls validate; outpaint updates canvas dimensions predictably.
- [ ] Mock processing supports progress/cancel/failure and preview/reject/apply; Apply is undoable and preserves other layers.
- [ ] Changing images or masks during a job cannot apply a stale result to the wrong document.

### 27. Library

Baseline: Scaffold
Current check: Library remains a placeholder; sessions and generic documents now have data services.
Next implementation instruction: Build one Library aggregation model over existing services; keep source records authoritative.
Depends on: 10, 28, 54
Deliverable: Shared searchable item model for Chats, Documents, Research and Archive.
Done only when:

- [ ] Each tab uses consistent search, sorting, selection and empty/error states and opens the correct underlying item.
- [ ] Archive/restore/delete and bulk actions keep source modules synchronized; tidy previews changes before applying them.
- [ ] Persisted items retain stable IDs and category metadata; incognito sessions are excluded.

### 28. Documents

Baseline: Data foundation only
Current check: Document records/service exist; no document editor, import flow or viewer is exposed.
Next implementation instruction: Implement local text/Markdown workflows and unsaved-edit protection; add a real route/entry point.
Depends on: 53, 54
Deliverable: Local plain-text/Markdown document import, editor and viewer.
Done only when:

- [ ] Create/import/open/edit/save supported text and Markdown files with title/content search and source metadata.
- [ ] Unsaved edits prompt save/discard/cancel; external write failure and unsupported encoding produce useful errors without losing editor text.
- [ ] Documents can be selected from the composer and Library; preview rendering does not execute embedded HTML or scripts.

### 29. Research Library

Baseline: Not started
Current check: No research report production or Research Library view exists.
Next implementation instruction: Connect completed jobs only after Research and Library services/views exist.
Depends on: 20, 27
Deliverable: Research category backed by completed research job artifacts.
Done only when:

- [ ] Each successful research job appears once with title, report, model/setup and date; incomplete jobs are absent from completed reports.
- [ ] Open/search/archive/restore/export a report through the shared Library operations.
- [ ] Reopening/restarting preserves report content and provenance; mock status stays visible in the viewer and exported document.

### 30. Notes dock

Baseline: Scaffold with data foundation
Current check: Notes records exist, but the route opens a floating placeholder rather than the planned right-side dock.
Next implementation instruction: Implement a dock and note CRUD; consume scheduler links after Tasks is ready.
Depends on: 31, 54
Deliverable: Right-side dock with notes, list/grid modes, archive, pin, selection and reminder links.
Done only when:

- [ ] Dock open/close/resize adjusts the available workspace without covering essential composer controls; saved width and view mode restore.
- [ ] Create/edit/search/pin/archive/restore/delete notes in list and grid views; bulk actions use explicit selection.
- [ ] Notes persist and reminder metadata creates/updates one linked local task; deleting either side handles the relationship explicitly.

### 31. Tasks and local scheduler

Baseline: Scaffold with data foundation
Current check: Task records exist; no scheduler, activity model or dedicated task tabs are exposed.
Next implementation instruction: Define deterministic transitions, recurrence/overdue policy and scheduler ownership before the tabs.
Depends on: 46, 53, 54
Deliverable: Task state model plus Tasks, Activity, Completed and Add views; safe in-process demo execution.
Done only when:

- [ ] Create/edit scheduled demo tasks with timezone-aware due dates and validated recurrence; search and tab counts match stored states.
- [ ] Pending/running/completed/failed/cancelled transitions and activity records are deterministic; Pause All prevents new starts.
- [ ] Restart handles overdue tasks using a documented catch-up policy and never duplicates completion; paused and cancelled tasks do not run.
- [ ] Execution is limited to local demo handlers while the application is open; UI explains that background execution while closed is outside this milestone.

### 32. Theme presets

Baseline: Implemented; native acceptance pending
Current check: All 16 built-ins are live and exercised by the smoke check. The previously light Customize scroll background is corrected in the observed Forest render.
Next implementation instruction: Preserve semantic theme implementation; complete matched-state Light/Copper/Ocean/Forest visual review, focus/disabled/readability and native restart evidence.
Depends on: 1
Deliverable: Sixteen semantic theme definitions consumed consistently by all widgets.
Done only when:

- [ ] Original, Light, Midnight, Paper, Cyberpunk, Retrowave, Forest, Ocean, Ume, Copper, Terminal, Organs, Lavender, GPT, Claude and Cute are selectable.
- [ ] Selecting a theme updates existing and newly opened windows, popovers, menus, scroll viewports and backgrounds immediately.
- [ ] No unstyled white viewport remains in dark themes; text, focus, selection and disabled controls remain readable in light and dark themes, and the selected preset survives restart.

### 33. Theme customization

Baseline: Implemented; native acceptance pending
Current check: Primary and More Colors controls, persistent overrides, reset and picker-cancel handling are implemented and covered by theme tests.
Next implementation instruction: Run actual picker cancel/live update and restart flows with multiple windows; retain current override semantics.
Depends on: 32, 54
Deliverable: Editable semantic palette with live preview and persistent custom overrides.
Done only when:

- [ ] Background, panel, text, sidebar, border and accent plus the expanded token set update their intended surfaces immediately.
- [ ] More Colors expands real controls; canceling a picker changes nothing and resetting overrides restores the selected preset.
- [ ] Custom colors survive restart and feed new windows; selecting a preset has a defined reset behavior and never leaves stale overrides.

### 34. Colour harmony generator

Baseline: Implemented; native acceptance pending
Current check: Deterministic four-mode light/dark harmony generation, preview, Apply and Reset are implemented with passing logic/Qt tests.
Next implementation instruction: Validate native interaction and generated-palette readability rather than rebuilding the generator.
Depends on: 33
Deliverable: Local deterministic palette generation, preview and explicit application.
Done only when:

- [ ] Complementary, Analogous, Triadic and Split Complementary modes generate valid palettes for both light and dark settings.
- [ ] Neutral/zero-saturation input and repeated generation are handled deterministically; the displayed palette matches the chosen accent and mode.
- [ ] Generate only previews; Apply maps the preview to named theme tokens and Reset/Cancel preserves or restores the prior theme as labelled.

### 35. Fonts, density and frosted surfaces

Baseline: Partial; visual defect found
Current check: Typography and density now affect styles, and Frosted has a documented translucent fallback. At 1100×680, Sans Serif/Large/Roomy, the fixed-width Nobody label visibly clips.
Next implementation instruction: Remove fixed-size assumptions that clip scaled controls; inspect both Theme tabs and Settings with every text-size/density combination. Preserve the explicitly non-compositor Frosted fallback.
Depends on: 32, 47
Deliverable: Central typography/spacing tokens and a defined frosted appearance with desktop fallback.
Done only when:

- [ ] Font family, text size and Compact/Comfortable/Roomy density visibly affect intended widgets; hardcoded QSS sizes do not defeat global settings.
- [ ] Long labels and large text remain reachable at the supported minimum window size, including Theme and Settings.
- [ ] Frosted toggle produces the documented appearance or indicates an unsupported fallback; all values restore after restart without sacrificing readability.

### 36. Animated backgrounds

Baseline: Implemented; performance/native acceptance pending
Current check: All ten effects switch in the smoke check; Solid timer disabling, independent pause/suspension, effect color and settings have passing tests.
Next implementation instruction: Capture actual animation/performance on the active desktop. Offscreen application suspension means this run cannot substantiate animation smoothness.
Depends on: 32, 54
Deliverable: Independent effect lifecycle and shared speed, intensity, size, quality, color and pause settings.
Done only when:

- [ ] All ten listed effects render, resize and switch repeatedly without stale paint or exceptions; Solid does not run an animation timer.
- [ ] Each applicable control changes the active effect, stays synchronized on panel reopen and persists; irrelevant controls are disabled with an explanation.
- [ ] Pause freezes updates, hidden/minimized application state suspends animation work, and restoration never overrides the user pause setting.
- [ ] On the recorded reference machine at 1720×900 and Balanced quality, a 60-second trace targets 60 FPS with p95 frame time ≤33 ms; slower effects must be tuned or have an explicit lower-quality fallback.

### 37. Theme save / share

Baseline: Implemented; native dialog acceptance pending
Current check: Named themes, validated/versioned atomic JSON, duplicate checks and saved bundles exist. Logic/Qt tests pass, including restart state.
Next implementation instruction: Exercise native save/import/export/cancel/error dialogs. Keep invalid import non-mutating; inspect long saved-theme lists for scroll/reachability.
Depends on: 33, 34, 35, 36
Deliverable: Named custom themes with versioned JSON import/export.
Done only when:

- [ ] Save creates or explicitly replaces a named theme and makes it selectable after restart.
- [ ] Export/import round-trip preserves the documented palette, typography, density and effect fields; generated palettes can be saved after application.
- [ ] Invalid colors, unsupported versions, duplicate names and file write failures are handled without altering the current theme; picker cancellation is a no-op.

### 38. Peek mode

Baseline: Implemented; native interaction pending
Current check: Visual-only Peek state and opacity lifecycle have passing Qt tests and smoke coverage.
Next implementation instruction: Check pointer interaction and background visibility through the real desktop compositor; do not claim click-through.
Depends on: 39
Deliverable: Temporary visual transparency for tool content while its titlebar stays usable.
Done only when:

- [ ] Peek visibly exposes the workspace through the tool body and restores the exact normal appearance when toggled off.
- [ ] The titlebar remains operable; focus/input behavior is explicitly defined as visual-only Peek for this milestone, without promising click-through.
- [ ] Peek behaves correctly through minimize/restore, theme changes and close/reopen and never leaves a hidden overlay intercepting input.

### 39. Floating tool-window framework

Baseline: Implemented; native interaction pending
Current check: Normal/minimized geometry separation, reuse, minimized reopen restoration, bounds recovery and commit behavior exist; all four window tests and smoke assertions pass.
Next implementation instruction: Complete real pointer drag/resize/raise and process-restart geometry checks. Do not repeat already-fixed minimized-height work.
Depends on: 1, 54
Deliverable: Shared window lifecycle, drag, resize, stacking, minimize/restore, close and geometry.
Done only when:

- [ ] Opening an already open tool focuses it; opening a minimized tool restores it and reopening a closed tool retains its intended local state.
- [ ] Drag/resize/raise/minimize/restore work with multiple tools; titlebar and resize controls remain reachable after host resizing.
- [ ] Normal geometry is saved separately from minimized geometry and restored within bounds after restart or display-size change.
- [ ] Closing one tool leaves chat and other tools intact; repeated open/close cycles do not accumulate duplicate widgets, signals or timers.

### 40. Settings — Add Models

Baseline: Partial shared shell; model page absent
Current check: Settings is now real, but only Appearance and Shortcuts tabs exist. ModelRepository/ModelService is available; Add Models form is absent.
Next implementation instruction: Extend the existing Settings shell with local/API model forms and a registry service rather than replacing working tabs.
Depends on: 1, 53, 54
Deliverable: Settings navigation shell and model configuration forms using a shared registry.
Done only when:

- [ ] All planned Settings sections are navigable with retained edits or an explicit discard choice; the model form supports local endpoint and API-provider records.
- [ ] Name, endpoint, provider and capability fields validate before save; deterministic Test results show testing/success/failure and do not issue real requests.
- [ ] Saving creates one registry entry visible in Added Models and selector; any credential control is session-only/mocked until a secure credential adapter exists.

### 41. Settings — Added Models

Baseline: Data foundation only
Current check: Models can be stored through services, but Added Models UI, edit/remove and probe states are absent.
Next implementation instruction: Extend service operations and implement list/probe flows with reference invalidation.
Depends on: 40
Deliverable: Shared model list with edit/remove/probe and availability states.
Done only when:

- [ ] Local/API filters show saved registry records; edit and remove update all dependent selectors.
- [ ] Mock probe supports online/offline/testing/error states and retry without freezing the UI.
- [ ] Removing a default or in-use model shows the affected selections and clears/replaces references consistently; no stale ID is submitted.

### 42. Settings — AI Defaults

Baseline: Not started
Current check: No capability-default configuration UI or resolver is exposed.
Next implementation instruction: Implement after model management and share it across consumers.
Depends on: 41
Deliverable: Central capability-based selection for chat, fallbacks, utility, vision, research, images and writing style.
Done only when:

- [ ] Only compatible configured models can be assigned to each role; unsupported roles show a useful empty state.
- [ ] Fallbacks can be ordered without duplicates and model removal invalidates affected defaults visibly.
- [ ] Composer, comparison, research and image mock adapters resolve the same settings; writing style and defaults restore after restart.

### 43. Settings — Search

Baseline: Not started
Current check: No provider/search-limit configuration page exists.
Next implementation instruction: Add schema-backed settings and mock provider testing.
Depends on: 40, 54
Deliverable: Provider settings plus research limits/timeouts through a replaceable adapter.
Done only when:

- [ ] Provider, result count, endpoint, rounds and timeout fields have documented defaults and enforced valid ranges.
- [ ] Test shows deterministic mock success/failure with actionable feedback; fields and results clearly indicate that no live provider was contacted.
- [ ] Saved settings populate composer search and Deep Research setup consistently and survive restart.

### 44. Settings — Integrations

Baseline: Not started
Current check: No integration wizard/configuration pages exist.
Next implementation instruction: Use shared forms and credential boundaries; preserve mock-only execution scope.
Depends on: 40
Deliverable: Schema-driven configuration pages for API Service, CalDAV, Claude Agent, Codex Agent, CardDAV, IMAP/SMTP and MCP.
Done only when:

- [ ] Each listed integration has complete add/edit/remove configuration, required-field validation, mock test state and a clear connected-demo/offline distinction.
- [ ] Contacts import previews supported local files and validates records before applying; invalid entries are reported and cancellation leaves the store unchanged.
- [ ] Non-secret configuration persists; secrets never enter QSettings, exported JSON or logs. Real services, agent processes and network authentication are outside this GUI milestone.

### 45. Settings — Email navigation

Baseline: Not started
Current check: No Settings Email hub exists.
Next implementation instruction: Connect real module/subsection routes once Email and Tasks exist.
Depends on: 12, 31, 44
Deliverable: Navigation hub linking Email, mail accounts and related tasks.
Done only when:

- [ ] Each link opens/focuses the correct module and relevant subsection without creating duplicate windows.
- [ ] Account summaries and task counts use shared models and update after edits elsewhere.
- [ ] No-account and no-task states provide working setup/create entry points.

### 46. Settings — Reminders

Baseline: Not started
Current check: No reminder-provider settings page exists.
Next implementation instruction: Implement local configuration/preview and simulated delivery before native notification validation.
Depends on: 44, 54
Deliverable: Reminder-provider settings for desktop, email, ntfy and webhook with simulated delivery.
Done only when:

- [ ] Provider forms validate required fields; test actions show labelled mock delivery success/failure and never send a notification externally.
- [ ] Synthesis/persona and public URL preferences persist and are used by the local reminder preview.
- [ ] Browser-notification reference behavior is mapped explicitly to desktop notifications; optional real Fedora notifications are completed under step 55, not implied by a mock test.

### 47. Settings — Appearance

Baseline: Partial
Current check: Appearance controls persist and update existing UI, with passing reset/draft-preservation tests. Sensitive-span blur only sets a property, and status summaries are a static label rather than process rendering.
Next implementation instruction: Retain working preferences. Mark dependent capabilities unavailable or accurately described until 48/49 supply behavior; do not present a checked blur control as actual protection.
Depends on: 1, 32, 54
Deliverable: Declarative live preferences for chat, composer, sidebar and presentation.
Done only when:

- [ ] Full width, welcome, Nobody visibility, emoji behavior, status summaries, sensitive blur, composer actions and sidebar entries each have a documented default and observable effect.
- [ ] Changes update already open UI immediately and survive restart; hiding controls preserves underlying session content.
- [ ] Settings and New Chat remain accessible through a stable command even if their usual navigation surface is hidden; reset restores documented defaults.

### 48. Sensitive-span presentation

Baseline: Preference only
Current check: The sensitiveBlurEnabled property exists; no sensitive-span renderer, conceal/reveal or copy/export policy is implemented.
Next implementation instruction: Complete actual rendering and copy/accessibility behavior before claiming the setting works.
Depends on: 10, 47
Deliverable: Presentation layer for explicitly marked sensitive demo spans; detection remains an adapter concern.
Done only when:

- [ ] Marked emails/tokens/secrets are concealed when enabled and can be intentionally revealed with an accessible control.
- [ ] Copy/export behavior is explicit and defaults to concealed content; original sensitive text is not exposed through tooltips or accessibility labels while concealed.
- [ ] Toggle updates existing messages; unmarked text is unaffected and the UI does not claim general secret detection.

### 49. Process/status presentation

Baseline: UI only
Current check: One static session-summary label is available, optionally shown; no expandable process/status containers exist. It remains persistence-labelled after an incognito transition.
Next implementation instruction: Bind session status to actual state immediately; later add provider-supplied progress/status components.
Depends on: 10, 47
Deliverable: Expandable provider-supplied progress summaries and tool status, separate from answer content.
Done only when:

- [ ] Pending/running/completed/failed/cancelled fixtures show clear accessible status and can be expanded/collapsed without disrupting scroll position.
- [ ] Appearance preference shows/hides status summaries without deleting data or changing the main answer.
- [ ] Only supplied summaries and demo status are displayed; the GUI does not invent or claim access to hidden model reasoning.

### 50. Keyboard commands and shortcut editor

Baseline: Partial; registry/editor implemented
Current check: Nine canonical commands, conflict checking, persistent rebinding/clear/reset and a working Shortcuts page exist; tests pass. Favourite/Delete remain intentionally disabled and most tools remain scaffolds.
Next implementation instruction: Complete native focus/text-editing shortcut checks and activate feature commands as their workflows arrive; count the registry as implemented, not all actions complete.
Depends on: 1, 54
Deliverable: Canonical QAction/QShortcut command registry plus persistent user bindings.
Done only when:

- [ ] Navigation, new/favourite/delete session, incognito, tools and TTS demo actions have stable command IDs, labels and documented defaults.
- [ ] Rebinding detects conflicts within the applicable scope, supports clear/reset and restores custom bindings after restart.
- [ ] Commands work from intended contexts without stealing ordinary text editing; disabled commands explain why, and menus/tooltips show current bindings.

### 51. Account flows

Baseline: Scaffold
Current check: Account is now a registered unavailable route reached by the avatar, not an account workflow.
Next implementation instruction: Build demo account forms behind the current route and preserve honest simulated results.
Depends on: 40, 53
Deliverable: Profile, logout, password change and 2FA visual flows backed by an explicit demo account service.
Done only when:

- [ ] Profile details, change-password validation and 2FA setup/verification/cancel/error states are fully navigable.
- [ ] Logout resets demo account/session presentation according to an explicit keep-local-data choice; unsaved edits are protected.
- [ ] All success states say demo/simulated; no real authentication, password update or 2FA enrollment is claimed or persisted as plaintext credentials.

### 52. Profile / Study Mode area

Baseline: Partial entry point
Current check: Avatar button routes to Account and remains visible collapsed; Admin text is static and Study Mode/status switching is absent.
Next implementation instruction: Keep the entry point; add profile/mode state and defined effects after the Account service/view.
Depends on: 51
Deliverable: Interactive sidebar account/status/mode entry.
Done only when:

- [ ] Profile control opens Account; mode/status switching visibly updates the sidebar and relevant session presentation.
- [ ] Study Mode has a defined GUI effect and explanatory text instead of a decorative label; saved non-sensitive preference restores.
- [ ] Profile and mode controls remain accessible in collapsed sidebar mode and by keyboard.

### 53. Shared states and feedback

Baseline: Accepted baseline; regression suite passes
Current check: Existing step-53 evidence records prior acceptance. Shared state components, stale-result protection, retry/cancel fixtures, feedback and retained issues pass the current suite.
Next implementation instruction: Reuse these components in new modules. Source-constructor error-signal timing and startup recovery presentation still need explicit end-to-end evidence; acceptance of components is not blanket acceptance of every caller.
Depends on: 1
Deliverable: Reusable empty, loading, error, retry and toast components plus deterministic demo adapters.
Done only when:

- [ ] Components accept module-specific text/actions while sharing styling, focus behavior and accessible status announcements.
- [ ] Fixtures can explicitly select success, empty, loading, failure and cancellation; retries cannot duplicate requests or apply stale results.
- [ ] Toasts do not steal focus or cover essential controls; important errors remain available after toast dismissal.
- [ ] Every completed feature demonstrates its applicable states using the shared components.

### 54. Persistence and application data

Baseline: Partial; substantial data layer implemented
Current check: Schema v2 SQLite, stable IDs, repositories/services, migration fixture, incognito exclusion, atomic export and transactional import/reset exist; persistence tests pass. Data management has no user-facing import/export/reset surface yet.
Next implementation instruction: Add the management/recovery GUI and malformed-input paths without duplicating repositories. Distinguish working incognito disk exclusion from incomplete session disposal and draft semantics.
Depends on: None
Deliverable: QSettings for preferences/geometry; versioned SQLite for local content and explicit JSON import/export formats.
Done only when:

- [ ] Define stable IDs and repositories for sessions, models, documents, Brain items, notes, tasks, Gallery metadata and related records; UI accesses repositories through services.
- [ ] Normal content, preferences and geometry round-trip on restart; incognito data and credentials are excluded from ordinary stores.
- [ ] Writes are transactional or atomic; corrupted/unavailable stores report recovery options without silently deleting data, and schema upgrades have fixture-based migration checks.
- [ ] Tests and demo runs use isolated temporary storage, and reset/export/import clearly state which local data is affected.

### 55. Fedora desktop validation and release polish

Baseline: Not accepted; offscreen evidence only
Current check: Current run uses Fedora 44 KDE edition, Python 3.14.7, PySide6/Qt 6.11.2 and the offscreen platform. No new GNOME/KDE Wayland pointer, scaling, clipboard, notification or performance pass was performed.
Next implementation instruction: Run the release desktop matrix after functional fixes. Existing historical native-run reports remain historical, not evidence that every current release condition passed.
Depends on: All feature steps selected for the release
Deliverable: Native desktop behavior, accessibility, rendering parity, performance and clean shutdown.
Done only when:

- [ ] Record Fedora version, desktop/session type, Qt/PySide6 version, GPU and display scale; run the acceptance flows under both GNOME Wayland and KDE Wayland, with any unsupported environment explicitly scoped out.
- [ ] Check 100%, 150% and 200% display scaling, minimum/default/maximized layouts, focus/tab order, clipboard, drag/drop and native file dialogs; no unreachable primary control or unreadable text remains.
- [ ] If real local desktop notifications are included, opt-in/test/delivery/failure are verified on each supported desktop; otherwise the release labels them simulated.
- [ ] Closing during background/demo work stops timers/jobs safely and restores valid state on restart; no unintended process remains.
- [ ] Compare matched-state captures against the supplied references; document intentional native differences and verify the performance fixture targets in the acceptance protocol.

## ACCEPTANCE PROTOCOL AND TRACKING

For each step keep a short evidence record in docs/acceptance/ when it
is implemented. Suggested fields: step ID, status, build/revision, date, tester,
OS/session/Qt/display scale, fixture and storage location, actions, expected and
actual result, evidence paths, remaining failures. Documentation alone is not
acceptance evidence. Mark checkboxes only after executing the corresponding check.
Keep STATUS.md aligned with actual evidence and next action; keep ROADMAP.md
limited to execution order. Historical acceptance records retain their original
environment and date. Do not mark a step Done merely by updating documentation.

Reference comparisons:
- Match feature, selected theme, expanded/collapsed sidebar, window size and tool
  state before comparing. Record the source screenshot filename or video time.
- Check layout hierarchy, proportions, control order, spacing, typography, colors,
  borders, empty states and interaction. Native window chrome/file dialogs may
  differ intentionally; document those differences rather than claiming parity.
- Use Copper and Ocean for the detailed reference flows and Forest for home/
  background comparison; also verify Light and one other dark preset for contrast.

Shared performance fixtures (targets, to be measured on a recorded machine):
- 200 messages with mixed prose/code; 1,000 searchable content records; 500 photos
  with cached thumbnails; editor project of 2048×2048 pixels and five layers.
- After warm-up, local search at these sizes returns within 300 ms; ordinary
  selection/tab changes respond within 100 ms. Expensive I/O/decoding/processing
  shows progress promptly and does not block the GUI event loop for >100 ms.
- Background animation uses the step 36 target. Record measurement method, p95
  where applicable, and any bounded cache/history settings. Do not silently lower
  thresholds; revise the documented target with a rationale if hardware demands it.
- Repeatedly open/close ten tools and switch sessions/themes twenty times; verify
  that retained widgets, timers and background jobs do not accumulate unboundedly.

Release completion requires all 55 steps to satisfy this plan, or an explicitly
revised release scope listing deferred IDs. External backend integration is a
separate future plan with its own authentication, network, execution and service
acceptance tests. It is never inferred from a successful GUI simulation.

## Repository consolidation — 21 September 2026

Document roles and architectural contracts now live in this repository. The latest
repeat verification passed 65/65 tests and the smoke check offscreen; its logs and
source manifest are in docs/acceptance/evidence/2026-09-21-offscreen/. See
[the dated record](docs/acceptance/2026-09-21-offscreen.md). This corroborates prior
automated results, not the unresolved manual checks or defect fixes.
Git has no repository/HEAD here; no known-good commit/tag has been invented.
Next implementation remains R1, starting with failed-send draft preservation.
