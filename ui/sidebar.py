from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Property, QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QToolButton, QVBoxLayout

from core.routes import DEFAULT_ROUTE_REGISTRY
from ui.iconography import LineIcon


@dataclass(frozen=True)
class NavItem:
    route: str
    symbol: str
    label: str


NAV_ITEMS = tuple(
    NavItem(route.key, route.icon, route.title)
    for route in DEFAULT_ROUTE_REGISTRY.sidebar_routes()
)


class SidebarNavButton(QPushButton):
    """Sidebar row with a separately-sized glyph and label.

    Keeping the glyph as its own child avoids tying icon scale to the application
    text size, and gives the collapsed/expanded layouts the same visual weight.
    """

    def __init__(self, item: NavItem, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("NavButton")
        self.setText("")
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True)
        self.setAutoExclusive(False)
        self.setMinimumHeight(32)
        self.setProperty("route", item.route)
        self.setProperty("symbol", item.symbol)
        self.setProperty("label", item.label)
        self.setAccessibleName(item.label)
        self._command_tooltip = ""

        self.content_layout = QHBoxLayout(self)
        self.content_layout.setContentsMargins(6, 0, 6, 0)
        self.content_layout.setSpacing(8)

        self.icon_label = LineIcon(item.route, 22, self)
        self.icon_label.setObjectName("NavGlyph")
        self.content_layout.addWidget(self.icon_label, 0, Qt.AlignCenter)

        self.text_label = QLabel(item.label, self)
        self.text_label.setObjectName("NavText")
        self.text_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.content_layout.addWidget(self.text_label)
        self.content_layout.addStretch(1)

    def set_collapsed(self, collapsed: bool) -> None:
        self.text_label.setVisible(not collapsed)
        # Vector icons keep one optical size across Fedora fonts. Collapsed mode
        # gets a small bump because there is no label to provide visual weight.
        icon_size = 24 if collapsed else 22
        self.icon_label.setFixedSize(icon_size, icon_size)
        # Center the glyph in the available icon-only rail.
        self.content_layout.setContentsMargins(10 if collapsed else 6, 0, 10 if collapsed else 6, 0)
        label = str(self.property("label"))
        if self._command_tooltip:
            self.setToolTip(self._command_tooltip)
        else:
            self.setToolTip(label if collapsed else "")

    def set_command_tooltip(self, tooltip: str) -> None:
        self._command_tooltip = str(tooltip)
        self.set_collapsed(self.text_label.isHidden())


class Sidebar(QFrame):
    navigationRequested = Signal(str)
    collapsedChanged = Signal(bool)

    EXPANDED_WIDTH = 215
    COLLAPSED_WIDTH = 58

    def __init__(self, collapsed: bool = False, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self._collapsed = collapsed
        self._sidebar_width = self.COLLAPSED_WIDTH if collapsed else self.EXPANDED_WIDTH
        self.setFixedWidth(self._sidebar_width)

        root = QVBoxLayout(self)
        self.root_layout = root
        root.setContentsMargins(12, 12, 10, 12)
        root.setSpacing(4)

        head = QHBoxLayout()
        self.menu_button = QToolButton()
        self.menu_button.setObjectName("MenuButton")
        self.menu_button.setText("☰")
        self.menu_button.setCursor(Qt.PointingHandCursor)
        self.menu_button.clicked.connect(self.toggle_collapsed)
        self.brand = QLabel("Stark Studio")
        self.brand.setObjectName("Brand")
        head.addWidget(self.menu_button)
        head.addStretch()
        head.addWidget(self.brand)
        root.addLayout(head)
        root.addSpacing(12)

        self.buttons: dict[str, SidebarNavButton] = {}
        for item in NAV_ITEMS:
            button = SidebarNavButton(item, self)
            button.clicked.connect(lambda _checked=False, route=item.route: self.navigationRequested.emit(route))
            root.addWidget(button)
            self.buttons[item.route] = button

        root.addStretch()

        self.account_row = QFrame()
        account = QHBoxLayout(self.account_row)
        account.setContentsMargins(0, 0, 0, 0)
        account.setSpacing(4)
        self.avatar = QToolButton()
        self.avatar.setText("A")
        self.avatar.setObjectName("Avatar")
        self.avatar.setCursor(Qt.PointingHandCursor)
        self.avatar.setToolTip("Profile")
        self.avatar.setAccessibleName("Profile")
        self.avatar.clicked.connect(lambda: self.navigationRequested.emit("account"))
        self.account_name = QLabel("Admin")
        self.settings_button = QToolButton()
        self.settings_button.setObjectName("SidebarSettingsButton")
        self.settings_button.setText("⚙")
        self.settings_button.setCursor(Qt.PointingHandCursor)
        self.settings_button.setToolTip("Settings")
        self.settings_button.setAccessibleName("Settings")
        self.settings_button.setFixedSize(24, 24)
        settings_font = self.settings_button.font()
        settings_font.setPixelSize(16)
        self.settings_button.setFont(settings_font)
        self.settings_button.clicked.connect(lambda: self.navigationRequested.emit("settings"))
        account.addWidget(self.avatar)
        account.addWidget(self.account_name)
        account.addStretch()
        account.addWidget(self.settings_button)
        root.addWidget(self.account_row)

        self._animation = QPropertyAnimation(self, b"sidebarWidth", self)
        self._animation.setDuration(180)
        self._animation.setEasingCurve(QEasingCurve.InOutCubic)
        self._refresh_labels()

    def is_collapsed(self) -> bool:
        return self._collapsed

    def set_active(self, route: str | None) -> None:
        for key, button in self.buttons.items():
            button.setChecked(key == route)

    def set_route_visible(self, route: str, visible: bool) -> None:
        button = self.buttons.get(route)
        if button is not None:
            button.setVisible(bool(visible))

    def route_visible(self, route: str) -> bool:
        button = self.buttons.get(route)
        return bool(button is not None and button.isVisible())

    def toggle_collapsed(self) -> None:
        self.set_collapsed(not self._collapsed)

    def set_collapsed(self, collapsed: bool, animate: bool = True) -> None:
        collapsed = bool(collapsed)
        if collapsed == self._collapsed and animate:
            return
        self._collapsed = collapsed
        self._refresh_labels()
        target = self.COLLAPSED_WIDTH if collapsed else self.EXPANDED_WIDTH
        if animate:
            self._animation.stop()
            self._animation.setStartValue(self.width())
            self._animation.setEndValue(target)
            self._animation.start()
        else:
            self._set_sidebar_width(target)
        self.collapsedChanged.emit(collapsed)

    def _refresh_labels(self) -> None:
        self.brand.setVisible(not self._collapsed)
        self.account_name.setVisible(not self._collapsed)
        # Keep both Profile and Settings reachable when the sidebar is collapsed.
        self.settings_button.setVisible(True)
        if self._collapsed:
            self.root_layout.setContentsMargins(7, 12, 7, 12)
        else:
            self.root_layout.setContentsMargins(12, 12, 10, 12)
        for button in self.buttons.values():
            button.set_collapsed(self._collapsed)

    def _get_sidebar_width(self) -> int:
        return self._sidebar_width

    def _set_sidebar_width(self, width: int) -> None:
        self._sidebar_width = int(width)
        self.setFixedWidth(self._sidebar_width)

    sidebarWidth = Property(int, _get_sidebar_width, _set_sidebar_width)
