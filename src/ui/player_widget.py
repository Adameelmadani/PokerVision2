"""
Player widget showing avatar, cards, chips, and status.
"""
from PyQt6.QtWidgets import (
    QFrame, QLabel, QVBoxLayout, QHBoxLayout, QWidget,
    QGraphicsOpacityEffect, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QTimer, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from .card_widget import CardWidget
from ..engine.game import PlayerState, Action, ActionType


class PlayerWidget(QFrame):
    """Widget displaying a player's state at the table."""

    def __init__(self, seat: int, parent=None):
        super().__init__(parent)
        self.seat = seat
        self._is_active = False
        self._is_folded = False
        self._is_winner = False
        
        self.setObjectName("playerFrame")
        self.setFixedSize(145, 130)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the player widget layout."""
        self.setStyleSheet("""
            QFrame#playerFrame {
                background: rgba(10, 37, 10, 0.9);
                border: 3px solid #153515;
                border-radius: 12px;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(2)
        
        # Top row: Position badges
        top_row = QHBoxLayout()
        
        self.dealer_label = QLabel("D")
        self.dealer_label.setObjectName("dealerButton")
        self.dealer_label.setStyleSheet("""
            background: #ffffff;
            color: #1a1a2e;
            font-weight: bold;
            font-size: 9px;
            border-radius: 8px;
            padding: 1px 4px;
        """)
        self.dealer_label.setFixedSize(16, 16)
        self.dealer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dealer_label.hide()
        
        self.blind_label = QLabel("")
        self.blind_label.setStyleSheet("""
            background: #ffffff;
            color: #000000;
            font-weight: bold;
            font-size: 10px;
            border-radius: 8px;
            padding: 2px 6px;
        """)
        self.blind_label.hide()
        
        top_row.addWidget(self.dealer_label)
        top_row.addWidget(self.blind_label)
        top_row.addStretch()
        
        # Name and avatar row
        name_row = QHBoxLayout()
        
        # Player type indicator (text instead of emoji)
        self.avatar_label = QLabel("")
        self.avatar_label.setFont(QFont("Georgia", 11, QFont.Weight.Bold))
        self.avatar_label.setFixedWidth(50)
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        name_info = QVBoxLayout()
        
        self.name_label = QLabel("Empty")
        self.name_label.setObjectName("playerName")
        self.name_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.name_label.setStyleSheet("color: #ffffff;")
        
        self.type_label = QLabel("")
        self.type_label.setStyleSheet("color: #888888; font-size: 10px;")
        
        name_info.addWidget(self.name_label)
        name_info.addWidget(self.type_label)
        
        name_row.addWidget(self.avatar_label)
        name_row.addLayout(name_info, 1)
        
        # Chips row
        chips_row = QHBoxLayout()
        
        self.chips_label = QLabel("$0")
        self.chips_label.setObjectName("playerChips")
        self.chips_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.chips_label.setStyleSheet("color: #00ff00;")
        
        chips_row.addWidget(self.chips_label)
        chips_row.addStretch()
        
        # Cards row
        cards_row = QHBoxLayout()
        cards_row.setSpacing(5)
        
        self.card1 = CardWidget()
        self.card2 = CardWidget()
        self.card1.setFixedSize(38, 52)
        self.card2.setFixedSize(38, 52)
        
        cards_row.addStretch()
        cards_row.addWidget(self.card1)
        cards_row.addWidget(self.card2)
        cards_row.addStretch()
        
        # Action/bet row
        action_row = QHBoxLayout()
        
        self.action_label = QLabel("")
        self.action_label.setStyleSheet("""
            background: rgba(0, 128, 0, 0.3);
            color: #ffffff;
            font-size: 11px;
            font-weight: bold;
            border-radius: 8px;
            padding: 3px 8px;
        """)
        self.action_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.action_label.hide()
        
        self.bet_label = QLabel("")
        self.bet_label.setObjectName("playerBet")
        self.bet_label.setStyleSheet("""
            color: #ffffff;
            font-size: 12px;
            font-weight: bold;
        """)
        
        action_row.addWidget(self.action_label)
        action_row.addStretch()
        action_row.addWidget(self.bet_label)
        
        # Assemble layout
        main_layout.addLayout(top_row)
        main_layout.addLayout(name_row)
        main_layout.addLayout(chips_row)
        main_layout.addLayout(cards_row)
        main_layout.addLayout(action_row)
        
        # Setup glow effect for active player
        self.glow_effect = QGraphicsDropShadowEffect()
        self.glow_effect.setBlurRadius(20)
        self.glow_effect.setColor(QColor(0, 255, 0, 150))
        self.glow_effect.setOffset(0, 0)
        self.glow_effect.setEnabled(False)
        self.setGraphicsEffect(self.glow_effect)

    def update_state(self, player: PlayerState, show_cards: bool = False):
        """Update display from player state."""
        self.name_label.setText(player.name)
        self.chips_label.setText(f"${player.chips:,}")
        
        # Dealer button
        if player.is_dealer:
            self.dealer_label.show()
        else:
            self.dealer_label.hide()
        
        # Blinds
        if player.is_small_blind:
            self.blind_label.setText("SB")
            self.blind_label.setStyleSheet("""
                background: #008000;
                color: white;
                font-weight: bold;
                font-size: 10px;
                border-radius: 8px;
                padding: 2px 6px;
            """)
            self.blind_label.show()
        elif player.is_big_blind:
            self.blind_label.setText("BB")
            self.blind_label.setStyleSheet("""
                background: #ff0000;
                color: white;
                font-weight: bold;
                font-size: 10px;
                border-radius: 8px;
                padding: 2px 6px;
            """)
            self.blind_label.show()
        else:
            self.blind_label.hide()
        
        # Cards
        if show_cards and player.hole_cards:
            if len(player.hole_cards) >= 1:
                self.card1.set_card(player.hole_cards[0], animate=False)
            if len(player.hole_cards) >= 2:
                self.card2.set_card(player.hole_cards[1], animate=False)
        else:
            if player.hole_cards and not player.is_folded:
                self.card1._show_back()
                self.card2._show_back()
                self.card1.show()
                self.card2.show()
            else:
                self.card1.hide()
                self.card2.hide()
        
        # Current bet
        if player.current_bet > 0:
            self.bet_label.setText(f"${player.current_bet:,}")
            self.bet_label.show()
        else:
            self.bet_label.hide()
        
        # Last action
        if player.last_action:
            self.show_action(player.last_action)
        
        # Folded state
        self.set_folded(player.is_folded)
        
        # All-in indicator
        if player.is_all_in:
            self.action_label.setText("ALL IN")
            self.action_label.setStyleSheet("""
                background: rgba(255, 0, 0, 0.8);
                color: white;
                font-size: 11px;
                font-weight: bold;
                border-radius: 8px;
                padding: 3px 8px;
            """)
            self.action_label.show()

    def set_empty(self):
        """Show empty seat."""
        self.name_label.setText("Empty")
        self.type_label.setText("")
        self.chips_label.setText("")
        self.dealer_label.hide()
        self.blind_label.hide()
        self.card1.hide()
        self.card2.hide()
        self.action_label.hide()
        self.bet_label.hide()
        self.set_active(False)

    def set_active(self, active: bool):
        """Set whether this player is currently active (their turn)."""
        self._is_active = active
        self.glow_effect.setEnabled(active)
        
        if active:
            self.setStyleSheet("""
                QFrame#playerFrame {
                    background: rgba(0, 255, 0, 0.15);
                    border: 3px solid #00ff00;
                    border-radius: 12px;
                }
            """)
        elif self._is_folded:
            self.setStyleSheet("""
                QFrame#playerFrame {
                    background: rgba(50, 50, 50, 0.7);
                    border: 3px solid #444444;
                    border-radius: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame#playerFrame {
                    background: rgba(10, 37, 10, 0.9);
                    border: 3px solid #153515;
                    border-radius: 12px;
                }
            """)

    def set_folded(self, folded: bool):
        """Set folded visual state."""
        self._is_folded = folded
        
        if folded:
            opacity_effect = QGraphicsOpacityEffect()
            opacity_effect.setOpacity(0.5)
            self.setGraphicsEffect(opacity_effect)
            self.card1.hide()
            self.card2.hide()
        else:
            self.setGraphicsEffect(self.glow_effect)

    def set_winner(self, is_winner: bool):
        """Highlight as winner."""
        self._is_winner = is_winner
        
        if is_winner:
            self.glow_effect.setColor(QColor(255, 255, 255, 200))
            self.glow_effect.setBlurRadius(30)
            self.glow_effect.setEnabled(True)
            
            self.setStyleSheet("""
                QFrame#playerFrame {
                    background: rgba(255, 255, 255, 0.2);
                    border: 3px solid #ffffff;
                    border-radius: 12px;
                }
            """)
        else:
            self.glow_effect.setColor(QColor(0, 255, 0, 150))
            self.glow_effect.setBlurRadius(20)
            self.glow_effect.setEnabled(False)

    def show_action(self, action: Action):
        """Display player's action briefly."""
        action_colors = {
            ActionType.FOLD: ("#cc0000", "FOLD"),
            ActionType.CHECK: ("#008000", "CHECK"),
            ActionType.CALL: ("#008000", f"CALL ${action.amount:,}"),
            ActionType.BET: ("#cc0000", f"BET ${action.amount:,}"),
            ActionType.RAISE: ("#cc0000", f"RAISE ${action.amount:,}"),
            ActionType.ALL_IN: ("#ff0000", f"ALL IN ${action.amount:,}"),
        }
        
        color, text = action_colors.get(action.action_type, ("#888", ""))
        
        self.action_label.setText(text)
        self.action_label.setStyleSheet(f"""
            background: rgba({self._hex_to_rgb(color)}, 0.8);
            color: white;
            font-size: 11px;
            font-weight: bold;
            border-radius: 8px;
            padding: 3px 8px;
        """)
        self.action_label.show()
        
        # Hide after delay (unless all-in)
        if action.action_type != ActionType.ALL_IN:
            QTimer.singleShot(2000, lambda: self.action_label.hide())

    def _hex_to_rgb(self, hex_color: str) -> str:
        """Convert hex color to RGB string."""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"{r}, {g}, {b}"

    def set_player_type(self, player_type: str):
        """Set the player type label (Human/AI model name)."""
        if player_type == "human":
            self.type_label.setText("Human")
            self.type_label.setStyleSheet("color: #00ff00; font-size: 10px;")
            self.avatar_label.setText("H")
            self.avatar_label.setStyleSheet("color: #00ff00;")
        else:
            self.type_label.setText(player_type[:8])  # Truncate long model names
            self.type_label.setStyleSheet("color: #ffffff; font-size: 10px;")
            self.avatar_label.setText("AI")
            self.avatar_label.setStyleSheet("color: #ffffff;")
