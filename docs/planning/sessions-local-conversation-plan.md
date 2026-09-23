# Sessions and local conversation presentation plan

Status: proposed execution plan  
Date: 23 September 2026  
Canonical requirements: `PLAN.md` steps 03, 06, 10, 11, 48 and 49, with
preservation boundaries for steps 04, 47, 50, 53 and 54

## Objective

Complete Otter Cove's local session lifecycle and conversation presentation
without model configuration, inference, provider adapters or network requests.
Users should be able to create, navigate, rename, favourite, archive, restore and
delete persistent sessions; use a truthful memory-only Nobody session; inspect
safe local message fixtures; search persistent history; and understand explicit
sensitive spans and deterministic process/status fixtures.

No generated response is required. Assistant, tool, code, streaming and status
content in this milestone comes from deterministic local fixtures and is visibly
identified where a user could otherwise mistake it for live model output.

## Scope boundary

Included:

- Home and zero-message session presentation (03).
- Persistent/Nobody switching, draft ownership and private disposal (06).
- Session browser, CRUD and reusable safe message rendering (10).
- Persistent local session/message search (the conversation portion of 11).
- Explicitly marked sensitive-span conceal/reveal/copy behavior (48).
- Expandable deterministic process/status presentation (49).
- Activation of existing session commands only when their workflows are real.
- Automated, offscreen visual and native Fedora acceptance for this selected area.

Excluded:

- Model selector/configuration, model request construction and inference.
- Completing composer step 04, attachments step 07 or optional actions step 08.
- Prompt Studio, web search, shell execution and online/local model tools.
- Automatic secret detection, automatic memory/skill extraction or hidden-reasoning
  display.
- Library/document search, which is added when steps 27/28 are implemented.
- Notes-dock implementation, which is added under the productivity area.

## Cross-area completion boundaries

This plan intentionally records rather than hides three later gates:

1. Step 03's session behavior and responsive workspace implementation can finish
   now, but its explicit Notes-dock width criterion is re-run when step 30 exists.
2. Step 11's local history provider can finish now, but the canonical step remains
   Partial until Library metadata/content search from step 27 is connected.
3. Step 06 can prove disk/export/search exclusion now. Attachment and extraction
   exclusions are re-run when steps 07 and 16 introduce those consumers.

These deferred checks do not justify placeholder implementations. The interfaces
and privacy policy must make later consumers opt in to persistent records rather
than receive Nobody content by default.

## Current baseline

- Persistent session/message repositories and `SessionService` exist.
- The latest persistent session restores at startup and normal messages render as
  local user cards.
- Failed message storage retains the complete draft and selected mode; successful
  retry clears once and adds one message.
- Persistent and Nobody views have isolated messages/drafts and truthful storage
  summaries. New Chat disposes the live Nobody session.
- Nobody records are process-memory-only and excluded from SQLite and local-data
  export.
- No session browser, rename/favourite/archive/delete UI, rich message renderers or
  local history search provider exists.
- The current storage-status text is accurate, but there is no general expandable
  process/status component.
- Sensitive blur is correctly disabled as unavailable; no renderer or copy policy
  exists. `PLAN.md` current-check wording must be reconciled with this source state
  before step 48 work begins.

## Architectural decisions to preserve

1. `SessionService` is the presentation-facing boundary. Widgets do not issue SQL.
2. Persistent and Nobody sessions use the same public operations where safe, while
   private records remain owned exclusively in process memory.
3. A selected session ID owns its messages, draft and view state. A pending normal
   or Nobody slot owns draft state before the first accepted message.
4. Session/message storage is independent from rendering and provider execution.
5. Search receives persistent records through a local provider contract; it never
   inspects `SessionService`'s private in-memory collections.
6. Renderers consume validated local presentation records. Rich text never executes
   HTML, scripts or code.
7. Sensitive spans are explicit metadata supplied by fixtures or future trusted
   adapters. The GUI does not claim detection.
