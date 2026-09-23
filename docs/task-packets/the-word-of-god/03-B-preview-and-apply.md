# 03-B — Apply exactly the confirmed snapshot

**Authority:** [OC-03](../../../PLAN.md#oc-03). **Requires:** 03-A focused checks pass.
**Outcome:** the user confirms a validated snapshot, and that same data is applied.

Inspect the R2 settings import handler, operation reports and tests. This packet
builds on 03-A validation and 02-A's replacement lifecycle.

1. Separate preparation from application. Preparation reads/decodes/validates once
   and produces a service-owned immutable snapshot (or equivalently protected deep
   copy) and counts. Application accepts that prepared result rather than reopening
   the path. A caller must not bypass validation by constructing/mutating a result;
   keep construction controlled or revalidate the in-memory contents at apply.
2. Show validated incoming per-table counts, durable replacement scope, draft
   consequences and excluded private/settings/theme state before confirmation.
   Preserve explicit empty-table counts so an empty replacement is unmistakable.
   Invalid input shows safe feedback before any destructive confirmation/apply.
3. Cancel means no storage or UI changes. Confirm applies the exact prepared data
   in one transaction; transaction failure rolls back all old data. Refresh views
   only after commit through the OC-02 operation. Report actual counts/scope.
4. Retain a compatible service import entry point for non-GUI callers, internally
   using the same prepare/apply path. Do not duplicate validators in the shell.
5. Test a file replaced or deleted between preview and confirmation: either apply
   the original prepared snapshot or explicitly invalidate/cancel; never import
   different, unconfirmed data. Test mutation attempts against prepared data.
6. Extend GUI recovery tests for malformed UTF-8, title arrays and nested JSON,
   plus cancellation, write-time failure and an intentionally empty snapshot.

**Boundaries:** no async job system, partial merge mode or arbitrary size policy;
responsiveness work belongs to OC-07. Preserve OC-01 target guards and OC-02 state.
**Development checks:** counts match the confirmed/applied fixture; no re-read race;
full round trip preserves IDs, timestamps, order and all domain fields. Normalized
supported legacy defaults are the documented exception, never silent data loss.
**Next:** 03-G.
