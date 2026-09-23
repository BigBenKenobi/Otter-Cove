"""Chat workspace and composer widgets.

This presentation module owns the local chat surface, delegates session and
message persistence to :class:`core.data.SessionService`, and reflects accepted
messages in Qt widgets.  Composer text remains presentation-owned until the
service accepts a submission, which lets storage failures leave the complete
editable draft available for a safe retry.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
)

from core.data import DataStoreError, SessionService
from ui.iconography import LineIcon


@dataclass(frozen=True)
class ComposerDraft:
    """Text and mode owned by one session or one unsaved session slot."""

    text: str = ""
    mode: str = "Agent"


class PromptEditor(QPlainTextEdit):
    """Multiline editor that translates Ctrl+Enter into a submit request."""

    submitRequested = Signal()

    def keyPressEvent(self, event) -> None:
        """Request submission for Ctrl+Enter and preserve normal editor input."""

        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and event.modifiers() & Qt.ControlModifier:
            self.submitRequested.emit()
            event.accept()
            return
        super().keyPressEvent(event)


class PromptBox(QFrame):
    """Own the editable draft and emit submission attempts to the chat surface.

    The box retains its text and selected mode while a submission is attempted.
    Its owner must call :meth:`accept_submission` after durable acceptance; a
    failed attempt therefore leaves the exact draft ready for correction or
    retry instead of losing user input.
    """

    submitted = Signal(str, str)
    actionRequested = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("PromptBox")
        self.setMinimumWidth(520)
        self._full_width = False
        self.setMaximumWidth(720)
        self.setFixedHeight(96)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 8, 10, 8)
        root.setSpacing(4)

        top = QHBoxLayout()
        self.editor = PromptEditor()
        self.editor.setObjectName("PromptEditor")
        self.editor.setPlaceholderText("Message Odysseus...")
        self.editor.setMaximumHeight(42)
        self.editor.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        top.addWidget(self.editor, 1)
        self.model_button = QPushButton("Select model⌃")
        self.model_button.setObjectName("ModelButton")
        self.model_button.setCursor(Qt.PointingHandCursor)
        self.model_button.setAccessibleName("Select model")
        self.model_button.clicked.connect(lambda: self.actionRequested.emit("model_selector"))
        top.addWidget(self.model_button, 0, Qt.AlignTop)
        root.addLayout(top)

        bottom = QHBoxLayout()
        bottom.setSpacing(7)
        search = QPushButton("")
        self.search_button = search
        search.setObjectName("PromptIcon")
        search.setFixedSize(36, 36)
        search.setCursor(Qt.PointingHandCursor)
        search.setToolTip("Web search is unavailable in this local GUI milestone.")
        search.setAccessibleName("Web search, unavailable")
        search.setEnabled(False)
        search.clicked.connect(lambda: self.actionRequested.emit("search"))
        search_icon = LineIcon("search", 22, search, follow_parent=True)
        search_icon.move(7, 7)

        term = QPushButton("")
        self.shell_button = term
        term.setObjectName("PromptIcon")
        term.setFixedSize(36, 36)
        term.setCursor(Qt.PointingHandCursor)
        term.setToolTip("Shell access is unavailable; no command execution is connected.")
        term.setAccessibleName("Shell access, unavailable")
        term.setEnabled(False)
        term.clicked.connect(lambda: self.actionRequested.emit("tools"))
        term_icon = LineIcon("shell", 22, term, follow_parent=True)
        term_icon.move(7, 7)
        bottom.addWidget(search)
        bottom.addWidget(term)
        bottom.addStretch()

        toggle = QFrame()
        toggle.setObjectName("ModeToggle")
        tl = QHBoxLayout(toggle)
        tl.setContentsMargins(2, 2, 2, 2)
        tl.setSpacing(0)
        self.agent_button = QPushButton("Agent")
        self.chat_button = QPushButton("Chat")
        self.mode_group = QButtonGroup(self)
        self.mode_group.setExclusive(True)
        for button in (self.agent_button, self.chat_button):
            button.setCheckable(True)
            button.setObjectName("ModeButton")
            button.setCursor(Qt.PointingHandCursor)
            button.setAccessibleName(f"{button.text()} mode")
            button.setToolTip(f"Switch to {button.text()} mode")
            self.mode_group.addButton(button)
            tl.addWidget(button)
        self.agent_button.setChecked(True)
        bottom.addWidget(toggle)

        send = QPushButton("")
        self.send_button = send
        send.setObjectName("SendButton")
        send.setFixedSize(34, 34)
        send.setCursor(Qt.PointingHandCursor)
        send.setToolTip("Send")
        send.setAccessibleName("Send message")
        send.clicked.connect(self.submit)
        send_icon = LineIcon("send", 22, send, follow_parent=True)
        send_icon.move(6, 6)
        bottom.addWidget(send)
        root.addLayout(bottom)

        self.editor.submitRequested.connect(self.submit)


    def set_full_width(self, full_width: bool) -> None:
        self._full_width = bool(full_width)
        self.setMaximumWidth(16777215 if self._full_width else 720)

    def set_action_visibility(self, *, web_search: bool, shell: bool) -> None:
        self.search_button.setVisible(bool(web_search))
        self.shell_button.setVisible(bool(shell))

    def draft_text(self) -> str:
        """Return the complete editor contents without trimming user input."""

        return self.editor.toPlainText()

    def set_draft_text(self, text: str) -> None:
        """Replace the editable draft, primarily for restoration and tests."""

        self.editor.setPlainText(text)

    def mode(self) -> str:
        """Return the currently selected submission mode."""

        return "Agent" if self.agent_button.isChecked() else "Chat"

    def set_mode(self, mode: str) -> None:
        """Restore a draft's valid Agent/Chat selection."""

        (self.chat_button if mode == "Chat" else self.agent_button).setChecked(True)

    def submit(self) -> None:
        """Emit a non-empty submission attempt without consuming its draft.

        Storage is performed by :class:`ChatSurface`.  Keeping ownership here
        until that boundary reports success prevents local-data failures from
        clearing text or changing the selected mode.
        """

        text = self.editor.toPlainText().strip()
        if not text:
            return
        self.submitted.emit(text, self.mode())

    def accept_submission(self, text: str, mode: str) -> None:
        """Clear the draft accepted by the owner if it is still current.

        The identity check protects a newer edit or mode change if persistence
        later becomes asynchronous.  A successful synchronous submission clears
        exactly once; a failed submission never calls this method.
        """

        if self.editor.toPlainText().strip() == text and self.mode() == mode:
            self.editor.clear()


