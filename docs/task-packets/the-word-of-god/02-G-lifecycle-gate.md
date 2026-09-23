# 02-G — Replacement lifecycle gate

**Authority:** [OC-02](../../../PLAN.md#oc-02). Requires 02-A and the common gate.

- [ ] 02.1: Both import and reset preserve excluded private messages/draft/mode
  while private is active and while normal is active with private state retained.
- [ ] 02.2: Removed durable IDs, rendered messages and cached drafts cannot reappear,
  including after switching modes and when imported IDs collide with old IDs.
- [ ] 02.3: Normal view displays correct imported content or a truthful empty state;
  a currently active private view is not switched by replacement.
- [ ] 02.4: Pending normal draft protection and any destructive draft confirmation
  match the documented policy; service/dialog/result scope statements agree.
- [ ] 02.5: Cancellation and validation/storage failures preserve all pre-operation
  visible and service state for both operations, with usable error feedback.
- [ ] 02.6: Explicit New Chat still disposes the private session/draft when intended;
  no private data or unsent draft has entered persistent storage/export.

Fail: BLOCKED, return to 02-A. Pass: PASSED → 03-A.
