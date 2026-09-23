# Foundation and desktop completion plan

Status: proposed execution plan  
Date: 23 September 2026  
Canonical requirements: `PLAN.md` steps 01, 02, 32–39, 47, 50, 53, 54 and the
foundation-selected portion of 55

## Objective

Finish Otter Cove's shared desktop foundation on Fedora without implementing model
configuration, inference, provider adapters, online services or model-backed
features. The outcome is a reliable shell, local-data recovery surface, visual
system, floating-window framework, keyboard command layer and recorded native
desktop evidence that later feature modules can safely reuse.

This document expands one area from `non-model-work-prep.md`. `PLAN.md` remains the
authority for feature acceptance. If the two conflict, update the proposal before
implementation rather than silently weakening `PLAN.md`.

## Scope boundary

Included:

- Application shell and route integrity (01).
- Sidebar collapse, focus, restore and accessibility behavior (02).
- Theme presets, customization, harmony, typography/density/frosted appearance,
  animated backgrounds, theme interchange, Peek and floating tools (32–39).
- Working Appearance settings and honest unavailable states (foundation portion
  of 47).
- Shared command/shortcut behavior (50), shared states/feedback (53), and local
  persistence, management and recovery (54).
- Native Fedora validation required by these selected features (scoped 55).

Explicitly excluded:

- Model registry, selector, defaults, probes, inference and model execution.
- Enabling Sensitive blur, Web Search or Shell controls. They stay disabled and
  visibly unavailable until steps 48 and 08 supply real consumers.
- Feature-specific Favourite/Delete/TTS commands whose workflows do not exist.
- Real notifications, authentication, mail delivery, external integrations,
  public networking and AI image processing.
- General completion of step 55 for features outside this selected foundation.

The foundation milestone may record the accepted subset of step 47 and step 55,
but must not mark either entire canonical step Done while excluded dependencies
remain incomplete.

## Current baseline

The existing implementation should be extended, not rebuilt:

- Step 01 and step 53 have prior scoped acceptance and regression coverage.
- Steps 32–34 and 36–39 are substantially implemented; their main gaps are native
  interaction, dialog, compositor, restart and performance evidence.
- Step 35 has working typography/density plus a documented Frosted fallback; the
  broader clipping/reachability matrix remains open.
- Step 50 has a command registry, conflict detection and persistent editor; native
  focus/text-editing behavior and feature-command activation remain scoped.
- PR #6 contains the current step-54 management/recovery UI, nested import
  validation and animation measurement tooling. It must be reviewed and landed or
  explicitly superseded before this plan establishes its baseline.
- Offscreen tests and smoke runs are useful regression evidence but do not satisfy
  native Fedora, pointer, compositor, dialog, scaling or performance gates.

## Completion rules

1. Preserve existing shell, service, route, theme, command and data ownership.
2. Fix only reproduced defects or missing acceptance behavior; do not redesign
   stable controls during the validation pass.
3. Add focused automated regression coverage for logic/state defects. Native-only
   behavior receives reproducible manual evidence rather than a misleading mock.
4. Use isolated SQLite and QSettings fixtures for every automated/demo run.
5. Never store credentials or include them in export, logs, captures or fixtures.
6. Never convert an offscreen pass into a native acceptance claim.
7. Mark a criterion complete only when its required automated and native evidence
   identifies the exact tested commit and environment.

## Execution packages

### FD-0 — Establish the review baseline

Purpose: start all later work from one known source state.

Work:

1. Review PR #6, including local-data scope wording, destructive confirmations,
   invalid/malformed import rollback and measurement instrumentation.
2. Resolve review findings, then merge #6 or document the replacement commit.
3. Use a clean checkout of the selected commit. Record `git status`, full SHA,
   Python, PySide6 and Qt versions.
4. Run the complete test suite with no skips, compile validation, diff checks and
   the isolated offscreen smoke check.
5. Reconcile `STATUS.md`, `CHANGELOG.md`, `PLAN.md` current checks and acceptance
   notes with actual results; do not mark native gates complete.

