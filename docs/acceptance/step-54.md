# Acceptance evidence — Step 54 Persistence and application data

- **Step:** 54
- **Status:** In progress; not marked Done
- **Build:** step54-foundation-1
- **Date:** 2026-09-21
- **Environment used for automated checks:** Linux build container, Python 3; PySide6 unavailable in this container
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
- `STARK_STUDIO_DATA_DIR` supports explicitly isolated demo/test data roots.
- v1 fixture migration test preserves an existing document while upgrading to v2.

## Automated checks executed

Command: `PYTHONPATH=. python3 -m unittest discover -s tests -v`

Result: **8/8 passed**.

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
- Exercise startup recovery presentation against an unavailable/corrupt store in the real GUI.
- Wire reset/export/import into its eventual GUI management surface and manually verify the affected/excluded-data wording.
- Add a GUI/demo launch fixture that supplies both temporary SQLite and temporary QSettings locations; both SQLite and QSettings now accept explicit isolated paths, but the Qt runtime could not be executed in this container.
