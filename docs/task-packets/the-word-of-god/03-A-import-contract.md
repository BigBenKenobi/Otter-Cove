# 03-A — Define and validate complete import snapshots

**Authority:** [OC-03](../../../PLAN.md#oc-03). **Requires:** 02-G PASSED.
**Outcome:** a fully validated in-memory snapshot exists before any replacement.

Read LocalDataService in `core/data/services.py`, repositories, records, migrations,
errors and time utilities in `core/data/`, and `tests/test_persistence.py`. Preserve
PR #6's `_nested_json` recovery behavior. Current schema is 2 and export version 1;
verify these facts rather than assuming a schema migration is needed.

1. Write a compact contract table alongside the validation code/docs: envelope
   versions, required tables, each field's type/nullability, supported role/state
   values, integer/range rules and timestamp representation. Derive valid values
   from existing domain call sites/tests and PLAN. Timestamps are currently strings;
   do not incorrectly convert them to numeric epochs. Preserve valid exact values.
   If a domain permits free text, state it; do not invent a restrictive enum.
2. Define supported export/schema pairs explicitly. Reject unknown future versions.
   If schema-1 snapshots are supported, normalize their missing document `source`
   deliberately with a fixture; do not infer support merely because v1 databases
   migrate. Document any older snapshot format rejected as unsupported.
3. Require all eight TABLES collections as lists, including explicit empty lists.
   Require object rows, nonempty string IDs, required fields and correctly typed
   optional values. Reject null restore IDs instead of generating them. Preserve
   ordinary create-with-no-ID behavior for new records outside restore.
4. Validate uniqueness and references before mutation: IDs within each table,
   messages' session references, per-session ordinal uniqueness, nonnegative integer
   ordinals (not booleans), booleans using explicitly supported JSON/SQLite forms,
   finite bounded numerics and valid timestamps. Do not coerce arrays into text,
   arbitrary truthy values into booleans, or invalid numbers into defaults.
5. Decode metadata/config objects and string-list tags before mutation. Reject
   malformed nested JSON and wrong shapes with DataValidationError carrying safe
   table/row/field context. Reject bad UTF-8/JSON through the same recoverable path.
   Do not echo offending values in errors. Raw programming errors should not be
   concealed by a blanket catch-all.
6. Share field validation with lower-level writes so direct service/repository
   calls cannot persist records that the import contract would reject. Separate
   restore-only completeness/identity requirements from new-record defaults.
   Keep transaction rollback as the final guard against write-time failures.

**Development checks:** future version, missing table, title array, null/duplicate
IDs, broken reference, duplicate ordinal, wrong booleans, malformed timestamps,
NaN/infinity, invalid nested structures and positive current export round trip.
For rejected imports assert old rows/IDs remain unchanged, not just an exception.
**Next:** 03-B after these focused checks pass. OC-03 is not yet gated complete.
