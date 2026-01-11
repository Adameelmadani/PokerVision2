"""
Card widget with flip animation.
"""
from PyQt6.QtWidgets import (
    QFrame, QLabel, QVBoxLayout, QHBoxLayout,
    QGraphicsOpacityEffect
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup,
    QParallelAnimationGroup, QPoint, pyqtProperty, QTimer
)
from PyQt6.QtGui import QFont, QPainter, QBrush, QColor, QPen

from ..engine.deck import Card, Suit


class CardWidget(QFrame):
    """Widget displaying a playing card with animations."""

    CARD_WIDTH = 55
    CARD_HEIGHT = 78

    def __init__(self, parent=None):
        super().__init__(parent)
        self._card: Card = None
        self._face_up = False
        self._scale = 1.0
        
        self.setFixedSize(self.CARD_WIDTH, self.CARD_HEIGHT)
        self.setObjectName("cardFrame")
        self._setup_ui()

    def _setup_ui(self):
        """Setup the card layout."""
        self.setStyleSheet("""
            QFrame#cardFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #800000, stop:0.5 #600000, stop:1 #800000);
                border: 2px solid #ffffff;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(0)
        
        # Top rank
        self.rank_label_top = QLabel("")
        self.rank_label_top.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.rank_label_top.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        
        # Center suit
        self.suit_label = QLabel("")
        self.suit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.suit_label.setFont(QFont("Arial", 20))
        
        # Bottom rank (inverted)
        self.rank_label_bottom = QLabel("")
        self.rank_label_bottom.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self.rank_label_bottom.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        
        layout.addWidget(self.rank_label_top)
        layout.addWidget(self.suit_label, 1)
        layout.addWidget(self.rank_label_bottom)
        
        # Initially show card back
        self._show_back()

    def set_card(self, card: Card, animate: bool = True):
        """Set the card to display."""
        self._card = card
        
        if animate and not self._face_up:
            self._animate_flip()
        else:
            self._show_front()

    def _show_front(self):
        """Show card face."""
        if not self._card:
            return
        
        self._face_up = True
        color = "#cc0000" if self._card.suit.color == "red" else "#000000"
        
        self.setStyleSheet(f"""
            QFrame#cardFrame {{
                background: #fefefe;
                border: 2px solid #333333;
                border-radius: 8px;
            }}
            QLabel {{
                color: {color};
            }}
        """)
        
        self.rank_label_top.setText(self._card.rank.symbol)
        self.suit_label.setText(self._card.suit.symbol)
        self.rank_label_bottom.setText(self._card.rank.symbol)

    def _show_back(self):
        """Show card back."""
        self._face_up = False
        
        self.setStyleSheet("""
            QFrame#cardFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #800000, stop:0.5 #600000, stop:1 #800000);
                border: 2px solid #ffffff;
                border-radius: 8px;
            }
            QLabel {
                color: transparent;
            }
        """)
        
        self.rank_label_top.setText("")
        self.suit_label.setText("🂠")
        self.rank_label_bottom.setText("")
        self.suit_label.setStyleSheet("color: #ffffff; font-size: 24px;")

    def _animate_flip(self):
        """Animate card flip."""
        # Simple fade animation for flip effect
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        
        # Fade out
        self.fade_out = QPropertyAnimation(self.effect, b"opacity")
        self.fade_out.setDuration(100)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        
        # Fade in
        self.fade_in = QPropertyAnimation(self.effect, b"opacity")
        self.fade_in.setDuration(100)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        
        # Sequence
        self.flip_group = QSequentialAnimationGroup(self)
        self.flip_group.addAnimation(self.fade_out)
        self.flip_group.addAnimation(self.fade_in)
        
        # Show front at midpoint
        self.fade_out.finished.connect(self._show_front)
        
        self.flip_group.start()

    def animate_deal(self, start_pos: QPoint, end_pos: QPoint, delay: int = 0):
        """Animate card dealing from deck position."""
        self.move(start_pos)
        self.show()
        
        def start_animation():
            self.anim = QPropertyAnimation(self, b"pos")
            self.anim.setDuration(300)
            self.anim.setStartValue(start_pos)
            self.anim.setEndValue(end_pos)
            self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.anim.start()
        
        if delay > 0:
            QTimer.singleShot(delay, start_animation)
        else:
            start_animation()

    def clear(self):
        """Clear the card display."""
        self._card = None
        self._show_back()

    def set_highlighted(self, highlighted: bool):
        """Highlight this card (e.g., for winning hand)."""
        if highlighted:
            self.setStyleSheet(self.styleSheet() + """
                QFrame#cardFrame {
                    border: 3px solid #00ff00;
                    box-shadow: 0 0 15px #00ff00;
                }
            """)
        else:
            # Restore normal style
            if self._face_up:
                self._show_front()
            else:
                self._show_back()


class MiniCardWidget(QFrame):
    """Smaller card widget for community cards or compact display."""

    CARD_WIDTH = 48
    CARD_HEIGHT = 68

    def __init__(self, parent=None):
        super().__init__(parent)
        self._card: Card = None
        self._face_up = False
        
        self.setFixedSize(self.CARD_WIDTH, self.CARD_HEIGHT)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the mini card layout."""
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #800000, stop:0.5 #600000, stop:1 #800000);
                border: 2px solid #ffffff;
                border-radius: 6px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(0)
        
        self.rank_label = QLabel("")
        self.rank_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rank_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        
        self.suit_label = QLabel("")
        self.suit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.suit_label.setFont(QFont("Arial", 16))
        
        layout.addWidget(self.rank_label)
        layout.addWidget(self.suit_label)

    def set_card(self, card: Card, animate: bool = True):
        """Set the card to display."""
        self._card = card
        self._face_up = True
        
        color = "#cc0000" if card.suit.color == "red" else "#000000"
        
        self.suit_label.setStyleSheet("")
        self.setStyleSheet(f"""
            QFrame {{
                background: #fefefe;
                border: 2px solid #333333;
                border-radius: 6px;
            }}
            QLabel {{
                color: {color};
            }}
        """)
        
        self.rank_label.setText(card.rank.symbol)
        self.suit_label.setText(card.suit.symbol)

    def _show_back(self):
        """Show card back."""
        self._face_up = False
        
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #800000, stop:0.5 #600000, stop:1 #800000);
                border: 2px solid #ffffff;
                border-radius: 6px;
            }
            QLabel {
                color: transparent;
            }
        """)
        
        self.rank_label.setText("")
        self.suit_label.setText("🂠")
        self.suit_label.setStyleSheet("color: #ffffff; font-size: 20px;")

    def clear(self):
        """Clear the card."""
        self._card = None
        self._show_back()