8. Process/status fixtures contain supplied summaries only. They never expose or
   invent hidden model reasoning.

## Data and state changes

Before UI work, define the durable contracts:

- Add an atomic schema migration for session favourite state if it is not already
  represented by a dedicated field. Do not hide a core query/sort field in opaque
  metadata merely to avoid a migration.
- Preserve stable session/message IDs and existing created/updated timestamps.
- Add repository/service operations for rename, favourite, archive/restore and
  delete with explicit not-found/error outcomes.
- Define ordering: active non-archived sessions first by `updated_at`, with
  favourite ordering deterministic and archived records separately queryable.
- Define delete semantics: destructive confirmation is required; archive remains
  the reversible ordinary removal path. If undo is offered, its snapshot/expiry
  and restart behavior must be explicit.
- Define validated message presentation metadata for fixture kind, timestamp,
  language/code, sensitive spans and status data. Reject malformed ranges/states
  at the service boundary.
- Drafts restore while switching live sessions. This plan does not add restart
  persistence for unsent drafts unless `PLAN.md` is explicitly revised.
- Define per-session transient view state for scroll-follow and expanded statuses;
  do not persist it unless a user-facing restore requirement is added.
- Extend local-data import/export and migration fixtures for any new durable field.

## Execution packages

### SC-0 — Establish contracts and baseline

Purpose: prevent UI work from creating a competing session store or ambiguous
privacy behavior.

Work:

1. Start from the accepted Foundation/Desktop baseline, including PR #6 or its
   recorded replacement.
2. Record the exact SHA and run the full suite, compile checks and isolated smoke.
3. Reconcile PLAN steps 06, 48 and 49 current-check text with the implemented R1
   privacy/status changes; do not change their acceptance conditions.
4. Write the session lifecycle table covering persistent pending, persistent live,
   Nobody pending, Nobody live, archived and deleted states.
5. Write explicit policies for draft ownership, close/New Chat, privacy-mode changes
   after messages exist, archive, delete and restart.
6. Decide the favourite storage/migration shape and the validated message/status
   metadata shape before modifying widgets.

Exit:

- One source revision and passing baseline are recorded.
- Lifecycle transitions and ownership have no undefined branch.
- Schema/service changes are reviewable independently from presentation changes.

### SC-1 — Session repository and service lifecycle

Purpose: make every user-visible session action use one transactional local model.

Work:

1. Add the schema migration and v2-to-current fixture if favourite or other durable
   query fields require it.
2. Implement service operations for create, get, list active, list archived,
   rename, favourite/unfavourite, archive/restore and delete.
3. Validate blank/overlong titles and normalize only documented whitespace; never
   silently merge distinct sessions.
4. Make missing IDs, constraint failures and unavailable stores return the existing
   user-oriented data errors without partially updating memory/UI state.
5. Keep message order monotonic and deterministic through reopen/import. Deleting a
   session removes its durable messages transactionally.
6. Preserve Nobody operations in memory and prohibit archive/favourite operations
   that would imply persistence; expose a clear unsupported outcome to the UI.
7. Update import/export counts, field validation and credential/privacy assertions.

Automated evidence:

- CRUD, ordering and restart round trips.
- Migration from the previous schema with messages intact.
- Transaction rollback on injected failure.
- Archive/restore and confirmed delete behavior.
- Nobody operations never touching SQLite/export.

Exit:

- The service is the only source of truth for all session actions.
- Persistent and private lifecycle tests pass with isolated storage.

### SC-2 — Session browser and Home states

Purpose: expose existing sessions without losing the active conversation or draft.

Work:

1. Turn the current chat-title affordance into an anchored session browser using a
   shared popover/floating primitive rather than a second navigation framework.
2. Show active sessions with title, updated time, favourite and storage state;
   provide a separate archived view or filter.
