# Local composer utilities plan

Status: proposed execution plan  
Date: 23 September 2026  
Canonical requirements: `PLAN.md` steps 07 and 08, with preservation boundaries
for steps 04, 06, 09, 27, 28, 47, 50 and 53

## Objective

Complete the reusable local utilities around Otter Cove's composer without model
configuration, inference, provider adapters, web access or command execution. The
milestone supplies an accessible anchored popover, safe attachment draft state,
native file and workspace selection, stable command-backed action registration and
clearly labelled deterministic Web Search and Shell simulations.

The result is infrastructure later model/request work can consume. It must not
pretend that selected files have been sent to a model, that a web search occurred,
or that a shell command ran.

## Scope boundary

Included:

- Shared anchored popover/focus primitive used by the composer tool menu.
- Attach Files selection, validation, removable chips and draft ownership.
- Workspace folder selection and visible local context descriptor without scanning
  or executing content.
- Typed Documents and Prompt entry adapters with honest availability states.
- Command-backed composer action registry with stable IDs and ordering.
- Deterministic Web Search and Shell demo actions with loading, success, empty,
  failure, cancellation, retry and stale-result protection.
- Appearance visibility controls once the corresponding simulated action is real.
- Normal/Nobody draft isolation and disposal for attachments/workspace selection.
- Automated and native Fedora interaction/accessibility evidence.

Excluded:

- Model selector, request builder, tokenization, context-window handling and
  inference.
- Reading attachment contents for a model or uploading/sending them anywhere.
- Persisting draft file contents or absolute paths in SQLite/export.
- Recursive workspace indexing, code execution, file watching or repository tools.
- Real network search, browser automation, subprocess/shell execution or terminal
  emulation.
- Implementing Documents/Library or Prompt Studio inside this milestone.
- Claiming full completion of composer step 04.

## Cross-area completion boundaries

1. Step 07's popover, file attachment and workspace behavior can finish here. Its
   Documents entry is revalidated when steps 27/28 provide the real module; its
   Prompt entry remains unavailable until step 09 exists. Canonical step 07 stays
   Partial until both open their actual modules.
2. Attachment draft ownership and failure preservation can finish here, but step
   04 remains Partial until a later request record includes the selected model,
   mode and accepted attachment descriptors.
3. Step 08 can meet its GUI-milestone acceptance using explicit simulations. This
   enables only the Web Search and Shell visibility settings; other unavailable
   Appearance controls retain their own gates.
4. Step 06's Nobody attachment exclusion can be demonstrated here and added to the
   privacy evidence from the Sessions/Conversation plan.

## Current baseline

- The composer has fixed Web Search and Shell buttons, currently disabled and
  labelled unavailable because no consumers exist.
- Their old clicks routed to unrelated Search/Tools scaffolds; there is no composer
  action registry.
- There is no tool-menu trigger, attachment descriptor/chip, workspace selection,
  anchored popover or Documents/Prompt entry.
- `ComposerDraft` owns text and Agent/Chat mode per concrete session or pending
  privacy slot. Failed local message storage retains text/mode and safe retry clears
  once after success.
- Normal and Nobody views/drafts are isolated; New Chat disposes live Nobody state.
- Shared command, feedback and deterministic demo-state infrastructure exists and
  should be reused rather than duplicated.

## Architectural decisions

### Anchored popover

- One presentation primitive owns anchor tracking, bounded placement, focus entry,
  Escape/outside-click dismissal and focus restoration.
- Popover content is injected; the primitive contains no model, document or action
  business logic.
- Only one composer popover is active at a time. Reopening the current trigger
  toggles it; opening another replaces it without orphan widgets or event filters.
- Placement is recalculated after host resize, scale change and anchor movement and
  remains inside the available workspace.

### Attachment draft state

- Add an immutable typed descriptor containing a generated draft-local ID, display
  name, canonical local path, kind/MIME, byte size, source and availability state.
- Absolute paths and file contents remain transient draft state. They are not put
  into message metadata, SQLite, QSettings, export, logs or diagnostics in this
  milestone.
- Define documented maximum attachment count, per-file size and supported-type
  policy before implementation. Limits must produce readable per-file errors and
  must not be silently raised to pass a fixture.
- Validate that a selection is an existing readable regular file. Never execute,
  import or parse selected files beyond the minimum metadata/type inspection.
- File changes/removal after selection produce a stale/unavailable chip state; they
  do not trigger background reads.
- Draft text, mode, attachments and workspace descriptor form one session-owned
  draft aggregate for switch/failure/disposal behavior.

### Workspace descriptor

