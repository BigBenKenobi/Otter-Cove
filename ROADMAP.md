# Roadmap

Sequence summary only. [PLAN.md](PLAN.md#execution-order) is the replacement
implementation/acceptance plan; [STATUS.md](STATUS.md) records progress/evidence.
The former R1–R6/model-first phase sequence is superseded.

**Next: OC-00 baseline, then OC-01–04 data-protection fixes before R2 landing.**

| Order | Area / work | Completion boundary |
|---|---|---|
| 1 | Existing foundation: OC-00–22 by dependency, then OC-23 | Data safety, current UI reliability, packaging and scoped native evidence |
| 2 | Sessions: SC-1, shared CU-0/CU-1 before SC-2, then SC-2–6 | Local lifecycle/browser/renderers/search and sensitive/status presentation |
| 3 | Composer: CU-2–6 | Transient file/folder selections, action registry and explicit simulations |
| 4 | Documents/Library: 28 → 27, then 11/07 integration | Real local editing, Library search and document picker |
| 5 | Brain: 13 → 14 → 15 → 16 | Local records and simulated audit/extraction |
| 6 | Productivity: scoped non-AI 44, then 31 → 30 → 12 → 45 → 46 → 17 | Local tasks/notes/calendar, fixture email and simulated reminders |
| 7 | Gallery/editor: 21 → 22 → 23 → 25 → 24 | Local images/albums and conventional editing/layers/history |
| 8 | Demo identity/study: 51 → 52 | Truthful simulated account flows and local Study Mode |

Use the shared acceptance gate after each area and revalidate affected consumers.
Areas 4–8 retain their full feature criteria; expand the selected area's detailed
packages inside PLAN before implementation. Model work stays deferred. Partial
steps and future Prompt/Library/Notes/attachment/extraction/model dependencies
remain explicit in PLAN; this order does not waive their completion gates.
