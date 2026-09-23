# 02-A — Preserve excluded state during durable replacement

**Authority:** [OC-02](../../../PLAN.md#oc-02). **Requires:** 01-G PASSED.
**Outcome:** successful import/reset refreshes durable state without disposing Nobody.

Inspect PR #6's `_import_local_data` / `_reset_local_data` in `app.py`,
`ui/chat.py` session IDs, `_mode_session_ids`, `_drafts`, rendering and `reset_chat`,
and `SessionService` private collections in `core/data/services.py`. Read existing
settings-command and shell Qt tests before adding coverage.

1. Add a failing GUI regression: private message plus unsent draft, normal session
   history, and reset/import through the real settings handlers. Show the current
   unwanted private disposal caused by `reset_chat()`.
2. Add a dedicated durable-replacement refresh operation. Call it only after the
   service commits successfully. Preserve live private messages, draft, identity,
   composer mode and active view. Never invoke New Chat as a replacement shortcut.
3. Remove stale durable session IDs, rendered messages and per-session draft keys.
   An imported record reusing an old ID must not inherit the deleted record's cached
   draft. In normal mode render the selected imported normal session (or truthful
   empty view); in private mode defer normal selection without switching the view.
4. Choose and document an explicit normal-draft policy. Preferred pilot policy:
   preserve the pending normal draft; warn that drafts tied to replaced durable
   sessions are discarded and require confirmation. If the current UI cannot
   distinguish these states safely, implement that distinction here. Confirmation,
   affected/excluded reports and actual cache behavior must agree. Do not save
   private or unsent draft text into SQLite or export as a preservation shortcut.
5. Cancelled dialogs and failed service operations must leave all IDs, messages,
   modes and drafts unchanged. Keep explicit New Chat's existing private disposal
   semantics. Tests should call handlers, process Qt events and inspect both UI
   and service state; mocking away the lifecycle would miss this defect.

**Boundaries:** preserve current text/mode state; no attachment aggregate, session
browser, persistence of unsent drafts or SC/CU implementation. OC-03 will improve
import preview; keep this lifecycle usable by that later handler change.
**Development checks:** both operations × normal/private view; live private message
and draft; pending normal draft; stale durable IDs; cancellation/failure; later New Chat.
**Next:** 02-G.
