# Native Fedora acceptance checklist

This is a procedure supporting [PLAN's shared acceptance gate](../PLAN.md#shared-acceptance-gate),
not a second requirements list. Execute only against the corrected implementation
for the selected scope; keep every unrun or failed cell open.

```bash
./scripts/fedora_phase_a_check.sh
```

Record full SHA, Fedora version, KDE/GNOME, Wayland/actual Qt platform, Python/Qt,
GPU/driver, display scale and available logical screen bounds. Use disposable data
and settings for destructive cases. The current runner's “native” label alone
does not prove its platform, and the printed checklist does not constitute a pass.

## Current foundation and chat

- [ ] Re-run full automation without skips; distinguish offscreen output from native tests.
- [ ] Exercise startup against fresh/saved/corrupt/unavailable data with non-destructive recovery messages.
- [ ] On the corrected R2 build, exercise export/import/reset happy/failure/cancel/confirm paths, protected destinations and preservation of excluded Nobody messages/drafts.
- [ ] Open overlapping tools; drag/resize/raise/minimize/reopen; preserve chat/draft and distinct normal/minimized geometry through resize/restart/display changes.
- [ ] Collapse/expand rapidly; check navigation, accessible names and Settings/New Chat keyboard access when optional entries are hidden.
- [ ] Verify long composer drafts, empty restored sessions, normal/private transitions and ordinary keyboard editing/copy at minimum size.
- [ ] Exercise all presets and semantic color controls with existing/new tools; test harmony preview/apply/reset, theme save/replace/import/export and every cancelled native dialog.
- [ ] Verify implemented Appearance settings live and after restart. Sensitive blur, Web Search and Shell remain unavailable until their actual consumers pass; do not try to accept an inert control as working.
- [ ] Inspect affected surfaces at Small/Default/Large and Compact/Comfortable/Roomy, including long labels and focus/selection/disabled contrast in light/dark themes. Verify the documented Frosted fallback.
- [ ] Switch effects, resize, change controls, Pause/minimize/restore and test Solid's stopped timer. Peek remains visual-only with usable titlebar and exact restoration.
- [ ] Rebind/conflict/clear/reset shortcuts; verify focus return, accessible announcements and ordinary text-editor keys.
- [ ] Burst important errors, read details after toast dismissal, close during demo/animation/data work and restart safely.

Repeat relevant cells under KDE and GNOME Wayland at 100%, 150%, 200%, using the
supported minimum/default/maximized layouts. Explicitly scope out unsupported
environments; do not record them as passed. Capture matched states only against
available supplied originals; missing originals remain a named parity blocker.

## Later session/composer additions

- [ ] After SC, exercise browser CRUD/archive/delete, search navigation, every streaming/status result, safe copy/reveal and private exclusion with the PLAN fixtures.
- [ ] After CU, exercise popup focus/edges/lifecycle, native files/folders, removable/stale chips and complete normal/private draft ownership.
- [ ] Verify Web/Shell fixtures remain labelled simulations with no network/process calls, and attachment-bearing Send remains unavailable until the submission contract exists.
- [ ] Revalidate the named Notes/Library/Prompt/attachment/extraction gates when those consumers are implemented.

## Measurements and evidence

Execute PLAN's native 60-second 1720×900/Balanced animation trace and record
method/machine/samples/results; include Leaves and the most expensive observed
effect. Apply the retained search/render/resource targets when those features exist.

Store actual checklist outcomes, logs, performance output and needed captures
with one source/environment manifest. Link acceptance records and update STATUS;
do not mark whole feature steps Done when their remaining criteria are unrun.
