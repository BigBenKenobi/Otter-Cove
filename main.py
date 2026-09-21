from __future__ import annotations

import sys

from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication, QMessageBox

from app import MainWindow
from core import DataStoreError


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Stark Studio")
    app.setOrganizationName("Stark Studio")
    app.setStyle("Fusion")
    app.setFont(QFont(QFontDatabase.systemFont(QFontDatabase.FixedFont).family(), 10))

    try:
        window = MainWindow()
    except DataStoreError as exc:
        QMessageBox.critical(None, "Stark Studio local data", exc.user_message())
        raise SystemExit(2)

    window.show()
    raise SystemExit(app.exec())


if __name__ == "__main__":
    main()
