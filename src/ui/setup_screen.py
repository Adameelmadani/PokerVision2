"""
Setup screen for configuring players and game settings.
"""
import os
from pathlib import Path
from typing import List, Optional, Tuple

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QFrame, QGridLayout, QGroupBox,
    QAbstractSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QColor, QBrush, QPen, QLinearGradient

from .styles import SETUP_STYLESHEET


class SeatWidget(QFrame):
    """Widget for configuring a single seat."""

    def __init__(self, seat_num: int, models: List[str], parent=None):
        super().__init__(parent)
        self.seat_num = seat_num
        self.models = models
        self.setObjectName("seatFrame")
        self._setup_ui()

    def _setup_ui(self):
        """Setup the seat configuration UI."""
        self.setStyleSheet("""
            QFrame#seatFrame {
                background: rgba(10, 37, 10, 0.8);
                border: 2px solid #153515;
                border-radius: 15px;
                padding: 10px;
            }
            QFrame#seatFrame:hover {
                border-color: #00ff00;
                background: rgba(10, 37, 10, 0.95);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Seat number
        seat_label = QLabel(f"Seat {self.seat_num + 1}")
        seat_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        seat_label.setStyleSheet("color: #00ff00;")
        seat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Player type dropdown
        self.type_combo = QComboBox()
        self.type_combo.addItem("Empty", "empty")
        self.type_combo.addItem("Human Player", "human")
        
        # Add AI models
        for model_path in self.models:
            model_name = Path(model_path).stem
            self.type_combo.addItem(f"{model_name}", model_path)
        
        self.type_combo.setFixedWidth(130)
        self.type_combo.setStyleSheet("""
            QComboBox {
                padding: 3px 3px 3px 10px;
                margin-top: 2px;
            }
        """)
        self.type_combo.currentIndexChanged.connect(self._on_type_change)
        
        # Name input (for human players)
        self.name_label = QLabel("Name:")
        self.name_label.setStyleSheet("color: #cccccc;")
        
        from PyQt6.QtWidgets import QLineEdit
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter name...")
        self.name_input.setText(f"Player {self.seat_num + 1}")
        self.name_input.setMaxLength(15)
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 3px 3px 3px 10px;
                margin-top: 2px;
            }
        """)
        
        # Status indicator (text based, no emoji)
        self.avatar_label = QLabel("--")
        self.avatar_label.setFont(QFont("Georgia", 14, QFont.Weight.Bold))
        self.avatar_label.setStyleSheet("color: #888888;")
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(seat_label)
        layout.addWidget(self.avatar_label)
        layout.addWidget(self.type_combo, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        
        self._update_visibility()

    def _on_type_change(self, index: int):
        """Handle player type change."""
        self._update_visibility()

    def _update_visibility(self):
        """Update visibility of components based on selected type."""
        data = self.type_combo.currentData()
        
        if data == "empty":
            self.avatar_label.setText("--")
            self.avatar_label.setStyleSheet("color: #555555;")
            self.name_label.hide()
            self.name_input.hide()
        elif data == "human":
            self.avatar_label.setText("HUMAN")
            self.avatar_label.setStyleSheet("color: #00ff00; font-size: 11px;")
            self.name_label.show()
            self.name_input.show()
            self.name_input.setEnabled(True)
        else:
            # AI model
            self.avatar_label.setText("AI")
            self.avatar_label.setStyleSheet("color: #ffffff; font-size: 12px;")
            model_name = Path(data).stem
            self.name_input.setText(model_name)
            self.name_label.show()
            self.name_input.show()
            self.name_input.setEnabled(True)

    def get_config(self) -> Tuple[str, Optional[str]]:
        """
        Get the configuration for this seat.
        
        Returns:
            Tuple of (player_type, model_path or None)
            player_type: "empty", "human", or "ai"
        """
        data = self.type_combo.currentData()
        name = self.name_input.text().strip() or f"Player {self.seat_num + 1}"
        
        if data == "empty":
            return ("empty", None, None)
        elif data == "human":
            return ("human", name, None)
        else:
            return ("ai", name, data)


class SetupScreen(QWidget):
    """Screen for setting up the poker game."""

    start_game = pyqtSignal(list, int, int, int)  # players, chips, sb, bb

    def __init__(self, parent=None):
        super().__init__(parent)
        self.models = self._scan_models()
        self._setup_ui()

    def _scan_models(self) -> List[str]:
        """Scan models directory for .pth files."""
        models_dir = Path("models")
        if not models_dir.exists():
            models_dir.mkdir(exist_ok=True)
            return []
        
        return [str(f) for f in models_dir.glob("*.pth")]

    def _setup_ui(self):
        """Setup the setup screen UI."""
        self.setStyleSheet(SETUP_STYLESHEET)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(8)
        
        # Title with poker-style font
        title = QLabel("TEXAS HOLD'EM")
        title.setObjectName("titleLabel")
        title.setFont(QFont("Georgia", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff; letter-spacing: 3px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        

        
        # Seats configuration - arranged in oval
        seats_container = QWidget()
        seats_layout = QGridLayout(seats_container)
        seats_layout.setSpacing(10)
        
        # Create 6 seat widgets arranged like a poker table
        # Top row: seats 0, 1
        # Middle row: seats 5, (table center), 2
        # Bottom row: seats 4, 3
        
        self.seat_widgets = []
        for i in range(6):
            seat = SeatWidget(i, self.models)
            seat.setFixedSize(205, 175)
            self.seat_widgets.append(seat)
        
        # Position seats in grid (2-row layout for compactness)
        # Col 0: Left (S5)
        # Col 1: Top-Left (S0) / Bot-Left (S4)
        # Col 2: Spacer
        # Col 3: Top-Right (S1) / Bot-Right (S3)
        # Col 4: Right (S2)
        
        seats_layout.addWidget(self.seat_widgets[5], 0, 0, 2, 1)  # Left (spans 2 rows)
        seats_layout.addWidget(self.seat_widgets[0], 0, 1)        # Top-Left
        seats_layout.addWidget(self.seat_widgets[4], 1, 1)        # Bot-Left
        
        seats_layout.addWidget(self.seat_widgets[1], 0, 3)        # Top-Right
        seats_layout.addWidget(self.seat_widgets[3], 1, 3)        # Bot-Right
        seats_layout.addWidget(self.seat_widgets[2], 0, 4, 2, 1)  # Right (spans 2 rows)
        
        # Center spacer
        center_spacer = QWidget()
        center_spacer.setFixedSize(20, 20)
        seats_layout.addWidget(center_spacer, 0, 2, 2, 1)         # Spacer (spans 2 rows)
        
        # Game settings
        settings_group = QGroupBox("Game Settings")
        settings_group.setFont(QFont("Segoe UI", 14))
        settings_layout = QHBoxLayout(settings_group)
        settings_layout.setSpacing(20)
        
        # Starting chips
        chips_layout = QVBoxLayout()
        chips_label = QLabel("Starting Chips")
        chips_label.setStyleSheet("color: #ffffff;")
        self.chips_spin = QSpinBox()
        self.chips_spin.setRange(100, 1000000)
        self.chips_spin.setValue(10000)
        self.chips_spin.setSingleStep(1000)
        self.chips_spin.setPrefix("$")
        chips_layout.addWidget(chips_label)
        chips_layout.addWidget(self.chips_spin)
        
        # Small blind
        sb_layout = QVBoxLayout()
        sb_label = QLabel("Small Blind")
        sb_label.setStyleSheet("color: #ffffff;")
        self.sb_spin = QSpinBox()
        self.sb_spin.setRange(1, 10000)
        self.sb_spin.setValue(50)
        self.sb_spin.setSingleStep(10)
        self.sb_spin.setPrefix("$")
        sb_layout.addWidget(sb_label)
        sb_layout.addWidget(self.sb_spin)
        
        # Big blind
        bb_layout = QVBoxLayout()
        bb_label = QLabel("Big Blind")
        bb_label.setStyleSheet("color: #ffffff;")
        self.bb_spin = QSpinBox()
        self.bb_spin.setRange(2, 20000)
        self.bb_spin.setValue(100)
        self.bb_spin.setSingleStep(20)
        self.bb_spin.setPrefix("$")
        bb_layout.addWidget(bb_label)
        bb_layout.addWidget(self.bb_spin)
        
        # Link small and big blind
        self.sb_spin.valueChanged.connect(
            lambda v: self.bb_spin.setValue(max(self.bb_spin.value(), v * 2))
        )
        
        settings_layout.addLayout(chips_layout)
        settings_layout.addLayout(sb_layout)
        settings_layout.addLayout(bb_layout)
        settings_layout.addStretch()
        
        # Start button
        self.start_btn = QPushButton("START GAME")
        self.start_btn.setObjectName("startButton")
        self.start_btn.setFont(QFont("Georgia", 14, QFont.Weight.Bold))
        self.start_btn.setFixedSize(180, 45)
        self.start_btn.clicked.connect(self._on_start)
        
        # Error label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #ff0000; font-size: 14px;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.hide()
        
        # Assemble layout
        main_layout.addWidget(title)

        main_layout.addWidget(seats_container, 1)
        
        # Error label (moved above controls)
        main_layout.addWidget(self.error_label)
        
        # Bottom controls (Settings + Start Button)
        bottom_controls = QHBoxLayout()
        bottom_controls.setSpacing(20)
        
        # Settings take available space
        bottom_controls.addWidget(settings_group, 1)
        
        # Start button aligned to center vertical of the row
        bottom_controls.addWidget(self.start_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        
        main_layout.addLayout(bottom_controls)

    def _on_start(self):
        """Handle start game button."""
        # Collect player configs
        players = []
        for seat in self.seat_widgets:
            config = seat.get_config()
            if config[0] != "empty":
                players.append({
                    "seat": seat.seat_num,
                    "type": config[0],
                    "name": config[1],
                    "model_path": config[2]
                })
        
        # Validate
        if len(players) < 2:
            self.error_label.setText("Need at least 2 players to start!")
            self.error_label.show()
            return
        
        self.error_label.hide()
        
        # Emit start signal
        self.start_game.emit(
            players,
            self.chips_spin.value(),
            self.sb_spin.value(),
            self.bb_spin.value()
        )

    def refresh_models(self):
        """Refresh the list of available models."""
        self.models = self._scan_models()
        for seat in self.seat_widgets:
            current = seat.type_combo.currentData()
            seat.type_combo.clear()
            seat.type_combo.addItem("Empty", "empty")
            seat.type_combo.addItem("Human Player", "human")
            for model_path in self.models:
                model_name = Path(model_path).stem
                seat.type_combo.addItem(f"{model_name}", model_path)
            
            # Restore selection if possible
            for i in range(seat.type_combo.count()):
                if seat.type_combo.itemData(i) == current:
                    seat.type_combo.setCurrentIndex(i)
                    break
