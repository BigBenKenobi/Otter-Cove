# Decisions

Accepted architectural choices, recorded 21 September 2026; document ownership
reconciled 23 September 2026. Change a decision
explicitly with its rationale; do not silently reopen it in a feature patch.

| ID | Decision | Rationale / consequence |
|---|---|---|
| D01 | PySide6 / Qt Widgets | Keep one native desktop UI implementation; entry point stays small. |
| D02 | Fedora 44 primary target | Validate the supported KDE/GNOME desktop matrix; current offscreen evidence is not Wayland acceptance. |
| D03 | SQLite content; QSettings preferences | Version/migrate domain content independently from desktop geometry/preferences. |
| D04 | Services over repositories over SQLite | Keep business behavior and persistence out of widgets. Existing local services remain in core/data; services/ is for future integrations. |
| D05 | Floating tools are child widgets | One workspace owns stacking, bounds and lifecycle rather than separate OS windows. |
| D06 | Peek is visual-only | Fade tool content without promising click-through or changing titlebar usability. |
| D07 | Deterministic mock adapters for GUI milestones | Exercise states without pretending real backend connectivity, authentication or execution. |
| D08 | Semantic themes and central typography | Live restyling must work across all surfaces and supported text sizes. |
| D09 | Private sessions are transient | Exclude private content from durable history, export and extraction; fix known lifecycle gaps before accepting the flow. |
| D10 | One current PLAN.md | PLAN now contains the consolidated OC/SC/CU tasks and all 55 criteria. ROADMAP summarizes order; STATUS and ACCEPTANCE index progress/evidence. Former proposals are pointers only. |
| D11 | Original media has one home | docs/reference is the intended home for supplied originals; they are absent from the reviewed checkout and OC-00 tracks recovery. Generated captures belong with acceptance evidence. |
| D12 | Tag only an evidenced commit | No fabricated tag or acceptance claim; distinguish offscreen automated checks from native/manual acceptance. |

Release/delivery archives remain outside the application source tree. Regenerable
caches/runtime state are excluded. Curated acceptance logs
and manifests are evidence and may be retained under docs/acceptance/evidence/.
