#!/usr/bin/env python3
"""
Google Dorking Tool v1.2 - Main Entry Point.
"""

import sys
import os

# Add package directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from dork_tool.ui import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Google Dorking Tool")
    app.setOrganizationName("OSINT Security")

    # Set base application font to prevent pointSize <= 0 warnings
    app_font = QFont("Segoe UI", 10)
    app.setFont(app_font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
