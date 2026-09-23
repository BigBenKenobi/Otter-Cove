# Architecture contracts

Read [STATUS](../STATUS.md), [PLAN](../PLAN.md) and the relevant acceptance record
before changing behavior. This document defines boundaries, not duplicate scope.

| Area | Contract |
|---|---|
| `main.py` | Bootstrap QApplication and report startup failure; no feature logic. |
| `app.py` | Composition root: owns services, preferences, routing, workspace and window manager. Connect components through signals/contracts. |
| `core/` | Shared route/command registries, application state, semantic themes and preferences. |
| `core/data/` | Existing local services, repositories, validation and versioned SQLite transactions/migrations. |
| `ui/` | Presentation and user interaction. Consume services; do not issue SQL or make network/process calls directly. |
| `services/` | Reserved external-provider adapters. Do not move or duplicate working `core/data/` services just to fill this directory. |
| `effects/` | Independent animated-background implementations and their lifecycle/timing manager. |
| `assets/` | Runtime packaged assets, distinct from reference media and acceptance captures. |

## Data and state

SQLite stores durable content; QSettings stores preferences and geometry. Stable
IDs connect domain records. Repositories own SQL; services own use-case behavior;
widgets display state rather than becoming the only copy of it. Import/reset are
transactional; export is atomic. Migrations must preserve existing content or fail
without replacing the store. No plaintext credentials belong in normal storage.

Incognito content must remain transient, excluded from history/export/search and
memory extraction. Closing a private session must dispose it. Main already has
normal/private view and draft isolation plus New Chat disposal.
The replacement PLAN tracks the remaining explicit transitions, durable-reset
preservation and shutdown/consumer boundaries; the contract does not imply full
feature acceptance.
Failed saves must retain editable drafts; persistence errors must be recoverable.

## Shell, windows and commands

The route registry owns navigation metadata. The command registry owns stable IDs,
bindings, enabled state and conflict handling. UI labels/tooltips reflect current
bindings. A route scaffold is unavailable functionality, not a feature implementation.

Workspace layers are background, chat and floating tools. `StudioWindow` tools
are child widgets managed by one window manager; preserve content through hide/
reopen and persist full geometry separately from minimized geometry. Peek fades
the body only and is visual-only; titlebar interaction remains available.

## Theme and effect contracts

Use semantic theme tokens and centralized typography/density. Existing and new
widgets must react to live changes; avoid literal colors and fixed sizes that
break large text. Frosted is the documented translucent fallback, not OS blur.
Effects implement reset/resize/update/paint; the manager owns timing and shared
settings. Pause is independent from hidden/inactive suspension. Solid does not
need an animation timer. Performance acceptance belongs to PLAN.md.

## Service adapters and feedback

GUI milestones use deterministic, explicitly labelled demo adapters for external
operations. Fixtures cover success, empty, loading, failure and cancellation.
Request tokens prevent stale completions; cancellation and retry must not duplicate
work. Reuse shared state/feedback components; important errors remain accessible
after transient toasts. Future live providers replace adapters, not widget logic.
