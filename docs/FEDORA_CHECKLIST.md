# Deferred Fedora acceptance batch

When you are back at the Fedora machine, start with one command from the project root:

```bash
./scripts/fedora_phase_a_check.sh
```

It records the Fedora/desktop/session/PySide6/Qt/GPU context, runs the full automated test suite, runs an isolated native-Qt smoke pass, and then prints the manual checks below. The smoke pass uses a temporary database and settings file; it does **not** modify your normal Otter Cove data.

## Manual checks to batch

- [ ] **Floating tools (39):** open two tools, drag/resize/raise them, minimize one, reopen it from navigation, close/reopen it, and resize the main window. Restart once and confirm normal geometry returns rather than the collapsed height.
- [ ] **Theme presets (32):** with Theme and Settings open, switch several dark and light presets. Existing surfaces should update immediately and no light/white scroll viewport should appear in a dark preset. Restart on the chosen preset.
- [ ] **Theme customization (33):** change primary and More Colors tokens, restart, then Reset Colors. Open a color picker and cancel; cancellation must change nothing.
- [ ] **Appearance (47):** while text is sitting unsent in the composer, toggle full-width, welcome, Nobody, Web Search, Shell and one sidebar entry. The draft/session must remain. Reset must restore documented defaults.
- [ ] **Typography/layout (35):** exercise Small/Default/Large, Compact/Comfortable/Roomy and Frosted at 1100×680 and your normal size. No primary control should become unreachable or unreadable.
- [ ] **Backgrounds (36):** switch all ten effects. Solid should disable animation-only controls and run no animation timer. Change color/speed/intensity/quality/size, Pause, minimize the application briefly, restore it, and confirm the user Pause value did not change.
- [ ] **Peek (38):** Peek a tool, minimize/restore it, change theme, close/reopen it. Only the body should fade; titlebar controls must remain usable and normal opacity must restore exactly.
- [ ] **Harmony + theme save/share (34/37):** Generate should preview only; Apply should mutate theme colors. Save a named theme, restart/select it, export/import it, and try a duplicate/invalid import. Failed import must not alter the current theme.
- [ ] **Shortcuts (50):** rebind Theme, deliberately create a conflict, clear/reset, restart, and verify the binding persists. Hide the usual New Chat/Settings navigation entries and verify their shortcuts still work.

## Performance pass (later in the same Fedora session)

Step 36 still needs its reference-machine 60-second animation trace at 1720×900 / Balanced quality. Do that after the functional checks so any visual/effect bug is fixed before spending time profiling.

## Phase A fix 1

The Fedora run on 2026-09-21 reached 64/65 automated tests with the native GUI smoke passing. The sole failure was the More Colors acceptance test querying effective visibility while the Customize stacked page was hidden. The toggle now tracks its own expansion state, and the test switches to Customize before asserting user-visible state.

Re-run `./scripts/fedora_phase_a_check.sh`; expected automated result is 65/65 before manual checks.
