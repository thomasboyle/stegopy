"""
Stylesheet definitions for Stegosuite GUI.

Provides modern, web-inspired styling for the application.
"""

LIGHT_THEME = """
/* Main Window */
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #f8fafc, stop:1 #f1f5f9);
}

/* Base Widget Styling */
QWidget {
    background-color: #ffffff;
    color: #1e293b;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* Modern Card-based Group Boxes */
QGroupBox {
    font-weight: 600;
    font-size: 14px;
    color: #334155;
    border: none;
    border-radius: 12px;
    margin-top: 8px;
    padding: 16px;
    background-color: #ffffff;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    top: -8px;
    padding: 4px 12px;
    background-color: #ffffff;
    color: #475569;
    font-weight: 600;
    font-size: 13px;
}

/* Modern Web-style Buttons */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #ffffff, stop:1 #f8fafc);
    color: #475569;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 10px 16px;
    font-weight: 500;
    font-size: 13px;
    min-height: 20px;
    transition: all 0.2s ease;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #f8fafc, stop:1 #f1f5f9);
    border-color: #cbd5e1;
    color: #334155;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #f1f5f9, stop:1 #e2e8f0);
    transform: translateY(0px);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

QPushButton:disabled {
    background-color: #f1f5f9;
    color: #94a3b8;
    border-color: #e2e8f0;
}

/* Primary Action Button */
QPushButton[class="primary"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #3b82f6, stop:1 #2563eb);
    color: #ffffff;
    border: none;
    font-weight: 600;
}

QPushButton[class="primary"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #2563eb, stop:1 #1d4ed8);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

QPushButton[class="primary"]:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #1d4ed8, stop:1 #1e40af);
}

/* Success Button */
QPushButton[class="success"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #10b981, stop:1 #059669);
    color: #ffffff;
    border: none;
    font-weight: 600;
}

QPushButton[class="success"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #059669, stop:1 #047857);
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

/* Modern Input Fields */
QLineEdit, QTextEdit {
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    padding: 10px 12px;
    background-color: #ffffff;
    font-size: 13px;
    transition: all 0.2s ease;
}

QLineEdit:focus, QTextEdit:focus {
    border: 2px solid #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    outline: none;
}

QLineEdit::placeholder, QTextEdit::placeholder {
    color: #94a3b8;
}

/* Modern Progress Bars */
QProgressBar {
    border: none;
    border-radius: 6px;
    background-color: #f1f5f9;
    text-align: center;
    font-size: 11px;
    font-weight: 500;
    color: #475569;
    min-height: 8px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #10b981, stop:1 #059669);
    border-radius: 6px;
}

/* Enhanced Labels */
QLabel {
    color: #1e293b;
    font-size: 13px;
}

QLabel[class="title"] {
    font-size: 24px;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 8px;
}

QLabel[class="subtitle"] {
    font-size: 14px;
    color: #64748b;
    font-style: italic;
}

QLabel[class="section-title"] {
    font-size: 16px;
    font-weight: 600;
    color: #334155;
    margin-bottom: 8px;
}

/* Modern Tab Widget */
QTabWidget::pane {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    background-color: #ffffff;
    top: -1px;
}

QTabBar::tab {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #f8fafc, stop:1 #f1f5f9);
    color: #64748b;
    padding: 12px 20px;
    border: 1px solid #e2e8f0;
    border-bottom: none;
    border-radius: 8px 8px 0 0;
    margin-right: 4px;
    font-weight: 500;
    font-size: 13px;
    transition: all 0.2s ease;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #e2e8f0;
    border-bottom: 2px solid #3b82f6;
    font-weight: 600;
}

QTabBar::tab:hover {
    background-color: #f1f5f9;
    color: #334155;
}

/* Modern List Widgets */
QListWidget {
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    background-color: #ffffff;
    alternate-background-color: #f8fafc;
    selection-background-color: #dbeafe;
    selection-color: #1e293b;
    font-size: 13px;
}

QListWidget::item {
    padding: 8px 12px;
    border-bottom: 1px solid #f1f5f9;
}

QListWidget::item:selected {
    background-color: #dbeafe;
    color: #1e293b;
}

QListWidget::item:hover {
    background-color: #f1f5f9;
}

/* Scroll Bar Styling */
QScrollBar:vertical {
    background-color: #f1f5f9;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #cbd5e1;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #94a3b8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}
"""