Exit:

- One clean foundation baseline SHA is recorded.
- All automated checks pass with no skips.
- PR #6 is either included or its replacement is identified.
- Known native-only gaps are listed separately from implementation defects.

### FD-1 — Close deterministic foundation gaps

Purpose: exercise everything that can be proven without a compositor before the
native matrix begins.

Work:

1. Audit existing coverage before adding tests; retain current route, draft,
   window, theme, effect, shortcut, feedback and persistence suites.
2. Add missing focused checks for:
   - rapid sidebar collapse/expand settling at the requested state;
   - icon-only accessible names/tooltips and collapsed Settings/account reachability;
   - route resolution and draft preservation while tools open;
   - theme/appearance/shortcut persistence across reconstructed windows;
   - minimum-size reachability under Large/Roomy typography;
   - malformed local-data shapes, rollback, cancellation and recovery messages;
   - startup error presentation boundaries where Qt automation can prove them;
   - timers and retained widgets not accumulating across repeated lifecycle cycles.
3. Keep platform-specific pointer, native dialog, real focus/compositor and display
   scaling checks out of automated claims unless the test truly uses that platform.
4. Update the Fedora runner only where needed to guarantee isolated paths, report
   the actual Qt platform, reject accidental offscreen native runs and retain logs.

Exit:

- The full suite passes with no skips on isolated data/settings.
- Every reproduced logic defect has a focused regression test.
- The native checklist contains only behavior that still requires a real desktop.

### FD-2 — Complete local-data management and recovery

Purpose: close the remaining step-54 and shared-error presentation boundaries.

Work:

1. Verify Export JSON, confirmed Import JSON and confirmed Reset from Settings.
2. Exercise cancel, malformed outer JSON, malformed nested JSON, unsupported
   version, duplicate/constraint failure, unreadable source and unwritable target.
3. Confirm every failed import is non-mutating and every destructive path states
   affected and excluded data, including Nobody sessions, credentials and
   QSettings geometry/preferences.
4. Start against corrupt and unavailable stores. Confirm startup presents the
   service-owned recovery options and never replaces or truncates the source.
5. Confirm normal records, settings and geometry restore after restart while
   Nobody content never appears in SQLite or export.
6. Capture native file-dialog and confirmation behavior on Fedora; cancellation
   must return focus safely and leave state unchanged.

Exit:

- Step 54 has automated transaction/policy coverage plus native dialog/recovery
  evidence.
- Startup and in-app errors use shared feedback and remain available after transient
  toast dismissal where applicable.
- Original bytes/data are demonstrated intact after each rejected recovery case.

### FD-3 — Shell, sidebar, floating tools and commands

Purpose: validate the reusable desktop interaction framework before new modules use
it heavily.

Work:

1. At 1100×680, normal working size and 1920×1080, open every exposed route and
   confirm it resolves to the intended component or honest unavailable state.
2. With an unsent draft and active session, repeatedly open/focus/minimize/restore/
   close tools; confirm chat, session and draft remain unchanged.
3. Rapidly toggle the sidebar. Confirm final width, active route, optional entries,
   badges, accessible names/tooltips and restart restoration.
4. With two or more floating tools, exercise pointer drag, all resize edges/corners,
   raise/focus, minimize/restore, host resizing, bounds recovery and process restart.
5. Verify normal and minimized geometry stay distinct and inaccessible off-screen
   geometry is recovered after display/scale changes.
6. Rebind, conflict, clear and reset shortcuts. Verify restart persistence and that
   ordinary editor navigation/copy/paste/undo text shortcuts are not stolen.
7. Keep unimplemented feature commands disabled with a visible reason.

Exit:

- Steps 01 and 39 retain their scoped automated acceptance and gain current native
  interaction evidence.
- Step 02 satisfies collapse, accessibility and restart criteria.
- Step 50 records the foundation command subset; deferred feature commands remain
  explicitly outside the accepted subset.

