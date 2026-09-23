# 04-A — Enforce structured credential policy on writes

**Authority:** [OC-04](../../../PLAN.md#oc-04). **Requires:** 03-G PASSED.
**Outcome:** existing structured write paths reject credentials without rejecting
legitimate non-secret settings. This is storage repair, not model feature work.

Inspect `core/data/policy.py`, ModelService/ModelRepository, metadata/config write
paths, AppSettings' policy use, and the new OC-03 validators.

1. Add a synthetic regression through both service and direct repository create:
   `https://synthetic-user:synthetic-pass@example.invalid/?api_key=synthetic`.
   Assert typed rejection and no inserted record. Use no real endpoint credentials.
2. Define a documented structured-field policy. Normalize field/key names
   consistently; reject credential fields recursively through mappings/lists.
   Replace arbitrary substring matching with explicit credential names/patterns
   and narrowly defined legitimate numeric settings such as token limits. An
   allowlisted numeric setting carrying a secret string must still reject.
3. Parse known endpoint/URL fields with a standard URL parser. Reject userinfo,
   including username-only forms, and credential-bearing query parameters with
   normalized/decoded names. Cover case and percent-encoding variants; malformed
   structured endpoints must give safe typed errors rather than bypass policy.
   Do not fetch the URL or add authentication/provider logic.
4. Apply the same policy to service and repository paths and decoded import data,
   including nested config/metadata. Keep Qt outside this policy. Check effects
   on QSettings callers so the shared policy does not create another bypass.
5. Specify that ordinary document/message body text is content, not recursively
   interpreted as structured endpoint/config data. Do not silently redact, rewrite
   or promise to discover every secret in arbitrary prose. Keep that limitation
   explicit in policy documentation and positive-control tests.

**Development checks:** forbidden credential keys/URL values nested in objects and
lists; direct repository/service/import rejection; allowed non-secret endpoint
and numeric token limit; free text retains original bytes/meaning. Error messages
identify the field, never the supplied credential or full unsafe URL.
**Next:** 04-B after focused checks pass; OC-04 is not yet gated complete.