3. Implement keyboard traversal, selection, rename, favourite, archive/restore and
   confirmed delete. Outside click/Escape returns focus to the trigger.
4. Activate Favourite/Delete commands only when their action is valid; tooltips and
   menus display current bindings and disabled reasons.
5. Save the outgoing draft before selection and restore the incoming session draft.
   A failed load keeps the current session rendered and reports the error.
6. Render a restored zero-message session as Home/welcome, then replace it with
   conversation content only after the first accepted stored message.
7. New Chat creates a separate pending persistent slot and never overwrites or
   deletes the prior session/draft.
8. Keep hero/composer centered as sidebar and host width change. Add a reusable
   layout assertion that step 30 can rerun when the Notes dock arrives.

Exit:

- Steps 03/10 session navigation and empty/restored state behavior work by mouse
  and keyboard.
- Switching, errors and destructive actions never mix or silently lose drafts.
- The Notes-dock-specific step-03 criterion remains explicitly pending.

### SC-3 — Nobody privacy lifecycle

Purpose: make mode transitions explicit and prevent accidental persistence or
cross-session presentation.

Work:

1. Keep a persistent visible Nobody indicator and an accessible tooltip explaining
   memory-only, process-local behavior and New Chat/close disposal.
2. When messages exist and the user changes privacy mode, present an explicit
   choice: switch and retain the live session for return, start a new session, or
   cancel. Never copy content between modes.
3. Render only the selected mode's session, draft and statuses. Returning to a live
   mode restores only its owned state.
4. Define Close Nobody separately from ordinary switching. Closing disposes its
   messages, draft, sensitive state and status fixtures immediately.
5. Verify New Chat closes any live Nobody session and returns to a blank persistent
   pending slot.
6. Ensure session browser, local search, export, diagnostics and error messages do
   not enumerate or serialize Nobody content.
7. Restart after private use and verify no private session, content, title, draft or
   derived search data returns.
8. Add explicit later-consumer tests/hooks so attachments and extraction features
   must request persistent sessions and cannot receive private content by default.

Exit:

- Step 06's current persistence, view isolation, transition and disposal behavior
  has automated plus native visual evidence.
- Future attachment/extraction revalidation remains named, not presumed complete.

### SC-4 — Safe message renderers and deterministic streaming

Purpose: complete conversation presentation without coupling it to a model.

Work:

1. Introduce reusable renderers for user, assistant fixture, system/tool, code and
   status records with stable accessible role/name/description behavior.
2. Support selection, copy and timestamps. Sanitize/escape rich text; code blocks
   are inert text and no embedded HTML/script is executed.
3. Use deterministic local fixtures for assistant/tool content and visibly label
   fixture/demo output where provenance could be ambiguous.
4. Implement a local streaming fixture with pending/running/completed/failed/
   cancelled states. Retry uses a new operation ID; stale/duplicate completion is
   ignored.
5. Separate partial streaming presentation from durable messages. Persist only the
   accepted terminal fixture result under an explicit policy; failure/cancel must
   not create a completed assistant record.
6. Track whether the user is following the bottom. Auto-follow only while following;
   manual upward scroll is never pulled away by updates.
7. Render a 200-message mixed fixture with correct ordering, bounded widget/cache
   ownership and responsive selection/copy/scroll.
8. Reopen a persisted normal session and verify exact message order and safe
   renderer choice independently of any provider.

Exit:

- Step 10 message/render/streaming criteria pass using labelled deterministic data.
- No renderer can execute content or imply a live model response.
- Long-history behavior meets the shared interaction target and does not leak
  widgets/timers over repeated session changes.

### SC-5 — Persistent local history search

Purpose: provide useful conversation search through a replaceable local provider.

Work:

1. Define a local search-provider protocol whose initial implementation queries
   persistent session titles and message text through repositories/services.
2. Exclude archived records by default with an explicit include-archived filter.
   Nobody content must be structurally unavailable to the provider.
