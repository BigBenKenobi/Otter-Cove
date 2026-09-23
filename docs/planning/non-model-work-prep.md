# Non-model work — planning preparation

Status: preparatory scope inventory, not an implementation plan  
Date: 23 September 2026

## Purpose

This note identifies what Otter Cove can be completed without building model
configuration, model selection, inference, provider adapters, or model execution.
It does not replace `PLAN.md`, change acceptance criteria, assign estimates, or
authorize a new implementation sequence. A later planning pass can use this
inventory to choose a deliberately limited milestone.

“Without model work” still permits deterministic local fixtures where the current
GUI milestone explicitly accepts them. Those fixtures must remain labelled as
simulated, make no network requests, execute no model, and store no credentials.

## Can be completed without the model side

| Area | PLAN steps | Completion boundary |
|---|---:|---|
| Foundation and desktop acceptance | 01, 02, 32–39, 47, 50, 53, 54, scoped 55 | Finish native interaction, dialogs, scaling, restart, accessibility and performance evidence; retain honest unavailable states for deferred model-dependent controls. PR #6 contains the current R2 implementation and remains the immediate review gate. |
| Sessions and local conversation presentation | 03, 06, 10, 11, 48, 49 | Complete local session CRUD, empty/restored states, Nobody lifecycle, history search, message/status rendering and explicit sensitive-span presentation. No generated response is required. See the [execution-ready plan](sessions-local-conversation-plan.md). |
| Local composer utilities | 07, 08 | Complete the shared popover, attachments, document/workspace selection and command-backed optional actions using local or clearly simulated behavior. |
| Documents and Library | 27, 28 | Complete safe text/Markdown import/edit/view, unsaved-change protection, aggregation, archive/search and stable cross-module IDs. |
| Brain records and controls | 13–16 | Complete memories, skills, focused import/export and preference behavior using deterministic audit/extraction fixtures. No model evaluates, extracts or injects content. |
| Local productivity workspaces | 12, 17, 30, 31, 45, 46 | Complete fixture email, local calendars/ICS, notes, tasks and simulated reminders. Calendar/email/reminder settings need a non-AI integration slice separated from step 44’s future agent/model integrations. |
| Gallery and conventional editor | 21–25 | Complete local photo import, thumbnails, albums, canvas, layers/history and ordinary editing tools. AI-labelled controls remain mock adapters and must not imply processing. |
| Demo identity and study presentation | 51, 52 | Complete explicitly simulated account/profile/2FA flows and meaningful local Study Mode behavior without authentication or external identity services. |

These areas can meet their existing GUI-milestone acceptance conditions using
local storage, deterministic services and native Fedora validation. Completing
them would produce substantial useful application behavior while leaving the
model layer untouched.

The execution-ready plan for the first area is
[Foundation and desktop completion](foundation-desktop-plan.md).

## Useful work that cannot be called complete yet

| Area | PLAN steps | Why completion is blocked |
|---|---:|---|
| Chat composer | 04 | Autosizing, draft, attachment and cancellation mechanics can advance, but final submission records require model selection and the shared request contract. |
| Prompt Studio | 09 | Prompt CRUD and editors can be built, but Inject/Persona/Group completion depends on the model selector and prompt-consumption contract. |
| Research Library | 29 | Library presentation can be prepared, but its accepted provenance and completed artifacts depend on Deep Research. |
| Inpaint editor shell | 26 | Mask editing and stale-result protection can be built, but the accepted model field/default and processing workflow depend on step 42. |
| Mixed integrations | 44 | Local CalDAV/CardDAV/contact-file and mail configuration can be separated, but the combined step also includes model/agent services and should not be marked complete as currently written. |

This work should only be included in a later milestone if its partial status is
explicit; visible controls or deterministic fixtures alone must not be reported as
completion of the blocked step.

## Defer with the model side

| Area | PLAN steps | Reason |
|---|---:|---|
| Model registry, selector and defaults | 05, 40–42 | Direct model configuration and selection work. Closed PR #7 is preserved but intentionally deferred; it should be rebased and reviewed against the future model architecture before reuse. |
| Model operations console | 19 | Even simulated cache/download/launch UI is organized around model management and is better designed with that later architecture. |
| Model comparison and research | 18, 20 | Their primary workflows and accepted setup depend on shared model records/defaults. |
| Search-provider settings | 43 | Currently depends on model Settings step 40 and feeds Deep Research; revisit when those contracts are intentionally scheduled. |
| Model-driven inpaint completion | 26 | Model/default selection and processing-adapter behavior belong with the future image-model layer. |

Real inference, Ollama/API connections, credentials, online search, agent execution,
mail delivery, CalDAV synchronization and AI image processing are outside this
non-model scope even where the GUI has a labelled simulated state.

## Candidate scope groups for the later plan

This is ordering guidance only, not the requested full plan:

1. Close the R2 review/native-evidence gap.
2. Complete the local session, document, Library, search and attachment spine.
3. Complete independent personal tools: Brain, tasks, notes, calendar and fixture email.
4. Complete Gallery import, albums and conventional editing.
5. Finish cross-cutting accessibility, native Fedora validation and release polish
   for whichever of those groups are selected.

The later plan should choose a subset, resolve the mixed step-44 dependencies, and
write detailed sequencing only for that selected scope. It should not reopen model
configuration merely to satisfy an incidental dependency.
