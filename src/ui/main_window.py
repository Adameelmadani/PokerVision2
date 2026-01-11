"""
Main application window.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QStackedWidget, QWidget, QVBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from .styles import MAIN_STYLESHEET
from .setup_screen import SetupScreen
from .game_screen import GameScreen


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Texas Hold'em Poker")
        self.setMinimumSize(1280, 800)
        self.setStyleSheet(MAIN_STYLESHEET)
        
        self._setup_ui()

    def _setup_ui(self):
        """Setup the main window UI."""
        # Central stacked widget
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Setup screen
        self.setup_screen = SetupScreen()
        self.setup_screen.start_game.connect(self._on_start_game)
        
        # Game screen
        self.game_screen = GameScreen()
        self.game_screen.return_to_setup.connect(self._show_setup)
        
        # Add to stack
        self.stack.addWidget(self.setup_screen)
        self.stack.addWidget(self.game_screen)
        
        # Show setup first
        self.stack.setCurrentWidget(self.setup_screen)

    def _on_start_game(self, players, chips, sb, bb):
        """Handle game start from setup screen."""
        self.stack.setCurrentWidget(self.game_screen)
        self.game_screen.start_game(players, chips, sb, bb)

    def _show_setup(self):
        """Return to setup screen."""
        self.stack.setCurrentWidget(self.setup_screen)
        self.setup_screen.refresh_models()

    def closeEvent(self, event):
        """Handle window close."""
        # Clean up any running game
        event.accept()