- Store one canonical selected directory path in the in-memory draft aggregate.
- Display name/path and a clear “selected only; not scanned or executed” status.
- Selection performs no recursive enumeration, symlink traversal, file reading,
  watcher installation or persistence.
- Removal and session/privacy switching follow the same draft ownership as files.

### Composer actions

- Introduce a pure registry of immutable action specs: stable ID, label, icon key,
  order, preference key, availability, disabled reason and handler key.
- Use distinct IDs such as `composer.web_search_demo` and
  `composer.shell_demo`; never reuse conversation-search or general Tools routes.
- The registry controls visible order and enabled state. Adding an action does not
  require changing composer layout code.
- Handlers run through deterministic demo adapters and shared state/feedback. The
  registry never directly performs I/O, network access or subprocess execution.

## Execution packages

### CU-0 — Contracts, threat boundary and baseline

Purpose: define what local selection and simulation mean before visible controls
suggest stronger behavior.

Work:

1. Start from the accepted Foundation/Desktop and session draft/privacy contracts.
2. Record the exact baseline SHA and run the full suite, compile checks and isolated
   smoke with no skips.
3. Define the attachment count/size/type policy, error behavior, transient path
   policy and stale-file behavior.
4. Define the workspace descriptor and confirm no scanning/indexing/execution.
5. Define action IDs, labels, preference mapping, ordering and exact simulated
   wording for Web Search and Shell.
6. Add a security assertion/test seam proving composer demo handlers have no
   network client or subprocess dependency.
7. Define when attachment-bearing Send is allowed. Until step 04 has an accepted
   attachment submission record, sending must not silently discard or claim to
   consume attachments; use a clear actionable unavailable state.

Exit:

- Data/state contracts and limits are documented and reviewed.
- No path can mistake transient selections or simulations for executed work.
- Baseline checks pass on one recorded source revision.

### CU-1 — Shared anchored popover primitive

Purpose: create one reliable keyboard/pointer surface for composer utilities and
later selectors.

Work:

1. Implement the primitive with an anchor widget and injected content widget.
2. Place below/above the anchor based on available space; clamp horizontally and
   vertically inside the workspace at minimum/default/maximized sizes.
3. Move focus to the first enabled control on keyboard open. Preserve a sensible
   pointer-open focus policy and restore focus to the trigger after dismissal.
4. Support Tab/Shift+Tab, arrows where the content exposes a list, Enter/Space,
   Escape and outside-click dismissal.
5. Close/reposition safely on anchor destruction, host resize, tool minimize,
   route change and application deactivation without leaking event filters.
6. Expose accessible popup role/name, item states and disabled reasons.
7. Verify repeated open/close/replacement does not accumulate widgets, signals or
   filters and never leaves an invisible input blocker.

Automated evidence:

- Edge/corner placement and host-resize clamping.
- Keyboard traversal, Escape and focus return.
- Outside click, replacement and destroyed-anchor lifecycle.
- Repeated-cycle ownership/leak regression.

Exit:

- The primitive is reusable and contains no feature-specific state.
- Native pointer/focus behavior is the only remaining platform evidence.

### CU-2 — Session-owned attachment/workspace drafts

Purpose: extend draft ownership without weakening failure or Nobody guarantees.

Work:

1. Extend the draft aggregate with ordered attachments and optional workspace
   descriptor while preserving text/mode compatibility.
2. Provide add, remove, clear, reorder (only if exposed), mark-unavailable and
   replace-workspace operations through a presentation-neutral draft controller.
3. Generate stable IDs for the live draft so duplicate filenames remain distinct.
   De-duplicate the same canonical path within one draft with a visible explanation.
4. Preserve the complete aggregate across normal session switches and storage
   failures. A newer edit cannot be cleared by a stale acceptance callback.
5. Keep pending normal and pending Nobody drafts separate before either session has
   a record ID.
6. Dispose private attachments/workspace path on Close Nobody and New Chat. Verify
   they never enter SQLite, QSettings, export, logs, search or error details.
7. On persistent New Chat, preserve prior concrete-session draft ownership and
   start an empty pending aggregate under the established session policy.

Exit:

- Attachment/workspace state obeys the same tested ownership as text/mode.
- Nobody disposal removes every reference from application-owned state.
- No durable storage schema is added for transient paths/content.

### CU-3 — Tool menu, native files and workspace UI

Purpose: expose safe local selection with clear state and recovery.

Work:

1. Add a keyboard-focusable tool-menu trigger with accessible name, tooltip and
   current-state indication.
2. Populate Attach Files, Documents, Workspace and Prompt entries from typed specs,
   including enabled state and disabled reason.
3. Attach Files opens a native multi-file picker. Cancel is a strict no-op. Validate
   each selected file under CU-0 policy and report accepted/rejected items without
   losing previously attached files.