3. Return stable result IDs, source/session title, safe snippet, timestamp and match
   location sufficient to open the correct session/message.
4. Implement debounced query generations so edited queries cannot display stale
   results. Cover empty, loading/searching, results, no matches and failure/retry.
5. Make Ctrl+F open/focus the search surface; arrows move results, Enter opens one
   and Escape restores focus without changing the draft.
6. Opening a result selects the correct persistent session and scrolls/highlights
   the matched message without altering content.
7. Exercise a 1,000-record local fixture against the shared warm-search target and
   record method/results; expensive search must not block the GUI event loop.
8. Leave a typed Library-provider extension point. Do not add placeholder Library
   results or mark canonical step 11 Done before step 27 connects them.

Exit:

- Persistent conversation search is complete and independently tested.
- Nobody exclusion is demonstrated through query results and provider inputs.
- Step 11 remains Partial solely for its named Library integration gate.

### SC-6 — Sensitive spans and process/status presentation

Purpose: enable the currently unavailable presentation preferences only after they
have observable, safe behavior.

Sensitive spans:

1. Define explicit validated span metadata with non-overlapping in-bounds ranges
   and semantic labels. Reject malformed ranges without exposing hidden text.
2. Conceal marked fixture emails/tokens/secrets when enabled and provide an
   intentional keyboard-accessible reveal/conceal action.
3. Default copy/export to redacted text. If original-copy is offered, require an
   explicit action and clear warning; never expose originals through tooltips,
   accessible labels, selection previews or logs while concealed.
4. Update existing rendered messages immediately when the preference changes.
   Unmarked text remains unchanged; UI copy states that detection is not provided.
5. Enable the Appearance control only after this renderer and policy pass focused
   tests. Use fake fixture secrets only.

Process/status:

1. Replace the static overloaded summary concept with two explicit surfaces:
   session storage status and expandable supplied process/status entries.
2. Support pending/running/completed/failed/cancelled deterministic fixtures with
   accessible announcements, timestamps and module-supplied summaries.
3. Preserve scroll position when expanding/collapsing. Hiding status summaries
   changes presentation only and never deletes status or answer content.
4. Never label a summary as chain of thought, internal reasoning or hidden model
   state. Display only fixture/adapter data that was explicitly supplied.
5. Keep private-session statuses in memory and dispose/exclude them with the Nobody
   session.

Exit:

- Steps 48 and 49 satisfy their full local presentation criteria.
- The Sensitive blur and status-summary Appearance controls become enabled only
  for behavior that actually exists; unrelated Web Search/Shell controls remain
  unavailable.

### SC-7 — Native, performance and evidence closeout

Purpose: validate real interaction and accurately record complete versus pending
cross-area conditions.

Native matrix:

- Fedora KDE Wayland and GNOME Wayland where supported; unavailable environments
  are explicitly scoped out.
- 100%, 150% and 200% scale at 1100×680, normal and maximized layouts.
- Mouse and keyboard-only session browser, confirmations, search and reveal/status
  interactions.
- Light plus representative dark themes, Small/Default/Large text and
  Compact/Comfortable/Roomy density.

Work:

1. Run the full suite with no skips, isolated smoke and the selected native matrix
   against one exact commit.
2. Exercise fresh, zero-message, populated, archived, failed-load and 200-message
   persistent sessions plus pending/live Nobody states.
3. Verify focus return, accessible names/status announcements, ordinary copy and
   text selection, context menus and confirmation cancel paths.
4. Measure local search with 1,000 searchable records and renderer interaction with
   200 mixed messages. Record warm-up, machine, sample count and actual response.
5. Close/reopen tools and restart the application after normal/private use. Confirm
   persistent records restore and private records do not.
6. Store curated evidence under
   `docs/acceptance/evidence/<date>-sessions-conversation/` with manifest, automated
   log, native checklist, performance result and necessary captures.
