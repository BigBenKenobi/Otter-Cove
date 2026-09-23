# Pilot run record — OC-04

- Tested implementation commit: `6b5e4e1c4092207055425a9c598005069a41e949`
- Gate result: PASSED

Structured endpoint fields now reject URL userinfo and normalized credential query names; exact credential key names recurse through structured mappings/lists without rejecting legitimate `token_limit` values. Ordinary document/message content is explicitly outside this scanner. Snapshot decoding rechecks legacy JSON fields before export.

| Criterion | Evidence | Result |
|---|---|---|
| 04.1–04.2 | `test_credential_endpoint_is_rejected_without_leaking_or_inserting` | PASS |
| 04.3–04.4 | `test_legacy_unsafe_structured_record_blocks_export_without_writing` | PASS |
| 04.5 | ordinary document positive control in endpoint regression | PASS |
| 04.6/common gate | 83 tests, zero skips/expected failures; offscreen smoke exit 0 | [final-full-suite.log](04/final-full-suite.log), [final-smoke.log](04/final-smoke.log) |

No native or reference acceptance is claimed.