4. Render removable attachment chips with filename, type/kind, size, availability,
   keyboard removal and full accessible description. Long names elide visually but
   remain available accessibly without exposing paths unnecessarily.
5. Chips wrap or use a bounded scroll region and never cover the editor, mode or
   Send controls at 1100×680 and Large/Roomy.
6. Workspace opens a native directory picker and shows its transient descriptor
   plus remove/change actions and non-scanning explanation.
7. Missing/unreadable/stale paths update only the affected chip and offer remove or
   reselect; no automatic read/retry loop occurs.
8. Closing/reopening the tool menu preserves the draft; changing routes or opening
   tools does not clear it.

Exit:

- File and workspace happy/cancel/invalid/stale states are usable by pointer and
  keyboard.
- Selected content is not read, persisted, executed or sent.

### CU-4 — Documents and Prompt entry contracts

Purpose: avoid hard-coded placeholder routing while respecting later module gates.

Work:

1. Define a document-picker provider interface that returns stable document IDs and
   display metadata from the shared Document service; do not create a second store.
2. Until steps 27/28 implement the picker/view, show Documents as unavailable with
   its dependency and a working route to the existing honest module state where
   useful.
3. Define a Prompt entry route/command contract without storing prompt definitions
   or implementing step 09.
4. Until Prompt Studio exists, keep Prompt unavailable with a precise explanation;
   do not substitute a fake prompt editor.
5. Add contract tests so later modules can enable the entries without changing the
   popover or draft ownership APIs.

Exit:

- Both entries have stable typed integration points and truthful current states.
- Canonical step 07 remains Partial only for the named Documents/Prompt module
  gates after local file/workspace behavior passes.

### CU-5 — Command-backed composer action registry

Purpose: remove fixed button/route coupling and make action behavior extensible.

Work:

1. Implement the pure registry and reject duplicate IDs, order collisions and
   missing handlers or disabled reasons.
2. Render composer action buttons/menu items entirely from registered specs while
   preserving current layout, accessibility and theme behavior.
3. Bind actions through canonical command handlers where shortcuts/global menus are
   exposed; retain composer-local scope for controls without global bindings.
4. Separate conversation Search (`navigation.search`) from simulated Web Search
   (`composer.web_search_demo`) in IDs, labels, tooltips and routing.
5. Replace the Shell-to-Tools route with `composer.shell_demo`; no generic tool
   route may be presented as execution.
6. Make preference changes recompute visible actions immediately without deleting
   their local fixture state. Restart restores documented visibility.
7. Unknown/unavailable actions fail closed and display their reason rather than
   calling a fallback route.

Exit:

- Step 08 has stable registry-backed actions and adding one requires no composer
  layout edit.
- Search and shell labels cannot be confused with unrelated modules or real I/O.

### CU-6 — Deterministic Web and Shell simulations

Purpose: satisfy the GUI milestone's optional-action behavior without external
effects.

Work:

1. Build dedicated deterministic adapters with explicit scenario selection for
   loading, success, empty, failure and cancellation.
2. Allocate operation IDs and reject stale or duplicate completion. Retry creates a
   fresh ID and never duplicates a result.
3. Web Search demo displays fixed local fixture results/citations labelled
   “Simulated — no web request was made.” It does not accept or fetch arbitrary URLs.
4. Shell demo displays fixed command/output fixtures labelled
   “Simulated — no command was executed.” User text is never passed to a subprocess.
5. Cancellation leaves the composer draft/attachments unchanged. Errors remain
   available through shared feedback after transient toast dismissal.
6. Route output into an explicit local demo panel/status surface, not an assistant
   answer that could be mistaken for model content.
7. Add tests that patch/guard networking and process launch boundaries and fail if
   either adapter attempts external I/O.
8. After the consumers pass, enable Web Search and Shell Appearance controls,
   update their explanations to “simulated,” and verify live/restart/reset behavior.

Exit:

- Step 08's success/error/cancel/retry and no-I/O claims have automated evidence.
- The two Appearance controls describe and control only implemented simulations.
- Sensitive blur and all unrelated unavailable controls remain unchanged.

### CU-7 — Integration, native matrix and evidence closeout

Purpose: validate the completed utilities in real composer/session states and
record exact partial/full boundaries.

Integration work:

1. Exercise tool menu, file/workspace selections and simulated actions in pending
   and concrete persistent drafts plus pending/live Nobody drafts.
2. Verify session switching restores the correct aggregate and opening Theme,
   Settings or another tool preserves it.
3. Inject local message storage failure while attachments exist. Confirm text,
   mode, chips and workspace survive unchanged and retry cannot duplicate state.
