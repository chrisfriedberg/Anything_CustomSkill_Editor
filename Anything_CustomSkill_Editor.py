# Anything_CustomSkillEditor
# PySide6 GUI App for Managing Custom Skills in AnythingLLM

import sys
import os
import json
import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
                               QMenuBar, QMenu, QFileDialog, QDialog, QTextEdit, QLineEdit, QFormLayout,
                               QCheckBox, QComboBox, QMessageBox, QToolBar, QStatusBar)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QFont

class NavButton(QPushButton):
    """Navigation button class with glossy, pill-shaped black styling and sizing"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumSize(120, 35)  # Standard minimum size
        self.setFont(QFont("Segoe UI", 10, QFont.Bold))  # Standard bold font
        self.setStyleSheet("""
            QPushButton {
                color: white;
                font-weight: bold;
                border: 2px solid #222;
                border-radius: 18px;
                padding: 8px 30px;
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #444444, stop:0.5 #222222, stop:1 #000000
                );
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #666666, stop:0.5 #333333, stop:1 #111111
                );
            }
            QPushButton:pressed {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #222222, stop:1 #000000
                );
            }
            QPushButton:disabled {
                background: #222222;
                color: #bbbbbb;
                border: 2px solid #444444;
            }
        """)

class MenuBarButton(QPushButton):
    """Menu bar button with rectangular styling and less-rounded corners"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumSize(100, 32)
        self.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.setStyleSheet("""
            QPushButton {
                color: white;
                font-weight: bold;
                border: 1.5px solid #222;
                border-radius: 6px;
                padding: 6px 18px;
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #444, stop:1 #222
                );
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #666, stop:1 #333
                );
            }
            QPushButton:pressed {
                background: #222;
            }
            QPushButton:disabled {
                background: #333;
                color: #bbb;
                border: 1.5px solid #444;
            }
        """)

LOG_DIR = os.path.expanduser("~/Documents/AnythingCustomSkillLogs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE_STANDARD = os.path.join(LOG_DIR, "custom_skill_log_standard.txt")
LOG_FILE_VERBOSE = os.path.join(LOG_DIR, "custom_skill_log_verbose.txt")

REQUIRED_FIELDS = {
    "name": "The user-friendly name of the skill.",
    "hubId": "Internal skill ID. Must match folder name.",
    "description": "Short summary of what the skill does.",
    "entrypoint_file": "Name of the JS file with the handler (usually 'handler.js').",
    "entrypoint_params": "Inputs expected by the skill (name, type, description).",
    "output_description": "What the skill will return. Must be a string.",
    "version": "Version of the skill, e.g., '1.0.0'.",
    "schema": "Must always be 'skill-1.0.0'."
}

class ConfigDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Default Configuration")
        self.resize(400, 600)  # Increased height for better usability
        self.layout = QFormLayout()

        self.fields = {}
        self.checkboxes = {}

        for key, description in REQUIRED_FIELDS.items():
            cb = QCheckBox(f"Lock '{key}' (default)")
            cb.setChecked(True)
            le = QLineEdit()
            le.setReadOnly(True)
            le.setPlaceholderText(description)
            self.checkboxes[key] = cb
            self.fields[key] = le
            cb.stateChanged.connect(lambda state, k=key: self.toggle_field_edit(k, state))
            self.layout.addRow(cb)
            self.layout.addRow(le)

        # Button layout for Save and Cancel
        btn_layout = QHBoxLayout()
        save_btn = NavButton("Save")
        save_btn.clicked.connect(self.save_config)
        cancel_btn = NavButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        self.layout.addRow(btn_layout)
        self.setLayout(self.layout)

    def toggle_field_edit(self, key, state):
        self.fields[key].setReadOnly(state == Qt.Checked)

    def save_config(self):
        config = {key: self.fields[key].text() for key in self.fields}
        log_standard(f"Config saved: {json.dumps(config)}")
        QMessageBox.information(self, "Saved", "Configuration saved.")
        self.accept()


class SkillEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Anything Custom Skill Editor")
        self.setMinimumSize(800, 600)

        self.init_ui()

    def init_ui(self):
        # Tool Bar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        tools_menu_btn = MenuBarButton("Tools")
        tools_menu_btn.clicked.connect(self.open_tools_menu)
        toolbar.addWidget(tools_menu_btn)

        # Nav Buttons
        nav_layout = QHBoxLayout()
        for label in ["Add New", "Modify Skill", "Delete Skill", "Open Skills Directory"]:
            btn = NavButton(label)
            btn.clicked.connect(self.placeholder_popup)
            nav_layout.addWidget(btn)

        nav_widget = QWidget()
        nav_widget.setLayout(nav_layout)

        # Main Layout
        layout = QVBoxLayout()
        layout.addWidget(nav_widget)

        info = QLabel("Use the Tools menu to configure skill settings. Nav buttons will trigger skill editors.")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)

        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        # Status Bar
        self.setStatusBar(QStatusBar())

    def open_tools_menu(self):
        dialog = ConfigDialog()
        dialog.exec()

    def placeholder_popup(self):
        QMessageBox.information(self, "Coming Soon", "This function is not yet implemented.")


def log_standard(message):
    with open(LOG_FILE_STANDARD, "a") as f:
        f.write(f"[{datetime.datetime.now()}] {message}\n")

def log_verbose(message):
    with open(LOG_FILE_VERBOSE, "a") as f:
        f.write(f"[{datetime.datetime.now()}] {message}\n")

def main():
    app = QApplication(sys.argv)
    window = SkillEditor()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
