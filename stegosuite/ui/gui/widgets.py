"""
Reusable widgets for Stegosuite GUI.

Custom PyQt6 widgets for common UI elements.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QSpinBox, QComboBox, QProgressBar, QListWidget,
    QListWidgetItem, QFileDialog, QMessageBox, QFrame, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QColor
from pathlib import Path


class CapacityIndicator(QWidget):
    """Widget to display payload capacity and usage."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.label = QLabel("📊 Embedding Capacity: 0 / 0 bytes")
        self.label.setProperty("class", "section-title")
        layout.addWidget(self.label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.info_label = QLabel("Ready")
        self.info_label.setStyleSheet("color: green;")
        layout.addWidget(self.info_label)

        self.setLayout(layout)

    def set_capacity(self, used: int, total: int):
        """Update capacity display."""
        self.label.setText(f"Embedding Capacity: {used} / {total} bytes")
        if total > 0:
            percentage = int((used / total) * 100)
            self.progress.setValue(percentage)
            if percentage > 80:
                self.progress.setStyleSheet("QProgressBar::chunk { background-color: #ff6b6b; }")
            elif percentage > 50:
                self.progress.setStyleSheet("QProgressBar::chunk { background-color: #ffa500; }")
            else:
                self.progress.setStyleSheet("QProgressBar::chunk { background-color: #51cf66; }")


class FileList(QWidget):
    """Widget to manage payload files."""

    files_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.files = []
        self.init_ui()

    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        # Header
        header = QLabel("Payload Files")
        header.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(header)

        # File list
        self.list_widget = QListWidget()
        self.list_widget.setMinimumHeight(60)
        self.list_widget.setMaximumHeight(150)
        layout.addWidget(self.list_widget)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("➕ Add File")
        self.add_button.setToolTip("Select a file to embed alongside your message")
        self.add_button.clicked.connect(self.add_file)
        button_layout.addWidget(self.add_button)

        self.remove_button = QPushButton("➖ Remove")
        self.remove_button.setToolTip("Remove the selected file from the embedding list")
        self.remove_button.clicked.connect(self.remove_file)
        button_layout.addWidget(self.remove_button)

        self.clear_button = QPushButton("🗑️ Clear All")
        self.clear_button.setToolTip("Remove all files from the embedding list")
        self.clear_button.clicked.connect(self.clear_files)
        button_layout.addWidget(self.clear_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def add_file(self):
        """Add file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File to Embed", "",
            "All Files (*.*)"
        )
        if file_path:
            self.files.append(file_path)
            self.list_widget.addItem(Path(file_path).name)
            self.files_changed.emit()

    def remove_file(self):
        """Remove selected file."""
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            self.list_widget.takeItem(current_row)
            del self.files[current_row]
            self.files_changed.emit()

    def clear_files(self):
        """Clear all files."""
        self.list_widget.clear()
        self.files.clear()
        self.files_changed.emit()

    def get_files(self):
        """Get list of files."""
        return self.files

    def get_total_size(self):
        """Get total size of all files."""
        import os
        return sum(os.path.getsize(f) for f in self.files if os.path.exists(f))


class ProgressPanel(QWidget):
    """Widget to show operation progress."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.status_label = QLabel("⏳ Ready")
        self.status_label.setProperty("class", "section-title")
        layout.addWidget(self.status_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.details_label = QLabel("")
        layout.addWidget(self.details_label)

        self.setLayout(layout)

    def set_status(self, status: str):
        """Set status text."""
        self.status_label.setText(status)

    def set_progress(self, current: int, total: int):
        """Update progress."""
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress.setValue(percentage)
            self.details_label.setText(f"{current} / {total} bytes")

    def set_complete(self):
        """Mark as complete."""
        self.progress.setValue(100)
        self.status_label.setText("✅ Complete")
        self.status_label.setProperty("class", "section-title")

    def set_error(self, error_msg: str):
        """Mark as error."""
        self.status_label.setText(f"❌ Error: {error_msg}")
        self.status_label.setProperty("class", "section-title")

    def reset(self):
        """Reset to initial state."""
        self.status_label.setText("⏳ Ready")
        self.status_label.setProperty("class", "section-title")
        self.progress.setValue(0)
        self.details_label.setText("")
