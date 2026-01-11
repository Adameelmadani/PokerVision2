"""
Action panel with betting controls.
"""
from PyQt6.QtWidgets import (
    QFrame, QLabel, QPushButton, QSlider, QSpinBox,
    QVBoxLayout, QHBoxLayout, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..engine.game import Action, ActionType


class ActionPanel(QFrame):
    """Panel with betting action buttons and raise slider."""

    action_selected = pyqtSignal(Action)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("actionPanel")
        
        self._min_bet = 0
        self._max_bet = 0
        self._call_amount = 0
        self._current_bet = 0
        self._pot_size = 0
        self._big_blind = 100
        
        self._setup_ui()
        self.setEnabled(False)

    def _setup_ui(self):
        """Setup the action panel layout."""
        self.setStyleSheet("""
            QFrame#actionPanel {
                background: rgba(5, 16, 5, 0.95);
                border: 2px solid #153515;
                border-radius: 15px;
                padding: 10px;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(10, 8, 10, 8)
        
        # Info row
        info_row = QHBoxLayout()
        
        self.pot_label = QLabel("Pot: $0")
        self.pot_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.pot_label.setStyleSheet("color: #ffffff;")
        
        self.to_call_label = QLabel("To Call: $0")
        self.to_call_label.setFont(QFont("Segoe UI", 10))
        self.to_call_label.setStyleSheet("color: #00ff00;")
        
        info_row.addWidget(self.pot_label)
        info_row.addStretch()
        info_row.addWidget(self.to_call_label)
        
        # Main action buttons row
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(6)
        
        # Fold button
        self.fold_btn = QPushButton("FOLD")
        self.fold_btn.setObjectName("foldButton")
        self.fold_btn.setFixedSize(80, 38)
        self.fold_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.fold_btn.clicked.connect(self._on_fold)
        
        # Check/Call button
        self.call_btn = QPushButton("CHECK")
        self.call_btn.setObjectName("checkButton")
        self.call_btn.setFixedSize(100, 38)
        self.call_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.call_btn.clicked.connect(self._on_call)
        
        # Raise/Bet button
        self.raise_btn = QPushButton("BET")
        self.raise_btn.setObjectName("betButton")
        self.raise_btn.setFixedSize(80, 38)
        self.raise_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.raise_btn.clicked.connect(self._on_raise)
        
        # All-In button
        self.allin_btn = QPushButton("ALL IN")
        self.allin_btn.setObjectName("allInButton")
        self.allin_btn.setFixedSize(80, 38)
        self.allin_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.allin_btn.clicked.connect(self._on_allin)
        
        buttons_row.addWidget(self.fold_btn)
        buttons_row.addWidget(self.call_btn)
        buttons_row.addWidget(self.raise_btn)
        buttons_row.addWidget(self.allin_btn)
        
        # Raise slider row
        slider_row = QHBoxLayout()
        slider_row.setSpacing(10)
        
        self.raise_label = QLabel("Raise:")
        self.raise_label.setFont(QFont("Segoe UI", 10))
        self.raise_label.setStyleSheet("color: #ffffff;")
        
        self.raise_slider = QSlider(Qt.Orientation.Horizontal)
        self.raise_slider.setMinimum(0)
        self.raise_slider.setMaximum(100)
        self.raise_slider.setValue(0)
        self.raise_slider.valueChanged.connect(self._on_slider_change)
        
        self.raise_amount = QSpinBox()
        self.raise_amount.setMinimum(0)
        self.raise_amount.setMaximum(1000000)
        self.raise_amount.setSingleStep(self._big_blind)
        self.raise_amount.setFont(QFont("Segoe UI", 10))
        self.raise_amount.setMinimumWidth(90)
        self.raise_amount.setMaximumWidth(100)
        self.raise_amount.valueChanged.connect(self._on_spinbox_change)
        
        slider_row.addWidget(self.raise_label)
        slider_row.addWidget(self.raise_slider, 1)
        slider_row.addWidget(self.raise_amount)
        
        # Quick bet buttons row
        quick_row = QHBoxLayout()
        quick_row.setSpacing(8)
        
        self.btn_min = QPushButton("Min")
        self.btn_half = QPushButton("½ Pot")
        self.btn_3_4 = QPushButton("¾ Pot")
        self.btn_pot = QPushButton("Pot")
        self.btn_2x = QPushButton("2x Pot")
        
        for btn in [self.btn_min, self.btn_half, self.btn_3_4, self.btn_pot, self.btn_2x]:
            btn.setFixedHeight(28)
            btn.setFont(QFont("Segoe UI", 9))
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(10, 37, 10, 0.8);
                    border: 1px solid #153515;
                    border-radius: 6px;
                    color: #00ff00;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background: rgba(0, 255, 0, 0.2);
                    border-color: #00ff00;
                }
            """)
        
        self.btn_min.clicked.connect(lambda: self._set_raise(self._min_bet))
        self.btn_half.clicked.connect(lambda: self._set_raise(self._current_bet + self._pot_size // 2))
        self.btn_3_4.clicked.connect(lambda: self._set_raise(self._current_bet + self._pot_size * 3 // 4))
        self.btn_pot.clicked.connect(lambda: self._set_raise(self._current_bet + self._pot_size))
        self.btn_2x.clicked.connect(lambda: self._set_raise(self._current_bet + self._pot_size * 2))
        
        quick_row.addWidget(self.btn_min)
        quick_row.addWidget(self.btn_half)
        quick_row.addWidget(self.btn_3_4)
        quick_row.addWidget(self.btn_pot)
        quick_row.addWidget(self.btn_2x)
        
        # Assemble layout
        main_layout.addLayout(info_row)
        main_layout.addLayout(buttons_row)
        main_layout.addLayout(slider_row)
        main_layout.addLayout(quick_row)

    def configure(
        self,
        pot_size: int,
        call_amount: int,
        min_bet: int,
        max_bet: int,
        current_bet: int,
        big_blind: int
    ):
        """Configure the action panel with current game state."""
        self._pot_size = pot_size
        self._call_amount = call_amount
        self._min_bet = min_bet
        self._max_bet = max_bet
        self._current_bet = current_bet
        self._big_blind = big_blind
        
        # Update labels
        self.pot_label.setText(f"Pot: ${pot_size:,}")
        
        if call_amount > 0:
            self.to_call_label.setText(f"To Call: ${call_amount:,}")
            self.call_btn.setText(f"CALL ${call_amount:,}")
            self.call_btn.setObjectName("callButton")
        else:
            self.to_call_label.setText("Free to see")
            self.call_btn.setText("CHECK")
            self.call_btn.setObjectName("checkButton")
        
        # Update raise button
        if current_bet == 0:
            self.raise_btn.setText("BET")
            self.raise_btn.setObjectName("betButton")
        else:
            self.raise_btn.setText("RAISE")
            self.raise_btn.setObjectName("raiseButton")
        
        # Update slider/spinbox
        self.raise_amount.setMinimum(min_bet)
        self.raise_amount.setMaximum(max_bet)
        self.raise_amount.setSingleStep(big_blind)
        self.raise_amount.setValue(min_bet)
        
        self._update_slider_from_spinbox()
        
        # Enable/disable raise if can't afford
        can_raise = max_bet > min_bet
        self.raise_btn.setEnabled(can_raise)
        self.raise_slider.setEnabled(can_raise)
        self.raise_amount.setEnabled(can_raise)
        
        for btn in [self.btn_min, self.btn_half, self.btn_3_4, self.btn_pot, self.btn_2x]:
            btn.setEnabled(can_raise)
        
        self.setEnabled(True)

    def _set_raise(self, amount: int):
        """Set the raise amount."""
        amount = max(self._min_bet, min(self._max_bet, amount))
        self.raise_amount.setValue(amount)

    def _on_slider_change(self, value: int):
        """Handle slider change."""
        # Map 0-100 to min-max
        range_size = self._max_bet - self._min_bet
        if range_size > 0:
            amount = self._min_bet + (value * range_size // 100)
            self.raise_amount.blockSignals(True)
            self.raise_amount.setValue(amount)
            self.raise_amount.blockSignals(False)

    def _on_spinbox_change(self, value: int):
        """Handle spinbox change."""
        self._update_slider_from_spinbox()

    def _update_slider_from_spinbox(self):
        """Update slider position from spinbox value."""
        value = self.raise_amount.value()
        range_size = self._max_bet - self._min_bet
        if range_size > 0:
            slider_value = ((value - self._min_bet) * 100) // range_size
            self.raise_slider.blockSignals(True)
            self.raise_slider.setValue(slider_value)
            self.raise_slider.blockSignals(False)

    def _on_fold(self):
        """Handle fold button."""
        self.setEnabled(False)
        self.action_selected.emit(Action(ActionType.FOLD))

    def _on_call(self):
        """Handle call/check button."""
        self.setEnabled(False)
        if self._call_amount > 0:
            self.action_selected.emit(Action(ActionType.CALL, self._call_amount))
        else:
            self.action_selected.emit(Action(ActionType.CHECK))

    def _on_raise(self):
        """Handle raise/bet button."""
        self.setEnabled(False)
        amount = self.raise_amount.value()
        if self._current_bet == 0:
            self.action_selected.emit(Action(ActionType.BET, amount))
        else:
            self.action_selected.emit(Action(ActionType.RAISE, amount))

    def _on_allin(self):
        """Handle all-in button."""
        self.setEnabled(False)
        self.action_selected.emit(Action(ActionType.ALL_IN, self._max_bet))

    def hide_panel(self):
        """Hide the action panel."""
        self.setEnabled(False)

    def show_panel(self):
        """Show the action panel."""
        self.setEnabled(True)
