"""
Main entry point for Stegopy application.

Launches the PyQt6 GUI.
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor

from stegopy.ui.gui import MainWindow, styles


def main():
    """Launch the application."""
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    # Apply light theme by default
    app.setStyleSheet(styles.LIGHT_THEME)

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