class ChatSurface(QWidget):
    """Home/chat surface backed by SessionService, including ephemeral Nobody mode."""

    actionRequested = Signal(str)
    storageError = Signal(str)

    def __init__(self, sessions: SessionService, parent=None) -> None:
        super().__init__(parent)
        self.sessions = sessions
        self._session_id: str | None = None
        self._session_incognito = False
        self._session_title = "New Chat"
        # Each privacy mode remembers its active session independently. Drafts
        # belong to a concrete session ID when one exists, or to the pending slot
        # for that mode before its first accepted message.
        self._mode_session_ids: dict[bool, str | None] = {False: None, True: None}
        self._drafts: dict[str, ComposerDraft] = {}

        self.setObjectName("ChatSurface")
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 10, 22, 18)

        header = QHBoxLayout()
        header.addStretch()
        self.chat_label = QLabel("New Chat⌄")
        self.chat_label.setObjectName("ChatHeader")
        header.addWidget(self.chat_label)
        header.addStretch()
        root.addLayout(header)
        self.status_summary = QLabel("Local GUI session · persistent storage")
        self.status_summary.setObjectName("HeroHint")
        self.status_summary.setAlignment(Qt.AlignCenter)
        self.status_summary.setAccessibleName("Session status summary")
        root.addWidget(self.status_summary)
        root.addStretch(2)

        self.hero = QWidget()
        hero = QVBoxLayout(self.hero)
        hero.setContentsMargins(0, 0, 0, 0)
        hero.setAlignment(Qt.AlignCenter)
        hero.setSpacing(8)
        self.hero_title = QLabel("♠ Otter Cove")
        self.hero_title.setObjectName("HeroTitle")
        self.hero_title.setAlignment(Qt.AlignCenter)
        hero.addWidget(self.hero_title)
        self.hero_ready = QLabel("New chat ready.")
        self.hero_ready.setObjectName("HeroSub")
        self.hero_ready.setAlignment(Qt.AlignCenter)
        hero.addWidget(self.hero_ready)
        self.hero_hint = QLabel("Pick a model if you want, or just type.")
        self.hero_hint.setObjectName("HeroHint")
        self.hero_hint.setAlignment(Qt.AlignCenter)
        hero.addWidget(self.hero_hint)
        self.nobody = QPushButton("⊙ Nobody")
        self.nobody.setObjectName("NobodyButton")
        self.nobody.setCheckable(True)
        self.nobody.setCursor(Qt.PointingHandCursor)
        self.nobody.setAccessibleName("Nobody mode")
        self.nobody.setToolTip("Nobody mode is ephemeral: this session is not written to local history.")
        # Keep the compact reference width while allowing translated or enlarged
        # text and Roomy density to expand the control instead of clipping it.
        self.nobody.setMinimumWidth(82)
        self.nobody.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.nobody.toggled.connect(self._on_nobody_toggled)
        hero.addWidget(self.nobody, alignment=Qt.AlignCenter)
        root.addWidget(self.hero)

        self.message_area = QScrollArea()
        self.message_area.setObjectName("MessageArea")
        self.message_area.setWidgetResizable(True)
        self.message_area.setFrameShape(QFrame.NoFrame)
        self.message_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.message_area.setVisible(False)
        self.message_host = QWidget()
        self.message_host.setObjectName("MessageHost")
        self.message_layout = QVBoxLayout(self.message_host)
        self.message_layout.setContentsMargins(120, 12, 120, 12)
        self.message_layout.setSpacing(8)
        self.message_layout.addStretch()
        self.message_area.setWidget(self.message_host)
        root.addWidget(self.message_area, 1)

        root.addSpacing(82)
        self.prompt = PromptBox()
        self.prompt.submitted.connect(self._on_submitted)
        self.prompt.actionRequested.connect(self.actionRequested.emit)
        root.addWidget(self.prompt, alignment=Qt.AlignHCenter)
        root.addStretch(3)

        self._appearance = {
            "full_width": False,
            "show_welcome": True,
            "show_nobody": True,
            "emoji_mode": "Native",
            "show_status_summaries": False,
            "sensitive_blur": True,
            "show_web_search": True,
            "show_shell": True,
        }
        self._restore_latest_session()

    def draft_text(self) -> str:
        return self.prompt.draft_text()

    def set_draft_text(self, text: str) -> None:
        self.prompt.set_draft_text(text)

    @property
    def session_id(self) -> str | None:
        return self._session_id

    def reset_chat(self) -> None:
        """Start a blank persistent chat and close any live Nobody session.

        Drafts attached to existing persistent sessions remain session-owned for
        future session navigation.  Pending unsent text is deliberately cleared
        by the explicit New Chat action.  Nobody records and their drafts are
        destroyed because their privacy contract ends when that session closes.
        """

        self._save_active_draft()
        private_id = self._mode_session_ids[True]
        self.sessions.dispose_incognito_session(private_id)
        if private_id:
            self._drafts.pop(private_id, None)
        self._drafts.pop(self._pending_draft_key(True), None)
        self._drafts.pop(self._pending_draft_key(False), None)
        self._mode_session_ids = {False: None, True: None}
        self._clear_message_widgets()
        self._session_id = None
        self._session_incognito = False
        self._session_title = "New Chat"
        previous = self.nobody.blockSignals(True)
        self.nobody.setChecked(False)
        self.nobody.blockSignals(previous)
        self.prompt.set_draft_text("")
        self.prompt.set_mode("Agent")
        self.message_area.hide()
        self.hero.show()
        self.chat_label.setText("New Chat⌄")
        self._update_session_status()

    def refresh_after_durable_replacement(self) -> None:
        """Refresh only durable session state after a successful import or reset.

        Settings replacement never owns Nobody records, drafts, mode, or the
        active private view, so it must not reuse :meth:`reset_chat`. Persistent
        session IDs and drafts point into tables that were replaced; this method
        drops those stale cache entries, preserves the pending normal draft, and
        renders a current durable session only when normal mode is active.
        """

        # Save first so a pending normal draft remains available. A draft attached
        # to a concrete persistent ID is intentionally discarded: its owner was
        # deleted/replaced and cannot safely be attributed to an imported record
        # that happens to reuse the same stable ID.
        self._save_active_draft()
        private_id = self._mode_session_ids[True]
        for key in tuple(self._drafts):
            if key not in {private_id, self._pending_draft_key(True), self._pending_draft_key(False)}:
                self._drafts.pop(key, None)

        latest = self.sessions.latest_persistent_session()
        self._mode_session_ids[False] = latest.id if latest is not None else None
        if self._session_incognito:
            # Do not switch a private user into durable content merely because a
            # replacement completed in the background settings operation.
            self._render_active_session()
            return
        self._session_id = self._mode_session_ids[False]
        self._render_active_session()

    def apply_appearance(self, preferences: dict) -> None:
        self._appearance.update(preferences)
        self.prompt.set_full_width(bool(self._appearance.get("full_width", False)))
        self.prompt.set_action_visibility(
            web_search=bool(self._appearance.get("show_web_search", True)),
            shell=bool(self._appearance.get("show_shell", True)),
        )
        show_welcome = bool(self._appearance.get("show_welcome", True))
        self.hero_title.setVisible(show_welcome)
        self.hero_ready.setVisible(show_welcome)
        self.hero_hint.setVisible(show_welcome)
        self.nobody.setVisible(bool(self._appearance.get("show_nobody", True)))
        self.status_summary.setVisible(bool(self._appearance.get("show_status_summaries", True)))
        minimal = str(self._appearance.get("emoji_mode", "Native")) == "Minimal"
        self.hero_title.setText("Otter Cove" if minimal else "♠ Otter Cove")
        # Sensitive-span configuration remains in the declarative preference
        # model for its future renderer. No widget property is set here because
        # doing so would imply that protection exists before step 48 implements it.
        self._update_prompt_width()

    def _update_prompt_width(self) -> None:
        if not hasattr(self, "prompt"):
            return
        available = max(520, self.width() - 96)
        target = available if bool(self._appearance.get("full_width", False)) else min(720, available)
        if self.prompt.width() != target:
            self.prompt.setFixedWidth(target)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        # Keep the composer visually identical at normal sizes while allowing the
        # shell to remain usable at the documented 1100px minimum width.
        self._update_prompt_width()

    def _clear_message_widgets(self) -> None:
        while self.message_layout.count() > 1:
            item = self.message_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _restore_latest_session(self) -> None:
        try:
            session = self.sessions.latest_persistent_session()
            if session is None:
                return
            messages = self.sessions.messages(session.id)
        except DataStoreError as exc:
            self.storageError.emit(exc.user_message())
            return
        self._session_id = session.id
        self._session_incognito = False
        self._session_title = session.title
        self._mode_session_ids[False] = session.id
        self.nobody.setChecked(False)
        self.hero.hide()
        self.message_area.show()
        self.chat_label.setText(f"{session.title}⌄")
        for message in messages:
            mode = str(message.metadata.get("mode", "Chat"))
            self._append_message_widget(message.content, mode, role=message.role)
        self._update_session_status()

    def _pending_draft_key(self, incognito: bool) -> str:
        """Return the stable key for a mode that has no accepted session yet."""

        return "pending:nobody" if incognito else "pending:persistent"

    def _active_draft_key(self) -> str:
        """Return the current concrete-session or pending-mode draft key."""

        return self._session_id or self._pending_draft_key(self._session_incognito)

    def _save_active_draft(self) -> None:
        """Snapshot the current editor text and mode under its owning session."""

        self._drafts[self._active_draft_key()] = ComposerDraft(
            self.prompt.draft_text(), self.prompt.mode()
        )

    def _restore_active_draft(self) -> None:
        """Restore the editor state owned by the currently selected session."""

        draft = self._drafts.get(self._active_draft_key(), ComposerDraft())
        self.prompt.set_draft_text(draft.text)
        self.prompt.set_mode(draft.mode)

    def _on_nobody_toggled(self, incognito: bool) -> None:
        """Switch privacy modes without mixing messages or composer drafts.

        The outgoing view is saved under its own session identity. The selected
        mode then restores its last live session, messages, draft, and truthful
        storage status. A new session remains lazy until its first accepted send.
        """

        if bool(incognito) == self._session_incognito:
            return
        self._save_active_draft()
        self._mode_session_ids[self._session_incognito] = self._session_id
        self._session_incognito = bool(incognito)
        self._session_id = self._mode_session_ids[self._session_incognito]
        self._render_active_session()
        self._restore_active_draft()

    def _render_active_session(self) -> None:
        """Render only the selected session and refresh its privacy indicators."""

        self._clear_message_widgets()
        session = self.sessions.get_session(self._session_id)
        if session is None:
            self._session_id = None
            self._mode_session_ids[self._session_incognito] = None
            self._session_title = "New Chat"
            self.message_area.hide()
            self.hero.show()
            prefix = "Nobody · " if self._session_incognito else ""
            self.chat_label.setText(f"{prefix}New Chat⌄")
            self._update_session_status()
            return
        try:
            messages = self.sessions.messages(session.id)
        except DataStoreError as exc:
            self.storageError.emit(exc.user_message())
            messages = []
        self._session_title = session.title
        self.hero.setVisible(not messages)
        self.message_area.setVisible(bool(messages))
        prefix = "Nobody · " if self._session_incognito else ""
        self.chat_label.setText(f"{prefix}{session.title}⌄")
        for message in messages:
            mode = str(message.metadata.get("mode", "Chat"))
            self._append_message_widget(message.content, mode, role=message.role)
        self._update_session_status()

    def _update_session_status(self) -> None:
        """Describe the actual persistence policy of the selected chat view."""

        if self._session_incognito:
            text = "Nobody session · memory only · discarded by New Chat"
        else:
            text = "Local GUI session · persistent storage"
        self.status_summary.setText(text)
        self.status_summary.setAccessibleDescription(text)

    def _on_submitted(self, text: str, mode: str) -> None:
        """Persist one user submission and commit its presentation on success.

        Session creation may succeed before message storage fails.  In that case
        the retained session is reused on retry, while the composer draft and
        mode stay untouched.  The message widget and draft clear are both
        committed only after ``add_message`` returns successfully.
        """

        requested_incognito = self.nobody.isChecked()
        try:
            if self._session_id is None or self._session_incognito != requested_incognito:
                title = self._derive_title(text)
                session = self.sessions.create_session(title, incognito=requested_incognito)
                self._session_id = session.id
                self._session_incognito = requested_incognito
                self._session_title = session.title
                self._mode_session_ids[requested_incognito] = session.id
            self.sessions.add_message(self._session_id, "user", text, metadata={"mode": mode})
        except DataStoreError as exc:
            self.storageError.emit(exc.user_message())
            return

        self.hero.hide()
        self.message_area.show()
        prefix = "Nobody · " if self._session_incognito else ""
        self.chat_label.setText(f"{prefix}{self._session_title}⌄")
        self._append_message_widget(text, mode, role="user")
        self.prompt.accept_submission(text, mode)
        self._drafts.pop(self._active_draft_key(), None)
        self._update_session_status()
        self.message_area.verticalScrollBar().setValue(self.message_area.verticalScrollBar().maximum())

    def _append_message_widget(self, text: str, mode: str, *, role: str) -> None:
        who = "You" if role == "user" else role.title()
        label = QLabel(f"{mode} · {who}\n{text}")
        label.setObjectName("LocalMessage")
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        insert_at = max(0, self.message_layout.count() - 1)
        self.message_layout.insertWidget(insert_at, label)

    @staticmethod
    def _derive_title(text: str) -> str:
        compact = " ".join(text.split())
        return (compact[:45] + "…") if len(compact) > 46 else compact or "New Chat"