DARK_THEME = """
/* Dark Theme - Modern Web-inspired */

/* Main Window */
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #1e1e1e, stop:1 #0f172a);
}

/* Base Widget Styling */
QWidget {
    background-color: #0f172a;
    color: #f1f5f9;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* Modern Dark Card-based Group Boxes */
QGroupBox {
    font-weight: 600;
    font-size: 14px;
    color: #cbd5e1;
    border: none;
    border-radius: 12px;
    margin-top: 8px;
    padding: 16px;
    background-color: #1e293b;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3), 0 1px 2px rgba(0, 0, 0, 0.2);
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    top: -8px;
    padding: 4px 12px;
    background-color: #1e293b;
    color: #94a3b8;
    font-weight: 600;
    font-size: 13px;
}

/* Modern Dark Web-style Buttons */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #334155, stop:1 #1e293b);
    color: #cbd5e1;
    border: 1px solid #475569;
    border-radius: 8px;
    padding: 10px 16px;
    font-weight: 500;
    font-size: 13px;
    min-height: 20px;
    transition: all 0.2s ease;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #475569, stop:1 #334155);
    border-color: #64748b;
    color: #f1f5f9;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #1e293b, stop:1 #0f172a);
    transform: translateY(0px);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

QPushButton:disabled {
    background-color: #1e293b;
    color: #64748b;
    border-color: #475569;
}

/* Primary Action Button - Dark */
QPushButton[class="primary"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #3b82f6, stop:1 #2563eb);
    color: #ffffff;
    border: none;
    font-weight: 600;
}

QPushButton[class="primary"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #2563eb, stop:1 #1d4ed8);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.5);
}

/* Success Button - Dark */
QPushButton[class="success"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #10b981, stop:1 #059669);
    color: #ffffff;
    border: none;
    font-weight: 600;
}

QPushButton[class="success"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #059669, stop:1 #047857);
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.5);
}

/* Modern Dark Input Fields */
QLineEdit, QTextEdit {
    border: 2px solid #475569;
    border-radius: 8px;
    padding: 10px 12px;
    background-color: #1e293b;
    color: #f1f5f9;
    font-size: 13px;
    transition: all 0.2s ease;
}

QLineEdit:focus, QTextEdit:focus {
    border: 2px solid #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
    outline: none;
}

QLineEdit::placeholder, QTextEdit::placeholder {
    color: #64748b;
}

/* Modern Dark Progress Bars */
QProgressBar {
    border: none;
    border-radius: 6px;
    background-color: #1e293b;
    text-align: center;
    font-size: 11px;
    font-weight: 500;
    color: #cbd5e1;
    min-height: 8px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #10b981, stop:1 #059669);
    border-radius: 6px;
}

/* Enhanced Dark Labels */
QLabel {
    color: #f1f5f9;
    font-size: 13px;
}

QLabel[class="title"] {
    font-size: 24px;
    font-weight: 700;
    color: #f1f5f9;
    margin-bottom: 8px;
}

QLabel[class="subtitle"] {
    font-size: 14px;
    color: #94a3b8;
    font-style: italic;
}

QLabel[class="section-title"] {
    font-size: 16px;
    font-weight: 600;
    color: #cbd5e1;
    margin-bottom: 8px;
}

/* Modern Dark Tab Widget */
QTabWidget::pane {
    border: 1px solid #475569;
    border-radius: 8px;
    background-color: #1e293b;
    top: -1px;
}

QTabBar::tab {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #334155, stop:1 #1e293b);
    color: #94a3b8;
    padding: 12px 20px;
    border: 1px solid #475569;
    border-bottom: none;
    border-radius: 8px 8px 0 0;
    margin-right: 4px;
    font-weight: 500;
    font-size: 13px;
    transition: all 0.2s ease;
}

QTabBar::tab:selected {
    background-color: #1e293b;
    color: #f1f5f9;
    border: 1px solid #475569;
    border-bottom: 2px solid #3b82f6;
    font-weight: 600;
}

QTabBar::tab:hover {
    background-color: #334155;
    color: #cbd5e1;
}

/* Modern Dark List Widgets */
QListWidget {
    border: 2px solid #475569;
    border-radius: 8px;
    background-color: #1e293b;
    alternate-background-color: #334155;
    selection-background-color: #1e40af;
    selection-color: #f1f5f9;
    font-size: 13px;
}

QListWidget::item {
    padding: 8px 12px;
    border-bottom: 1px solid #334155;
}

QListWidget::item:selected {
    background-color: #1e40af;
    color: #f1f5f9;
}

QListWidget::item:hover {
    background-color: #334155;
}

/* Dark Scroll Bar Styling */
QScrollBar:vertical {
    background-color: #1e293b;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #64748b;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #94a3b8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}
"""
