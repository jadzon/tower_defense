"""
Army Defense Game
Main entry point for the application
"""
import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MyWindow

def main():
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()