# Status

Updated 21 September 2026. Start here when returning to the project.

**Current focus:** finish and verify Phase A foundations; correct the GUI review
findings before expanding into new feature modules.

**Next action:** R1 in [PLAN.md](PLAN.md) — preserve the complete composer draft
when submission/storage fails, then verify successful retry adds only one message.

## What works

- Shell, shared feedback/states, floating windows and persistent local data services.
- Theme customization, harmony, named-theme import/export, animated backgrounds.
- Appearance settings and shortcut editing. Most product workspaces remain scaffolds.
- Steps 01/53 have scoped prior acceptance; this is not full release acceptance.

## Latest recorded verification

The 21 September GUI review ran **65/65 tests with no skips** and the GUI smoke
check successfully on Fedora 44, Python 3.14.7, PySide6/Qt 6.11.2, **offscreen**.
Native pointer/dialog/scaling checks and animation performance remain pending.
These are recorded review results; a repeat consolidation check also passed 65/65 and smoke offscreen; no
application fixes were made. Durable logs and source hashes are in
[the acceptance record](docs/acceptance/2026-09-21-offscreen.md); test commands are in [docs/TESTING.md](docs/TESTING.md).

## Known open issues, in priority order

1. Failed storage during Send clears the unsaved draft.
2. Normal/Nobody transitions mix message views and show stale persistence status.
3. Closed private-session cleanup and session-scoped draft ownership are incomplete.
4. Nobody label clips with Large text / Roomy density at the minimum window size.
5. Sensitive blur and process presentation have preferences ahead of functionality.

## Working agreements

- [PLAN.md](PLAN.md): sole current scope, implementation and acceptance plan.
- [ROADMAP.md](ROADMAP.md): sequence; [docs/acceptance/](docs/acceptance/): new evidence.
- Run commands from `stark_studio_pyside6/`; use isolated data/settings for checks.
- Retired files under `docs/archive/` and workspace `Version History/` are historical.
- Update this file after meaningful implementation/verification; retain the difference
  between implemented, automatically checked and manually accepted.

## Verified baseline identity

No Git repository/HEAD is available, so **commit/tag: unavailable**. The passing
automated snapshot is identified by the [source manifest](docs/acceptance/evidence/2026-09-21-offscreen/source-manifest.json).
Do not label it a complete known-good GUI release; the issues above are unresolved.
Milestone tagging awaits an actual committed and appropriately verified baseline.
