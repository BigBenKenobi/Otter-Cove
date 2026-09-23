# 03-G — Import gate

**Authority:** [OC-03](../../../PLAN.md#oc-03). Requires 03-A/B and the common gate.

- [ ] 03.1: Supported version pairs are documented/tested; future/unsupported pairs
  reject. Any supported legacy normalization has a representative fixture.
- [ ] 03.2: Missing collections, wrong row/field types, missing/null/duplicate IDs,
  broken references and duplicate/invalid ordinals reject before replacement.
- [ ] 03.3: Allowed states/roles, booleans, timestamps, finite numerics and nested
  metadata/config/tags follow the documented contract through import and direct writes.
- [ ] 03.4: Invalid UTF-8/JSON and title-array/nested-JSON regressions give typed,
  visible errors, with old persistent rows and UI/private state unchanged.
- [ ] 03.5: A representative all-table snapshot round-trips stable IDs, timestamps,
  message order and every persisted domain field; explicit empty lists work.
- [ ] 03.6: Preview counts/scope are accurate. Cancel changes nothing. Changed files
  and prepared-object mutation cannot substitute unconfirmed content.
- [ ] 03.7: A write-time failure after deletion has begun rolls the transaction back;
  no partial replacement or success-only UI refresh occurs.
- [ ] 03.8: OC-01/02 regressions still pass through the updated import handler.

Fail: BLOCKED, return to the responsible 03 packet. Pass: PASSED → 04-A.