### FD-4 — Theme, appearance and interchange matrix

Purpose: finish the visual foundation across supported states without expanding
feature scope.

Work:

1. Verify all 16 presets select, update existing/new windows and survive restart.
2. Perform matched-state review for Light, Copper, Ocean and Forest with Home,
   Theme and Settings open. Inspect text, focus, selection, disabled controls,
   menus, scroll viewports and floating windows.
3. Exercise every primary and More Colors token, picker cancel, live preview,
   Reset Colors and preset-switch override semantics across multiple windows.
4. Exercise Complementary, Analogous, Triadic and Split Complementary harmony in
   light/dark and neutral inputs. Confirm Generate is preview-only and Apply/Reset
   semantics match the labels.
5. Run the typography matrix: supported fonts and Small/Default/Large crossed with
   Compact/Comfortable/Roomy at minimum and normal sizes. Inspect Theme tabs,
   Settings tabs, sidebar, composer, dialogs and title bars for clipping or
   unreachable controls.
6. Verify Frosted produces the documented translucent appearance or documented
   fallback without implying compositor blur.
7. Save, replace, restart, export and import named themes. Exercise duplicate,
   unsupported, malformed, cancellation and write-failure paths without mutating
   the current theme.
8. Verify working Appearance settings update open UI and survive restart. Confirm
   deferred Sensitive blur, Web Search and Shell controls remain disabled,
   explained and non-deceptive.

Exit:

- Steps 32–35 and 37 have current automated/native evidence for their complete
  acceptance matrices.
- The foundation portion of step 47 is recorded precisely; the canonical step
  remains Partial until its excluded consumers exist.
- Reference differences are documented as intentional or fixed.

### FD-5 — Animated backgrounds and Peek

Purpose: close compositor and performance risks after functional visual defects are
fixed.

Work:

1. Switch all ten effects repeatedly at minimum, 1720×900 and maximized sizes.
2. Verify effect color/speed/intensity/size/quality controls, panel reopen sync,
   persistence, disabled irrelevant controls and Solid's stopped timer.
3. Verify Pause, hide/minimize suspension and restoration remain independent; a
   system visibility transition must never override the user's Pause value.
4. Run a short native sweep to identify the costliest animated effect, then run the
   recorded 60-second 1720×900/Balanced trace on that effect. Also retain the
   documented Leaves command for comparable evidence.
5. Target approximately 60 FPS with p95 frame interval no greater than 33 ms. If
   the target fails, reproduce, profile and tune or add an explicit lower-quality
   fallback; do not lower the threshold silently.
6. Toggle Peek with overlapping tools. Verify exact opacity restoration, visible
   workspace, usable titlebar and visual-only (not click-through) behavior through
   minimize/restore, theme change and close/reopen.
7. Confirm no hidden overlay intercepts input and no effect timer continues after
   shutdown.

Exit:

- Step 36 has actual native performance output tied to the machine/build.
- Step 38 has real compositor and pointer evidence with its visual-only semantics.
- Any hardware-specific fallback is explicit in UI/docs and regression tested.

### FD-6 — Fedora desktop matrix

Purpose: apply scoped step-55 validation to the completed foundation build.

Primary matrix:

| Dimension | Required coverage |
|---|---|
| Desktop | KDE Wayland and GNOME Wayland; explicitly scope out an unavailable desktop rather than claiming it passed |
| Scale | 100%, 150% and 200% |
| Window | 1100×680, normal/default and maximized |
| Theme states | Light plus representative Copper, Ocean and Forest states |
| Input | Pointer, keyboard-only traversal, ordinary text editing, clipboard and drag/drop where exposed |
| Native UI | File/color dialogs, confirmations, focus return and error presentation |
| Lifecycle | Fresh start, saved restart, minimize/restore and shutdown during active demo/timer work |

For each supported desktop:

1. Record Fedora release, desktop, session type, display scale, Python, PySide6,
   Qt, GPU/driver and tested commit.
