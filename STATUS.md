# Status

Updated 22 September 2026. Start here when returning to the project.

**Current focus:** finish and verify Phase A foundations; correct the GUI review
findings before expanding into new feature modules.

**Next action:** Review the stacked R2 local-data/recovery implementation, then run
the native Fedora foundation checklist and 60-second animation measurement.

## What works

- Failed message storage preserves the complete composer draft and selected mode;
  a successful retry clears it once and adds one message.
- Normal and Nobody sessions render isolated messages, own separate drafts and show
  truthful storage status; New Chat disposes transient private records.
- The Nobody control expands for Large text / Roomy density at minimum window size.
- Sensitive blur, Web Search and Shell controls are visibly unavailable until their
  consumers exist; session storage status describes behavior that is implemented.
- Settings now exposes Local Data export/import/reset with confirmation, explicit
  affected/excluded scope and non-destructive error reporting.
- Shell, shared feedback/states, floating windows and persistent local data services.
- Theme customization, harmony, named-theme import/export, animated backgrounds.
- Appearance settings and shortcut editing. Most product workspaces remain scaffolds.
- Steps 01/53 have scoped prior acceptance; this is not full release acceptance.

## Latest verification

On 22 September, the current stacked R2 workspace passed **74/74 tests with no
skips**, plus the offscreen GUI smoke check. The run covers failed-send retry, bidirectional
normal/Nobody isolation, session-owned drafts, transient disposal and Large/Roomy
control sizing, and Local Data export/error/reset GUI paths. The 1100×680
Large/Roomy state was also rendered and inspected offscreen. A one-second
offscreen animation-instrumentation check observed 62.04 FPS and 16.83 ms p95;
this validates measurement plumbing only, not native desktop performance.

The 21 September **65/65** Fedora offscreen record remains historical evidence for
the pre-rename source snapshot. Its durable logs and source hashes remain in
[the acceptance record](docs/acceptance/2026-09-21-offscreen.md). Native
pointer/dialog/scaling checks and animation performance are still pending.

## Known open issues, in priority order

The reproduced R1 defects and R2 Local Data gap have targeted code fixes and
offscreen regression coverage. Native visual/interaction acceptance, startup
recovery presentation on a real desktop and broader incomplete feature steps remain
open as recorded in PLAN.md.

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
