# 01-A — Protect storage from export destinations

**Authority:** [OC-01](../../../PLAN.md#oc-01). **Requires:** 00-G PASSED.
**Outcome:** both local-data and theme exports reject application storage targets.

Inspect `LocalDataService.export_json` in `core/data/services.py`, store path
ownership in `core/data/database.py`, AppSettings in `core/settings.py`, and
`MainWindow._export_theme` / `save_theme_bundle_atomic` in app/theme logic.

1. Reproduce the live-database overwrite using a disposable store with known rows.
   Never point a probe at the user's active profile. Add a regression that checks
   typed rejection and that the database reopens with its original records.
2. Introduce a shared, Qt-independent target validation helper. Supply it the real
   protected paths from owners: active SQLite file, `-wal`, `-shm`, and preferences.
   Add a public settings-path accessor if needed; do not hard-code the default
   profile when the app uses injected paths. Thread protection through services
   and the shell-owned theme export boundary without making core depend on Qt.
3. Validate before mkdir, temporary-file creation or destination writes. Compare
   normalized/resolved paths and existing file identity so relative aliases,
   symlinks (including a symlinked parent) and hard links cannot bypass protection.
   Handle absent sidecars too. Convert expected target errors into an appropriate
   typed, readable error caught by the relevant UI.
4. Keep atomic writing for valid destinations. Do not rely on filename extensions
   or dialog filtering. A rejected target must leave storage, preferences and any
   existing destination unchanged, with no created output directory/temp file.
5. Add focused data-service and theme/shell regression tests. Exercise aliases on
   the real filesystem, and verify rejection precedes writer/mkdir calls where
   byte preservation alone would miss an attempted side effect.

**Boundaries:** no general file sandbox, TOCTOU security redesign or theme feature
rewrite. The policy covers known active storage paths and their identities.
**Development checks:** direct/alias/sidecar/preferences rejection, readable UI
feedback, normal replacement of an ordinary export, failure preserves its bytes.
**Next:** 01-G.