4. Until step 04 accepts attachment submission records, prevent Send from claiming
   attachment consumption or clearing them; present the CU-0 actionable state.
5. Verify Close Nobody/New Chat disposes private selections and no exported/local
   data or diagnostic string contains their paths/names.

Native matrix:

- Fedora KDE Wayland and GNOME Wayland where supported.
- 100%, 150% and 200% scaling at 1100×680, normal and maximized layouts.
- Pointer and keyboard-only popover, file/directory dialogs, chips and demo actions.
- Light/dark themes plus Large/Roomy and long filename/path fixtures.

Evidence and closeout:

1. Run the full suite with no skips, isolated smoke and native cells against one
   exact commit.
2. Store curated evidence under
   `docs/acceptance/evidence/<date>-composer-utilities/` with manifest, automated
   log, native checklist and necessary captures.
3. Update PLAN current checks and acceptance records. Mark step 08 Done only if all
   simulated action criteria pass. Keep step 07 Partial for Documents/Prompt and
   step 04 Partial for the request/submission contract.
4. Add the completed Nobody attachment-exclusion result to step 06 evidence without
   reopening unrelated session implementation.
5. Update `STATUS.md`, `ROADMAP.md` and `CHANGELOG.md` with exact completed and
   deferred boundaries.

Exit:

- Local file/workspace selection, draft ownership and demo actions have automated
  and native evidence.
- No file content/path is persisted or sent and no network/process I/O occurs.
- Cross-area gates remain named and no model/composer completion is overstated.

## Interaction acceptance table

| State | Action | Required result |
|---|---|---|
| Popover closed | Open by pointer | Bounded popup opens; trigger remains coherent |
| Popover closed | Open by keyboard | Popup opens and first enabled item receives focus |
| Popover open | Escape/outside click | Close once and restore trigger focus appropriately |
| Popover open | Host resize/anchor move | Reposition inside workspace; no detached overlay |
| Draft | Cancel native file/folder dialog | Strict no-op; retain draft and selections |
| Draft | Select valid and invalid files | Add valid chips; report each invalid item; retain prior chips |
| Draft | Remove/reselect stale file | Change only that descriptor; never read automatically |
| Persistent session | Switch away/back | Restore its text, mode, files and workspace only |
| Nobody session | Close/New Chat | Dispose text, files, paths, workspace and demo status |
| Web demo | Run/cancel/retry | Label simulation; no request; reject stale completion |
| Shell demo | Run/cancel/retry | Label simulation; no subprocess; reject stale completion |
| Attachment-bearing draft | Send before step 04 contract | Do not clear/claim consumption; explain required next step |

## Required fixtures

- Empty draft; text-only draft; file-only and mixed draft.
- Duplicate filenames at different paths and duplicate canonical path selection.
- Long Unicode filename, unsupported type, oversized, unreadable, missing and
  directory-selected-as-file cases.
- Workspace directory with nested files, symlink and executable-looking names to
  prove no enumeration/execution.
- Pending/concrete persistent and pending/live Nobody draft ownership.
- Web/Shell loading, success, empty, failure, cancellation, retry and stale result.
- Minimum-size Large/Roomy layout and 100/150/200% native scale.

Fixtures use temporary local paths, synthetic names and no credentials or personal
content. Tests clean them up and must not print absolute private paths unnecessarily.

## Defect loop

For every failure:

1. Record build, desktop/scale, draft/session privacy state, action and actual result.
2. Classify popover lifecycle, draft ownership, file validation, registry/command,
   demo state, privacy or native dialog/layout behavior.
3. Add the smallest deterministic regression where the platform is not the subject.
4. Fix the owning primitive/controller/registry instead of adding route-specific
   widget exceptions.
5. Run focused tests, full suite, smoke and the failed native cell.
6. Keep the criterion open until its required real environment passes.

## Final acceptance gate

This area is ready to hand to Documents/Library and later composer work only when:

- CU-0 through CU-7 exits are satisfied for one recorded revision;
- the full automated suite passes with no skips and native evidence identifies the
  actual platform/session/scale;
- popover placement, dismissal, focus and lifecycle work across the matrix;
- attachment/workspace state is bounded, accessible, session-owned and transient;
- Nobody disposal and export/search/diagnostic exclusion are demonstrated;
- Web/Shell demos cover all states and automated guards prove no network or process
  execution path;
- Appearance visibility accurately controls the implemented simulated actions;
- Send cannot silently consume or discard attachments before step 04 accepts them;
- Documents, Prompt and full composer/request gates remain explicitly Partial; and
- documentation states exactly which criteria are complete and which later module
  must perform each revalidation.
