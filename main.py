"""
Texas Hold'em Poker - Main Entry Point

A professional poker interface with AI opponents.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.ui.main_window import MainWindow


def main():
    """Main entry point."""
    # Enable high DPI scaling
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Texas Hold'em Poker")
    app.setOrganizationName("PokerVision")
    
    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Set style
    app.setStyle("Fusion")
    
    # Create and show main window
    window = MainWindow()
    window.showMaximized()
    
    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
