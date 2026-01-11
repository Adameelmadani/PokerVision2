"""
Stylesheet and theming for the poker application.
PokerStars-inspired dark theme with green accents.
"""

# Color palette
COLORS = {
    'bg_dark': '#1a1a2e',
    'bg_medium': '#16213e',
    'bg_light': '#0f3460',
    'accent': '#00d9ff',
    'accent_green': '#00c851',
    'accent_gold': '#ffd700',
    'accent_red': '#ff4444',
    'text_primary': '#ffffff',
    'text_secondary': '#b0b0b0',
    'table_felt': '#0d5c2e',
    'table_border': '#8b4513',
    'card_white': '#fefefe',
    'card_red': '#cc0000',
    'card_black': '#1a1a1a',
    'button_primary': '#00c851',
    'button_danger': '#cc0000',
    'button_neutral': '#3d5a80',
}

# Main application stylesheet
MAIN_STYLESHEET = """
QMainWindow {
    background-color: #1a1a2e;
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
        stop:0 #4a90d9, stop:1 #357abd);
    border: 2px solid #5a9fd4;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: bold;
    color: white;
    min-width: 80px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #5aa0e9, stop:1 #4588c7);
    border-color: #7ab8f5;
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #357abd, stop:1 #2a6298);
}

QPushButton:disabled {
    background: #555555;
    border-color: #666666;
    color: #888888;
}

QPushButton#foldButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #d94452, stop:1 #c0392b);
    border-color: #e74c3c;
}

QPushButton#foldButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #e95463, stop:1 #d0493b);
}

QPushButton#callButton, QPushButton#checkButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #2ecc71, stop:1 #27ae60);
    border-color: #3ddc84;
}

QPushButton#callButton:hover, QPushButton#checkButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #3edc81, stop:1 #37be70);
}

QPushButton#raiseButton, QPushButton#betButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #f39c12, stop:1 #d68910);
    border-color: #f5b041;
}

QPushButton#raiseButton:hover, QPushButton#betButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #f5ac22, stop:1 #e69920);
}

QPushButton#allInButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #9b59b6, stop:1 #8e44ad);
    border-color: #a569c6;
}

QPushButton#allInButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #ab69c6, stop:1 #9e54bd);
}

QComboBox {
    background-color: #16213e;
    border: 2px solid #0f3460;
    border-radius: 6px;
    padding: 8px 15px;
    font-size: 13px;
    color: white;
    min-width: 150px;
}

QComboBox:hover {
    border-color: #00d9ff;
}

QComboBox::drop-down {
    border: none;
    padding-right: 10px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 8px solid white;
    margin-right: 10px;
}

QComboBox QAbstractItemView {
    background-color: #16213e;
    border: 2px solid #0f3460;
    selection-background-color: #0f3460;
    color: white;
}

QSlider::groove:horizontal {
    border: 1px solid #0f3460;
    height: 10px;
    background: #16213e;
    border-radius: 5px;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #f39c12, stop:1 #d68910);
    border: 2px solid #f5b041;
    width: 20px;
    height: 20px;
    margin: -6px 0;
    border-radius: 10px;
}

QSlider::handle:horizontal:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #f5ac22, stop:1 #e69920);
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #00c851, stop:1 #00d9ff);
    border-radius: 5px;
}

QSpinBox, QLineEdit {
    background-color: #16213e;
    border: 2px solid #0f3460;
    border-radius: 6px;
    padding: 8px;
    font-size: 13px;
    color: white;
}

QSpinBox:focus, QLineEdit:focus {
    border-color: #00d9ff;
}

QGroupBox {
    border: 2px solid #0f3460;
    border-radius: 10px;
    margin-top: 15px;
    padding-top: 15px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 10px;
    color: #00d9ff;
}

QScrollBar:vertical {
    border: none;
    background: #16213e;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: #0f3460;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #00d9ff;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

# Setup screen specific styles
SETUP_STYLESHEET = """
QWidget#setupContainer {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #1a1a2e, stop:0.5 #16213e, stop:1 #1a1a2e);
    border-radius: 20px;
}

QLabel#titleLabel {
    font-size: 42px;
    font-weight: bold;
    color: #ffd700;
    padding: 20px;
}

QLabel#subtitleLabel {
    font-size: 18px;
    color: #00d9ff;
}

QFrame#seatFrame {
    background: rgba(22, 33, 62, 0.8);
    border: 2px solid #0f3460;
    border-radius: 15px;
    padding: 15px;
}

QFrame#seatFrame:hover {
    border-color: #00d9ff;
    background: rgba(22, 33, 62, 0.95);
}

QPushButton#startButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #00c851, stop:1 #00a040);
    border: 3px solid #00d861;
    border-radius: 15px;
    padding: 15px 40px;
    font-size: 20px;
    font-weight: bold;
    min-width: 200px;
}

QPushButton#startButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #00d861, stop:1 #00b850);
    border-color: #00e871;
}
"""

# Game screen specific styles  
GAME_STYLESHEET = """
QWidget#gameContainer {
    background: #0a0a14;
}

QWidget#tableWidget {
    background: transparent;
}

QLabel#potLabel {
    font-size: 28px;
    font-weight: bold;
    color: #ffd700;
    background: rgba(0, 0, 0, 0.6);
    border-radius: 15px;
    padding: 10px 25px;
}

QLabel#phaseLabel {
    font-size: 16px;
    color: #00d9ff;
    background: rgba(0, 0, 0, 0.5);
    border-radius: 10px;
    padding: 5px 15px;
}

QFrame#playerFrame {
    background: rgba(22, 33, 62, 0.9);
    border: 3px solid #0f3460;
    border-radius: 12px;
    padding: 8px;
}

QFrame#playerFrame[active="true"] {
    border-color: #00d9ff;
    background: rgba(0, 217, 255, 0.15);
}

QFrame#playerFrame[folded="true"] {
    opacity: 0.5;
    background: rgba(50, 50, 50, 0.7);
}

QFrame#playerFrame[winner="true"] {
    border-color: #ffd700;
    background: rgba(255, 215, 0, 0.2);
}

QLabel#playerName {
    font-size: 14px;
    font-weight: bold;
    color: #ffffff;
}

QLabel#playerChips {
    font-size: 13px;
    color: #00c851;
    font-weight: bold;
}

QLabel#playerBet {
    font-size: 12px;
    color: #ffd700;
}

QLabel#dealerButton {
    background: #ffffff;
    color: #1a1a2e;
    font-weight: bold;
    font-size: 11px;
    border-radius: 12px;
    padding: 3px 8px;
}

QFrame#actionPanel {
    background: rgba(26, 26, 46, 0.95);
    border: 2px solid #0f3460;
    border-radius: 15px;
    padding: 15px;
}

QLabel#raiseLabel {
    font-size: 18px;
    font-weight: bold;
    color: #f39c12;
}
"""

# Card widget styles
CARD_STYLESHEET = """
QFrame#cardFrame {
    background: #fefefe;
    border: 2px solid #333333;
    border-radius: 8px;
}

QFrame#cardFrame[back="true"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #1e3a5f, stop:0.5 #0d2137, stop:1 #1e3a5f);
    border-color: #4a90d9;
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
    color: #1a1a1a;
}

QLabel#suitLabel[suit="red"] {
    color: #cc0000;
}

QLabel#suitLabel[suit="black"] {
    color: #1a1a1a;
}
"""
