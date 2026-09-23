# The word of God — Pilot 1 run index

- Base: `ada8b9992786006af57e34631096c3a195108a55` (`main`, fetched 23 September 2026)
- R2 candidate: `a560b5d7c7d88fc6d941e0d5da8542c9ac7d64c3` (`origin/fix/r2-data-recovery`, fetched 23 September 2026)
- Branch: `terra/word-of-god-pilot-2026-09-23`
- Current tested implementation: `6b5e4e1c4092207055425a9c598005069a41e949`

| Task | Status | Record |
|---|---|---|
| OC-00 | PASSED | [00-baseline.md](00-baseline.md) |
| OC-01 | PASSED | [01-export-targets.md](01-export-targets.md) |
| OC-02 | PASSED | [02-replacement-lifecycle.md](02-replacement-lifecycle.md) |
| OC-03 | PASSED | [03-import-contract.md](03-import-contract.md) |
| OC-04 | PASSED | [04-credential-policy.md](04-credential-policy.md) |

Current packet: `FINAL`.

Next command: hand control to the owner; do not start OC-05.

Blockers: none for the automated Pilot 1 gates.

Native/reference status: pending. The run used Qt `offscreen` on Fedora 44; its smoke log is supplementary only. `docs/reference/` is ignored and absent from this checkout, so original-reference parity cannot be assessed.
