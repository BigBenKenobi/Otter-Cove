from __future__ import annotations

import os

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from core.demo_states import DemoScenario
from core.routes import DEFAULT_ROUTE_REGISTRY, RouteRegistry
from .shared_states import DemoStateHost, EmptyState, StateHost


class FeaturePlaceholder(QWidget):
    """Explicit unavailable state for routes whose dedicated milestone is pending.

    The ordinary build shows a module-specific shared empty/unavailable state. A
    deterministic state fixture can be enabled for acceptance work with either the
    ``demo_scenario`` constructor argument or OTTER_COVE_DEMO_SCENARIO.
    """

    def __init__(
        self,
        route: str,
        parent=None,
        *,
        registry: RouteRegistry = DEFAULT_ROUTE_REGISTRY,
        feedback=None,
        demo_scenario: str | DemoScenario | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("FeaturePlaceholder")
        spec = registry.get(route)
        if spec is None:
            title = route.replace("_", " ").title() or "Unknown route"
            plan = "This route is not registered in this Otter Cove build."
        else:
            title = spec.title
            plan = spec.description or "This feature has no implementation notes yet."
        self.feature_title = title

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 20, 22, 22)
        root.setSpacing(12)

        title_label = QLabel(title)
        title_label.setObjectName("FeatureTitle")
        root.addWidget(title_label)

        chip_row = QHBoxLayout()
        chip = QLabel("Unavailable — UI milestone queued")
        chip.setObjectName("StatusChip")
        chip.setAccessibleName("Feature unavailable")
        chip_row.addWidget(chip)
        chip_row.addStretch()
        root.addLayout(chip_row)

        text = QLabel(plan)
        text.setObjectName("FeatureMuted")
        text.setWordWrap(True)
        text.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        root.addWidget(text)

        rule = QFrame()
        rule.setFrameShape(QFrame.HLine)
        rule.setObjectName("SectionRule")
        root.addWidget(rule)

        self.state_host = StateHost()
        root.addWidget(self.state_host)
        self.state_host.set_state(
            EmptyState(
                f"{title} is not wired yet",
                "The route and shared Otter Cove window shell are working. The dedicated feature milestone has not been implemented, and opening this window does not disturb the current chat session or composer draft.",
            ),
            announce=False,
        )

        # Optional deterministic fixture UI for acceptance/development builds.
        self.demo_host: DemoStateHost | None = None
        scenario_value = demo_scenario or os.environ.get("OTTER_COVE_DEMO_SCENARIO", "").strip()
        show_controls = os.environ.get("OTTER_COVE_SHOW_STATE_FIXTURES", "0") == "1"
        if scenario_value or show_controls:
            self.demo_host = DemoStateHost(title, feedback=feedback)
            root.addWidget(self.demo_host)
            self.state_host.hide()

            if show_controls:
                fixture_row = QHBoxLayout()
                fixture_label = QLabel("State fixture")
                fixture_label.setObjectName("FeatureMuted")
                fixture_row.addWidget(fixture_label)
                self.fixture_combo = QComboBox()
                self.fixture_combo.setAccessibleName("Shared state fixture")
                for scenario in DemoScenario:
                    self.fixture_combo.addItem(scenario.value.title(), scenario.value)
                fixture_row.addWidget(self.fixture_combo)
                run_button = QPushButton("Run")
                run_button.setObjectName("OutlineButton")
                run_button.setCursor(Qt.PointingHandCursor)
                run_button.clicked.connect(lambda: self.demo_host.run(self.fixture_combo.currentData()))
                fixture_row.addWidget(run_button)
                fixture_row.addStretch()
                root.addLayout(fixture_row)

            if scenario_value:
                try:
                    parsed = DemoScenario.parse(scenario_value)
                except ValueError:
                    parsed = DemoScenario.FAILURE
                QTimer.singleShot(0, lambda s=parsed: self.demo_host.run(s))

        root.addStretch()
