"""Minimal executable bootstrap for the Stark Studio desktop application.

Application composition belongs in :mod:`app`; keeping this module narrowly
focused on Qt process setup makes startup failure handling explicit and lets tests
construct ``MainWindow`` with isolated dependencies without entering an event loop.
"""

from __future__ import annotations

import sys

from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication, QMessageBox

from app import MainWindow
from core import DataStoreError


def main() -> None:
    """Create the Qt application, build the shell, and transfer control to Qt.

    The process-wide ``QApplication`` must exist before ``MainWindow`` creates Qt
    widgets, settings-backed presentation objects, or theme fonts.  A datastore
    startup failure is caught at this outer boundary so users get a clear modal
    recovery message instead of a raw traceback; other unexpected exceptions are
    deliberately not concealed.
    """
    # These values identify the application to Qt and its platform integrations,
    # while Fusion supplies a stable cross-desktop widget baseline for this concept.
    app = QApplication(sys.argv)
    app.setApplicationName("Stark Studio")
    app.setOrganizationName("Stark Studio")
    app.setStyle("Fusion")
    # Start with a deterministic system monospace default.  ThemeManager may apply
    # the user's saved font/size afterward while MainWindow is being composed.
    app.setFont(QFont(QFontDatabase.systemFont(QFontDatabase.FixedFont).family(), 10))

    try:
        window = MainWindow()
    except DataStoreError as exc:
        # Local content cannot safely be used when its store fails to open.  The
        # service provides a user-oriented message; exit code 2 distinguishes this
        # known initialization failure from ordinary event-loop termination.
        QMessageBox.critical(None, "Stark Studio local data", exc.user_message())
        raise SystemExit(2)

    # ``exec`` owns the GUI loop until the user closes the shell.  Raising
    # SystemExit forwards Qt's final status to command-line launchers unchanged.
    window.show()
    raise SystemExit(app.exec())


if __name__ == "__main__":
    # Keep import and direct-execution behavior separate for testability.
    main()
