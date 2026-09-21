from __future__ import annotations

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


class PromptEditor(QPlainTextEdit):
    submitRequested = Signal()

    def keyPressEvent(self, event) -> None:
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and event.modifiers() & Qt.ControlModifier:
            self.submitRequested.emit()
            event.accept()
            return
        super().keyPressEvent(event)


class PromptBox(QFrame):
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
        search.setToolTip("Web search")
        search.setAccessibleName("Web search")
        search.clicked.connect(lambda: self.actionRequested.emit("search"))
        search_icon = LineIcon("search", 22, search, follow_parent=True)
        search_icon.move(7, 7)

        term = QPushButton("")
        self.shell_button = term
        term.setObjectName("PromptIcon")
        term.setFixedSize(36, 36)
        term.setCursor(Qt.PointingHandCursor)
        term.setToolTip("Shell access")
        term.setAccessibleName("Shell access")
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
        return self.editor.toPlainText()

    def set_draft_text(self, text: str) -> None:
        self.editor.setPlainText(text)

    def mode(self) -> str:
        return "Agent" if self.agent_button.isChecked() else "Chat"

    def submit(self) -> None:
        text = self.editor.toPlainText().strip()
        if not text:
            return
        self.editor.clear()
        self.submitted.emit(text, self.mode())


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
        self.hero_title = QLabel("♠ Stark Studio")
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
        self.nobody.setFixedWidth(82)
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
        self._clear_message_widgets()
        self._session_id = None
        self._session_incognito = False
        self._session_title = "New Chat"
        self.nobody.setChecked(False)
        self.message_area.hide()
        self.hero.show()
        self.chat_label.setText("New Chat⌄")

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
        self.hero_title.setText("Stark Studio" if minimal else "♠ Stark Studio")
        # Sensitive-span handling is completed by step 48. The preference is
        # retained here so existing/future message widgets can react live without
        # changing the underlying session content.
        self.setProperty("sensitiveBlurEnabled", bool(self._appearance.get("sensitive_blur", True)))
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
        self.nobody.setChecked(False)
        self.hero.hide()
        self.message_area.show()
        self.chat_label.setText(f"{session.title}⌄")
        for message in messages:
            mode = str(message.metadata.get("mode", "Chat"))
            self._append_message_widget(message.content, mode, role=message.role)

    def _on_submitted(self, text: str, mode: str) -> None:
        requested_incognito = self.nobody.isChecked()
        try:
            if self._session_id is None or self._session_incognito != requested_incognito:
                title = self._derive_title(text)
                session = self.sessions.create_session(title, incognito=requested_incognito)
                self._session_id = session.id
                self._session_incognito = requested_incognito
                self._session_title = session.title
            self.sessions.add_message(self._session_id, "user", text, metadata={"mode": mode})
        except DataStoreError as exc:
            self.storageError.emit(exc.user_message())
            return

        self.hero.hide()
        self.message_area.show()
        prefix = "Nobody · " if self._session_incognito else ""
        self.chat_label.setText(f"{prefix}{self._session_title}⌄")
        self._append_message_widget(text, mode, role="user")
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
