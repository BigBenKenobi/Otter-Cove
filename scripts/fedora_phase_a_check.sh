#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/.."

echo "=== Otter Cove Phase A Fedora check ==="
echo "Date: $(date -Is 2>/dev/null || date)"
echo "Python: $(python3 --version 2>&1)"
python3 - <<'PY'
try:
    import PySide6
    from PySide6.QtCore import qVersion
    print(f"PySide6: {PySide6.__version__}")
    print(f"Qt: {qVersion()}")
except Exception as exc:
    print(f"PySide6/Qt: unavailable ({exc})")
PY
if [[ -r /etc/os-release ]]; then
  . /etc/os-release
  echo "OS: ${PRETTY_NAME:-unknown}"
fi
echo "Desktop: ${XDG_CURRENT_DESKTOP:-unknown}"
echo "Session: ${XDG_SESSION_TYPE:-unknown}"
echo "Wayland display: ${WAYLAND_DISPLAY:-not-set}"
echo "Scale env: QT_SCALE_FACTOR=${QT_SCALE_FACTOR:-not-set} GDK_SCALE=${GDK_SCALE:-not-set}"
if command -v lspci >/dev/null 2>&1; then
  echo "GPU:"
  lspci | grep -Ei 'VGA|3D|Display' | sed 's/^/  /' || true
fi

echo
echo "=== Automated acceptance suite ==="
PYTHONPATH=. python3 -m unittest discover -s tests -v
status=$?

echo
if [[ $status -eq 0 ]]; then
  echo "Automated suite: PASS"
else
  echo "Automated suite: FAIL ($status)"
fi

echo
echo "=== Native Qt GUI smoke ==="
PYTHONPATH=. python3 scripts/fedora_gui_smoke.py
smoke_status=$?
if [[ $smoke_status -eq 0 ]]; then
  echo "Native GUI smoke: PASS"
else
  echo "Native GUI smoke: FAIL ($smoke_status)"
fi
if [[ $status -eq 0 && $smoke_status -ne 0 ]]; then
  status=$smoke_status
fi

echo
echo "=== Deferred manual batch ==="
cat <<'EOF'
[ ] Step 39: open two tools; drag/resize/raise, minimize one, reopen it from navigation, close/reopen, then resize the main window.
[ ] Step 39 restart: move/resize a normal tool, restart, confirm full geometry; minimize/move it and confirm collapsed height never replaces normal geometry.
[ ] Theme presets: switch several dark/light presets with Theme + Settings both open; confirm no white scroll viewport and all open surfaces update immediately; restart on the selected preset.
[ ] Custom colors: change base + More Colors tokens, restart, then Reset colors; canceled color picker must be a no-op.
[ ] Appearance: toggle full-width composer, welcome, Nobody, Web Search, Shell and one sidebar entry; draft/session must survive; Reset restores defaults.
[ ] Typography/layout: test Small/Default/Large, Compact/Comfortable/Roomy and Frosted at 1100x680 and your normal window size; no primary control becomes unreachable.
[ ] Backgrounds: switch all ten effects; Solid should disable animation-only controls; change effect color/speed/intensity/quality/size; pause, minimize the app briefly, restore, and confirm user Pause was not changed.
[ ] Peek: toggle Peek, minimize/restore the tool, switch theme, close/reopen it; body fades/restores exactly and titlebar remains usable.
[ ] Harmony + save/share: Generate must only preview; Apply changes colors. Save a named theme, restart/select it, export/import it, and verify duplicate/invalid imports do not change the current theme.
[ ] Shortcuts: rebind Theme, test a deliberate conflict, clear/reset it, restart, and confirm Settings/New Chat shortcuts still work even if their usual navigation surface is hidden.
[ ] Local Data: export JSON, cancel one import/reset, reject a malformed import, then confirm a valid import and reset report affected/excluded content accurately.
[ ] Animation measurement: run `PYTHONPATH=. python3 scripts/measure_background.py --effect Leaves --duration 60` while the window remains visible and unobscured; retain the native output with the acceptance record.
EOF

exit "$status"
