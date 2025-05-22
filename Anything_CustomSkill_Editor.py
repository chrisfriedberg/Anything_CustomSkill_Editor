# Anything_CustomSkillEditor
# PySide6 GUI App for Managing Custom Skills in AnythingLLM

import sys
import os
import json
import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
                               QMenuBar, QMenu, QFileDialog, QDialog, QTextEdit, QLineEdit, QFormLayout,
                               QCheckBox, QComboBox, QMessageBox, QToolBar, QStatusBar, QDockWidget, QTabWidget)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QFont

APP_CONFIG_FILE = "Anything_CustomSkill_Config.json"

APP_CONFIG_DEFAULTS = {
    "log_level": "Standard",  # "Standard" or "Verbose"
    "default_skill_output_path": os.path.join(
        os.environ["APPDATA"], "AnythingLLM", "plugins", "agent-skills"
    ),
    "lock_fields_by_default": True,
    "show_field_tooltips": True,
    "allow_skill_overwrite": False
}

REVERSE_TEXT_SKILL_DEFAULTS = {
    "name": "Reverse Text",
    "hubId": "reverse-text",
    "description": "Takes a string input and returns the reversed version.",
    "entrypoint_file": "handler.js",
    "entrypoint_params": '{ "text": { "description": "The text to reverse.", "type": "string" } }',
    "output_description": "Returns the reversed string.",
    "version": "1.0.0",
    "schema": "skill-1.0.0"
}

REVERSE_TEXT_SKILL_TOOLTIPS = {
    "name": "Human-friendly name for the skill. This is what will show in the interface.",
    "hubId": "Internal skill ID. Must match the folder name exactly.",
    "description": "Short description of what the skill does. Used by the LLM to decide when to call it.",
    "entrypoint_file": "Name of the JavaScript file to execute (usually 'handler.js').",
    "entrypoint_params": "JSON object defining what inputs the skill accepts (names, types, descriptions).",
    "output_description": "What the skill returns. This must always be a string.",
    "version": "Version number for the skill, e.g., '1.0.0'.",
    "schema": "Must always be 'skill-1.0.0'. Required by AnythingLLM."
}

