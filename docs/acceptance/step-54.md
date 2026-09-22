# Acceptance evidence — Step 54 Persistence and application data

- **Step:** 54
- **Status:** In progress; not marked Done
- **Build:** stacked R2 local-data-management update
- **Date:** 2026-09-22
- **Environment used for current automated checks:** Linux build container, PySide6 offscreen
- **Storage fixture:** isolated `tempfile.TemporaryDirectory()` per test

## Implemented in this build

- Versioned SQLite store with schema v2 and atomic migrations.
- Stable prefixed UUID IDs.
- Repositories for sessions/messages, models, documents, Brain items, notes, tasks and Gallery metadata.
- UI-facing service layer; chat uses `SessionService` rather than direct SQL.
- Nobody/incognito sessions remain process-memory-only and are excluded from SQLite/export snapshots.
- Credential-like model/config fields are rejected from ordinary storage; no credential table exists.
- Atomic JSON export (`fsync` + `os.replace`), transactional reset/import and structured operation reports listing affected/excluded data.
- Corrupt/unavailable-store exceptions include non-destructive recovery options; startup reports them instead of replacing the store.
- `OTTER_COVE_DATA_DIR` supports explicitly isolated demo/test data roots.
- v1 fixture migration test preserves an existing document while upgrading to v2.
- Settings exposes export, confirmed import and confirmed reset through the service
  layer, reports affected/excluded data and keeps malformed imports non-mutating.

## Automated checks executed

Command: `PYTHONPATH=. python3 -m unittest discover -s tests -v`

Current full-suite result: **74/74 passed with no skips**, plus the offscreen GUI
smoke check. The original focused persistence record was **8/8 passed**.

1. Fresh schema reaches current version and all domain repository records survive close/reopen.
2. Incognito session/message never appears in SQLite or exported JSON and does not restore after reopen.
3. Credential-like configuration is rejected before persistence.
4. Export → reset → import restores stable session/note IDs.
5. v1 fixture migrates to v2 without losing the existing row.
6. Failed replace-import rolls back and preserves existing content.
7. An unavailable store path reports recovery options without replacing the blocking file.
8. Corrupt database bytes are reported and left byte-for-byte untouched.

`python3 -m compileall -q .` also passed.

## Remaining before Step 54 can be marked Done

- Fedora/PySide6 QSettings sidebar/main-geometry restart round-trip is now covered by the passing Step 01 shell acceptance test.
- Exercise startup recovery presentation against an unavailable/corrupt store in
  the real GUI; the outer startup boundary already presents the service recovery
  message without replacing the store.
- Manually verify native import/export dialogs, confirmation/cancel behavior and
  affected/excluded-data wording on Fedora/Wayland.
- Record a native GUI run with isolated SQLite and QSettings locations. Automated
  Qt coverage uses isolated fixtures offscreen and is supplementary evidence.
