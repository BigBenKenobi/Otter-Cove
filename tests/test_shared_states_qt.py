from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication, QLineEdit, QWidget
    HAS_QT = True
except ModuleNotFoundError:
    HAS_QT = False


@unittest.skipUnless(HAS_QT, "PySide6 is required for shared-state acceptance tests")
class SharedStateQtAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if HAS_QT:
            cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        if not HAS_QT:
            return
        from ui.feedback import FeedbackManager

        self.host = QWidget()
        self.host.resize(1000, 700)
        self.host.show()
        self.feedback = FeedbackManager(self.host)
        self.app.processEvents()

    def tearDown(self) -> None:
        if HAS_QT:
            self.host.close()
            self.app.processEvents()

    def test_shared_state_actions_are_keyboard_focusable_and_accessible(self) -> None:
        from ui.shared_states import EmptyState, ErrorState, LoadingState

        states = [
            EmptyState("No notes", "There are no notes yet.", action_label="Create note"),
            LoadingState("Loading notes", "Please wait."),
            ErrorState("Couldn’t load notes", "Demo failure."),
        ]
        for state in states:
            with self.subTest(state=type(state).__name__):
                self.assertTrue(state.accessibleName())
                self.assertTrue(state.accessibleDescription())
                self.assertIsNotNone(state.primary_button)
                self.assertEqual(state.primary_button.focusPolicy(), Qt.StrongFocus)

    def test_toast_does_not_steal_focus_and_important_error_survives_dismissal(self) -> None:
        editor = QLineEdit(self.host)
        editor.show()
        editor.setFocus()
        self.app.processEvents()
        before = self.app.focusWidget()

        entry = self.feedback.error("Storage", "Database is unavailable.", important=True, timeout_ms=0)
        self.app.processEvents()
        self.assertIs(self.app.focusWidget(), before)
        self.assertTrue(self.feedback.issue_button.isVisible())
        self.assertEqual(len(self.feedback.important_errors()), 1)

        self.feedback.dismiss(entry.entry_id)
        self.app.processEvents()
        self.assertEqual(len(self.feedback.important_errors()), 1)
        self.assertTrue(self.feedback.issue_button.isVisible())

        self.feedback.resolve(entry.entry_id)
        self.app.processEvents()
        self.assertEqual(len(self.feedback.important_errors()), 0)
        self.assertFalse(self.feedback.issue_button.isVisible())

    def test_toast_stack_stays_inside_host(self) -> None:
        self.feedback.info("One", "First", timeout_ms=0)
        self.feedback.info("Two", "Second", timeout_ms=0)
        self.app.processEvents()
        for toast in self.feedback._toasts.values():
            self.assertGreaterEqual(toast.x(), 0)
            self.assertGreaterEqual(toast.y(), 0)
            self.assertLessEqual(toast.x() + toast.width(), self.host.width())
            self.assertLessEqual(toast.y() + toast.height(), self.host.height())

    def test_demo_host_ignores_stale_request_completion(self) -> None:
        from core.demo_states import DemoScenario, DemoStatus
        from ui.shared_states import DemoStateHost, LoadingState

        host = DemoStateHost("Email", feedback=self.feedback, parent=self.host)
        old_id = host.run(DemoScenario.SUCCESS)
        current_id = host.run(DemoScenario.FAILURE)
        stale = host.finish(old_id)
        self.assertEqual(stale.status, DemoStatus.STALE)
        self.assertIsInstance(host.current, LoadingState)
        result = host.finish(current_id)
        self.assertEqual(result.status, DemoStatus.FAILURE)


if __name__ == "__main__":
    unittest.main()
