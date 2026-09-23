# Status

Updated 23 September 2026.

**Current plan:** [PLAN.md](PLAN.md) is the consolidated replacement. It contains
the 24 OC improvements, unique Sessions/Composer packages, eight-area execution
order and all 55 original feature criteria. The earlier PR #8/#9 standalone
proposals are superseded; `docs/planning/` contains pointers only.

**Next action:** Pilot 1 OC-00–04 is implemented locally and awaits native/reference
and reviewer acceptance. Do not start OC-05 from this handoff. The reviewed
R2 recovery UI is integrated locally but remains
unpublished pending the Pilot gates.
Model configuration and execution remain deferred.

## Current implementation

- Pilot baseline `fb41db85e8108ea0606b329da7c83b0e8d7967b3` combines current main
  `ada8b9992786006af57e34631096c3a195108a55` with the reviewed PR #6 runtime
  delta `a560b5d7c7d88fc6d941e0d5da8542c9ac7d64c3`. Its evidence is in
  `docs/acceptance/evidence/2026-09-23-word-of-god-pilot/`; it is a local
  implementation baseline, not a merged or native-accepted release.
- Shell, floating windows, shared feedback/states, SQLite services, themes,
  background effects, Appearance and shortcuts are substantially implemented.
- R1's failed-send retention/retry, normal/private view/draft isolation, New Chat
  private disposal, Nobody sizing and unavailable-control corrections are on main.
- Most product workspaces remain scaffolds. A complete session browser, rich/status
  renderers, local search and composer file utilities are planned next.
- PR #6 contains the management/recovery UI and nested-JSON import correction on
  its separate branch; it remains pending review and the additional fixes below.

## Priority findings

1. **OC-01:** local-data and theme export now reject active database, sidecar,
   settings, symlink and hard-link targets on the Pilot branch; native/reviewer
   acceptance remains pending.
2. **OC-02:** replacement now preserves excluded Nobody state and uses a dedicated
   durable-data refresh on the Pilot branch; native/reviewer acceptance remains pending.
3. **OC-03:** validate complete supported import snapshots, types and stable IDs.
4. **OC-04:** reject credentials in existing structured endpoint/config fields
   before storage/import/export.

Further OC tasks cover expected errors, invalid preferences, long drafts, empty
session restoration, explicit safe text rendering, themes, responsive/accessibility
checks, bounded work/resources, CI, packaging and native acceptance. The
[review record](docs/reviews/2026-09-23-current-implementation.md) distinguishes
reproductions from source observations and evidence gaps.

## Latest code verification

| Source | Result | Environment/scope |
|---|---|---|
| Main runtime `6aa8022` | 73/73 tests, no skips | 23 September; Ubuntu 24.04.3, Python 3.12.14, PySide6/Qt 6.11.2, offscreen |
| PR #6 `a560b5d` | 74/74 tests, no skips; offscreen smoke PASS | Same environment; separate unmerged implementation |
| Earlier Fedora evidence | 65/65 plus offscreen smoke | [21 September historical record](docs/acceptance/2026-09-21-offscreen.md); not current native acceptance |
| Pilot OC-00 combined baseline `fb41db8` | 74/74, no skips/expected failures; offscreen smoke pass | [Pilot record](docs/acceptance/evidence/2026-09-23-word-of-god-pilot/00-baseline.md); source is local and native acceptance remains pending |

Additional probes reproduced the listed code gaps despite the passing suites.
Consolidation validates documentation coverage/links/order, not new runtime behavior.
Steps 01/53 retain earlier scoped acceptance; native pointer/dialog/scaling,
screen-reader checks and the 60-second animation target remain pending.

Original visual references are absent from this checkout. OC-00 must locate the
supplied originals before reference-parity acceptance. No release tag or full GUI
acceptance is implied by the documentation replacement.

## Working agreements

- Implement from PLAN; ROADMAP is only its sequence summary.
- Apply AGENTS.md and the architecture/decision contracts.
- Use isolated data/settings and record the tested source/platform/skips.
- Preserve historical evidence; never relabel offscreen results as native.
- Update this file after meaningful implementation/verification, including the
  exact next task and remaining partial integration gates.
