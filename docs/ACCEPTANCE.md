# Acceptance ledger

[PLAN.md](../PLAN.md) is the sole source of completion criteria. This ledger indexes
state/evidence and does not redefine those criteria. Updated 21 September 2026.

- **Not started:** no dedicated behavior (including unavailable route scaffolds).
- **Partial:** implementation exists but requirements remain.
- **Automated pass:** focused automated checks passed; manual/release gates remain.
- **Manual pass:** identified manual checks passed; other gates may remain.
- **Done:** scoped step accepted with evidence. Earlier scoped acceptance does not
  imply the entire application meets the step-55 desktop release gate.

No new manual pass is claimed. Steps 01/53 retain their prior scoped acceptance.
[Current 65/65 offscreen record](acceptance/2026-09-21-offscreen.md) corroborates
automated checks only. Known review findings remain open even with a green suite.

| Step | Feature | State | Evidence / remaining boundary |
|---|---|---|---|
| 01 | Application shell | Done (scoped baseline) | [Prior record](acceptance/step-01.md); step 55 remains open |
| 02 | Collapsible sidebar | Partial | Known implementation gaps; see PLAN |
| 03 | Home / empty session | Partial | Known implementation gaps; see PLAN |
| 04 | Chat composer | Partial | Known implementation gaps; see PLAN |
| 05 | Model selector | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 06 | Nobody / incognito session | Partial | Known implementation gaps; see PLAN |
| 07 | Composer tool menu and attachments | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 08 | Optional composer actions | Partial | Known implementation gaps; see PLAN |
| 09 | Prompt Studio | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 10 | Sessions and message rendering | Partial | Known implementation gaps; see PLAN |
| 11 | Search | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 12 | Email | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 13 | Brain — Memories | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 14 | Brain — Skills | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 15 | Brain — Add / import / export | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 16 | Brain automation preferences | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 17 | Calendar | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 18 | Model Compare | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 19 | Cookbook | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 20 | Deep Research | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 21 | Gallery — Photos | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 22 | Gallery — Albums | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 23 | Gallery editor foundation | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 24 | Gallery editing tools | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 25 | Gallery layers and history | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 26 | Inpaint workflow | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 27 | Library | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 28 | Documents | Partial | Known implementation gaps; see PLAN |
| 29 | Research Library | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 30 | Notes dock | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 31 | Tasks and local scheduler | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 32 | Theme presets | Automated pass | [Current run](acceptance/2026-09-21-offscreen.md); native/visual/performance gates in PLAN |
| 33 | Theme customization | Automated pass | [Current run](acceptance/2026-09-21-offscreen.md); native/visual/performance gates in PLAN |
| 34 | Colour harmony generator | Automated pass | [Current run](acceptance/2026-09-21-offscreen.md); native/visual/performance gates in PLAN |
| 35 | Fonts, density and frosted surfaces | Partial | Known implementation gaps; see PLAN |
| 36 | Animated backgrounds | Automated pass | [Current run](acceptance/2026-09-21-offscreen.md); native/visual/performance gates in PLAN |
| 37 | Theme save / share | Automated pass | [Current run](acceptance/2026-09-21-offscreen.md); native/visual/performance gates in PLAN |
| 38 | Peek mode | Automated pass | [Current run](acceptance/2026-09-21-offscreen.md); native/visual/performance gates in PLAN |
| 39 | Floating tool-window framework | Automated pass | [Current run](acceptance/2026-09-21-offscreen.md); native/visual/performance gates in PLAN |
| 40 | Settings — Add Models | Partial | Known implementation gaps; see PLAN |
| 41 | Settings — Added Models | Partial | Known implementation gaps; see PLAN |
| 42 | Settings — AI Defaults | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 43 | Settings — Search | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 44 | Settings — Integrations | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 45 | Settings — Email navigation | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 46 | Settings — Reminders | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 47 | Settings — Appearance | Partial | Known implementation gaps; see PLAN |
| 48 | Sensitive-span presentation | Partial | Known implementation gaps; see PLAN |
| 49 | Process/status presentation | Partial | Known implementation gaps; see PLAN |
| 50 | Keyboard commands and shortcut editor | Partial | Known implementation gaps; see PLAN |
| 51 | Account flows | Not started | Unavailable scaffold or no dedicated UI; see PLAN |
| 52 | Profile / Study Mode area | Partial | Known implementation gaps; see PLAN |
| 53 | Shared states and feedback | Done (scoped baseline) | [Prior record](acceptance/step-53.md); step 55 remains open |
| 54 | Persistence and application data | Partial | [Storage record](acceptance/step-54.md); management/recovery GUI incomplete |
| 55 | Fedora desktop validation and release polish | Partial | Offscreen evidence only; native matrix pending |

## Updating evidence

Store new records in `docs/acceptance/`, with build/commit or source manifest,
environment/platform, actions, expected/actual results, skips and remaining gaps.
Keep dated records intact; append a dated correction or create a new record rather
than rewriting old evidence as if it ran on a newer build. The former root
acceptance/ duplicates were consolidated here byte-for-byte.
