"""
UI Loader and Theme Manager for PySide6 and Qt Designer.
Seamless support for both development and PyInstaller frozen executable environments.
Version 1.2.0
"""

import os
import sys
from typing import Optional
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QFile

try:
    from PySide6.QtUiTools import QUiLoader
    UI_LOADER_AVAILABLE = True
except ImportError:
    UI_LOADER_AVAILABLE = False


def get_ui_base_dir() -> str:
    """Returns base directory for UI assets, supporting PyInstaller bundles."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        bundle_path = os.path.join(sys._MEIPASS, "dork_tool", "ui")
        if os.path.exists(bundle_path):
            return bundle_path
    return os.path.dirname(__file__)


class ThemeManager:
    """Loads and manages QSS stylesheets."""

    @classmethod
    def get_styles_dir(cls) -> str:
        return os.path.join(get_ui_base_dir(), "styles")

    @classmethod
    def get_stylesheet(cls, theme_name: str = "dark") -> str:
        qss_filename = f"{theme_name.lower()}.qss"
        qss_path = os.path.join(cls.get_styles_dir(), qss_filename)
        if os.path.exists(qss_path):
            try:
                with open(qss_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                print(f"[ERROR] Failed to read stylesheet {qss_path}: {e}")
        return ""

    @classmethod
    def apply_theme(cls, target_widget: QWidget, theme_name: str = "dark"):
        stylesheet = cls.get_stylesheet(theme_name)
        if stylesheet:
            target_widget.setStyleSheet(stylesheet)


def load_ui_file(ui_relative_path: str, parent: Optional[QWidget] = None) -> Optional[QWidget]:
    """Loads a .ui file using PySide6 QUiLoader."""
    if not UI_LOADER_AVAILABLE:
        return None

    full_path = os.path.join(get_ui_base_dir(), ui_relative_path)
    if not os.path.exists(full_path):
        print(f"[WARN] UI file not found: {full_path}")
        return None

    try:
        loader = QUiLoader()
        ui_file = QFile(full_path)
        ui_file.open(QFile.ReadOnly)
        widget = loader.load(ui_file, parent)
        ui_file.close()
        return widget
    except Exception as e:
        print(f"[ERROR] Failed to load UI file {full_path}: {e}")
        return None
