"""
Main game screen - the poker table view.
"""
import asyncio
import math
from typing import List, Dict, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPainter, QColor, QBrush, QPen, QLinearGradient, QRadialGradient

from .styles import GAME_STYLESHEET
from .player_widget import PlayerWidget
from .card_widget import CardWidget, MiniCardWidget
from .action_panel import ActionPanel
from .sound_manager import play_sound
from ..engine.game import PokerGame, GameState, GamePhase, Action, ActionType
from ..engine.deck import Card
from ..players.human_player import HumanPlayer
from ..players.ai_player import AIPlayer


class TableWidget(QWidget):
    """Custom widget that draws the poker table."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(700, 380)

    def paintEvent(self, event):
        """Draw the poker table."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Table dimensions
        table_margin = 40
        table_width = w - 2 * table_margin
        table_height = 450
        
        # Outer border (Dark Green/Black)
        border_gradient = QLinearGradient(0, 0, 0, h)
        border_gradient.setColorAt(0, QColor("#051005"))
        border_gradient.setColorAt(0.5, QColor("#0a250a"))
        border_gradient.setColorAt(1, QColor("#020502"))
        
        painter.setBrush(QBrush(border_gradient))
        painter.setPen(QPen(QColor("#00ff00"), 2))
        painter.drawRoundedRect(
            table_margin - 15, table_margin - 15,
            table_width + 30, table_height + 30,
            table_height / 2 + 15, table_height / 2 + 15
        )
        
        # Felt (green) with gradient
        felt_gradient = QRadialGradient(w / 2, h / 2, max(table_width, table_height) / 2)
        felt_gradient.setColorAt(0, QColor("#0d5c2e"))
        felt_gradient.setColorAt(0.7, QColor("#0a4520"))
        felt_gradient.setColorAt(1, QColor("#052510"))
        
        painter.setBrush(QBrush(felt_gradient))
        painter.setPen(QPen(QColor("#00ff00"), 2))
        painter.drawRoundedRect(
            table_margin, table_margin,
            table_width, table_height,
            table_height / 2, table_height / 2
        )
        
        # Inner decorative line
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor("#00ff00"), 1, Qt.PenStyle.DotLine))
        inner_margin = 25
        painter.drawRoundedRect(
            table_margin + inner_margin, table_margin + inner_margin,
            table_width - 2 * inner_margin, table_height - 2 * inner_margin,
            (table_height - 2 * inner_margin) / 2, (table_height - 2 * inner_margin) / 2
        )


