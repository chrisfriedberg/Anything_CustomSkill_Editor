# Anything_CustomSkillEditor
# PySide6 GUI App for Managing Custom Skills in AnythingLLM

import sys
import os
import json
import datetime
import configparser
import time
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
                               QMenuBar, QMenu, QFileDialog, QDialog, QTextEdit, QLineEdit, QFormLayout,
                               QCheckBox, QComboBox, QMessageBox, QToolBar, QStatusBar, QDockWidget, QTabWidget,
                               QListWidget, QListWidgetItem)
from PySide6.QtCore import Qt, QDateTime, QEvent
from PySide6.QtGui import QFont, QIcon

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
        self.setMinimumSize(114, 33)  # Reduced by 5%
        self.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.setStyleSheet("""
            QPushButton {
                color: white;
                font-weight: bold;
                border: 2px solid #222;
                border-radius: 17px;
                padding: 7px 28px;
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
        self.setMinimumSize(90, 28)  # Reduced by 10%
        self.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.setStyleSheet("""
            QPushButton {
                color: white;
                font-weight: bold;
                border: 1.5px solid #222;
                border-radius: 6px;
                padding: 4px 15px;
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

# INI file handling
def load_ini_config():
    config = configparser.ConfigParser(interpolation=None)  # Disable interpolation
    ini_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Anything_CustomSkill_Editor.ini")
    
    # Create default INI if it doesn't exist
    if not os.path.exists(ini_path):
        config['Paths'] = {
            'icon_path': 'icons/app_icon.ico',
            'log_directory': 'Documents/AnythingCustomSkillLogs',
            'config_file': 'Anything_CustomSkill_Config.json'
        }
        config['Appearance'] = {
            'window_title': 'Anything Custom Skill Editor',
            'icon_theme': 'default'
        }
        config['Logging'] = {
            'standard_log': 'custom_skill_log_standard.txt',
            'verbose_log': 'custom_skill_log_verbose.txt',
            'log_level': 'Standard'
        }
        config['SkillDefaults'] = {
            'output_path': '{APPDATA}/AnythingLLM/plugins/agent-skills',
            'lock_fields': 'true',
            'show_tooltips': 'true',
            'allow_overwrite': 'false'
        }
        
        # Create icons directory if it doesn't exist
        icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons')
        if not os.path.exists(icons_dir):
            os.makedirs(icons_dir)
        
        with open(ini_path, 'w') as f:
            config.write(f)
    
    config.read(ini_path)
    return config

def expand_path(path):
    """Expand environment variables in a path string"""
    if '{APPDATA}' in path:
        path = path.replace('{APPDATA}', os.environ.get('APPDATA', ''))
    return path

# Get INI config
INI_CONFIG = load_ini_config()

# Update constants based on INI
APP_CONFIG_FILE = INI_CONFIG['Paths']['config_file']
LOG_DIR = os.path.expanduser(f"~/{INI_CONFIG['Paths']['log_directory']}")
LOG_FILE_STANDARD = os.path.join(LOG_DIR, INI_CONFIG['Logging']['standard_log'])
LOG_FILE_VERBOSE = os.path.join(LOG_DIR, INI_CONFIG['Logging']['verbose_log'])

# Icon handling
def get_app_icon():
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                            INI_CONFIG['Paths']['icon_path'])
    if os.path.exists(icon_path):
        return QIcon(icon_path)
    return None

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
        
        # Set dialog icon if available
        app_icon = get_app_icon()
        if app_icon:
            self.setWindowIcon(app_icon)

        self.layout = QFormLayout()

        # log_level dropdown
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["Standard", "Verbose"])
        self.log_level_combo.setCurrentText(INI_CONFIG['Logging']['log_level'])
        self.layout.addRow("Log Level:", self.log_level_combo)

        # default_skill_output_path with browse
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit(expand_path(INI_CONFIG['SkillDefaults']['output_path']))
        browse_btn = MenuBarButton("Browse")
        browse_btn.clicked.connect(self.browse_path)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_btn)
        path_widget = QWidget()
        path_widget.setLayout(path_layout)
        self.layout.addRow("Default Skill Output Path:", path_widget)

        # lock_fields_by_default
        self.lock_fields_cb = QCheckBox("Lock fields by default")
        self.lock_fields_cb.setChecked(INI_CONFIG['SkillDefaults'].getboolean('lock_fields'))
        self.layout.addRow(self.lock_fields_cb)

        # show_field_tooltips
        self.tooltips_cb = QCheckBox("Show field tooltips")
        self.tooltips_cb.setChecked(INI_CONFIG['SkillDefaults'].getboolean('show_tooltips'))
        self.layout.addRow(self.tooltips_cb)

        # allow_skill_overwrite
        self.overwrite_cb = QCheckBox("Allow skill overwrite")
        self.overwrite_cb.setChecked(INI_CONFIG['SkillDefaults'].getboolean('allow_overwrite'))
        self.layout.addRow(self.overwrite_cb)

        # Log management buttons
        log_btn_layout = QHBoxLayout()
        review_log_btn = MenuBarButton("Review Log")
        review_log_btn.setStyleSheet("""
            QPushButton {
                color: white;
                font-weight: bold;
                border: 1.5px solid #0057b8;
                border-radius: 6px;
                padding: 4px 15px;
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
        review_log_btn.clicked.connect(self.review_log)
        clear_log_btn = MenuBarButton("Clear Log File")
        clear_log_btn.setStyleSheet(review_log_btn.styleSheet())
        clear_log_btn.clicked.connect(self.clear_log)
        backup_log_btn = MenuBarButton("Back Up Log File")
        backup_log_btn.setStyleSheet(review_log_btn.styleSheet())
        backup_log_btn.clicked.connect(self.backup_log)
        log_btn_layout.addWidget(review_log_btn)
        log_btn_layout.addWidget(clear_log_btn)
        log_btn_layout.addWidget(backup_log_btn)
        self.layout.addRow(log_btn_layout)

        # Save/Cancel buttons (moved to bottom)
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
                padding: 4px 15px;
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
        default_path = os.path.expandvars(INI_CONFIG['SkillDefaults']['output_path'])
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
            # Update INI config
            INI_CONFIG['Logging']['log_level'] = config['log_level']
            INI_CONFIG['SkillDefaults']['output_path'] = config['default_skill_output_path']
            INI_CONFIG['SkillDefaults']['lock_fields'] = str(config['lock_fields_by_default']).lower()
            INI_CONFIG['SkillDefaults']['show_tooltips'] = str(config['show_field_tooltips']).lower()
            INI_CONFIG['SkillDefaults']['allow_overwrite'] = str(config['allow_skill_overwrite']).lower()
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                 "Anything_CustomSkill_Editor.ini"), 'w') as f:
                INI_CONFIG.write(f)

            # Update JSON config
            with open(APP_CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=2)
            
            log_standard(f"Config saved: {json.dumps(config)}")
            QMessageBox.information(self, "Saved", "Configuration saved to disk.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "File Error", f"Failed to save configuration.\n{str(e)}")

    def review_log(self):
        config = load_app_config()
        log_level = config.get("log_level", "Standard")
        log_file = LOG_FILE_STANDARD if log_level == "Standard" else LOG_FILE_VERBOSE
        try:
            if not os.path.exists(log_file):
                QMessageBox.information(self, "Log Not Found", "No log file found.")
                return
            os.startfile(log_file)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open log file:\n{e}")

    def clear_log(self):
        try:
            with open(LOG_FILE_STANDARD, "w") as f:
                f.write("")
            QMessageBox.information(self, "Log Cleared", "Log file has been cleared.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not clear log file:\n{e}")

    def backup_log(self):
        try:
            if not os.path.exists(LOG_FILE_STANDARD):
                QMessageBox.information(self, "Log Not Found", "No log file found.")
                return
            import shutil
            import datetime
            downloads = os.path.join(os.path.expanduser("~"), "Downloads")
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"custom_skill_log_standard_{timestamp}.txt"
            backup_path = os.path.join(downloads, backup_name)
            shutil.copy(LOG_FILE_STANDARD, backup_path)
            QMessageBox.information(self, "Log Backed Up", f"Log file backed up to:\n{backup_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not back up log file:\n{e}")

class SkillEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(INI_CONFIG['Appearance']['window_title'])
        self.setMinimumSize(800, 600)
        
        # Set application icon
        app_icon = get_app_icon()
        if app_icon:
            self.setWindowIcon(app_icon)
            QApplication.setWindowIcon(app_icon)

        self.add_btn = None  # Reference to Add New button
        self.modify_btn = None
        self.delete_btn = None
        self.skill_loaded_label = None  # Indicator label
        self.init_ui()
        # Log app start
        config = load_app_config()
        if config.get("log_level", "Standard") == "Verbose":
            log_verbose("App started", action="App Start")

    def init_ui(self):
        # Tool Bar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        tools_menu_btn = MenuBarButton("Tools")
        tools_menu_btn.clicked.connect(self.open_tools_menu)
        toolbar.addWidget(tools_menu_btn)

        # Nav Buttons (centered)
        nav_layout = QHBoxLayout()
        for label in ["Add New", "Modify Skill", "Delete Skill"]:
            btn = NavButton(label)
            btn.clicked.connect(self.placeholder_popup)
            nav_layout.addWidget(btn)
            if label == "Add New":
                self.add_btn = btn
            if label == "Modify Skill":
                self.modify_btn = btn
            if label == "Delete Skill":
                self.delete_btn = btn
        nav_widget = QWidget()
        nav_widget.setLayout(nav_layout)

        # Centering layout for nav buttons
        center_layout = QVBoxLayout()
        center_layout.addStretch()
        # Skill loaded label (hidden by default)
        self.skill_loaded_label = QLabel("Skill Loaded")
        self.skill_loaded_label.setAlignment(Qt.AlignCenter)
        self.skill_loaded_label.setStyleSheet("font-size: 48px; color: #1ec41e; font-weight: bold;")
        self.skill_loaded_label.setVisible(False)
        center_layout.addWidget(self.skill_loaded_label)
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

        self.skill_dropdown.currentIndexChanged.connect(self.on_skill_selected)
        # Log UI init
        config = load_app_config()
        if config.get("log_level", "Standard") == "Verbose":
            log_verbose("Main window UI initialized", action="UI Init")

        # Ensure correct initial button states
        if self.modify_btn:
            self.modify_btn.setEnabled(False)
        if self.delete_btn:
            self.delete_btn.setEnabled(False)
        if self.add_btn:
            self.add_btn.setEnabled(True)

    def populate_skill_dropdown(self):
        self.skill_dropdown.clear()
        # Add placeholder item
        self.skill_dropdown.addItem("Load Existing Skill")
        config = load_app_config()
        skills_dir = config.get("default_skill_output_path", "")
        valid_subdirs = []
        descriptions = {}
        if os.path.isdir(skills_dir):
            for name in os.listdir(skills_dir):
                subdir_path = os.path.join(skills_dir, name)
                if os.path.isdir(subdir_path):
                    plugin_json = os.path.join(subdir_path, "plugin.json")
                    handler_js = os.path.join(subdir_path, "handler.js")
                    if os.path.isfile(plugin_json) and os.path.isfile(handler_js):
                        try:
                            # Validate plugin.json is valid JSON
                            with open(plugin_json, "r", encoding="utf-8") as f:
                                pdata = json.load(f)
                                # Validate required fields
                                if all(key in pdata for key in ["name", "hubId", "description", "version", "schema"]):
                                    valid_subdirs.append(name)
                                    desc = pdata.get("description", "")
                                    descriptions[name] = desc
                        except Exception:
                            continue
        for subdir in sorted(valid_subdirs, key=lambda s: s.lower()):
            self.skill_dropdown.addItem(subdir)
            idx = self.skill_dropdown.findText(subdir)
            if idx >= 0:
                self.skill_dropdown.setItemData(idx, descriptions.get(subdir, ""), Qt.ToolTipRole)

    def open_tools_menu(self):
        config = load_app_config()
        if config.get("log_level", "Standard") == "Verbose":
            log_verbose("Tools menu opened", action="Menu Open")
        self.tools_menu = QMenu()
        self.tools_menu.addAction("Review Log", self.review_log)
        self.tools_menu.addAction("Clear Log File", self.clear_log)
        self.tools_menu.addAction("Back Up Log File", self.backup_log)
        self.tools_menu.addSeparator()
        self.tools_menu.addAction("Change Icon", self.open_icon_dialog)
        self.tools_menu.addSeparator()
        self.tools_menu.addAction("Configuration", self.open_config_dialog)
        self.tools_menu.exec(self.sender().mapToGlobal(self.sender().rect().bottomLeft()))

    def placeholder_popup(self):
        sender = self.sender()
        config = load_app_config()
        if config.get("log_level", "Standard") == "Verbose":
            log_verbose(f"Button clicked: {sender.text()}", action="Button Click")
        if sender.text() == "Add New":
            if config.get("log_level", "Standard") == "Verbose":
                log_verbose("AddSkillDialog opened", action="Dialog Open")
            dialog = AddSkillDialog(self)
            dialog.exec()
            # After adding, repopulate dropdown and hide loaded label
            self.populate_skill_dropdown()
            self.show_skill_loaded(False)
        elif sender.text() == "Modify Skill":
            if config.get("log_level", "Standard") == "Verbose":
                log_verbose("ModifySkillDialog opened", action="Dialog Open", skill_data={"skill": self.skill_dropdown.currentText()})
            dialog = ModifySkillDialog(self.skill_dropdown.currentText(), self)
            if dialog.exec() == QDialog.Accepted:
                self.populate_skill_dropdown()
                self.reset_ui_after_save()
        elif sender.text() == "Delete Skill":
            if config.get("log_level", "Standard") == "Verbose":
                log_verbose("DeleteSkillDialog opened", action="Dialog Open", skill_data={"skill": self.skill_dropdown.currentText()})
            dialog = DeleteSkillDialog(self.skill_dropdown.currentText(), self)
            if dialog.exec() == QDialog.Accepted:
                self.populate_skill_dropdown()
                self.show_skill_loaded(False)
        else:
            QMessageBox.information(self, "Coming Soon", "This function is not yet implemented.")

    def on_skill_selected(self, idx):
        config = load_app_config()
        if config.get("log_level", "Standard") == "Verbose":
            log_verbose(f"Dropdown selection changed: {self.skill_dropdown.currentText()}", action="Dropdown Change")
        # Only trigger if not the placeholder
        if idx > 0:
            skill_name = self.skill_dropdown.currentText()
            config = load_app_config()
            skills_dir = config.get("default_skill_output_path", "")
            skill_folder = os.path.join(skills_dir, skill_name)
            start_time = time.time()
            try:
                dialog = LoadSkillDialog(skill_folder, self)
                result = dialog.exec()
                duration = time.time() - start_time
                if result == QDialog.Accepted:
                    if self.modify_btn:
                        self.modify_btn.setEnabled(True)
                    if self.delete_btn:
                        self.delete_btn.setEnabled(True)
                    # Verbose logging
                    if config.get("log_level", "Standard") == "Verbose":
                        try:
                            with open(os.path.join(skill_folder, "plugin.json"), "r", encoding="utf-8") as f:
                                plugin_data = json.load(f)
                        except Exception as e:
                            plugin_data = {"error": str(e)}
                        log_verbose(
                            message="Skill loaded successfully.",
                            skill_data=plugin_data,
                            action="Skill Load",
                            duration=duration
                        )
                    self.show_skill_loaded(True)
                else:
                    if self.modify_btn:
                        self.modify_btn.setEnabled(False)
                    if self.delete_btn:
                        self.delete_btn.setEnabled(False)
                    self.show_skill_loaded(False)
            except Exception as e:
                duration = time.time() - start_time
                log_verbose(
                    message="Error during skill load.",
                    skill_data={"skill_name": skill_name},
                    action="Skill Load",
                    duration=duration,
                    error=e
                )
                self.show_skill_loaded(False)
        else:
            if self.modify_btn:
                self.modify_btn.setEnabled(False)
            if self.delete_btn:
                self.delete_btn.setEnabled(False)
            self.show_skill_loaded(False)

    def show_skill_loaded(self, show=True):
        if self.skill_loaded_label:
            self.skill_loaded_label.setVisible(show)

    def open_icon_dialog(self):
        dialog = IconDialog(self)
        dialog.exec()

    def review_log(self):
        config = load_app_config()
        log_level = config.get("log_level", "Standard")
        log_file = LOG_FILE_STANDARD if log_level == "Standard" else LOG_FILE_VERBOSE
        try:
            if not os.path.exists(log_file):
                QMessageBox.information(self, "Log Not Found", "No log file found.")
                return
            os.startfile(log_file)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open log file:\n{e}")

    def clear_log(self):
        try:
            with open(LOG_FILE_STANDARD, "w") as f:
                f.write("")
            QMessageBox.information(self, "Log Cleared", "Log file has been cleared.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not clear log file:\n{e}")

    def backup_log(self):
        try:
            if not os.path.exists(LOG_FILE_STANDARD):
                QMessageBox.information(self, "Log Not Found", "No log file found.")
                return
            import shutil
            import datetime
            downloads = os.path.join(os.path.expanduser("~"), "Downloads")
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"custom_skill_log_standard_{timestamp}.txt"
            backup_path = os.path.join(downloads, backup_name)
            shutil.copy(LOG_FILE_STANDARD, backup_path)
            QMessageBox.information(self, "Log Backed Up", f"Log file backed up to:\n{backup_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not back up log file:\n{e}")

    def open_config_dialog(self):
        dialog = ConfigDialog()
        dialog.exec()

    def reset_ui_after_save(self):
        self.show_skill_loaded(False)
        if self.modify_btn:
            self.modify_btn.setEnabled(False)
        if self.delete_btn:
            self.delete_btn.setEnabled(False)
        if self.skill_dropdown:
            self.skill_dropdown.setCurrentIndex(0)

class AddSkillDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Skill")
        self.setMinimumWidth(500)
        
        # Set dialog icon
        app_icon = get_app_icon()
        if app_icon:
            self.setWindowIcon(app_icon)

        # Load config and INI for field locking and tooltips
        config = load_app_config()
        ini_lock = INI_CONFIG['SkillDefaults'].getboolean('lock_fields')
        ini_tooltips = INI_CONFIG['SkillDefaults'].getboolean('show_tooltips')
        allow_overwrite = INI_CONFIG['SkillDefaults'].getboolean('allow_overwrite')
        self.layout = QVBoxLayout()
        self.form_layout = QFormLayout()
        self.fields = {}

        for key in REQUIRED_FIELDS:
            row_layout = QHBoxLayout()
            le = QLineEdit()
            le.setPlaceholderText(REQUIRED_FIELDS[key])
            le.setText(REVERSE_TEXT_SKILL_DEFAULTS.get(key, ""))
            le.setReadOnly(ini_lock)
            # Add extra tooltip for entrypoint_file
            if ini_tooltips:
                if key == "entrypoint_file":
                    extra_tip = "This file must live inside the same folder as plugin.json. Each skill has its own handler.js."
                    le.setToolTip(REVERSE_TEXT_SKILL_TOOLTIPS.get(key, "") + "\n" + extra_tip)
                else:
                    le.setToolTip(REVERSE_TEXT_SKILL_TOOLTIPS.get(key, ""))
            else:
                le.setToolTip("")
            self.fields[key] = le
            row_layout.addWidget(le)
            # Info button
            info_btn = QPushButton("ℹ️")
            info_btn.setFixedWidth(28)
            if ini_tooltips:
                if key == "entrypoint_file":
                    info_btn.setToolTip(REVERSE_TEXT_SKILL_TOOLTIPS.get(key, "") + "\n" + extra_tip)
                else:
                    info_btn.setToolTip(REVERSE_TEXT_SKILL_TOOLTIPS.get(key, ""))
            else:
                info_btn.setToolTip("")
            info_btn.clicked.connect(lambda _, k=key: self.show_info(k))
            row_layout.addWidget(info_btn)
            self.form_layout.addRow(f"{key}:", row_layout)

        self.layout.addLayout(self.form_layout)

        # Preview/Clear Form buttons (upper left above preview)
        upper_btn_layout = QHBoxLayout()
        preview_btn = MenuBarButton("Preview")
        if ini_tooltips:
            preview_btn.setToolTip("This file must live inside the same folder as plugin.json. Each skill has its own handler.js.")
        else:
            preview_btn.setToolTip("")
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
        self.preview_area.setReadOnly(False)
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
        self.allow_skill_overwrite = allow_overwrite

    def show_info(self, key):
        ini_tooltips = INI_CONFIG['SkillDefaults'].getboolean('show_tooltips')
        if ini_tooltips:
            QMessageBox.information(self, f"Info: {key}", REVERSE_TEXT_SKILL_TOOLTIPS.get(key, "No info available."))
        else:
            QMessageBox.information(self, f"Info: {key}", "No info available.")

    def confirm_create(self):
        reply = QMessageBox.question(self, "Confirm Create", "Are you sure you want to create this skill?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.create_skill()

    def create_skill(self):
        config = load_app_config()
        log_level = config.get("log_level", "Standard")
        data = {}
        errors = []
        start_time = datetime.datetime.now()

        # STEP 1: Validate and collect all field values
        for key, field in self.fields.items():
            val = field.text().strip()
            if not val:
                errors.append(f"'{key}' cannot be empty.")
            else:
                data[key] = val
        if errors:
            log_verbose("Validation failed", skill_data=data, action="Validation", 
                       error="\n".join(errors))
            QMessageBox.critical(self, "Validation Error", "\n".join(errors))
            return

        # STEP 2: Build target folder path
        target_folder = os.path.join(config["default_skill_output_path"], data["hubId"])
        log_verbose("Building target folder path", skill_data=data, action="Path Setup")

        # STEP 3: Check for overwrite
        if os.path.exists(target_folder):
            if not self.allow_skill_overwrite:
                log_verbose("Skill already exists", skill_data=data, action="Overwrite Check",
                           error="Skill exists and overwrite not allowed")
                QMessageBox.critical(self, "Error", f"Skill '{data['hubId']}' already exists.")
                return

        try:
            # STEP 4: Create the skill folder
            os.makedirs(target_folder, exist_ok=True)
            log_verbose("Created skill folder", skill_data=data, action="Folder Creation")

            # STEP 5: Parse entrypoint_params as JSON
            try:
                params_json = json.loads(data["entrypoint_params"])
                log_verbose("Parsed entrypoint_params", skill_data=data, action="JSON Parsing")
            except Exception as e:
                log_verbose("Failed to parse entrypoint_params", skill_data=data, 
                           action="JSON Parsing", error=e)
                QMessageBox.critical(self, "Error", f"Invalid entrypoint_params JSON: {e}")
                return

            # STEP 6: Build plugin.json content
            plugin_data = {
                "active": True,
                "hubId": data["hubId"],
                "name": data["name"],
                "schema": data["schema"],
                "version": data["version"],
                "description": data["description"],
                "entrypoint": {
                    "file": data["entrypoint_file"],
                    "params": params_json
                }
            }
            log_verbose("Built plugin.json content", skill_data=plugin_data, action="JSON Building")

            # STEP 7: Write plugin.json
            with open(os.path.join(target_folder, "plugin.json"), "w") as f:
                json.dump(plugin_data, f, indent=2)
            log_verbose("Wrote plugin.json", skill_data=plugin_data, action="File Writing")

            # STEP 8: Get handler code from editable preview
            handler_code = self.preview_area.toPlainText().strip()
            if not handler_code:
                handler_code = """module.exports.runtime = {
    handler: async function (params) {
        const input = params.text || "";
        const reversed = input.split("").reverse().join("");
        return `Reversed: ${reversed}`;
    }
};"""
            log_verbose("Prepared handler code", skill_data={"handler_code": handler_code}, 
                       action="Handler Preparation")

            # STEP 9: Write handler.js
            handler_path = os.path.join(target_folder, data["entrypoint_file"])
            with open(handler_path, "w") as f:
                f.write(handler_code)
            log_verbose("Wrote handler.js", skill_data={"handler_path": handler_path}, 
                       action="Handler Writing")

            # STEP 10: Log and notify success
            duration = (datetime.datetime.now() - start_time).total_seconds()
            log_standard(f"Created skill: {data['hubId']} at {target_folder}")
            log_verbose("Skill creation completed", skill_data=plugin_data, 
                       action="Skill Creation", duration=duration)
            
            QMessageBox.information(self, "Success", f"Skill '{data['hubId']}' created.")
            # Refresh dropdown in main window if present
            if isinstance(self.parent(), SkillEditor):
                self.parent().populate_skill_dropdown()
            self.accept()

        except Exception as e:
            duration = (datetime.datetime.now() - start_time).total_seconds()
            log_verbose("Exception during skill creation", skill_data=data, 
                       action="Skill Creation", duration=duration, error=e)
            QMessageBox.critical(self, "Error", f"Failed to create skill:\n{str(e)}")

    def preview_skill(self):
        data = {key: field.text().strip() for key, field in self.fields.items()}
        try:
            params_obj = json.loads(data["entrypoint_params"])
        except Exception as e:
            params_obj = data["entrypoint_params"]
        try:
            plugin_json = json.dumps({
                "active": True,
                "hubId": data["hubId"],
                "name": data["name"],
                "schema": data["schema"],
                "version": data["version"],
                "description": data["description"],
                "output_description": data["output_description"],
                "entrypoint": {
                    "file": data["entrypoint_file"],
                    "params": params_obj
                }
            }, indent=2)
        except Exception as e:
            plugin_json = f"Error generating JSON: {e}"
        self.preview_area.setPlainText(plugin_json)
        # Enable update button after preview
        self.update_btn.setEnabled(True)
        self.update_btn.setToolTip("")

    def clear_form(self):
        for field in self.fields.values():
            field.clear()

class ModifySkillDialog(QDialog):
    def __init__(self, skill_folder, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modify Skill")
        self.setMinimumWidth(500)
        self.skill_folder = skill_folder
        # Load config and INI for field locking and tooltips
        config = load_app_config()
        ini_lock = INI_CONFIG['SkillDefaults'].getboolean('lock_fields')
        ini_tooltips = INI_CONFIG['SkillDefaults'].getboolean('show_tooltips')
        self.layout = QVBoxLayout()
        self.form_layout = QFormLayout()
        self.fields = {}
        # Load plugin.json
        plugin_json_path = os.path.join(skill_folder, "plugin.json")
        plugin_data = REVERSE_TEXT_SKILL_DEFAULTS.copy()
        if os.path.exists(plugin_json_path):
            try:
                with open(plugin_json_path, "r", encoding="utf-8") as f:
                    plugin_data = json.load(f)
                # Flatten entrypoint fields
                if "entrypoint" in plugin_data:
                    plugin_data["entrypoint_file"] = plugin_data["entrypoint"].get("file", "handler.js")
                    params = plugin_data["entrypoint"].get("params", "")
                    if isinstance(params, dict):
                        plugin_data["entrypoint_params"] = json.dumps(params)
                    else:
                        plugin_data["entrypoint_params"] = str(params)
                # Ensure all required fields are present for display
                for key in REQUIRED_FIELDS:
                    if key not in plugin_data:
                        plugin_data[key] = ""
            except Exception:
                pass
        for key in REQUIRED_FIELDS:
            row_layout = QHBoxLayout()
            le = QLineEdit()
            le.setPlaceholderText(REQUIRED_FIELDS[key])
            le.setText(plugin_data.get(key, ""))
            le.setReadOnly(ini_lock)
            if ini_tooltips:
                if key == "entrypoint_file":
                    extra_tip = "This file must live inside the same folder as plugin.json. Each skill has its own handler.js."
                    le.setToolTip(REVERSE_TEXT_SKILL_TOOLTIPS.get(key, "") + "\n" + extra_tip)
                else:
                    le.setToolTip(REVERSE_TEXT_SKILL_TOOLTIPS.get(key, ""))
            else:
                le.setToolTip("")
            self.fields[key] = le
            row_layout.addWidget(le)
            info_btn = QPushButton("ℹ️")
            info_btn.setFixedWidth(28)
            if ini_tooltips:
                if key == "entrypoint_file":
                    info_btn.setToolTip(REVERSE_TEXT_SKILL_TOOLTIPS.get(key, "") + "\n" + extra_tip)
                else:
                    info_btn.setToolTip(REVERSE_TEXT_SKILL_TOOLTIPS.get(key, ""))
            else:
                info_btn.setToolTip("")
            info_btn.clicked.connect(lambda _, k=key: self.show_info(k))
            row_layout.addWidget(info_btn)
            self.form_layout.addRow(f"{key}:", row_layout)
            # Connect focus event
            le.installEventFilter(self)
        self.layout.addLayout(self.form_layout)
        # Preview/Clear Form buttons (upper left above preview)
        upper_btn_layout = QHBoxLayout()
        preview_btn = MenuBarButton("Preview")
        if ini_tooltips:
            preview_btn.setToolTip("This file must live inside the same folder as plugin.json. Each skill has its own handler.js.")
        else:
            preview_btn.setToolTip("")
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
        self.preview_area.setReadOnly(False)
        self.preview_area.setPlaceholderText("Preview of plugin.json will appear here...")
        self.layout.addWidget(self.preview_area)
        # Update/Cancel buttons (below preview)
        lower_btn_layout = QHBoxLayout()
        self.update_btn = MenuBarButton("Update")
        self.update_btn.setStyleSheet("""
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
        self.update_btn.clicked.connect(self.confirm_update)
        self.update_btn.setEnabled(False)
        self.update_btn.setToolTip("Must view preview first")
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
        lower_btn_layout.addWidget(self.update_btn)
        lower_btn_layout.addStretch()
        lower_btn_layout.addWidget(cancel_btn)
        self.layout.addLayout(lower_btn_layout)
        self.setLayout(self.layout)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.FocusIn:
            if obj in self.fields.values():
                self.update_btn.setEnabled(False)
                self.update_btn.setToolTip("Must view preview first")
                self.preview_area.clear()
        return super().eventFilter(obj, event)

    def show_info(self, key):
        ini_tooltips = INI_CONFIG['SkillDefaults'].getboolean('show_tooltips')
        if ini_tooltips:
            QMessageBox.information(self, f"Info: {key}", REVERSE_TEXT_SKILL_TOOLTIPS.get(key, "No info available."))
        else:
            QMessageBox.information(self, f"Info: {key}", "No info available.")

    def confirm_update(self):
        reply = QMessageBox.question(self, "Confirm Update", "Are you sure you want to update this skill?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.update_skill()

    def update_skill(self):
        # Use the JSON from the preview area
        try:
            plugin_json = json.loads(self.preview_area.toPlainText())
        except Exception as e:
            log_verbose(
                message="Preview JSON is invalid",
                action="Validation",
                error=str(e)
            )
            QMessageBox.critical(self, "Validation Error", f"Preview JSON is invalid: {e}")
            return
        data = plugin_json
        errors = []
        # Validate top-level required fields
        for key in ["name", "hubId", "description", "version", "schema"]:
            if key not in data or not str(data[key]).strip():
                errors.append(f"'{key}' cannot be empty.")
        # Validate entrypoint subfields
        if "entrypoint" not in data or not isinstance(data["entrypoint"], dict):
            errors.append("'entrypoint' must be a dictionary with 'file' and 'params'.")
        else:
            if not data["entrypoint"].get("file", "").strip():
                errors.append("'entrypoint_file' cannot be empty.")
            params = data["entrypoint"].get("params")
            if not params or (isinstance(params, str) and not params.strip()) or (isinstance(params, dict) and not params):
                errors.append("'entrypoint_params' cannot be empty.")
        # Validate output_description (if present at top level)
        if not data.get("output_description", "").strip():
            errors.append("'output_description' cannot be empty.")
        if errors:
            log_verbose(
                message="Validation failed",
                skill_data=data,
                action="Validation",
                error="\n".join(errors)
            )
            QMessageBox.critical(self, "Validation Error", "\n".join(errors))
            return
        # Ensure skill folder exists before writing
        plugin_json_path = os.path.abspath(os.path.join(self.skill_folder, "plugin.json"))
        if not os.path.isdir(self.skill_folder):
            try:
                os.makedirs(self.skill_folder, exist_ok=True)
                log_verbose(
                    message="Skill folder was missing and created automatically.",
                    skill_data=data,
                    action="Update"
                )
            except Exception as e:
                log_verbose(
                    message="Failed to create missing skill folder",
                    skill_data=data,
                    action="Update",
                    error=str(e)
                )
                QMessageBox.critical(self, "Error", f"Could not create skill folder:\n{self.skill_folder}\n{str(e)}")
                return
        # Check if plugin.json exists and is writable
        if os.path.isfile(plugin_json_path) and not os.access(plugin_json_path, os.W_OK):
            log_verbose(
                message="plugin.json exists but is not writable (locked or permission issue)",
                skill_data=data,
                action="Update",
                error=f"File not writable: {plugin_json_path}"
            )
            QMessageBox.critical(self, "Error", f"Cannot write to plugin.json (file may be locked or you lack permissions):\n{plugin_json_path}")
            return
        try:
            with open(plugin_json_path, "w", encoding="utf-8") as f:
                json.dump(plugin_json, f, indent=2)
            QMessageBox.information(self, "Success", f"Skill '{data['hubId']}' updated.")
            self.accept()
            # After dialog accepted, reset main window state
            parent = self.parent()
            if parent and hasattr(parent, 'reset_ui_after_save'):
                parent.reset_ui_after_save()
        except Exception as e:
            log_verbose(
                message="Failed to write plugin.json",
                skill_data=data,
                action="Update",
                error=str(e)
            )
            QMessageBox.critical(self, "Error", f"Failed to update skill:\n{str(e)}")
            # Clear Skill Loaded and disable Modify/Delete in main window
            parent = self.parent()
            if parent and hasattr(parent, 'show_skill_loaded'):
                parent.show_skill_loaded(False)
            if parent and hasattr(parent, 'modify_btn') and parent.modify_btn:
                parent.modify_btn.setEnabled(False)
            if parent and hasattr(parent, 'delete_btn') and parent.delete_btn:
                parent.delete_btn.setEnabled(False)
            return

    def preview_skill(self):
        data = {key: field.text().strip() for key, field in self.fields.items()}
        try:
            params_obj = json.loads(data["entrypoint_params"])
        except Exception as e:
            params_obj = data["entrypoint_params"]
        try:
            plugin_json = json.dumps({
                "active": True,
                "hubId": data["hubId"],
                "name": data["name"],
                "schema": data["schema"],
                "version": data["version"],
                "description": data["description"],
                "output_description": data["output_description"],
                "entrypoint": {
                    "file": data["entrypoint_file"],
                    "params": params_obj
                }
            }, indent=2)
        except Exception as e:
            plugin_json = f"Error generating JSON: {e}"
        self.preview_area.setPlainText(plugin_json)
        # Enable update button after preview
        self.update_btn.setEnabled(True)
        self.update_btn.setToolTip("")

    def clear_form(self):
        for field in self.fields.values():
            field.clear()

class DeleteSkillDialog(QDialog):
    def __init__(self, skill_folder, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delete Skill")
        self.setMinimumWidth(500)
        
        # Set dialog icon
        app_icon = get_app_icon()
        if app_icon:
            self.setWindowIcon(app_icon)

        self.skill_folder = skill_folder
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel(f"Are you sure you want to delete the skill in the folder: {skill_folder}?"))
        # Confirm/Cancel buttons
        btn_layout = QHBoxLayout()
        confirm_btn = MenuBarButton("Confirm")
        confirm_btn.clicked.connect(self.confirm_delete)
        cancel_btn = MenuBarButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(confirm_btn)
        btn_layout.addWidget(cancel_btn)
        self.layout.addLayout(btn_layout)
        self.setLayout(self.layout)

    def confirm_delete(self):
        try:
            shutil.rmtree(self.skill_folder)
            QMessageBox.information(self, "Success", f"Skill in folder '{self.skill_folder}' deleted.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete skill:\n{str(e)}")

class LoadSkillDialog(QDialog):
    def __init__(self, skill_folder, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Load Existing Skill")
        self.setMinimumWidth(500)
        self.skill_folder = skill_folder
        self.layout = QVBoxLayout()
        self.form_layout = QFormLayout()
        # Load plugin.json
        plugin_json_path = os.path.join(skill_folder, "plugin.json")
        plugin_data = REVERSE_TEXT_SKILL_DEFAULTS.copy()
        if os.path.exists(plugin_json_path):
            try:
                with open(plugin_json_path, "r", encoding="utf-8") as f:
                    plugin_data = json.load(f)
                # Flatten entrypoint fields
                if "entrypoint" in plugin_data:
                    plugin_data["entrypoint_file"] = plugin_data["entrypoint"].get("file", "handler.js")
                    params = plugin_data["entrypoint"].get("params", "")
                    if isinstance(params, dict):
                        plugin_data["entrypoint_params"] = json.dumps(params)
                    else:
                        plugin_data["entrypoint_params"] = str(params)
                # Ensure all required fields are present for display
                for key in REQUIRED_FIELDS:
                    if key not in plugin_data:
                        plugin_data[key] = ""
            except Exception:
                pass
        self.fields = {}
        for key in REQUIRED_FIELDS:
            row_layout = QHBoxLayout()
            le = QLineEdit()
            le.setPlaceholderText(REQUIRED_FIELDS[key])
            # Always set the value to the actual data, never just the placeholder
            le.setText(str(plugin_data.get(key, "")))
            le.setReadOnly(True)
            self.fields[key] = le
            row_layout.addWidget(le)
            info_btn = QPushButton("ℹ️")
            info_btn.setFixedWidth(28)
            info_btn.setToolTip("Continue back to main screen to either modify or delete the chosen skill.")
            info_btn.clicked.connect(lambda _, k=key: self.show_info(k))
            row_layout.addWidget(info_btn)
            self.form_layout.addRow(f"{key}:", row_layout)
        self.layout.addLayout(self.form_layout)
        # Preview area
        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        self.preview_area.setPlaceholderText("Preview of plugin.json will appear here...")
        try:
            params_obj = json.loads(plugin_data["entrypoint_params"])
        except Exception as e:
            params_obj = plugin_data["entrypoint_params"]
        try:
            plugin_json = json.dumps({
                "active": True,
                "hubId": plugin_data["hubId"],
                "name": plugin_data["name"],
                "schema": plugin_data["schema"],
                "version": plugin_data["version"],
                "description": plugin_data["description"],
                "output_description": plugin_data["output_description"],
                "entrypoint": {
                    "file": plugin_data["entrypoint_file"],
                    "params": params_obj
                }
            }, indent=2)
        except Exception as e:
            plugin_json = f"Error generating JSON: {e}"
        self.preview_area.setPlainText(plugin_json)
        # Continue Load and Cancel buttons
        btn_layout = QHBoxLayout()
        continue_btn = MenuBarButton("Continue Load")
        continue_btn.setStyleSheet("""
            QPushButton {
                color: white;
                font-weight: bold;
                border: 1.5px solid #0a0;
                border-radius: 6px;
                padding: 4px 15px;
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
        continue_btn.clicked.connect(self.continue_load)
        cancel_btn = MenuBarButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                color: white;
                font-weight: bold;
                border: 1.5px solid #a00;
                border-radius: 6px;
                padding: 4px 15px;
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
        btn_layout.addWidget(continue_btn)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addStretch()
        self.layout.addLayout(btn_layout)
        self.setLayout(self.layout)

    def continue_load(self):
        # Enable Modify/Delete, disable Add in main window
        parent = self.parent()
        config = load_app_config()
        start_time = time.time()
        try:
            if parent and hasattr(parent, 'modify_btn') and hasattr(parent, 'delete_btn'):
                if parent.modify_btn:
                    parent.modify_btn.setEnabled(True)
                if parent.delete_btn:
                    parent.delete_btn.setEnabled(True)
                if hasattr(parent, 'add_btn') and parent.add_btn:
                    parent.add_btn.setEnabled(False)
            # Verbose logging
            if config.get("log_level", "Standard") == "Verbose":
                try:
                    with open(os.path.join(self.skill_folder, "plugin.json"), "r", encoding="utf-8") as f:
                        plugin_data = json.load(f)
                except Exception as e:
                    plugin_data = {"error": str(e)}
                duration = time.time() - start_time
                log_verbose(
                    message="Skill loaded successfully.",
                    skill_data=plugin_data,
                    action="Skill Load",
                    duration=duration
                )
        except Exception as e:
            duration = time.time() - start_time
            log_verbose(
                message="Error during skill load.",
                skill_data={"skill_folder": self.skill_folder},
                action="Skill Load",
                duration=duration,
                error=e
            )
        self.accept()

    def show_info(self, key):
        QMessageBox.information(self, "Info", "Continue back to main screen to either modify or delete the chosen skill.")

class IconDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Change Application Icon")
        self.setMinimumWidth(400)
        
        # Set dialog icon if available
        app_icon = get_app_icon()
        if app_icon:
            self.setWindowIcon(app_icon)

        layout = QVBoxLayout()
        
        # Current icon display
        self.icon_label = QLabel("Current Icon:")
        layout.addWidget(self.icon_label)
        
        # Icon path display
        self.path_edit = QLineEdit(INI_CONFIG['Paths']['icon_path'])
        self.path_edit.setReadOnly(True)
        layout.addWidget(self.path_edit)
        
        # Browse button
        browse_btn = MenuBarButton("Browse Icon")
        browse_btn.clicked.connect(self.browse_icon)
        layout.addWidget(browse_btn)
        
        # Close button
        close_btn = MenuBarButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                color: white;
                font-weight: bold;
                border: 1.5px solid #0057b8;
                border-radius: 6px;
                padding: 5px 17px;
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
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)

    def browse_icon(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Application Icon",
            "",
            "Icon Files (*.ico);;All Files (*.*)"
        )
        if file_path:
            icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons')
            if not os.path.exists(icons_dir):
                os.makedirs(icons_dir)
            icon_filename = os.path.basename(file_path)
            target_path = os.path.join(icons_dir, icon_filename)
            try:
                import shutil
                shutil.copy2(file_path, target_path)
                self.path_edit.setText(f"icons/{icon_filename}")
                INI_CONFIG['Paths']['icon_path'] = f"icons/{icon_filename}"
                with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                     "Anything_CustomSkill_Editor.ini"), 'w') as f:
                    INI_CONFIG.write(f)
                # Update icon immediately
                new_icon = QIcon(target_path)
                mw = self.parent()
                if mw:
                    mw.setWindowIcon(new_icon)
                    QApplication.setWindowIcon(new_icon)
                self.setWindowIcon(new_icon)
                QMessageBox.information(self, "Success", 
                    "Icon updated successfully. The new icon is now in use.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to copy icon file: {str(e)}")

class SkillSelectDialog(QDialog):
    def __init__(self, skills_dir, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select a Skill to Load")
        self.setMinimumWidth(400)
        self.selected_skill = None
        layout = QVBoxLayout()
        label = QLabel("Select a skill directory:")
        layout.addWidget(label)
        self.list_widget = QListWidget()
        valid_subdirs = []
        if os.path.isdir(skills_dir):
            for name in os.listdir(skills_dir):
                subdir_path = os.path.join(skills_dir, name)
                if os.path.isdir(subdir_path):
                    plugin_json = os.path.join(subdir_path, "plugin.json")
                    handler_js = os.path.join(subdir_path, "handler.js")
                    if os.path.isfile(plugin_json) and os.path.isfile(handler_js):
                        try:
                            # Validate plugin.json is valid JSON
                            with open(plugin_json, "r", encoding="utf-8") as f:
                                pdata = json.load(f)
                                # Validate required fields
                                if all(key in pdata for key in ["name", "hubId", "description", "version", "schema"]):
                                    valid_subdirs.append(name)
                        except Exception:
                            continue
        for subdir in sorted(valid_subdirs, key=lambda s: s.lower()):
            item = QListWidgetItem(subdir)
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget)
        btn_layout = QHBoxLayout()
        load_btn = MenuBarButton("Load")
        load_btn.clicked.connect(self.accept)
        cancel_btn = MenuBarButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(load_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.list_widget.itemDoubleClicked.connect(self.accept)
    def accept(self):
        selected = self.list_widget.currentItem()
        if selected:
            self.selected_skill = selected.text()
            super().accept()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a skill directory.")

def log_standard(message):
    """Standard logging - just the essential information"""
    with open(LOG_FILE_STANDARD, "a") as f:
        f.write(f"[{datetime.datetime.now()}] {message}\n")

def log_verbose(message, skill_data=None, action=None, duration=None, error=None):
    """Enhanced verbose logging with detailed information"""
    with open(LOG_FILE_VERBOSE, "a") as f:
        timestamp = datetime.datetime.now()
        log_parts = [f"[{timestamp}]"]
        
        # Add skill name if provided
        if skill_data and isinstance(skill_data, dict) and "name" in skill_data:
            log_parts.append(f"Skill: {skill_data['name']}")
        
        # Add action if provided
        if action:
            log_parts.append(f"Action: {action}")
        
        # Add duration if provided
        if duration:
            log_parts.append(f"Duration: {duration:.3f}s")
        
        # Add the main message
        log_parts.append(f"Message: {message}")
        
        # Add detailed skill data if provided
        if skill_data and isinstance(skill_data, dict):
            log_parts.append("\nSkill Details:")
            for key, value in skill_data.items():
                if isinstance(value, dict):
                    log_parts.append(f"  {key}:")
                    for subkey, subvalue in value.items():
                        log_parts.append(f"    {subkey}: {subvalue}")
                else:
                    log_parts.append(f"  {key}: {value}")
        
        # Add error information if provided
        if error:
            log_parts.append("\nError Details:")
            if isinstance(error, Exception):
                log_parts.append(f"  Type: {type(error).__name__}")
                log_parts.append(f"  Message: {str(error)}")
                import traceback
                log_parts.append("Stack Trace:")
                for line in traceback.format_tb(error.__traceback__):
                    log_parts.append(f"    {line.strip()}")
            else:
                log_parts.append(f"  {error}")
        
        # Write the formatted log entry
        f.write("\n".join(log_parts) + "\n" + "-"*80 + "\n")

def global_exception_hook(exc_type, exc_value, exc_traceback):
    import traceback
    log_verbose(
        message="UNHANDLED EXCEPTION",
        action="Global Exception",
        error={
            "type": exc_type.__name__,
            "message": str(exc_value),
            "stack": "".join(traceback.format_tb(exc_traceback))
        }
    )
    # Also call the default excepthook so errors still show in console
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = global_exception_hook

def main():
    app = QApplication(sys.argv)
    window = SkillEditor()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
