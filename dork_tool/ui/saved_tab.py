"""
Saved Dork Bookmarks and Search History Tab (PySide6).
Search Filtering, Quick Copy, and Re-run capabilities with Zero Emojis.
Version 1.2.0
"""

from typing import Callable
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QSplitter,
    QMessageBox, QDialog, QFormLayout, QDialogButtonBox, QTextEdit,
    QApplication
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
import urllib.parse

from ..bookmarks import BookmarksManager


class SavedTab(QWidget):
    """
    Split view displaying Saved Dork Bookmarks and Search History with search filters.
    """

    def __init__(self, bookmarks_mgr: BookmarksManager,
                 on_execute_query: Callable[[str], None],
                 parent=None):
        super().__init__(parent)
        self.bookmarks_mgr = bookmarks_mgr
        self.on_execute_query = on_execute_query
        self.raw_bookmarks = []
        self.raw_history = []

        self.init_ui()
        self.refresh_all()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        splitter = QSplitter(Qt.Vertical)

        # 1. Bookmarks Section
        bm_box = QGroupBox("Saved Dork Bookmarks")
        bm_layout = QVBoxLayout(bm_box)
        bm_layout.setSpacing(8)

        bm_bar = QHBoxLayout()
        self.bm_filter_input = QLineEdit()
        self.bm_filter_input.setPlaceholderText("Filter bookmarks by title or query...")
        self.bm_filter_input.textChanged.connect(self.filter_bookmarks)

        add_bm_btn = QPushButton("Add Bookmark")
        add_bm_btn.setObjectName("primaryBtn")
        add_bm_btn.clicked.connect(self.prompt_add_bookmark)

        load_bm_btn = QPushButton("Send to Search Tab")
        load_bm_btn.clicked.connect(self.load_selected_bookmark)

        copy_bm_btn = QPushButton("Copy Query")
        copy_bm_btn.clicked.connect(self.copy_selected_bookmark)

        run_bm_browser_btn = QPushButton("Open in Browser")
        run_bm_browser_btn.setObjectName("browserBtn")
        run_bm_browser_btn.clicked.connect(self.open_selected_bookmark_browser)

        delete_bm_btn = QPushButton("Delete")
        delete_bm_btn.setObjectName("dangerBtn")
        delete_bm_btn.clicked.connect(self.delete_selected_bookmark)

        bm_bar.addWidget(self.bm_filter_input, 2)
        bm_bar.addWidget(add_bm_btn)
        bm_bar.addWidget(load_bm_btn)
        bm_bar.addWidget(copy_bm_btn)
        bm_bar.addWidget(run_bm_browser_btn)
        bm_bar.addWidget(delete_bm_btn)
        bm_layout.addLayout(bm_bar)

        self.bm_table = QTableWidget()
        self.bm_table.setColumnCount(4)
        self.bm_table.setHorizontalHeaderLabels(["Title", "Query", "Category", "Created"])
        self.bm_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.bm_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.bm_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.bm_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.bm_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.bm_table.setAlternatingRowColors(True)
        self.bm_table.cellDoubleClicked.connect(lambda r, c: self.load_selected_bookmark())
        bm_layout.addWidget(self.bm_table)

        splitter.addWidget(bm_box)

        # 2. History Section
        hist_box = QGroupBox("Search Execution History")
        hist_layout = QVBoxLayout(hist_box)
        hist_layout.setSpacing(8)

        hist_bar = QHBoxLayout()
        self.hist_filter_input = QLineEdit()
        self.hist_filter_input.setPlaceholderText("Filter history by query or mode...")
        self.hist_filter_input.textChanged.connect(self.filter_history)

        rerun_btn = QPushButton("Re-run Selected Query")
        rerun_btn.setObjectName("primaryBtn")
        rerun_btn.clicked.connect(self.rerun_history_query)

        copy_hist_btn = QPushButton("Copy Query")
        copy_hist_btn.clicked.connect(self.copy_selected_history)

        clear_hist_btn = QPushButton("Clear History")
        clear_hist_btn.setObjectName("dangerBtn")
        clear_hist_btn.clicked.connect(self.clear_history)

        hist_bar.addWidget(self.hist_filter_input, 2)
        hist_bar.addWidget(rerun_btn)
        hist_bar.addWidget(copy_hist_btn)
        hist_bar.addWidget(clear_hist_btn)
        hist_layout.addLayout(hist_bar)

        self.hist_table = QTableWidget()
        self.hist_table.setColumnCount(4)
        self.hist_table.setHorizontalHeaderLabels(["Timestamp", "Mode", "Query", "Results"])
        self.hist_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.hist_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.hist_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.hist_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.hist_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.hist_table.setAlternatingRowColors(True)
        self.hist_table.cellDoubleClicked.connect(lambda r, c: self.rerun_history_query())
        hist_layout.addWidget(self.hist_table)

        splitter.addWidget(hist_box)
        layout.addWidget(splitter)

    def refresh_all(self):
        self.raw_bookmarks = self.bookmarks_mgr.load_bookmarks()
        self.raw_history = self.bookmarks_mgr.load_history()
        self.filter_bookmarks()
        self.filter_history()

    def refresh_history(self):
        self.raw_history = self.bookmarks_mgr.load_history()
        self.filter_history()

    def filter_bookmarks(self):
        query = self.bm_filter_input.text().strip().lower()
        if not query:
            items = self.raw_bookmarks
        else:
            items = [
                b for b in self.raw_bookmarks
                if query in b.get("title", "").lower() or query in b.get("query", "").lower() or query in b.get("category", "").lower()
            ]

        self.bm_table.setRowCount(len(items))
        for row, bm in enumerate(items):
            self.bm_table.setItem(row, 0, QTableWidgetItem(bm.get("title", "")))
            self.bm_table.setItem(row, 1, QTableWidgetItem(bm.get("query", "")))
            self.bm_table.setItem(row, 2, QTableWidgetItem(bm.get("category", "General")))
            self.bm_table.setItem(row, 3, QTableWidgetItem(bm.get("created_at", "")))

    def filter_history(self):
        query = self.hist_filter_input.text().strip().lower()
        if not query:
            items = self.raw_history
        else:
            items = [
                h for h in self.raw_history
                if query in h.get("query", "").lower() or query in h.get("mode", "").lower()
            ]

        self.hist_table.setRowCount(len(items))
        for row, h in enumerate(items):
            self.hist_table.setItem(row, 0, QTableWidgetItem(h.get("timestamp", "")))
            self.hist_table.setItem(row, 1, QTableWidgetItem(h.get("mode", "API")))
            self.hist_table.setItem(row, 2, QTableWidgetItem(h.get("query", "")))
            self.hist_table.setItem(row, 3, QTableWidgetItem(str(h.get("results_count", 0))))

    def prompt_add_bookmark(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Dork Bookmark")
        dialog.setMinimumWidth(420)
        d_layout = QFormLayout(dialog)

        title_edit = QLineEdit()
        query_edit = QTextEdit()
        query_edit.setMaximumHeight(80)
        cat_edit = QLineEdit("Custom")

        d_layout.addRow("Bookmark Title:", title_edit)
        d_layout.addRow("Search Query:", query_edit)
        d_layout.addRow("Category:", cat_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        d_layout.addRow(buttons)

        if dialog.exec() == QDialog.Accepted:
            title = title_edit.text().strip() or "Untitled Dork"
            query = query_edit.toPlainText().strip()
            category = cat_edit.text().strip() or "Custom"
            if query:
                self.bookmarks_mgr.add_bookmark(title, query, category)
                self.refresh_all()
                window = self.window()
                if hasattr(window, "show_toast"):
                    window.show_toast("Bookmark added successfully.")

    def delete_selected_bookmark(self):
        row = self.bm_table.currentRow()
        if row < 0:
            return
        title_item = self.bm_table.item(row, 0)
        query_item = self.bm_table.item(row, 1)
        if not query_item or not title_item:
            return
        target_title = title_item.text()
        target_query = query_item.text()

        # Find exact original index in raw bookmarks
        orig_idx = next(
            (i for i, b in enumerate(self.raw_bookmarks) if b.get("query") == target_query and b.get("title") == target_title),
            -1
        )
        if orig_idx >= 0 and self.bookmarks_mgr.delete_bookmark(orig_idx):
            self.refresh_all()
            window = self.window()
            if hasattr(window, "show_toast"):
                window.show_toast("Bookmark deleted.")

    def copy_selected_bookmark(self):
        row = self.bm_table.currentRow()
        if row >= 0:
            query_item = self.bm_table.item(row, 1)
            if query_item and query_item.text():
                QApplication.clipboard().setText(query_item.text())
                window = self.window()
                if hasattr(window, "show_toast"):
                    window.show_toast("Bookmark query copied.")

    def copy_selected_history(self):
        row = self.hist_table.currentRow()
        if row >= 0:
            query_item = self.hist_table.item(row, 2)
            if query_item and query_item.text():
                QApplication.clipboard().setText(query_item.text())
                window = self.window()
                if hasattr(window, "show_toast"):
                    window.show_toast("History query copied.")

    def load_selected_bookmark(self):
        row = self.bm_table.currentRow()
        if row >= 0:
            query_item = self.bm_table.item(row, 1)
            if query_item:
                self.on_execute_query(query_item.text())

    def open_selected_bookmark_browser(self):
        row = self.bm_table.currentRow()
        if row >= 0:
            query_item = self.bm_table.item(row, 1)
            if query_item and query_item.text().strip():
                query = query_item.text().strip()
                self.bookmarks_mgr.add_history(query, 0, mode="Browser")
                encoded = urllib.parse.quote_plus(query)
                QDesktopServices.openUrl(QUrl(f"https://www.google.com/search?q={encoded}"))

    def rerun_history_query(self):
        row = self.hist_table.currentRow()
        if row >= 0:
            query_item = self.hist_table.item(row, 2)
            if query_item:
                self.on_execute_query(query_item.text())

    def clear_history(self):
        reply = QMessageBox.question(self, "Clear History", "Are you sure you want to clear all search history?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.bookmarks_mgr.clear_history()
            self.refresh_all()
            window = self.window()
            if hasattr(window, "show_toast"):
                window.show_toast("Search history cleared.")
