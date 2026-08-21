"""
Reference and Documentation Tab Widget (PySide6).
Clean operator reference table and OSINT methodology guide with zero emojis.
Version 1.2.0
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from ..engine import DorkEngine


class HelpTab(QWidget):
    """
    Operator reference catalog and OSINT best practices guide.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # 1. Operators Table
        op_box = QGroupBox("Google Search Operators Reference")
        op_layout = QVBoxLayout(op_box)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Operator", "Description", "Example Syntax"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        self.table.setColumnWidth(2, 280)
        self.table.setAlternatingRowColors(True)

        self.table.setRowCount(len(DorkEngine.OPERATORS))
        for row, (op, meta) in enumerate(DorkEngine.OPERATORS.items()):
            op_item = QTableWidgetItem(op)
            op_item.setForeground(QColor("#58a6ff"))
            self.table.setItem(row, 0, op_item)
            self.table.setItem(row, 1, QTableWidgetItem(meta.get("desc", "")))
            self.table.setItem(row, 2, QTableWidgetItem(meta.get("example", "")))

        op_layout.addWidget(self.table)
        layout.addWidget(op_box)

        # 2. Methodologies & Ethics
        guide_box = QGroupBox("Methodology & Legal Disclaimer")
        g_layout = QVBoxLayout(guide_box)

        guide_text = QTextEdit()
        guide_text.setReadOnly(True)
        guide_text.setMaximumHeight(160)
        guide_text.setHtml("""
        <p><strong>Reconnaissance Methodology:</strong></p>
        <ul>
            <li><strong>Passive Information Gathering:</strong> Google Dorking queries Google's public search index without sending intrusive packets directly to the target web server.</li>
            <li><strong>Rate Limiting &amp; Stealth:</strong> Google imposes strict anti-scraping protections (CAPTCHAs/HTTP 429). The integrated rate limiter throttles API queries. For browser automation, use manual intervals.</li>
            <li><strong>Authorization &amp; Compliance:</strong> This software is engineered strictly for authorized security assessments, penetration testing, vulnerability research, and educational analysis. Obtaining written authorization before evaluating organizational assets is required.</li>
        </ul>
        """)
        g_layout.addWidget(guide_text)
        layout.addWidget(guide_box)
