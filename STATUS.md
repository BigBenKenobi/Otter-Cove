# Status

Updated 22 September 2026. Start here when returning to the project.

**Current focus:** finish and verify Phase A foundations; correct the GUI review
findings before expanding into new feature modules.

**Next action:** Finish R1 in [PLAN.md](PLAN.md) by correcting preferences that
currently imply sensitive-span or process/search functionality ahead of consumers.

## What works

- Failed message storage preserves the complete composer draft and selected mode;
  a successful retry clears it once and adds one message.
- Normal and Nobody sessions render isolated messages, own separate drafts and show
  truthful storage status; New Chat disposes transient private records.
- The Nobody control expands for Large text / Roomy density at minimum window size.
- Shell, shared feedback/states, floating windows and persistent local data services.
- Theme customization, harmony, named-theme import/export, animated backgrounds.
- Appearance settings and shortcut editing. Most product workspaces remain scaffolds.
- Steps 01/53 have scoped prior acceptance; this is not full release acceptance.

## Latest verification

On 22 September, the current R1 workspace passed **72/72 tests with no skips**,
plus the offscreen GUI smoke check. The run covers failed-send retry, bidirectional
normal/Nobody isolation, session-owned drafts, transient disposal and Large/Roomy
control sizing. The 1100×680 Large/Roomy state was also rendered and inspected
offscreen. This is automated/supplementary evidence, not native desktop acceptance.

The 21 September **65/65** Fedora offscreen record remains historical evidence for
the pre-rename source snapshot. Its durable logs and source hashes remain in
[the acceptance record](docs/acceptance/2026-09-21-offscreen.md). Native
pointer/dialog/scaling checks and animation performance are still pending.

## Known open issues, in priority order

1. Sensitive blur and process presentation have preferences ahead of functionality.

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
