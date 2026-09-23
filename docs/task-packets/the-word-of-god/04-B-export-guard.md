# 04-B — Stop unsafe legacy structured records at export

**Authority:** [OC-04](../../../PLAN.md#oc-04). **Requires:** 04-A focused checks pass.
**Outcome:** legacy unsafe structured content cannot escape through local export.

1. Inspect LocalDataService.snapshot/export. SQLite stores nested JSON as encoded
   strings; checking only the raw outer row cannot inspect those fields. Decode
   the known structured columns strictly and run the same policy as writes before
   producing an export. Malformed stored structured data must also fail safely.
2. Test a pre-existing unsafe record by seeding synthetic data directly in a
   disposable fixture (bypassing the production writer only for this regression).
   Cover endpoint credentials and nested metadata/config encoded in SQLite JSON.
3. Block export with a sanitized field-level remediation message. Leave database
   contents unchanged and any existing output untouched; do not delete unsafe
   records or silently drop fields to make export succeed. No unsafe temp output
   should remain. OC-01 destination protection must still run before side effects.
4. Verify UI reports failure usefully and does not leak the URL/secret through
   result text, exception formatting or captured logs. Assert absence of distinct
   synthetic secret strings in these outputs, not just an error class.
5. Add positive controls: legitimate numeric token limits, non-secret endpoints,
   ordinary content and safe nested data still create/import/export successfully.
   Re-run OC-03 round trips and OC-02 handler regressions against the combined code.
6. Document the repaired policy boundary for future feature 40–44 work without
   marking those features implemented or reopening deferred model PR #7.

**Development checks:** unsafe legacy export fails without destination/database
mutation; safe exports round-trip; errors are useful and sanitized.
**Next:** 04-G.