7. Update acceptance records and `PLAN.md` current checks. Mark steps 10, 48 and 49
   Done only if all criteria ran. Keep step 03 pending for Notes-dock layout, step 06
   pending for future attachment/extraction revalidation if required by the
   canonical wording, and step 11 pending for Library search.
8. Update `STATUS.md`, `ROADMAP.md` and `CHANGELOG.md` to state exactly which
   implementation and acceptance boundaries were completed.

Exit:

- Session CRUD, privacy, renderers, local history search and presentation policies
  have automated and native evidence.
- Performance fixtures meet the shared targets or retain a documented open defect.
- Cross-area gates are named precisely and no model-side completion is claimed.

## State-transition acceptance table

| From | Action | To | Required result |
|---|---|---|---|
| Persistent pending | First accepted local message | Persistent live | Create one session/message, hide Home, clear accepted draft once |
| Persistent live | Select another persistent session | Persistent live | Save outgoing draft, render only target records, restore target draft |
| Persistent live | New Chat | Persistent pending | Keep prior session, show zero-message Home, start separate draft slot |
| Persistent live | Toggle Nobody | Nobody pending/live | Apply explicit transition choice; never copy content |
| Nobody pending | First accepted local message | Nobody live | Allocate memory-only record; no SQLite/export row |
| Nobody live | Return to persistent | Persistent pending/live | Retain private state only in process for deliberate return |
| Nobody live | Close Nobody or New Chat | Persistent pending | Dispose private messages/draft/status and make them unreachable |
| Active persistent | Archive | Archived | Remove from active list, retain stable record/messages, allow restore |
| Archived | Restore | Persistent live/pending | Return to deterministic active ordering without duplication |
| Persistent | Confirm delete | Deleted | Transactionally remove session/messages and clear selection/draft |
| Any editable state | Storage/load failure | Same state | Preserve visible content/draft, show recoverable error, allow retry |

## Required fixtures

- Fresh database with no sessions.
- Restored zero-message session.
- Multiple persistent sessions with distinct drafts and messages.
- Active and archived favourites with deterministic timestamps.
- Missing/deleted selected session and injected unavailable-store failures.
- Pending/live Nobody session containing unmistakably private fixture text.
- User, assistant fixture, system/tool, code and every status-state message.
- Valid and malformed explicit sensitive-span metadata using fake secrets.
- 200-message mixed render fixture and 1,000-record search fixture.
- Light/dark, large/roomy and minimum-size presentation states.

All fixtures are local, deterministic, non-secret and disposable. Test output and
captures must never contain actual credentials or personal content.

## Defect loop

For every failure:

1. Record build, environment, session/privacy state, action, expected and actual.
2. Classify service/state, presentation, privacy, performance or native-only.
3. Add the smallest deterministic regression test before or with the fix.
4. Fix the owning layer; do not patch the widget around a broken service contract.
5. Run focused tests, the full suite, smoke and the failed native matrix cell.
6. Retain before/after evidence and keep the criterion open until its required
   environment passes.

## Final acceptance gate

This area is ready to hand to later non-model work only when:

- SC-0 through SC-7 exits are satisfied for one recorded source revision;
- the full automated suite passes with no skips and native checks identify their
  actual desktop/session/scale;
- persistent session CRUD and restart behavior are transactional and ordered;
- Nobody content is isolated, explicitly transitioned and disposed without disk,
  export, history-search or diagnostic leakage;
- message, streaming, status and sensitive-span fixtures are safe, accessible and
  never misrepresented as live model output or hidden reasoning;
- 200-message rendering and 1,000-record local search meet recorded interaction
  targets without blocking or stale results;
- failed operations preserve the current session/draft and provide a safe retry;
- model, attachment, Library and Notes-dock work remains outside this milestone;
  and
- steps blocked by those later areas remain visibly Partial with exact revalidation
  hooks rather than being reported as complete.