2. Run `scripts/fedora_phase_a_check.sh` without an inherited offscreen platform.
3. Execute the manual foundation checklist at each required scale; use a reduced
   repeated-state set only after the full 100% pass establishes behavior.
4. Verify focus/tab order, accessible names, keyboard activation, readable focus
   indicators and status announcements.
5. Verify clipboard and local drag/drop only where the selected foundation exposes
   them; do not invent coverage for future modules.
6. Close during active animation/demo state and confirm timers/jobs stop and no
   unintended process remains. Restart into valid state.
7. Capture matched-state screenshots and record intentional desktop differences.

Exit:

- Every claimed environment/scale has a completed result, not merely a printed
  checklist.
- Failures link to a defect and rerun evidence; unsupported environments are named.
- Scoped step 55 is accepted only for the foundation features in this plan.

### FD-7 — Evidence and closeout

Purpose: make the result reproducible and prevent status inflation.

Work:

1. Store curated evidence under
   `docs/acceptance/evidence/<date>-foundation-desktop/`:
   - `manifest.txt`: commit and environment identity;
   - `automated.log`: complete suite/smoke result and skips;
   - `native-checklist.md`: per-environment actions and actual outcomes;
   - `performance.txt`: command, samples, FPS and p95/max intervals;
   - matched-state captures needed to support visual findings.
2. Update or add concise acceptance records for affected PLAN steps. Link evidence
   rather than duplicating raw logs throughout documentation.
3. Update `STATUS.md`, `CHANGELOG.md`, `ROADMAP.md` and PLAN current checks to match
   evidence. Mark checkboxes only for criteria actually executed.
4. Run the full automated suite and one final native smoke against the exact
   closeout commit. If documentation changes afterward, record whether the source
   identity remains behaviorally identical.
5. Do not create or move a milestone tag unless separately approved.

Exit:

- The accepted and still-open boundaries are unambiguous.
- A clean checkout can reproduce automated checks and follow the native record.
- No model-side or unrelated feature completion is claimed.

## Defect loop

For every failure discovered during execution:

1. Record environment, state, exact action, expected result and actual result.
2. Decide whether it is an implementation defect, native-only behavior, unsupported
   environment or evidence gap.
3. Add the smallest focused automated regression when the behavior is deterministic.
4. Implement the fix without weakening thresholds or acceptance wording.
5. Run focused tests, the full suite, relevant smoke and the failed native cell.
6. Retain the before/after result in the acceptance record.

One failed matrix cell keeps its criterion open; success elsewhere does not average
it away.

## Required fixtures

- Fresh and saved QSettings files.
- Fresh, populated, corrupt and unavailable SQLite paths.
- Valid, malformed, unsupported and nested-malformed local-data exports.
- Valid, duplicate, malformed and unsupported theme bundles plus unwritable target.
- Two simultaneous floating tools with saved normal/minimized geometry.
- Long labels and long saved-theme lists under Large/Roomy at 1100×680.
- Every background effect at Balanced quality, plus Solid and user-paused states.
- Unsent composer draft used only to prove shell preservation; no model submission.

All fixtures must be local, deterministic, non-secret and disposable.

## Final acceptance gate

The Foundation and desktop area is complete only when:

- FD-0 through FD-7 exits are satisfied for one exact source revision;
- the full automated suite passes with no skips and the native smoke passes;
- all claimed KDE/GNOME and scale cells have recorded actual results;
- local-data failure/recovery cases are non-destructive and visibly explained;
- primary controls remain reachable and readable across the layout/theme matrix;
- window, shortcut, animation and Peek native behavior meets the stated contracts;
- performance meets the step-36 target or an explicit tested fallback is shipped;
- deferred controls and commands remain honestly unavailable;
- canonical step 47 and global step 55 are left Partial wherever excluded work is
  still outstanding; and
- documentation states exactly what was accepted, what remains native-blocked and
  what remains deferred to later non-model or model milestones.
