# Status

Updated 22 September 2026. Start here when returning to the project.

**Current focus:** finish and verify Phase A foundations; correct the GUI review
findings before expanding into new feature modules.

**Next action:** Continue R1 in [PLAN.md](PLAN.md) with normal/Nobody transition
isolation and stale persistence-status correction.

## What works

- Failed message storage preserves the complete composer draft and selected mode;
  a successful retry clears it once and adds one message.
- Shell, shared feedback/states, floating windows and persistent local data services.
- Theme customization, harmony, named-theme import/export, animated backgrounds.
- Appearance settings and shortcut editing. Most product workspaces remain scaffolds.
- Steps 01/53 have scoped prior acceptance; this is not full release acceptance.

## Latest verification

On 22 September, the R1 draft-preservation workspace passed **68/68 tests with no
skips**, plus the offscreen GUI smoke check. The run includes an injected message-
storage failure and successful retry. It used isolated temporary storage; it is
automated verification, not desktop release acceptance.

The 21 September **65/65** Fedora offscreen record remains historical evidence for
the pre-rename source snapshot. Its durable logs and source hashes remain in
[the acceptance record](docs/acceptance/2026-09-21-offscreen.md). Native
pointer/dialog/scaling checks and animation performance are still pending.

## Known open issues, in priority order

1. Normal/Nobody transitions mix message views and show stale persistence status.
2. Closed private-session cleanup and session-scoped draft ownership are incomplete.
3. Nobody label clips with Large text / Roomy density at the minimum window size.
4. Sensitive blur and process presentation have preferences ahead of functionality.

## Working agreements

- [PLAN.md](PLAN.md): sole current scope, implementation and acceptance plan.
- [ROADMAP.md](ROADMAP.md): sequence; [docs/acceptance/](docs/acceptance/): new evidence.
- [AGENTS.md](AGENTS.md): mandatory documentation standard for all new or materially modified code.
- Run commands from the repository root; use isolated data/settings for checks.
- Retired files under `docs/archive/` and workspace `Version History/` are historical.
- Update this file after meaningful implementation/verification; retain the difference
  between implemented, automatically checked and manually accepted.

## Repository and baseline identity

This project is a Git repository on `main` and tracks `origin/main` at
`BigBenKenobi/Otter-Cove`. The 22 September automated Otter Cove verification is
current workspace evidence; it is not a tagged release baseline. Do not label the
application a complete known-good GUI release while the issues above and native
desktop acceptance remain unresolved.
