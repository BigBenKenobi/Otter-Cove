# Step 39 — Floating tool-window framework

Status: **Partial / implementation complete, Fedora acceptance pending**

Plan deliverable: shared floating-tool lifecycle with focus/raise, drag, resize, minimize/restore, close/reopen and safe persisted geometry.

## Implemented

- `ui/studio_window.py`
  - Opening an already-created tool reuses the same `StudioWindow`, raises/focuses it and preserves its existing content widget/state.
  - Opening a minimized tool restores its full body in the same action before raising it.
  - Close remains a manager-owned hide operation rather than widget destruction, so local tool state survives close/reopen cycles without reconnecting signals or recreating timers.
  - Normal and minimized geometries are tracked and signalled independently.
  - Drag-end and resize-end explicitly call `commit_geometry()`.
  - Minimized-window dragging updates the future restore position while preserving the full normal size.
  - Host resizing clamps the full window inside the workspace so the titlebar and bottom-right resize grip remain reachable.
  - Recovered/clamped geometry is immediately persisted so a display-size change does not recreate an invalid layout on the next restart.
  - Peek state remains attached to the persistent window/body and therefore survives minimize/restore and close/reopen without creating an input-blocking overlay.
- `core/settings.py`
  - Added `windows/<key>/normal_rect` and `windows/<key>/minimized_rect` records.
  - Previous `windows/<key>/rect` values remain a compatibility fallback, so upgrading does not discard an existing layout.
  - Legacy `window_rect()` / `set_window_rect()` methods remain aliases to the full-size geometry API.

## Automated acceptance coverage

`tests/test_studio_window_qt.py` checks:

1. Reopening an existing/minimized tool returns the same object, restores it, and retains local widget state.
2. Multiple overlapping tools can be raised; bounded movement/commit, resizing and minimize/restore work; host shrink keeps titlebar/grip reachable. Exact pointer drag is retained as a native Fedora smoke check.
3. Normal and minimized rectangles persist separately; a fresh manager on a smaller host restores the normal geometry and safely bounds it rather than restoring the collapsed bar dimensions.
4. Repeated close/reopen cycles retain one window/content instance and do not accumulate duplicate child windows.

Run on Fedora:

```bash
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

Expected suite size for this build: **30 tests**. In the build container, 18 Qt-independent tests pass and 12 Qt tests are skipped because PySide6 is not installed.

## Remaining before Done

- Run all 30 tests on the target Fedora/PySide6 runtime.
- Manually exercise two or more simultaneous tools: drag, resize, raise, minimize, reopen, close/reopen and host resize.
- Restart after moving/resizing a normal tool and confirm its full geometry restores; repeat after minimizing it to confirm the collapsed height never replaces the full geometry.