def load_app_config():
    if os.path.exists(APP_CONFIG_FILE):
        try:
            with open(APP_CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            log_standard(f"Failed to load config: {e}")
    return APP_CONFIG_DEFAULTS.copy()

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
        self.setWindowTitle("App Configuration")
        self.resize(400, 350)
        self.layout = QFormLayout()

        # log_level dropdown
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["Standard", "Verbose"])
        self.log_level_combo.setCurrentText(APP_CONFIG_DEFAULTS["log_level"])
        self.layout.addRow("Log Level:", self.log_level_combo)

        # default_skill_output_path with browse
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit(APP_CONFIG_DEFAULTS["default_skill_output_path"])
        browse_btn = MenuBarButton("Browse")
        browse_btn.clicked.connect(self.browse_path)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_btn)
        path_widget = QWidget()
        path_widget.setLayout(path_layout)
        self.layout.addRow("Default Skill Output Path:", path_widget)

        # lock_fields_by_default
        self.lock_fields_cb = QCheckBox("Lock fields by default")
        self.lock_fields_cb.setChecked(APP_CONFIG_DEFAULTS["lock_fields_by_default"])
        self.layout.addRow(self.lock_fields_cb)

        # show_field_tooltips
        self.tooltips_cb = QCheckBox("Show field tooltips")
        self.tooltips_cb.setChecked(APP_CONFIG_DEFAULTS["show_field_tooltips"])
        self.layout.addRow(self.tooltips_cb)

        # allow_skill_overwrite
        self.overwrite_cb = QCheckBox("Allow skill overwrite")
        self.overwrite_cb.setChecked(APP_CONFIG_DEFAULTS["allow_skill_overwrite"])
        self.layout.addRow(self.overwrite_cb)

        # Save/Cancel buttons
        btn_layout = QHBoxLayout()
        save_btn = MenuBarButton("Save")
        save_btn.clicked.connect(self.save_config)
        cancel_btn = MenuBarButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                color: white;
                font-weight: bold;
                border: 1.5px solid #a00;
                border-radius: 6px;
                padding: 6px 18px;
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff4444, stop:1 #a00000
                );
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff6666, stop:1 #c00000
                );
            }
            QPushButton:pressed {
                background: #a00000;
            }
            QPushButton:disabled {
                background: #a00000;
                color: #bbbbbb;
                border: 1.5px solid #a00000;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        self.layout.addRow(btn_layout)
        self.setLayout(self.layout)

    def browse_path(self):
        # Expand environment variables and ensure the directory exists
        default_path = os.path.expandvars(APP_CONFIG_DEFAULTS["default_skill_output_path"])
        default_path = os.path.abspath(default_path)
        if not os.path.exists(default_path):
            os.makedirs(default_path)
        path = QFileDialog.getExistingDirectory(self, "Select Skill Output Directory", default_path)
        if path:
            self.path_edit.setText(path)

    def save_config(self):
        config = {
            "log_level": self.log_level_combo.currentText(),
            "default_skill_output_path": self.path_edit.text().strip(),
            "lock_fields_by_default": self.lock_fields_cb.isChecked(),
            "show_field_tooltips": self.tooltips_cb.isChecked(),
            "allow_skill_overwrite": self.overwrite_cb.isChecked()
        }
        errors = []
        if not config["default_skill_output_path"]:
            errors.append("The field 'default_skill_output_path' cannot be empty.")

        if errors:
            QMessageBox.critical(self, "Validation Error", "\n".join(errors))
            return

        try:
            with open(APP_CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=2)
            log_standard(f"Config saved: {json.dumps(config)}")
            QMessageBox.information(self, "Saved", "Configuration saved to disk.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "File Error", f"Failed to save configuration.\n{str(e)}")


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

        # Nav Buttons (centered)
        nav_layout = QHBoxLayout()
        for label in ["Add New", "Modify Skill", "Delete Skill", "Load Existing Skills"]:
            btn = NavButton(label)
            btn.clicked.connect(self.placeholder_popup)
            nav_layout.addWidget(btn)

        nav_widget = QWidget()
        nav_widget.setLayout(nav_layout)

        # Centering layout for nav buttons
        center_layout = QVBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(nav_widget, alignment=Qt.AlignHCenter)

        # Skill folders dropdown
        self.skill_dropdown = QComboBox()
        self.skill_dropdown.setFixedWidth(320)  # 4x typical default width (80px)
        self.populate_skill_dropdown()
        dropdown_widget = QWidget()
        dropdown_layout = QHBoxLayout()
        dropdown_layout.addStretch()
        dropdown_layout.addWidget(self.skill_dropdown)
        dropdown_layout.addStretch()
        dropdown_widget.setLayout(dropdown_layout)
        center_layout.addWidget(dropdown_widget)

        center_layout.addStretch()

        # Info label
        info = QLabel("Use the Tools menu to configure skill settings. Nav buttons will trigger skill editors.")
        info.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(info)

        # Main layout (vertical): center area + close button at bottom
        main_layout = QVBoxLayout()
        main_layout.addLayout(center_layout)

        # Close button layout (lower right)
        close_btn_layout = QHBoxLayout()
        close_btn_layout.addStretch()
        close_btn = MenuBarButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                color: white;
                font-weight: bold;
                border: 1.5px solid #a00;
                border-radius: 6px;
                padding: 6px 18px;
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff4444, stop:1 #a00000
                );
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff6666, stop:1 #c00000
                );
            }
            QPushButton:pressed {
                background: #a00000;
            }
            QPushButton:disabled {
                background: #a00000;
                color: #bbbbbb;
                border: 1.5px solid #a00000;
            }
        """)
        close_btn.clicked.connect(self.close)
        close_btn_layout.addWidget(close_btn)
        main_layout.addLayout(close_btn_layout)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Status Bar
        self.setStatusBar(QStatusBar())

    def populate_skill_dropdown(self):
        self.skill_dropdown.clear()
        # Add placeholder item
        self.skill_dropdown.addItem("Current Skill Subdirectories")
        config = load_app_config()
        skills_dir = config.get("default_skill_output_path", "")
        if os.path.isdir(skills_dir):
            subdirs = [name for name in os.listdir(skills_dir)
                       if os.path.isdir(os.path.join(skills_dir, name))]
            for subdir in subdirs:
                self.skill_dropdown.addItem(subdir)

    def open_tools_menu(self):
        dialog = ConfigDialog()
        dialog.exec()

    def placeholder_popup(self):
        sender = self.sender()
        if sender.text() == "Add New":
            dialog = AddSkillDialog(self)
            dialog.exec()
        else:
            QMessageBox.information(self, "Coming Soon", "This function is not yet implemented.")


class AddSkillDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Skill")
        self.setMinimumWidth(500)

        self.config = load_app_config()
        self.layout = QVBoxLayout()
        self.form_layout = QFormLayout()
        self.fields = {}

        for key in REQUIRED_FIELDS:
            row_layout = QHBoxLayout()
            le = QLineEdit()
            le.setPlaceholderText(REQUIRED_FIELDS[key])
            le.setText(REVERSE_TEXT_SKILL_DEFAULTS.get(key, ""))
            # Add extra tooltip for entrypoint_file
            if key == "entrypoint_file":
                extra_tip = "This file must live inside the same folder as plugin.json. Each skill has its own handler.js."
                le.setToolTip(REVERSE_TEXT_SKILL_TOOLTIPS.get(key, "") + "\n" + extra_tip)
            else:
                le.setToolTip(REVERSE_TEXT_SKILL_TOOLTIPS.get(key, ""))
            self.fields[key] = le
            row_layout.addWidget(le)
            # Info button
            info_btn = QPushButton("ℹ️")
            info_btn.setFixedWidth(28)
            # Add extra tooltip for entrypoint_file info button
            if key == "entrypoint_file":
                info_btn.setToolTip(REVERSE_TEXT_SKILL_TOOLTIPS.get(key, "") + "\n" + extra_tip)
            else:
                info_btn.setToolTip(REVERSE_TEXT_SKILL_TOOLTIPS.get(key, ""))
            info_btn.clicked.connect(lambda _, k=key: self.show_info(k))
            row_layout.addWidget(info_btn)
            self.form_layout.addRow(f"{key}:", row_layout)

        self.layout.addLayout(self.form_layout)

        # Preview/Clear Form buttons (upper left above preview)
        upper_btn_layout = QHBoxLayout()
        preview_btn = MenuBarButton("Preview")
        preview_btn.setToolTip("This file must live inside the same folder as plugin.json. Each skill has its own handler.js.")
        preview_btn.clicked.connect(self.preview_skill)
        clear_btn = MenuBarButton("Clear Form")
        clear_btn.setStyleSheet("""
            QPushButton {
                color: white;
                font-weight: bold;
                border: 1.5px solid #0057b8;
                border-radius: 6px;
                padding: 6px 18px;
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3399ff, stop:1 #0057b8
                );
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #66b3ff, stop:1 #0073e6
                );
            }
            QPushButton:pressed {
                background: #0057b8;
            }
            QPushButton:disabled {
                background: #0057b8;
                color: #bbbbbb;
                border: 1.5px solid #0057b8;
            }
        """)
        clear_btn.clicked.connect(self.clear_form)
        upper_btn_layout.addWidget(preview_btn)
        upper_btn_layout.addWidget(clear_btn)
        upper_btn_layout.addStretch()
        self.layout.addLayout(upper_btn_layout)

        # Preview area
        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        self.preview_area.setPlaceholderText("Preview of plugin.json will appear here...")
        self.layout.addWidget(self.preview_area)

        # Create/Cancel buttons (below preview)
        lower_btn_layout = QHBoxLayout()
        create_btn = MenuBarButton("Create")
        create_btn.setStyleSheet("""
            QPushButton {
                color: white;
                font-weight: bold;
                border: 1.5px solid #0a0;
                border-radius: 6px;
                padding: 6px 18px;
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #44ff44, stop:1 #008800
                );
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #66ff66, stop:1 #00bb00
                );
            }
            QPushButton:pressed {
                background: #008800;
            }
            QPushButton:disabled {
                background: #008800;
                color: #bbbbbb;
                border: 1.5px solid #008800;
            }
        """)
        create_btn.clicked.connect(self.confirm_create)
        cancel_btn = MenuBarButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                color: white;
                font-weight: bold;
                border: 1.5px solid #a00;
                border-radius: 6px;
                padding: 6px 18px;
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff4444, stop:1 #a00000
                );
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff6666, stop:1 #c00000
                );
            }
            QPushButton:pressed {
                background: #a00000;
            }
            QPushButton:disabled {
                background: #a00000;
                color: #bbbbbb;
                border: 1.5px solid #a00000;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        lower_btn_layout.addWidget(create_btn)
        lower_btn_layout.addStretch()
        lower_btn_layout.addWidget(cancel_btn)
        self.layout.addLayout(lower_btn_layout)
        self.setLayout(self.layout)

    def show_info(self, key):
        QMessageBox.information(self, f"Info: {key}", REVERSE_TEXT_SKILL_TOOLTIPS.get(key, "No info available."))

    def confirm_create(self):
        reply = QMessageBox.question(self, "Confirm Create", "Are you sure you want to create this skill?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.create_skill()

    def create_skill(self):
        data = {}
        errors = []

        for key, field in self.fields.items():
            val = field.text().strip()
            if not val:
                errors.append(f"'{key}' cannot be empty.")
            data[key] = val

        if errors:
            QMessageBox.critical(self, "Validation Error", "\n".join(errors))
            return

        # Build folder + files
        target_folder = os.path.join(self.config["default_skill_output_path"], data["hubId"])
        if os.path.exists(target_folder):
            if not self.config.get("allow_skill_overwrite", False):
                QMessageBox.critical(self, "Error", f"Skill '{data['hubId']}' already exists.")
                return

        try:
            os.makedirs(target_folder, exist_ok=True)
            with open(os.path.join(target_folder, "plugin.json"), "w") as f:
                json.dump({
                    "active": True,
                    "hubId": data["hubId"],
                    "name": data["name"],
                    "schema": data["schema"],
                    "version": data["version"],
                    "description": data["description"],
                    "entrypoint": {
                        "file": data["entrypoint_file"],
                        "params": data["entrypoint_params"]
                    }
                }, f, indent=2)

            with open(os.path.join(target_folder, data["entrypoint_file"]), "w") as f:
                f.write("// Auto-generated handler.js\n\nmodule.exports.runtime = {\n    handler: async function () {\n        return \"Skill executed successfully.\";\n    }\n};\n")

            log_standard(f"Created skill: {data['hubId']} at {target_folder}")
            QMessageBox.information(self, "Success", f"Skill '{data['hubId']}' created.")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create skill:\n{str(e)}")

    def preview_skill(self):
        data = {key: field.text().strip() for key, field in self.fields.items()}
        try:
            params_obj = json.loads(data["entrypoint_params"])
        except Exception as e:
            params_obj = data["entrypoint_params"]  # fallback to raw string if not valid JSON
        try:
            plugin_json = json.dumps({
                "active": True,
                "hubId": data["hubId"],
                "name": data["name"],
                "schema": data["schema"],
                "version": data["version"],
                "description": data["description"],
                "entrypoint": {
                    "file": data["entrypoint_file"],
                    "params": params_obj
                }
            }, indent=2)
        except Exception as e:
            plugin_json = f"Error generating JSON: {e}"
        self.preview_area.setPlainText(plugin_json)

    def clear_form(self):
        for field in self.fields.values():
            field.clear()


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
