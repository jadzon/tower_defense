"""
Simple bottom panel for Army Defense game
"""
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import pyqtSignal, Qt

class BottomPanel(QFrame):
    """Basic UI panel for the bottom of the game window"""

    # Signal for build button
    build_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Simple dark styling with border
        self.setStyleSheet("background-color: #222222; border-top: 2px solid black;")
        self.setMinimumHeight(70)
        self.setMaximumHeight(70)

        # Create simple layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)

        # Add avatar (placeholder until we set a real one)
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(60, 60)
        self.layout.addWidget(self.avatar_label)

        # Add spacer to push elements apart
        self.layout.addStretch(1)

        # Add build button
        self.build_button = QPushButton("Build")
        self.build_button.setMinimumWidth(100)
        self.build_button.clicked.connect(self.build_clicked.emit)
        self.layout.addWidget(self.build_button)

    def set_avatar(self, pixmap):
        """Set the avatar image from a pixmap"""
        if pixmap and not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio)
            self.avatar_label.setPixmap(scaled_pixmap)