"""
Extract tab for Stegosuite GUI.

Handles image extraction operations with content preview.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QFileDialog, QMessageBox, QTextEdit, QGroupBox,
    QScrollArea, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
import os
import traceback

from stegopy.core import load_image, LSBEmbedding, PVDEmbedding, DCTEmbedding, NoFilter
from stegopy.config import DEFAULT_EMBEDDING_METHOD
from stegopy.util import image_utils
from .widgets import ProgressPanel


class ExtractWorker(QThread):
    """Worker thread for extraction operations."""
    
    extraction_complete = pyqtSignal(object)  # payload
    extraction_error = pyqtSignal(str)
    
    def __init__(self, image, image_path, password):
        super().__init__()
        self.image = image
        self.image_path = image_path
        self.password = password
        self.payload = None
        
    def run(self):
        """Run extraction in worker thread."""
        try:
            # Determine embedding method based on format
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

            # Extract
            self.payload = embedding.extract(self.password)
            
            # Signal success
            self.extraction_complete.emit(self.payload)

        except ValueError as e:
            error_msg = f"ValueError: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            self.extraction_error.emit(error_msg)
        except Exception as e:
            error_msg = f"Exception: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            self.extraction_error.emit(error_msg)


class ExtractTab(QWidget):
    """Extract tab widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None
        self.image_path = None
        self.extracted_blocks = None
        self.extract_worker = None
        self.init_ui()
        self.setAcceptDrops(True)

    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Image selection section
        image_group = QGroupBox("1. Select Embedded Image")
        image_layout = QVBoxLayout()

        image_button_layout = QHBoxLayout()
        self.image_button = QPushButton("📁 Select Image File")
        self.image_button.setToolTip("Choose an image file that contains embedded data")
        self.image_button.clicked.connect(self.select_image)
        image_button_layout.addWidget(self.image_button)

        self.image_label = QLabel("No image selected")
        self.image_label.setStyleSheet("color: #999;")
        image_button_layout.addWidget(self.image_label)
        image_button_layout.addStretch()

        image_layout.addLayout(image_button_layout)
        image_group.setLayout(image_layout)
        layout.addWidget(image_group)

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

        # Password section
        crypto_group = QGroupBox("2. Decryption")
        crypto_layout = QHBoxLayout()

        crypto_layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Optional - leave blank if not encrypted")
        self.password_input.setToolTip("Enter the password used during embedding if the data was encrypted")
        crypto_layout.addWidget(self.password_input)

        crypto_group.setLayout(crypto_layout)
        scroll_layout.addWidget(crypto_group)

        # Extraction section
        extract_group = QGroupBox("3. Extract")
        extract_layout = QVBoxLayout()

        button_layout = QHBoxLayout()
        self.extract_button = QPushButton("🔓 Extract & Decode")
        self.extract_button.setProperty("class", "primary")
        self.extract_button.setToolTip("Extract and decode any hidden data from the selected image")
        self.extract_button.clicked.connect(self.start_extraction)
        button_layout.addWidget(self.extract_button)

        button_layout.addStretch()
        extract_layout.addLayout(button_layout)

        # Progress panel
        self.progress_panel = ProgressPanel()
        extract_layout.addWidget(self.progress_panel)

        extract_group.setLayout(extract_layout)
        scroll_layout.addWidget(extract_group)

        # Content preview section
        content_group = QGroupBox("4. Extracted Content")
        content_layout = QVBoxLayout()

        # Messages
        msg_label = QLabel("Messages:")
        msg_label.setStyleSheet("font-weight: bold;")
        content_layout.addWidget(msg_label)

        self.message_display = QTextEdit()
        self.message_display.setReadOnly(True)
        self.message_display.setMinimumHeight(80)
        self.message_display.setMaximumHeight(150)
        self.message_display.setPlaceholderText("No messages extracted")
        content_layout.addWidget(self.message_display)

        # Files
        file_label = QLabel("Files:")
        file_label.setStyleSheet("font-weight: bold;")
        content_layout.addWidget(file_label)

        self.file_display = QTextEdit()
        self.file_display.setReadOnly(True)
        self.file_display.setMinimumHeight(80)
        self.file_display.setMaximumHeight(150)
        self.file_display.setPlaceholderText("No files extracted")
        content_layout.addWidget(self.file_display)

        # Save files button
        save_layout = QHBoxLayout()
        self.save_files_button = QPushButton("💾 Save Extracted Files")
        self.save_files_button.clicked.connect(self.save_extracted_files)
        self.save_files_button.setEnabled(False)
        save_layout.addWidget(self.save_files_button)
        save_layout.addStretch()
        content_layout.addLayout(save_layout)

        content_group.setLayout(content_layout)
        scroll_layout.addWidget(content_group)

        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)

        layout.addWidget(scroll_area)
        self.setLayout(layout)

    def select_image(self):
        """Select image file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Embedded Image", "",
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
            self.image_label.setText(os.path.basename(file_path))
            self.image_label.setStyleSheet("color: #000; font-weight: bold;")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")

    def start_extraction(self):
        """Start extraction operation."""
        if not self.image or not self.image_path:
            QMessageBox.warning(self, "No Image", "Please select an image first")
            return

        # Disable buttons
        self.extract_button.setEnabled(False)
        self.progress_panel.reset()
        self.progress_panel.set_status("Extracting...")

        # Create and start worker thread
        self.extract_worker = ExtractWorker(
            self.image,
            self.image_path,
            self.password_input.text()
        )
        
        # Connect signals
        self.extract_worker.extraction_complete.connect(self._on_extraction_complete)
        self.extract_worker.extraction_error.connect(self._on_extraction_error)
        
        # Start worker
        self.extract_worker.start()

    def _on_extraction_complete(self, payload):
        """Handle successful extraction completion."""
        self.progress_panel.set_progress(50, 100)
        self.display_extracted_content(payload)
        self.extracted_blocks = payload._extracted_blocks
        self.save_files_button.setEnabled(True)
        self.progress_panel.set_complete()
        self.extract_button.setEnabled(True)

    def _on_extraction_error(self, error_message: str):
        """Handle extraction error."""
        self.progress_panel.set_error(error_message)
        self.extract_button.setEnabled(True)
        
        # Determine if it's a decryption error
        if "decryption" in error_message.lower() or "password" in error_message.lower():
            QMessageBox.critical(self, "Extraction Failed", f"Error: {error_message}")
        else:
            QMessageBox.critical(self, "Error", f"Extraction failed: {error_message}")

    def display_extracted_content(self, payload):
        """Display extracted content in UI."""
        if not hasattr(payload, '_extracted_blocks'):
            return

        messages = []
        files_info = []

        for block_type, content in payload._extracted_blocks:
            if block_type == "message":
                messages.append(content)
            elif block_type == "file":
                filename, file_data = content
                files_info.append((filename, len(file_data)))

        # Display messages
        if messages:
            self.message_display.setPlainText("\n---\n".join(messages))
        else:
            self.message_display.setPlainText("No messages")

        # Display files
        if files_info:
            files_text = "\n".join(f"{name} ({size} bytes)" for name, size in files_info)
            self.file_display.setPlainText(files_text)
        else:
            self.file_display.setPlainText("No files")

    def save_extracted_files(self):
        """Save extracted files to directory."""
        if not self.extracted_blocks:
            QMessageBox.warning(self, "No Files", "No extracted files to save")
            return

        output_dir = QFileDialog.getExistingDirectory(self, "Select Directory to Save Files")
        if not output_dir:
            return

        try:
            saved_count = 0
            for block_type, content in self.extracted_blocks:
                if block_type == "file":
                    filename, file_data = content
                    output_path = os.path.join(output_dir, filename)

                    # Create subdirectories if needed
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)

                    # Write file
                    with open(output_path, "wb") as f:
                        f.write(file_data)
                    saved_count += 1

            QMessageBox.information(
                self, "Success",
                f"Saved {saved_count} file(s) to:\n{output_dir}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save files: {str(e)}")

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
