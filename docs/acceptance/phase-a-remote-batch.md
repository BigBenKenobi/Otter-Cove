# Phase A remote batch — deferred Fedora acceptance

Status: **Implementation batch complete; native acceptance intentionally stacked**

This batch was prepared while the user was remote. It deliberately groups Fedora-only checks instead of requiring a new target-machine run after every small foundation change.

## What changed since the last Fedora 26/26 run

### Step 39 — floating tools
- Existing-window focus/raise and minimized-window restore.
- Separate normal/minimized geometry records and explicit commits.
- Bounds recovery after host size changes and persistent close/reopen state.

### Steps 32 / 33 — theme presets and customization
- Sixteen built-in semantic themes remain available.
- Custom overrides now persist in QSettings and restore on restart.
- Built-in preset selection explicitly clears stale overrides.
- More Colors exposes `muted`, `input_bg` and `send_bg` in addition to the six primary tokens.
- Reset colors restores the selected base preset; canceled QColorDialog selection is a no-op.
- Dark-theme scroll viewports are explicitly transparent instead of inheriting an unstyled light viewport.

### Step 47 — Appearance (partial by design)
- Settings is now a real reusable StudioWindow with Appearance and Shortcuts pages.
- Live/persistent controls: full-width composer, welcome visibility, Nobody visibility, Native/Minimal decorative glyph presentation, status summary, sensitive-blur preference, Web Search action, Shell action and per-sidebar-entry visibility.
- Hiding a control does not alter chat draft/session state.
- Reset restores documented defaults.
- The sensitive-blur preference is stored and propagated, but actual marked-span conceal/reveal remains step 48; therefore step 47 is not claimed Done.

### Step 35 — typography / density / frosted surfaces
- Global text size is now generated from the selected typography setting rather than defeated by a fixed 11px root rule.
- Derived title/section sizes track Small/Default/Large.
- Compact/Comfortable/Roomy changes semantic heights/padding.
- Frosted uses a documented translucent in-app fallback; no native compositor blur is claimed.

### Step 36 — animated backgrounds
- Effect color is independent, live and persisted.
- Solid disables animation-only controls with an explanation and does not run the timer.
- Hidden-widget and application-level suspension are independent reasons; show/hide cannot accidentally clear an external suspension.
- User Pause remains independent from suspension.

### Step 38 — Peek
- Peek button/programmatic state stays synchronized.
- Only the body is faded; the titlebar remains interactive.
- Peek state remains attached to the persistent StudioWindow through minimize/restore, theme/style changes and close/reopen.

### Step 34 — harmony generator
- Pure deterministic generator supports Complementary, Analogous, Triadic and Split Complementary in Light/Dark modes.
- Neutral/zero-saturation accents are handled deterministically.
- The exact requested accent remains in the preview.
- Generate is preview-only; Apply maps the preview to named theme tokens; Reset preview does not mutate the theme.

### Step 37 — theme save/share
- Saved themes include palette, typography, density, frosted flag and complete effect configuration.
- Saved themes persist and appear under Saved Themes.
- Import/export uses versioned JSON with validation and atomic replacement on successful write.
- Invalid versions/colors and duplicate names are rejected without switching the current theme.

### Step 50 — commands / shortcuts
- Stable command IDs/defaults exist for New Chat, Search, Theme, Settings, favourite/delete session, Nobody, Tools and TTS demo.
- Favourite/delete are intentionally disabled until session-management UI exists and expose a reason.
- Persistent rebind, conflict detection, clear, single reset and reset-all are implemented.
- Settings and New Chat have stable commands even if their usual navigation surface is hidden.
- Current bindings are surfaced by QAction/tooltips and the Settings shortcut editor.

## Automated suite

Run:

```bash
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

This batch contains **65 tests**. In the build container, **34 Qt-independent tests pass** and **31 Qt tests are skipped** because PySide6 is unavailable. The next Fedora run should execute all 65.

The Fedora batch script also runs `scripts/fedora_gui_smoke.py`, a native Qt smoke pass against isolated temporary storage. It opens/reuses/minimizes tools, cycles all built-in themes and effects, exercises Peek and Appearance, checks Solid timer behavior and pause/suspension separation, forces the minimum host size, and reconstructs the application to verify theme restart state.

New coverage includes:
- theme harmony/bundle validation and atomic export;
- custom-theme/palette persistence;
- More Colors/harmony/Solid UI behavior;
- effect timer and pause/suspension separation;
- Peek lifecycle behavior;
- Appearance defaults/persistence/reset;
- command IDs/conflicts/clear/reset;
- Settings/Appearance live UI updates and draft preservation;
- persistent shortcut rebinding and disabled-command reasons.

## One-command Fedora evidence

Run:

```bash
./scripts/fedora_phase_a_check.sh
```

It prints Fedora/desktop/session/PySide6/Qt/GPU context, executes the full test suite, then prints the combined manual checklist. It does not install packages or modify system configuration.

## Deferred manual checks

The script prints the authoritative batch. The high-value checks are:

1. Multiple floating tools: drag/resize/raise/minimize/restore/close/reopen/host resize and restart geometry.
2. Theme switch with multiple windows open, dark/light scroll styling and restart.
3. Persistent custom colors + More Colors + reset/cancel behavior.
4. Appearance toggles while a composer draft exists, including hidden sidebar items and reset.
5. Large text + all densities at 1100×680; Frosted readability.
6. All effects, Solid capability state, effect color, Pause + minimize/restore, then later the 60-second performance trace.
7. Peek through minimize/restore/theme/close-reopen.
8. Harmony preview-vs-Apply behavior plus saved theme restart/import/export.
9. Shortcut conflict/clear/reset/restart and stable Settings/New Chat commands.
