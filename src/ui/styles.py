"""
Stylesheet and theming for the poker application.
Strict White/Dark Green/Red theme for casino feel.
"""

# Color palette
COLORS = {
    'bg_dark': '#051005',      # Very dark green, almost black
    'bg_medium': '#0a250a',    # Dark green
    'bg_light': '#153515',     # Medium dark green
    'accent': '#ffffff',       # White for text/icons
    'accent_green': '#00ff00', # Bright green for highlights
    'accent_red': '#ff0000',   # Red for danger/action
    'text_primary': '#ffffff',
    'text_secondary': '#cccccc',
    'table_felt': '#0d5c2e',
    'table_border': '#021002', # Dark border
    'card_white': '#ffffff',
    'card_red': '#cc0000',
    'card_black': '#000000',
    'button_primary': '#008000', # Standard green button
    'button_danger': '#cc0000',
    'button_neutral': '#204020',
}

# Main application stylesheet
MAIN_STYLESHEET = """
QMainWindow {
    background-color: #051005;
}

QWidget {
    color: #ffffff;
    font-family: 'Segoe UI', 'Arial', sans-serif;
}

QLabel {
    color: #ffffff;
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1a4a1a, stop:1 #0e2e0e);
    border: 2px solid #2a6a2a;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: bold;
    color: white;
    min-width: 80px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #2a6a2a, stop:1 #1a4a1a);
    border-color: #00ff00;
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #0e2e0e, stop:1 #051005);
}

QPushButton:disabled {
    background: #152515;
    border-color: #203020;
    color: #556655;
}

QPushButton#foldButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #800000, stop:1 #600000);
    border-color: #ff0000;
}

QPushButton#foldButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #a00000, stop:1 #800000);
}

QPushButton#callButton, QPushButton#checkButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #008000, stop:1 #006000);
    border-color: #00ff00;
}

QPushButton#callButton:hover, QPushButton#checkButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #00a000, stop:1 #008000);
}

QPushButton#raiseButton, QPushButton#betButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #b30000, stop:1 #800000);
    border-color: #ff0000;
}

QPushButton#raiseButton:hover, QPushButton#betButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #cc0000, stop:1 #a00000);
}

QPushButton#allInButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #ff0000, stop:1 #cc0000);
    border-color: #ffffff;
}

QPushButton#allInButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #ff3333, stop:1 #ff0000);
}

QComboBox {
    background-color: #0a250a;
    border: 2px solid #153515;
    border-radius: 6px;
    padding: 8px 15px;
    font-size: 13px;
    color: white;
    min-width: 150px;
}

QComboBox:hover {
    border-color: #00ff00;
}

QComboBox::drop-down {
    border: none;
    width: 0px;
}

QComboBox::down-arrow {
    image: none;
    border: none;
}

QComboBox QAbstractItemView {
    background-color: #0a250a;
    border: 2px solid #153515;
    selection-background-color: #153515;
    color: white;
}

QSlider::groove:horizontal {
    border: 1px solid #153515;
    height: 10px;
    background: #0a250a;
    border-radius: 5px;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #ffffff, stop:1 #cccccc);
    border: 2px solid #ffffff;
    width: 20px;
    height: 20px;
    margin: -6px 0;
    border-radius: 10px;
}

QSlider::handle:horizontal:hover {
    background: #ffffff;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #008000, stop:1 #00ff00);
    border-radius: 5px;
}

QSpinBox, QLineEdit {
    background-color: #0a250a;
    border: 2px solid #153515;
    border-radius: 6px;
    padding: 8px;
    font-size: 13px;
    color: white;
}

QSpinBox:focus, QLineEdit:focus {
    border-color: #00ff00;
}

QGroupBox {
    border: 2px solid #153515;
    border-radius: 10px;
    margin-top: 15px;
    padding-top: 15px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 10px;
    color: #ffffff;
}

QScrollBar:vertical {
    border: none;
    background: #0a250a;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: #153515;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #00ff00;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

# Setup screen specific styles
SETUP_STYLESHEET = """
QWidget#setupContainer {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #051005, stop:0.5 #0a250a, stop:1 #051005);
    border-radius: 20px;
}

