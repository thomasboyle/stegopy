"""
Main window for Stegopy GUI.

Implements the main application window with tabbed interface for embed, extract, and settings.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QFont, QDropEvent, QDragEnterEvent
from pathlib import Path
import os
import threading

from stegopy.core import load_image, Payload, PVDEmbedding, DCTEmbedding
from stegopy.util import image_utils
from .widgets import CapacityIndicator, FileList, ProgressPanel
from .embed_tab import EmbedTab
from .extract_tab import ExtractTab


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stegopy - Modern Steganography Suite")
        self.setSize(900, 700)
        self.init_ui()

    def setSize(self, width: int, height: int):
        """Set window size."""
        self.resize(width, height)

    def init_ui(self):
        """Initialize UI."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("Stegopy")
        title.setProperty("class", "title")
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Securely hide information in image files using advanced steganography techniques")
        subtitle.setProperty("class", "subtitle")
        layout.addWidget(subtitle)

        # Tab widget
        self.tabs = QTabWidget()
        self.embed_tab = EmbedTab()
        self.extract_tab = ExtractTab()

        self.tabs.addTab(self.embed_tab, "Embed")
        self.tabs.addTab(self.extract_tab, "Extract")

        layout.addWidget(self.tabs, 1)

        # Status bar
        self.statusBar().showMessage("Ready")

        central_widget.setLayout(layout)

        # Set application icon
        self.setWindowIcon(QIcon())

        # Set minimum size to prevent overlapping
        self.setMinimumSize(900, 700)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter."""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Handle drop."""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if self.tabs.currentIndex() == 0:
                self.embed_tab.load_image(file_path)
            else:
                self.extract_tab.load_image(file_path)
