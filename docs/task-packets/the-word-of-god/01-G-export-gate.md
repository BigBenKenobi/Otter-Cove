# 01-G — Export gate

**Authority:** [OC-01](../../../PLAN.md#oc-01). Requires 01-A and the common gate.

- [ ] 01.1: Local-data and shell theme exports reject the active database, WAL,
  SHM and settings paths, including sidecars not currently present.
- [ ] 01.2: Relative aliases, symlink targets/parents and existing hard-link aliases
  are covered on a filesystem supporting them; missing coverage blocks this gate.
- [ ] 01.3: Rejection occurs before mkdir/temp creation/writing. Protected bytes and
  pre-existing targets are unchanged; the database reopens with the same rows.
- [ ] 01.4: Valid exports remain atomic, parseable and usable; simulated write
  failure leaves the old destination intact and cleans temporary output.
- [ ] 01.5: Service errors reach visible UI feedback without an uncaught exception.

Record test names per item. Fail: BLOCKED, return to 01-A. Pass: PASSED → 02-A.