QLabel#titleLabel {
    font-size: 34px;
    font-weight: bold;
    color: #ffffff;
    padding: 10px;
}

QLabel#subtitleLabel {
    font-size: 18px;
    color: #00ff00;
}

QFrame#seatFrame {
    background: rgba(10, 37, 10, 0.8);
    border: 2px solid #153515;
    border-radius: 15px;
    padding: 6px;
}

QFrame#seatFrame:hover {
    border-color: #00ff00;
    background: rgba(10, 37, 10, 0.95);
}

QPushButton#startButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #008000, stop:1 #006000);
    border: 3px solid #00ff00;
    border-radius: 15px;
    padding: 6px 10px;
    font-size: 18px;
    font-weight: bold;
    min-width: 200px;
}

QPushButton#startButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #00a000, stop:1 #008000);
    border-color: #ffffff;
}
"""

# Game screen specific styles  
GAME_STYLESHEET = """
QWidget#gameContainer {
    background: #051005;
}

QWidget#tableWidget {
    background: transparent;
}

QLabel#potLabel {
    font-size: 28px;
    font-weight: bold;
    color: #ffffff;
    background: rgba(0, 0, 0, 0.6);
    border: 2px solid #00ff00;
    border-radius: 15px;
    padding: 10px 25px;
}

QLabel#phaseLabel {
    font-size: 16px;
    color: #ffffff;
    background: rgba(0, 0, 0, 0.5);
    border-radius: 10px;
    padding: 5px 15px;
}

QFrame#playerFrame {
    background: rgba(10, 37, 10, 0.9);
    border: 3px solid #153515;
    border-radius: 12px;
    padding: 8px;
}

QFrame#playerFrame[active="true"] {
    border-color: #00ff00;
    background: rgba(0, 255, 0, 0.15);
}

QFrame#playerFrame[folded="true"] {
    opacity: 0.5;
    background: rgba(20, 20, 20, 0.7);
}

QFrame#playerFrame[winner="true"] {
    border-color: #ffffff;
    background: rgba(255, 255, 255, 0.2);
}

QLabel#playerName {
    font-size: 14px;
    font-weight: bold;
    color: #ffffff;
}

QLabel#playerChips {
    font-size: 13px;
    color: #00ff00;
    font-weight: bold;
}

QLabel#playerBet {
    font-size: 12px;
    color: #ffffff;
}

QLabel#dealerButton {
    background: #ffffff;
    color: #000000;
    font-weight: bold;
    font-size: 11px;
    border-radius: 12px;
    padding: 3px 8px;
}

QFrame#actionPanel {
    background: rgba(5, 16, 5, 0.95);
    border: 2px solid #153515;
    border-radius: 15px;
    padding: 15px;
}

QLabel#raiseLabel {
    font-size: 18px;
    font-weight: bold;
    color: #ffffff;
}
"""

# Card widget styles
CARD_STYLESHEET = """
QFrame#cardFrame {
    background: #ffffff;
    border: 2px solid #000000;
    border-radius: 8px;
}

QFrame#cardFrame[back="true"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #800000, stop:0.5 #600000, stop:1 #800000);
    border-color: #ffffff;
}

QLabel#rankLabel {
    font-size: 22px;
    font-weight: bold;
}

QLabel#suitLabel {
    font-size: 28px;
}

QLabel#rankLabel[suit="red"] {
    color: #cc0000;
}

QLabel#rankLabel[suit="black"] {
    color: #000000;
}

QLabel#suitLabel[suit="red"] {
    color: #cc0000;
}

QLabel#suitLabel[suit="black"] {
    color: #000000;
}
"""
