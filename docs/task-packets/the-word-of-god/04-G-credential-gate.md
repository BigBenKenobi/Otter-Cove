# 04-G — Credential boundary gate

**Authority:** [OC-04](../../../PLAN.md#oc-04). Requires 04-A/B and the common gate.

- [ ] 04.1: Service, direct repository and import paths reject credential-bearing
  endpoint/userinfo/query fields, including encoded/case variants and nested values.
- [ ] 04.2: Structured credential-key rules cover mappings/lists while legitimate
  numeric token limits and safe endpoint/config values remain usable.
- [ ] 04.3: Legacy unsafe endpoint/encoded metadata/config and malformed structured
  data block export; database and previous output are unchanged with no residue.
- [ ] 04.4: UI feedback, exceptions and captured logs contain no synthetic secret
  values; remediation identifies a safe field location.
- [ ] 04.5: Ordinary body/content semantics are explicit and tested; no silent
  deletion/redaction or unsupported general secret-detection claim is introduced.
- [ ] 04.6: All earlier pilot regressions pass with the final shared policy;
  model UI/provider work remains deferred.

Fail: BLOCKED, return to the responsible 04 packet. Pass: PASSED → FINAL.
