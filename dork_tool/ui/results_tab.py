"""
Results Explorer Tab Widget (PySide6).
Category Filter Chips, Live Search Filtering, Pagination, Context Menu, and Multi-Format Exports.
Version 1.2.0 - Zero Emojis
"""

import json
from collections import Counter
from typing import List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QFileDialog,
    QMessageBox, QApplication, QMenu, QScrollArea, QFrame, QButtonGroup
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QCursor, QColor

from ..models import SearchResult
from ..exporter import ExportManager


class ResultsTab(QWidget):
    """
    Results Explorer with category chip filtering, live search, pagination,
    table sorting, and multi-format exports.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_results: List[SearchResult] = []
        self.filtered_results: List[SearchResult] = []
        self.current_category_filter: str = "ALL"
        self.current_page: int = 1
        self.results_per_page: int = 10
        self.current_query: str = ""

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # 1. Filter and Search Bar
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(10)

        filter_label = QLabel("Search Findings:")
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter by title, URL, snippet, or category...")
        self.filter_input.textChanged.connect(self.on_filter_changed)

        self.results_count_label = QLabel("0 Results")
        self.results_count_label.setStyleSheet("font-weight: 600; color: #58a6ff;")

        filter_bar.addWidget(filter_label)
        filter_bar.addWidget(self.filter_input, 1)
        filter_bar.addWidget(self.results_count_label)
        layout.addLayout(filter_bar)

        # 2. Dynamic Category Filter Chips Scroll Area
        self.chips_scroll = QScrollArea()
        self.chips_scroll.setWidgetResizable(True)
        self.chips_scroll.setFixedHeight(48)
        self.chips_scroll.setFrameShape(QFrame.NoFrame)
        self.chips_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.chips_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.chips_widget = QWidget()
        self.chips_layout = QHBoxLayout(self.chips_widget)
        self.chips_layout.setContentsMargins(0, 4, 0, 4)
        self.chips_layout.setSpacing(6)
        self.chips_group = QButtonGroup(self)

        self.chips_scroll.setWidget(self.chips_widget)
        layout.addWidget(self.chips_scroll)

        # 3. Results Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["#", "Title", "URL / Link", "Category", "Snippet"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.setColumnWidth(1, 240)
        self.table.setColumnWidth(2, 300)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.cellDoubleClicked.connect(self.on_row_double_clicked)

        layout.addWidget(self.table)

        # 4. Pagination and Bottom Controls
        bottom_bar = QHBoxLayout()
        bottom_bar.setSpacing(10)

        # Pagination Controls
        self.prev_btn = QPushButton("< Prev")
        self.prev_btn.clicked.connect(self.prev_page)
        self.next_btn = QPushButton("Next >")
        self.next_btn.clicked.connect(self.next_page)
        self.page_label = QLabel("Page 1 of 1")
        self.page_label.setStyleSheet("color: #8b949e; font-weight: 600;")

        self.per_page_combo = QComboBox()
        self.per_page_combo.addItems(["10 per page", "25 per page", "50 per page", "100 per page"])
        self.per_page_combo.currentIndexChanged.connect(self.on_per_page_changed)

        bottom_bar.addWidget(self.prev_btn)
        bottom_bar.addWidget(self.page_label)
        bottom_bar.addWidget(self.next_btn)
        bottom_bar.addWidget(self.per_page_combo)
        bottom_bar.addStretch()

        # Export & Actions Buttons
        export_label = QLabel("Export:")
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["CSV (Excel UTF-8)", "JSON Data", "Styled HTML Report", "Markdown Table", "Plain Text"])

        self.export_btn = QPushButton("Export Findings")
        self.export_btn.setObjectName("primaryBtn")
        self.export_btn.clicked.connect(self.export_results)

        self.open_selected_btn = QPushButton("Open Link")
        self.open_selected_btn.setObjectName("browserBtn")
        self.open_selected_btn.clicked.connect(self.open_selected_in_browser)

        self.copy_selected_btn = QPushButton("Copy URL")
        self.copy_selected_btn.clicked.connect(self.copy_selected_url)

        bottom_bar.addWidget(export_label)
        bottom_bar.addWidget(self.export_format_combo)
        bottom_bar.addWidget(self.export_btn)
        bottom_bar.addWidget(self.open_selected_btn)
        bottom_bar.addWidget(self.copy_selected_btn)

        layout.addLayout(bottom_bar)
        self.rebuild_category_chips()

    def set_results(self, results: List[SearchResult], query: str = ""):
        self.all_results = results
        self.current_query = query
        self.current_category_filter = "ALL"
        self.filter_input.clear()
        self.rebuild_category_chips()
        self.apply_filter()

    def update_results(self, results: List[SearchResult]):
        """
        Replaces the current result set with a cumulative update from a worker.
        Batch workers emit all findings collected so far; replacing avoids
        duplicating earlier rows on every progress update.
        """
        self.all_results = list(results)
        self.rebuild_category_chips()
        self.apply_filter()

    def append_results(self, results: List[SearchResult]):
        """
        Appends new findings while deduplicating by URL, query, and category.
        Kept for callers that provide incremental result batches.
        """
        seen = {(r.link, r.query, r.category) for r in self.all_results}
        for result in results:
            key = (result.link, result.query, result.category)
            if key not in seen:
                self.all_results.append(result)
                seen.add(key)
        self.rebuild_category_chips()
        self.apply_filter()

    def rebuild_category_chips(self):
        # Clear existing buttons from group and layout
        for btn in self.chips_group.buttons():
            self.chips_group.removeButton(btn)
            btn.deleteLater()

        # Count findings per category
        cat_counts = Counter(r.category for r in self.all_results)
        total_count = len(self.all_results)

        # 1. "All" Chip
        all_btn = QPushButton(f"All ({total_count})")
        all_btn.setCheckable(True)
        all_btn.setChecked(self.current_category_filter == "ALL")
        all_btn.setProperty("class", "chip-btn")
        all_btn.clicked.connect(lambda: self.select_category_chip("ALL"))
        self.chips_group.addButton(all_btn)
        self.chips_layout.addWidget(all_btn)

        # 2. Category Chips
        for cat_name, count in sorted(cat_counts.items()):
            chip = QPushButton(f"{cat_name} ({count})")
            chip.setCheckable(True)
            chip.setChecked(self.current_category_filter == cat_name)
            chip.setProperty("class", "chip-btn")
            chip.clicked.connect(lambda _, c=cat_name: self.select_category_chip(c))
            self.chips_group.addButton(chip)
            self.chips_layout.addWidget(chip)

        self.chips_layout.addStretch()

    def select_category_chip(self, category: str):
        self.current_category_filter = category
        self.current_page = 1
        self.apply_filter()

    def on_filter_changed(self):
        self.current_page = 1
        self.apply_filter()

    def on_per_page_changed(self):
        text = self.per_page_combo.currentText()
        self.results_per_page = int(text.split()[0])
        self.current_page = 1
        self.render_page()

    def apply_filter(self):
        query = self.filter_input.text().strip().lower()

        filtered = []
        for r in self.all_results:
            if self.current_category_filter != "ALL" and r.category != self.current_category_filter:
                continue
            if not query or query in r.title.lower() or query in r.link.lower() or query in r.snippet.lower() or query in r.category.lower():
                filtered.append(r)

        self.filtered_results = filtered
        self.results_count_label.setText(f"{len(self.filtered_results)} of {len(self.all_results)} Results")
        self.render_page()

    def render_page(self):
        total = len(self.filtered_results)
        total_pages = max(1, (total + self.results_per_page - 1) // self.results_per_page)

        if self.current_page > total_pages:
            self.current_page = total_pages
        if self.current_page < 1:
            self.current_page = 1

        self.page_label.setText(f"Page {self.current_page} of {total_pages}")
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < total_pages)

        start_idx = (self.current_page - 1) * self.results_per_page
        end_idx = min(start_idx + self.results_per_page, total)
        page_items = self.filtered_results[start_idx:end_idx]

        self.table.setRowCount(len(page_items))

        # Check theme for adaptive link color
        window = self.window()
        is_light = hasattr(window, "current_theme") and window.current_theme == "light"
        link_color = QColor("#0969da") if is_light else QColor("#58a6ff")

        for row, item in enumerate(page_items):
            actual_idx = start_idx + row + 1

            idx_item = QTableWidgetItem(str(actual_idx))
            idx_item.setTextAlignment(Qt.AlignCenter)

            title_item = QTableWidgetItem(item.title)
            link_item = QTableWidgetItem(item.link)
            link_item.setForeground(link_color)

            cat_item = QTableWidgetItem(item.category)
            cat_item.setTextAlignment(Qt.AlignCenter)

            snippet_item = QTableWidgetItem(item.snippet)

            self.table.setItem(row, 0, idx_item)
            self.table.setItem(row, 1, title_item)
            self.table.setItem(row, 2, link_item)
            self.table.setItem(row, 3, cat_item)
            self.table.setItem(row, 4, snippet_item)

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.render_page()

    def next_page(self):
        total = len(self.filtered_results)
        total_pages = max(1, (total + self.results_per_page - 1) // self.results_per_page)
        if self.current_page < total_pages:
            self.current_page += 1
            self.render_page()

    def get_selected_result(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        start_idx = (self.current_page - 1) * self.results_per_page
        item_idx = start_idx + row
        if 0 <= item_idx < len(self.filtered_results):
            return self.filtered_results[item_idx]
        return None

    def on_row_double_clicked(self, row: int, col: int):
        r = self.get_selected_result()
        if r and r.link:
            QDesktopServices.openUrl(QUrl(r.link))

    def open_selected_in_browser(self):
        r = self.get_selected_result()
        if r and r.link:
            QDesktopServices.openUrl(QUrl(r.link))
        else:
            QMessageBox.information(self, "Selection Required", "Please select a result row to open.")

    def copy_selected_url(self):
        r = self.get_selected_result()
        if r and r.link:
            QApplication.clipboard().setText(r.link)
            window = self.window()
            if hasattr(window, "show_toast"):
                window.show_toast("URL copied to clipboard.")
        else:
            QMessageBox.information(self, "Selection Required", "Please select a result row to copy.")

    def show_context_menu(self, pos):
        row = self.table.rowAt(pos.y())
        if row < 0:
            return
        self.table.selectRow(row)
        r = self.get_selected_result()
        if not r:
            return

        menu = QMenu(self)
        open_act = menu.addAction("Open URL in Browser")
        copy_url_act = menu.addAction("Copy URL")
        copy_title_act = menu.addAction("Copy Title")
        copy_snippet_act = menu.addAction("Copy Snippet")
        menu.addSeparator()
        copy_json_act = menu.addAction("Copy Row as JSON")

        action = menu.exec(QCursor.pos())
        if action == open_act:
            QDesktopServices.openUrl(QUrl(r.link))
        elif action == copy_url_act:
            QApplication.clipboard().setText(r.link)
            window = self.window()
            if hasattr(window, "show_toast"):
                window.show_toast("URL copied to clipboard.")
        elif action == copy_title_act:
            QApplication.clipboard().setText(r.title)
            window = self.window()
            if hasattr(window, "show_toast"):
                window.show_toast("Title copied.")
        elif action == copy_snippet_act:
            QApplication.clipboard().setText(r.snippet)
            window = self.window()
            if hasattr(window, "show_toast"):
                window.show_toast("Snippet copied.")
        elif action == copy_json_act:
            QApplication.clipboard().setText(json.dumps(r.to_dict(), indent=2))
            window = self.window()
            if hasattr(window, "show_toast"):
                window.show_toast("JSON copied.")

    def export_results(self):
        target_results = self.filtered_results if self.filtered_results else self.all_results
        if not target_results:
            QMessageBox.warning(self, "No Results", "There are no results available to export.")
            return

        fmt_idx = self.export_format_combo.currentIndex()
        if fmt_idx == 0:
            filepath, _ = QFileDialog.getSaveFileName(self, "Export Findings as CSV", "dork_results.csv", "CSV Files (*.csv)")
            if filepath:
                if ExportManager.export_csv(filepath, target_results):
                    QMessageBox.information(self, "Export Succeeded", f"Saved {len(target_results)} findings to:\n{filepath}")
        elif fmt_idx == 1:
            filepath, _ = QFileDialog.getSaveFileName(self, "Export Findings as JSON", "dork_results.json", "JSON Files (*.json)")
            if filepath:
                if ExportManager.export_json(filepath, target_results):
                    QMessageBox.information(self, "Export Succeeded", f"Saved {len(target_results)} findings to:\n{filepath}")
        elif fmt_idx == 2:
            filepath, _ = QFileDialog.getSaveFileName(self, "Export Findings as HTML Report", "dork_report.html", "HTML Files (*.html)")
            if filepath:
                if ExportManager.export_html(filepath, target_results, self.current_query):
                    QMessageBox.information(self, "Export Succeeded", f"Saved HTML report to:\n{filepath}")
        elif fmt_idx == 3:
            filepath, _ = QFileDialog.getSaveFileName(self, "Export Findings as Markdown", "dork_results.md", "Markdown Files (*.md)")
            if filepath:
                if ExportManager.export_markdown(filepath, target_results, self.current_query):
                    QMessageBox.information(self, "Export Succeeded", f"Saved Markdown report to:\n{filepath}")
        elif fmt_idx == 4:
            filepath, _ = QFileDialog.getSaveFileName(self, "Export Findings as Plain Text", "dork_results.txt", "Text Files (*.txt)")
            if filepath:
                if ExportManager.export_txt(filepath, target_results, self.current_query):
                    QMessageBox.information(self, "Export Succeeded", f"Saved text report to:\n{filepath}")

