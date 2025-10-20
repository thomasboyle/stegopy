"""
Embed tab for Stegosuite GUI.

Handles image embedding operations with drag-drop support.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QFileDialog, QMessageBox, QTextEdit,
    QGroupBox, QSpinBox, QComboBox, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
import threading
import time

from stegosuite.core import load_image, Payload, PVDEmbedding, DCTEmbedding, LSBEmbedding, NoFilter
from stegosuite.config import DEFAULT_EMBEDDING_METHOD
from stegosuite.util import image_utils
from .widgets import CapacityIndicator, FileList, ProgressPanel


class EmbedWorker(QThread):
    """Worker thread for embedding operations."""
    
    progress_updated = pyqtSignal(int, int)
    embedding_complete = pyqtSignal(str)
    embedding_error = pyqtSignal(str)
    
    def __init__(self, image, image_path, message, files, password):
        super().__init__()
        self.image = image
        self.image_path = image_path
        self.message = message
        self.files = files
        self.password = password
        self.result_image = None
        
    def run(self):
        """Run embedding in worker thread."""
        try:
            # Create payload
            payload = Payload(self.password)
            if self.message:
                payload.add_message(self.message)
            for file_path in self.files:
                payload.add_file(file_path)

            # Select embedding method based on format
            format_str = image_utils.detect_format(self.image_path)
            method_name = DEFAULT_EMBEDDING_METHOD.get(format_str, "lsb")

            if method_name == "lsb":
                embedding = LSBEmbedding(self.image, NoFilter())
            elif method_name == "pvd":
                embedding = PVDEmbedding(self.image, NoFilter())
            elif method_name == "dct":
                embedding = DCTEmbedding(self.image, NoFilter())
            else:
                raise ValueError(f"Unsupported embedding method: {method_name}")

            # Embed
            embedding.set_progress_callback(self._update_progress)
            self.result_image = embedding.embed(payload)

            # Save
            output_path = image_utils.get_output_path(self.image_path)
            self.result_image.save(output_path)

            # Signal success
            self.embedding_complete.emit(output_path)

        except Exception as e:
            self.embedding_error.emit(str(e))
            
    def _update_progress(self, current: int, total: int):
        """Emit progress signal."""
        self.progress_updated.emit(current, total)


class EmbedTab(QWidget):
    """Embed tab widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None
        self.image_path = None
        self.embed_worker = None
        self.init_ui()
        self.setAcceptDrops(True)

    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Image selection section
        image_group = QGroupBox("1. Select Image")
        image_layout = QVBoxLayout()

        image_button_layout = QHBoxLayout()
        self.image_button = QPushButton("📁 Select Image File")
        self.image_button.setToolTip("Choose an image file (BMP, GIF, JPG, PNG) to embed data into")
        self.image_button.clicked.connect(self.select_image)
        image_button_layout.addWidget(self.image_button)

        self.image_label = QLabel("No image selected")
        self.image_label.setStyleSheet("color: #999;")
        image_button_layout.addWidget(self.image_label)
        image_button_layout.addStretch()

        image_layout.addLayout(image_button_layout)
        image_group.setLayout(image_layout)
        layout.addWidget(image_group)

        # Capacity indicator
        self.capacity_indicator = CapacityIndicator()
        layout.addWidget(self.capacity_indicator)

        # Create scrollable area for the rest of the content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea > QWidget {
                background-color: transparent;
            }
        """)

        # Container widget for scrollable content
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(15)

        # Payload section
        payload_group = QGroupBox("2. Add Payload")
        payload_layout = QVBoxLayout()

        # Message section
        msg_label = QLabel("Message:")
        payload_layout.addWidget(msg_label)
        self.message_input = QTextEdit()
        self.message_input.setMinimumHeight(80)
        self.message_input.setMaximumHeight(150)
        self.message_input.setPlaceholderText("Enter text message to embed...")
        self.message_input.setToolTip("Enter any text message you want to hide in the image")
        self.message_input.textChanged.connect(self.on_payload_changed)
        payload_layout.addWidget(self.message_input)

        # File section
        self.file_list = FileList()
        self.file_list.files_changed.connect(self.on_payload_changed)
        payload_layout.addWidget(self.file_list)

        payload_group.setLayout(payload_layout)
        scroll_layout.addWidget(payload_group)

        # Encryption section
        crypto_group = QGroupBox("3. Encryption")
        crypto_layout = QHBoxLayout()

        crypto_layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Optional - leave blank for no encryption")
        self.password_input.setToolTip("Set a password to encrypt the embedded data. Leave empty for no encryption.")
        crypto_layout.addWidget(self.password_input)

        crypto_group.setLayout(crypto_layout)
        scroll_layout.addWidget(crypto_group)

        # Embedding section
        embed_group = QGroupBox("4. Embed")
        embed_layout = QVBoxLayout()

        button_layout = QHBoxLayout()
        self.embed_button = QPushButton("🚀 Embed & Save")
        self.embed_button.setProperty("class", "success")
        self.embed_button.setToolTip("Start the embedding process and save the result as a new image file")
        self.embed_button.clicked.connect(self.start_embedding)
        button_layout.addWidget(self.embed_button)

        button_layout.addStretch()
        embed_layout.addLayout(button_layout)

        # Progress panel
        self.progress_panel = ProgressPanel()
        embed_layout.addWidget(self.progress_panel)

        embed_group.setLayout(embed_layout)
        scroll_layout.addWidget(embed_group)

        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)

        layout.addWidget(scroll_area)
        self.setLayout(layout)

    def select_image(self):
        """Select image file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
            "Image Files (*.bmp *.gif *.jpg *.jpeg *.png);;All Files (*.*)"
        )
        if file_path:
            self.load_image(file_path)

    def load_image(self, file_path: str):
        """Load image file."""
        try:
            is_valid, message = image_utils.validate_image_format(file_path)
            if not is_valid:
                QMessageBox.warning(self, "Invalid Image", message)
                return

            self.image = load_image(file_path)
            self.image_path = file_path
            self.image_label.setText(Path(file_path).name)
            self.image_label.setStyleSheet("color: #000; font-weight: bold;")

            # Update capacity
            self.on_payload_changed()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")

    def on_payload_changed(self):
        """Update capacity when payload changes."""
        if not self.image:
            self.capacity_indicator.set_capacity(0, 0)
            return

        # Calculate payload size
        message = self.message_input.toPlainText()
        message_size = len(message.encode("utf-8")) if message else 0
        file_size = self.file_list.get_total_size()
        payload_size = message_size + file_size

        # Get capacity
        capacity = self.image.get_capacity_estimate()

        self.capacity_indicator.set_capacity(payload_size, capacity)

    def start_embedding(self):
        """Start embedding operation."""
        if not self.image or not self.image_path:
            QMessageBox.warning(self, "No Image", "Please select an image first")
            return

        message = self.message_input.toPlainText()
        files = self.file_list.get_files()

        if not message and not files:
            QMessageBox.warning(self, "Empty Payload", "Please add a message or file to embed")
            return

        # Disable buttons
        self.embed_button.setEnabled(False)
        self.progress_panel.reset()
        self.progress_panel.set_status("Embedding...")

        # Create and start worker thread
        self.embed_worker = EmbedWorker(
            self.image, 
            self.image_path, 
            message, 
            files, 
            self.password_input.text()
        )
        
        # Connect signals
        self.embed_worker.progress_updated.connect(self._on_progress_updated)
        self.embed_worker.embedding_complete.connect(self._on_embedding_complete)
        self.embed_worker.embedding_error.connect(self._on_embedding_error)
        
        # Start worker
        self.embed_worker.start()

    def _on_progress_updated(self, current: int, total: int):
        """Handle progress update from worker thread."""
        self.progress_panel.set_progress(current, total)

    def _on_embedding_complete(self, output_path: str):
        """Handle successful embedding completion."""
        self.progress_panel.set_complete()
        self.embed_button.setEnabled(True)
        QMessageBox.information(
            self, "Success",
            f"Image embedded successfully!\nSaved to: {output_path}"
        )

    def _on_embedding_error(self, error_message: str):
        """Handle embedding error."""
        self.progress_panel.set_error(error_message)
        self.embed_button.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Embedding failed: {error_message}")

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
            self.load_image(urls[0].toLocalFile())


from pathlib import Path