class GameScreen(QWidget):
    """Main poker game screen."""

    hand_complete = pyqtSignal()
    return_to_setup = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.game: Optional[PokerGame] = None
        self.players: Dict[int, object] = {}  # seat -> player object
        self.human_seats: List[int] = []
        self._current_human_action: Optional[Action] = None
        self._game_loop_running = False
        
        self.setStyleSheet(GAME_STYLESHEET)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the game screen UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Game container
        self.game_container = QWidget()
        self.game_container.setObjectName("gameContainer")
        # Style is handled by stylesheet
        
        game_layout = QVBoxLayout(self.game_container)
        game_layout.setContentsMargins(10, 10, 10, 5)
        
        # Top bar with hand info
        top_bar = QHBoxLayout()
        
        self.hand_label = QLabel("Hand #1")
        self.hand_label.setFont(QFont("Segoe UI", 11))
        self.hand_label.setStyleSheet("color: #ffffff;")
        
        self.phase_label = QLabel("")
        self.phase_label.setObjectName("phaseLabel")
        self.phase_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        
        self.back_btn = QPushButton("← Back to Setup")
        self.back_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #ffffff;
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #00ff00;
            }
        """)
        self.back_btn.clicked.connect(self._on_back)
        
        top_bar.addWidget(self.back_btn)
        top_bar.addStretch()
        top_bar.addWidget(self.hand_label)
        top_bar.addStretch()
        top_bar.addWidget(self.phase_label)
        
        # Table area
        self.table_widget = TableWidget()
        self.table_widget.setMinimumSize(750, 400)
        
        # Create player widgets (positioned absolutely on table)
        self.player_widgets: List[PlayerWidget] = []
        for i in range(6):
            pw = PlayerWidget(i, self.table_widget)
            pw.hide()
            self.player_widgets.append(pw)
        
        # Community cards container (centered on table)
        self.community_container = QWidget(self.table_widget)
        self.community_container.setFixedSize(280, 75)
        community_layout = QHBoxLayout(self.community_container)
        community_layout.setSpacing(5)
        community_layout.setContentsMargins(0, 0, 0, 0)
        
        self.community_cards: List[MiniCardWidget] = []
        for i in range(5):
            card = MiniCardWidget()
            card.hide()
            self.community_cards.append(card)
            community_layout.addWidget(card)
        
        # Pot display
        self.pot_label = QLabel(self.table_widget)
        self.pot_label.setObjectName("potLabel")
        self.pot_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.pot_label.setStyleSheet("""
            background: rgba(0, 0, 0, 0.6);
            color: #ffffff;
            border: 2px solid #00ff00;
            border-radius: 10px;
            padding: 5px 15px;
        """)
        self.pot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Action panel
        self.action_panel = ActionPanel()
        self.action_panel.action_selected.connect(self._on_human_action)
        self.action_panel.setFixedHeight(140)
        sp = self.action_panel.sizePolicy()
        sp.setRetainSizeWhenHidden(True)
        self.action_panel.setSizePolicy(sp)
        self.action_panel.hide()
        
        # Winner announcement
        self.winner_label = QLabel(self.table_widget)
        self.winner_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.winner_label.setStyleSheet("""
            background: rgba(0, 128, 0, 0.9);
            color: #ffffff;
            border: 2px solid #ffffff;
            border-radius: 10px;
            padding: 10px 20px;
        """)
        self.winner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.winner_label.hide()
        
        # Next hand button
        self.next_hand_btn = QPushButton("Next Hand →", self.table_widget)
        self.next_hand_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.next_hand_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #008000, stop:1 #006000);
                border: 2px solid #00ff00;
                border-radius: 8px;
                padding: 8px 20px;
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00a000, stop:1 #008000);
            }
        """)
        self.next_hand_btn.clicked.connect(self._start_new_hand)
        self.next_hand_btn.hide()
        
        # Assemble layout
        game_layout.addLayout(top_bar)
        game_layout.addWidget(self.table_widget, 1)
        game_layout.addWidget(self.action_panel)
        
        main_layout.addWidget(self.game_container)

    def resizeEvent(self, event):
        """Handle resize to reposition elements."""
        super().resizeEvent(event)
        self._position_elements()

    def _position_elements(self):
        """Position UI elements on the table."""
        if not self.table_widget:
            return
        
        tw = self.table_widget.width()
        th = self.table_widget.height()
        
        # Player positions around oval table
        # Positions: 0=top-left, 1=top-right, 2=right, 3=bottom-right, 4=bottom-left, 5=left
        positions = [
            (tw * 0.27, 20),           # 1: Top left
            (tw * 0.60, 20),           # 2: Top right
            (tw * 0.85, th * 0.40),    # 3: Right
            (tw * 0.60, th * 0.73),    # 4: Bottom right
            (tw * 0.27, th * 0.73),    # 5: Bottom left
            (tw * 0.04, th * 0.40),    # 6: Left
        ]
        
        for i, pw in enumerate(self.player_widgets):
            x, y = positions[i]
            pw.move(int(x), int(y))
        
        # Community cards - center of table
        self.community_container.move(
            int((tw - self.community_container.width()) / 2),
            int((th - self.community_container.height()) / 2 - 20)
        )
        
        # Pot label - above community cards
        self.pot_label.adjustSize()
        self.pot_label.move(
            int((tw - self.pot_label.width()) / 2),
            int((th - self.pot_label.height()) / 2 - 80)
        )
        
        # Winner label - center
        self.winner_label.adjustSize()
        self.winner_label.move(
            int((tw - self.winner_label.width()) / 2),
            int((th - self.winner_label.height()) / 2 + 60)
        )
        
        # Next hand button - below winner
        self.next_hand_btn.move(
            int((tw - self.next_hand_btn.width()) / 2),
            int((th - self.next_hand_btn.height()) / 2 + 120)
        )

    def start_game(self, player_configs: List[dict], chips: int, sb: int, bb: int):
        """Start a new poker game."""
        # Create game engine
        self.game = PokerGame(
            num_players=6,
            starting_chips=chips,
            small_blind=sb,
            big_blind=bb
        )
        
        # Setup callbacks
        self.game.on_state_change = self._on_state_change
        self.game.on_winner = self._on_winner
        
        # Create player objects
        self.players.clear()
        self.human_seats.clear()
        player_names = [""] * 6  # Empty names for empty seats
        
        for config in player_configs:
            seat = config["seat"]
            name = config["name"]
            player_names[seat] = name
            
            if config["type"] == "human":
                self.players[seat] = HumanPlayer(seat, name)
                self.human_seats.append(seat)
            else:
                self.players[seat] = AIPlayer(
                    seat, name,
                    model_path=config.get("model_path"),
                    thinking_time=1.0
                )
        
        # Setup game players
        self.game.setup_players(player_names)
        
        # Update UI
        for i, pw in enumerate(self.player_widgets):
            if player_names[i]:
                pw.show()
                pw.name_label.setText(player_names[i])
                if i in self.players:
                    pw.set_player_type(self.players[i].player_type)
            else:
                pw.hide()
        
        self._position_elements()
        self._start_new_hand()

    def _start_new_hand(self):
        """Start a new hand."""
        self.winner_label.hide()
        self.next_hand_btn.hide()
        
        # Clear community cards
        for card in self.community_cards:
            card.clear()
            card.hide()
        
        # Reset player widgets
        for pw in self.player_widgets:
            pw.set_winner(False)
            pw.set_active(False)
        
        # Start hand in game engine
        self.game.start_hand()
        
        self.hand_label.setText(f"Hand #{self.game.hand_number}")
        
        # Start game loop
        QTimer.singleShot(500, self._run_game_loop)

    def _run_game_loop(self):
        """Run the game loop (called via timer for async-like behavior)."""
        if not self.game or self.game.is_hand_over():
            return
        
        state = self.game.get_state()
        current_seat = self._get_seat_for_player_idx(state.current_player_idx)
        
        if current_seat is None:
            return
        
        player = self.players.get(current_seat)
        if not player:
            return
        
        if isinstance(player, HumanPlayer):
            # Show action panel for human
            self._show_action_panel(state)
        else:
            # AI player - get action asynchronously
            self._get_ai_action(player, state)

    def _get_seat_for_player_idx(self, player_idx: int) -> Optional[int]:
        """Get seat number for a game player index."""
        if player_idx < 0 or player_idx >= len(self.game.players):
            return None
        return self.game.players[player_idx].seat

    def _show_action_panel(self, state: GameState):
        """Show action panel for human player."""
        player_idx = state.current_player_idx
        player = state.players[player_idx]
        
        call_amount = self.game.get_call_amount(player_idx)
        min_raise = self.game.get_min_raise_to(player_idx)
        max_raise = player.chips + player.current_bet
        
        self.action_panel.configure(
            pot_size=state.pot_total,
            call_amount=call_amount,
            min_bet=min_raise,
            max_bet=max_raise,
            current_bet=state.current_bet,
            big_blind=state.big_blind
        )
        self.action_panel.show()

    def _on_human_action(self, action: Action):
        """Handle action from human player."""
        if not self.game or self.game.is_hand_over():
            return
        
        player_idx = self.game.current_player_idx
        success = self.game.apply_action(player_idx, action)
        
        if success:
            self.action_panel.hide()
            # Continue game loop after short delay
            QTimer.singleShot(500, self._run_game_loop)

    def _get_ai_action(self, player: AIPlayer, state: GameState):
        """Get action from AI player."""
        player_idx = self.game.current_player_idx
        
        # Run AI in a timer to avoid blocking
        def get_action():
            import asyncio
            
            # Create event loop for async call
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                player_state = state.get_player_view(player.seat, show_all=False)
                action = loop.run_until_complete(player.get_action(player_state))
                loop.close()
                
                # Apply action on main thread
                if not self.game.is_hand_over():
                    success = self.game.apply_action(player_idx, action)
                    if success:
                        QTimer.singleShot(300, self._run_game_loop)
                        
            except Exception as e:
                print(f"AI error: {e}")
                # Fallback to check/fold
                if not self.game.is_hand_over():
                    call_amount = self.game.get_call_amount(player_idx)
                    if call_amount == 0:
                        self.game.apply_action(player_idx, Action(ActionType.CHECK))
                    else:
                        self.game.apply_action(player_idx, Action(ActionType.FOLD))
                    QTimer.singleShot(300, self._run_game_loop)
        
        QTimer.singleShot(100, get_action)

    def _on_state_change(self, state: GameState):
        """Handle game state change."""
        # Update phase label
        phase_names = {
            GamePhase.PREFLOP: "Pre-Flop",
            GamePhase.FLOP: "Flop",
            GamePhase.TURN: "Turn",
            GamePhase.RIVER: "River",
            GamePhase.SHOWDOWN: "Showdown",
            GamePhase.HAND_OVER: "Hand Complete",
        }
        self.phase_label.setText(phase_names.get(state.phase, ""))
        
        # Update pot
        self.pot_label.setText(f"Pot: ${state.pot_total:,}")
        self.pot_label.adjustSize()
        if self.table_widget:
            tw = self.table_widget.width()
            th = self.table_widget.height()
            self.pot_label.move(
                int((tw - self.pot_label.width()) / 2),
                int((th - self.pot_label.height()) / 2 - 80)
            )
        
        # Update player widgets
        for i, game_player in enumerate(state.players):
            seat = game_player.seat
            pw = self.player_widgets[seat]
            
            # Show hole cards for humans and at showdown
            show_cards = (seat in self.human_seats) or (state.phase == GamePhase.SHOWDOWN)
            pw.update_state(game_player, show_cards=show_cards)
            
            # Highlight current player
            is_current = (i == state.current_player_idx and state.phase not in 
                         [GamePhase.SHOWDOWN, GamePhase.HAND_OVER])
            pw.set_active(is_current)
        
        # Update community cards
        for i, card in enumerate(state.community_cards):
            if i < len(self.community_cards):
                self.community_cards[i].set_card(card)
                self.community_cards[i].show()

    def _on_winner(self, winners: List[int], amount: int, hand_result):
        """Handle winner announcement."""
        self.action_panel.hide()
        
        # Get winner names
        winner_names = []
        for idx in winners:
            if idx < len(self.game.players):
                name = self.game.players[idx].name
                winner_names.append(name)
                seat = self.game.players[idx].seat
                self.player_widgets[seat].set_winner(True)
        
        # Show winner message
        if hand_result:
            msg = f"🏆 {', '.join(winner_names)} wins ${amount:,}\n{hand_result.description}"
        else:
            msg = f"🏆 {', '.join(winner_names)} wins ${amount:,}"
        
        self.winner_label.setText(msg)
        self.winner_label.adjustSize()
        self.winner_label.show()
        
        # Show next hand button
        if self.game.get_remaining_players() >= 2:
            self.next_hand_btn.show()
        
        self._position_elements()

    def _on_back(self):
        """Return to setup screen."""
        self._game_loop_running = False
        self.return_to_setup.emit()

    def play_sound(self, sound_name: str):
        """Play a sound effect."""
        try:
            play_sound(sound_name)
        except Exception:
            pass  # Ignore sound errors
