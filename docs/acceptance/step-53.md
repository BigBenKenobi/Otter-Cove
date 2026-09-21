# Step 53 — Shared states and feedback

Status: **Done for the current GUI milestone.**

Plan deliverable: reusable empty, loading, error, retry and toast components plus deterministic demo adapters.

## Implemented

- `ui/shared_states.py`
  - `EmptyState`, `LoadingState`, `ErrorState`, `CancelledState`, `SuccessState` and `StateHost`.
  - Module-specific text/actions with shared styling.
  - Strong-focus actions and accessible names/descriptions.
  - Qt accessibility announcements without moving keyboard focus.
- `core/demo_states.py`
  - Explicit deterministic success, empty, loading, failure and cancellation fixtures.
  - Monotonic request tokens; newer requests supersede older ones.
  - Duplicate/stale completions cannot overwrite current state.
  - Retry always allocates a fresh request id.
- `ui/feedback.py`
  - Non-modal toast stack that does not request focus.
  - Important errors persist independently from toast lifetime.
  - Issues indicator exposes unresolved important errors after toast dismissal.
- `FeaturePlaceholder`
  - Unavailable routes use shared state visuals and deterministic demo fixtures.
- Main shell storage errors use shared feedback rather than a focus-stealing modal.

## Fedora acceptance evidence

On 2026-09-21 the user ran the complete 26-test suite on the Fedora/PySide6 target and received `OK`. All four `SharedStateQtAcceptanceTests` passed:

- `test_demo_host_ignores_stale_request_completion`
- `test_shared_state_actions_are_keyboard_focusable_and_accessible`
- `test_toast_does_not_steal_focus_and_important_error_survives_dismissal`
- `test_toast_stack_stays_inside_host`

The deterministic non-Qt request-state tests also passed. Later completed features must continue to use these shared components for their applicable states; final desktop accessibility/multi-scale validation is covered by Step 55.
