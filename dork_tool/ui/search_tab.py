"""
Search and Dork Builder Tab Widget (PySide6).
Visual Dork Form Builder, Plain-English Query Explainer, File Type Extension Pills,
Curated Goal-Based Recipes, and Multi-Target Entity Support (Domain, Email, Person, Username).
Version 1.2.0 - Zero Emojis
"""

import urllib.parse
from typing import List, Tuple, Callable, Dict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QComboBox, QGroupBox, QGridLayout, QScrollArea, QFrame,
    QCheckBox, QRadioButton, QButtonGroup, QMessageBox, QApplication,
    QTabWidget
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QKeyEvent

from ..engine import DorkEngine
from ..bookmarks import BookmarksManager


class QueryEditor(QTextEdit):
    """
    Subclassed QTextEdit supporting Ctrl+Enter to trigger instant search.
    """
    def __init__(self, on_submit: Callable[[], None], parent=None):
        super().__init__(parent)
        self.on_submit = on_submit

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and (event.modifiers() & Qt.ControlModifier):
            self.on_submit()
            event.accept()
        else:
            super().keyPressEvent(event)


class SearchTab(QWidget):
    """
    Interactive Search Tab with Visual Form Builder, Goal Recipes,
    Plain-English Explainer, and Automated Recon Suite.
    """

    def __init__(self, on_run_api_search: Callable[[str, str], None],
                 on_run_batch_recon: Callable[[str, List[str], str], None],
                 bookmarks_mgr: BookmarksManager,
                 parent=None):
        super().__init__(parent)
        self.on_run_api_search = on_run_api_search
        self.on_run_batch_recon = on_run_batch_recon
        self.bookmarks_mgr = bookmarks_mgr
        self.category_checkboxes: List[Tuple[str, QCheckBox]] = []
        self.filetype_buttons: Dict[str, QPushButton] = {}
        self.all_templates: List[Tuple[str, str, str]] = []  # (category, title, query)
        self._updating_form = False

        self.init_ui()
        self.populate_templates()

    def init_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # 1. Mode Selection Bar
        mode_box = QGroupBox("Reconnaissance Mode")
        mode_layout = QHBoxLayout(mode_box)
        mode_layout.setContentsMargins(16, 10, 16, 10)

        self.mode_group = QButtonGroup(self)
        self.builder_radio = QRadioButton("Visual Dork Builder")
        self.recipes_radio = QRadioButton("Curated Goal Recipes")
        self.auto_radio = QRadioButton("Automated Target Sweep")
        self.builder_radio.setChecked(True)

        self.mode_group.addButton(self.builder_radio)
        self.mode_group.addButton(self.recipes_radio)
        self.mode_group.addButton(self.auto_radio)

        mode_layout.addWidget(self.builder_radio)
        mode_layout.addWidget(self.recipes_radio)
        mode_layout.addWidget(self.auto_radio)
        mode_layout.addStretch()

        shortcut_hint = QLabel("Shortcut: Ctrl+Enter to search")
        shortcut_hint.setStyleSheet("color: #8b949e; font-size: 11px;")
        mode_layout.addWidget(shortcut_hint)

        self.builder_radio.toggled.connect(self.update_mode_visibility)
        self.recipes_radio.toggled.connect(self.update_mode_visibility)
        layout.addWidget(mode_box)

        # 2. Target Entity Scope Frame (Shared)
        scope_box = QGroupBox("Target Scope (Domain, Email, Person Name, or Username)")
        scope_layout = QVBoxLayout(scope_box)
        scope_layout.setSpacing(8)

        input_row = QHBoxLayout()
        self.target_scope_input = QLineEdit()
        self.target_scope_input.setPlaceholderText("e.g. target.com, user@corp.com, 'John Doe', or admin_user")
        self.target_scope_input.textChanged.connect(self.on_target_input_changed)

        self.target_type_combo = QComboBox()
        self.target_type_combo.addItems([
            "Auto-Detect Type",
            "Domain / Hostname",
            "Email Address",
            "Person / Full Name",
            "Username / Keyword"
        ])
        self.target_type_combo.currentIndexChanged.connect(self.on_target_input_changed)

        self.type_badge = QLabel("Detected: None")
        self.type_badge.setStyleSheet("color: #58a6ff; font-weight: 600; font-size: 11px;")

        input_row.addWidget(QLabel("Target:"))
        input_row.addWidget(self.target_scope_input, 2)
        input_row.addWidget(self.target_type_combo, 1)
        input_row.addWidget(self.type_badge)
        scope_layout.addLayout(input_row)

        layout.addWidget(scope_box)

        # 3. Mode 1: Visual Form Builder Container
        self.builder_container = QWidget()
        self.build_visual_form_mode()
        layout.addWidget(self.builder_container)

        # 4. Mode 2: Curated Goal Recipes Container
        self.recipes_container = QWidget()
        self.build_recipes_mode()
        self.recipes_container.setVisible(False)
        layout.addWidget(self.recipes_container)

        # 5. Mode 3: Automated Sweep Mode Container
        self.auto_container = QWidget()
        self.build_auto_mode()
        self.auto_container.setVisible(False)
        layout.addWidget(self.auto_container)

        # 6. Active Query Editor & Plain-English Explainer (Always Visible in Builder & Recipes)
        self.query_section = QGroupBox("Active Search Query & Plain-English Explainer")
        query_vbox = QVBoxLayout(self.query_section)
        query_vbox.setSpacing(8)

        self.query_editor = QueryEditor(on_submit=self.run_api_search, parent=self)
        self.query_editor.setPlaceholderText("Enter or construct your Google Dork search query here...")
        self.query_editor.setMaximumHeight(85)
        self.query_editor.textChanged.connect(self.on_query_changed)
        query_vbox.addWidget(self.query_editor)

        # Plain-English Explanation Frame
        self.explainer_frame = QFrame()
        self.explainer_frame.setStyleSheet("background-color: rgba(22, 27, 34, 0.7); border: 1px solid #30363d; border-radius: 6px; padding: 6px;")
        explainer_layout = QVBoxLayout(self.explainer_frame)
        explainer_layout.setContentsMargins(10, 6, 10, 6)

        self.explainer_label = QLabel("Plain English: Enter a search query or target above to see what Google will search for.")
        self.explainer_label.setStyleSheet("color: #7ee787; font-size: 12px; font-weight: 500;")
        self.explainer_label.setWordWrap(True)
        explainer_layout.addWidget(self.explainer_label)
        query_vbox.addWidget(self.explainer_frame)

        # Live Query Analysis Stats Bar
        self.stats_frame = QFrame()
        self.stats_frame.setStyleSheet("background-color: rgba(22, 27, 34, 0.5); border: 1px solid #30363d; border-radius: 6px; padding: 4px;")
        stats_layout = QHBoxLayout(self.stats_frame)
        stats_layout.setContentsMargins(8, 4, 8, 4)

        self.char_count_label = QLabel("0 chars | 0 words")
        self.char_count_label.setStyleSheet("color: #8b949e; font-size: 12px;")

        self.complexity_badge = QLabel("Complexity: Empty")
        self.complexity_badge.setStyleSheet("color: #8b949e; font-size: 12px; font-weight: bold;")

        self.detected_ops_label = QLabel("Operators: None")
        self.detected_ops_label.setStyleSheet("color: #58a6ff; font-size: 12px;")

        stats_layout.addWidget(self.char_count_label)
        stats_layout.addSpacing(16)
        stats_layout.addWidget(self.complexity_badge)
        stats_layout.addSpacing(16)
        stats_layout.addWidget(self.detected_ops_label)
        stats_layout.addStretch()
        query_vbox.addWidget(self.stats_frame)

        # Action Buttons
        actions_bar = QHBoxLayout()
        self.search_api_btn = QPushButton("Search via API (In-App)")
        self.search_api_btn.setObjectName("primaryBtn")
        self.search_api_btn.clicked.connect(self.run_api_search)

        self.search_browser_btn = QPushButton("Open in Browser (Direct)")
        self.search_browser_btn.setObjectName("browserBtn")
        self.search_browser_btn.clicked.connect(self.run_browser_search)

        self.save_bookmark_btn = QPushButton("Bookmark Query")
        self.save_bookmark_btn.clicked.connect(self.save_as_bookmark)

        self.copy_query_btn = QPushButton("Copy Query")
        self.copy_query_btn.clicked.connect(self.copy_query_to_clipboard)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setObjectName("dangerBtn")
        self.clear_btn.clicked.connect(self.clear_editor)

        actions_bar.addWidget(self.search_api_btn)
        actions_bar.addWidget(self.search_browser_btn)
        actions_bar.addWidget(self.save_bookmark_btn)
        actions_bar.addWidget(self.copy_query_btn)
        actions_bar.addWidget(self.clear_btn)
        actions_bar.addStretch()
        query_vbox.addLayout(actions_bar)

        layout.addWidget(self.query_section)
        layout.addStretch()

        self.scroll_area.setWidget(content_widget)
        outer_layout.addWidget(self.scroll_area)

    def update_mode_visibility(self):
        is_builder = self.builder_radio.isChecked()
        is_recipes = self.recipes_radio.isChecked()
        is_auto = self.auto_radio.isChecked()

        self.builder_container.setVisible(is_builder)
        self.recipes_container.setVisible(is_recipes)
        self.auto_container.setVisible(is_auto)
        self.query_section.setVisible(not is_auto)

    def build_visual_form_mode(self):
        layout = QVBoxLayout(self.builder_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        form_box = QGroupBox("Visual Dork Form Builder (Automatic Syntax Generation)")
        form_grid = QGridLayout(form_box)
        form_grid.setSpacing(8)

        # Field 1: In Page Title
        self.form_title_input = QLineEdit()
        self.form_title_input.setPlaceholderText("e.g. login, admin, dashboard, index of")
        self.form_title_input.textChanged.connect(self.compile_form_to_query)
        form_grid.addWidget(QLabel("In Title (intitle:):"), 0, 0)
        form_grid.addWidget(self.form_title_input, 0, 1)

        # Field 2: In URL Address
        self.form_url_input = QLineEdit()
        self.form_url_input.setPlaceholderText("e.g. admin, portal, wp-login, .php?id=")
        self.form_url_input.textChanged.connect(self.compile_form_to_query)
        form_grid.addWidget(QLabel("In URL (inurl:):"), 0, 2)
        form_grid.addWidget(self.form_url_input, 0, 3)

        # Field 3: In Page Content
        self.form_text_input = QLineEdit()
        self.form_text_input.setPlaceholderText("e.g. password, confidential, API_KEY")
        self.form_text_input.textChanged.connect(self.compile_form_to_query)
        form_grid.addWidget(QLabel("In Body (intext:):"), 1, 0)
        form_grid.addWidget(self.form_text_input, 1, 1)

        # Field 4: Exact Phrase
        self.form_exact_input = QLineEdit()
        self.form_exact_input.setPlaceholderText("e.g. \"Index of /\" or \"DB_PASSWORD\"")
        self.form_exact_input.textChanged.connect(self.compile_form_to_query)
        form_grid.addWidget(QLabel("Exact Phrase (\" \"):"), 1, 2)
        form_grid.addWidget(self.form_exact_input, 1, 3)

        # Field 5: Exclude Words / Sites
        self.form_exclude_input = QLineEdit()
        self.form_exclude_input.setPlaceholderText("e.g. github.com, stackoverflow.com, demo")
        self.form_exclude_input.textChanged.connect(self.compile_form_to_query)
        form_grid.addWidget(QLabel("Exclude (-):"), 2, 0)
        form_grid.addWidget(self.form_exclude_input, 2, 1, 1, 3)

        # Field 6: File Extension Pills Selector
        pills_layout = QHBoxLayout()
        pills_label = QLabel("File Types (filetype:):")
        pills_label.setStyleSheet("font-weight: 600; color: #8b949e;")
        pills_layout.addWidget(pills_label)

        extensions = ["PDF", "DOCX", "XLSX", "SQL", "ENV", "LOG", "BAK", "CONF", "YML", "JSON"]
        for ext in extensions:
            btn = QPushButton(ext)
            btn.setCheckable(True)
            btn.setProperty("class", "chip-btn")
            btn.clicked.connect(self.compile_form_to_query)
            self.filetype_buttons[ext] = btn
            pills_layout.addWidget(btn)

        clear_pills_btn = QPushButton("Clear Types")
        clear_pills_btn.clicked.connect(self.clear_filetype_pills)
        pills_layout.addWidget(clear_pills_btn)
        pills_layout.addStretch()

        form_grid.addLayout(pills_layout, 3, 0, 1, 4)
        layout.addWidget(form_box)

    def clear_filetype_pills(self):
        for btn in self.filetype_buttons.values():
            btn.setChecked(False)
        self.compile_form_to_query()

    def compile_form_to_query(self):
        if self._updating_form:
            return

        target = self.target_scope_input.text().strip()
        combo_idx = self.target_type_combo.currentIndex()
        t_type = self.get_resolved_target_type(target, combo_idx)

        query_parts = []

        # 1. Target Scope
        if target:
            if t_type == "DOMAIN":
                clean = DorkEngine.clean_target_domain(target)
                if clean:
                    query_parts.append(f"site:{clean}")
            else:
                query_parts.append(f'"{target}"')

        # 2. Title
        title = self.form_title_input.text().strip()
        if title:
            terms = [t.strip() for t in title.split(",") if t.strip()]
            if len(terms) == 1:
                query_parts.append(f'intitle:"{terms[0]}"' if " " in terms[0] else f'intitle:{terms[0]}')
            elif len(terms) > 1:
                formatted = " OR ".join([f'intitle:"{t}"' if " " in t else f'intitle:{t}' for t in terms])
                query_parts.append(f"({formatted})")

        # 3. URL
        url_text = self.form_url_input.text().strip()
        if url_text:
            terms = [t.strip() for t in url_text.split(",") if t.strip()]
            if len(terms) == 1:
                query_parts.append(f'inurl:"{terms[0]}"' if " " in terms[0] else f'inurl:{terms[0]}')
            elif len(terms) > 1:
                formatted = " OR ".join([f'inurl:"{t}"' if " " in t else f'inurl:{t}' for t in terms])
                query_parts.append(f"({formatted})")

        # 4. Body Content
        body_text = self.form_text_input.text().strip()
        if body_text:
            terms = [t.strip() for t in body_text.split(",") if t.strip()]
            if len(terms) == 1:
                query_parts.append(f'intext:"{terms[0]}"' if " " in terms[0] else f'intext:{terms[0]}')
            elif len(terms) > 1:
                formatted = " OR ".join([f'intext:"{t}"' if " " in t else f'intext:{t}' for t in terms])
                query_parts.append(f"({formatted})")

        # 5. Exact Phrase
        exact = self.form_exact_input.text().strip()
        if exact:
            clean_exact = exact.strip('"')
            query_parts.append(f'"{clean_exact}"')

        # 6. File Types
        selected_exts = [ext.lower() for ext, btn in self.filetype_buttons.items() if btn.isChecked()]
        if selected_exts:
            if len(selected_exts) == 1:
                query_parts.append(f"filetype:{selected_exts[0]}")
            else:
                formatted = " OR ".join([f"filetype:{e}" for e in selected_exts])
                query_parts.append(f"({formatted})")

        # 7. Exclusions
        exclude_text = self.form_exclude_input.text().strip()
        if exclude_text:
            for term in [t.strip() for t in exclude_text.split(",") if t.strip()]:
                if "." in term and " " not in term:
                    query_parts.append(f"-site:{term}")
                else:
                    query_parts.append(f"-{term}")

        final_query = " ".join(query_parts)
        self.query_editor.blockSignals(True)
        self.query_editor.setText(final_query)
        self.query_editor.blockSignals(False)
        self.on_query_changed()

    def build_recipes_mode(self):
        layout = QVBoxLayout(self.recipes_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        recipes_box = QGroupBox("Goal-Based Dork Recipes & Search Operators")
        recipes_layout = QVBoxLayout(recipes_box)
        recipes_layout.setSpacing(10)

        # Template Search Filter Bar
        tmpl_bar = QHBoxLayout()
        tmpl_label = QLabel("Search Recipes:")
        self.tmpl_filter_input = QLineEdit()
        self.tmpl_filter_input.setPlaceholderText("Filter 35+ recipes by objective (e.g. person, resume, email, password, aws, admin)...")
        self.tmpl_filter_input.textChanged.connect(self.filter_templates)

        self.template_combo = QComboBox()
        self.template_combo.currentIndexChanged.connect(self.on_template_selected)

        tmpl_bar.addWidget(tmpl_label)
        tmpl_bar.addWidget(self.tmpl_filter_input, 1)
        tmpl_bar.addWidget(self.template_combo, 2)
        recipes_layout.addLayout(tmpl_bar)

        # Quick Operator Grid
        op_label = QLabel("Manual Operator Insertion:")
        op_label.setStyleSheet("color: #8b949e; font-weight: 600;")
        recipes_layout.addWidget(op_label)

        ops_grid = QGridLayout()
        ops_grid.setSpacing(6)
        operators = [
            ("site:", "site:"),
            ("inurl:", "inurl:"),
            ("intitle:", "intitle:"),
            ("intext:", "intext:"),
            ("filetype:", "filetype:"),
            ("ext:", "ext:"),
            ("allinurl:", "allinurl:"),
            ("allintitle:", "allintitle:"),
            ("cache:", "cache:"),
            ("-site:", "-site:"),
            ("OR", " OR "),
            ('"exact phrase"', '""')
        ]
        for idx, (label, token) in enumerate(operators):
            btn = QPushButton(label)
            btn.clicked.connect(lambda _, t=token: self.insert_token(t))
            ops_grid.addWidget(btn, idx // 6, idx % 6)

        recipes_layout.addLayout(ops_grid)
        layout.addWidget(recipes_box)

    def build_auto_mode(self):
        layout = QVBoxLayout(self.auto_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Categories Multi-Select Frame
        cat_box = QGroupBox("Automated Reconnaissance Categories")
        cat_vbox = QVBoxLayout(cat_box)
        cat_grid = QGridLayout()
        cat_grid.setSpacing(8)

        self.category_checkboxes.clear()
        for idx, (cat_id, name, default_chk, desc) in enumerate(DorkEngine.CATEGORIES):
            cb = QCheckBox(name)
            cb.setChecked(default_chk)
            cb.setToolTip(desc)
            self.category_checkboxes.append((cat_id, cb))
            cat_grid.addWidget(cb, idx // 3, idx % 3)

        cat_vbox.addLayout(cat_grid)

        # Quick Presets Bar
        preset_bar = QHBoxLayout()
        preset_label = QLabel("Quick Presets:")
        preset_label.setStyleSheet("color: #8b949e; font-weight: 600;")

        domain_preset_btn = QPushButton("Domain Recon")
        domain_preset_btn.clicked.connect(self.apply_domain_preset)

        email_preset_btn = QPushButton("Email OSINT")
        email_preset_btn.clicked.connect(self.apply_email_preset)

        person_preset_btn = QPushButton("Person OSINT")
        person_preset_btn.clicked.connect(self.apply_person_preset)

        user_preset_btn = QPushButton("Username OSINT")
        user_preset_btn.clicked.connect(self.apply_username_preset)

        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(lambda: [cb.setChecked(True) for _, cb in self.category_checkboxes])
        select_none_btn = QPushButton("Deselect All")
        select_none_btn.clicked.connect(lambda: [cb.setChecked(False) for _, cb in self.category_checkboxes])

        preset_bar.addWidget(preset_label)
        preset_bar.addWidget(domain_preset_btn)
        preset_bar.addWidget(email_preset_btn)
        preset_bar.addWidget(person_preset_btn)
        preset_bar.addWidget(user_preset_btn)
        preset_bar.addSpacing(12)
        preset_bar.addWidget(select_all_btn)
        preset_bar.addWidget(select_none_btn)
        preset_bar.addStretch()
        cat_vbox.addLayout(preset_bar)

        layout.addWidget(cat_box)

        # Execution Controls
        exec_bar = QHBoxLayout()
        self.run_sweep_btn = QPushButton("Launch Automated API Sweep")
        self.run_sweep_btn.setObjectName("primaryBtn")
        self.run_sweep_btn.clicked.connect(self.run_auto_sweep)

        self.preview_dorks_btn = QPushButton("Preview Generated Dorks")
        self.preview_dorks_btn.clicked.connect(self.preview_dork_queries)

        exec_bar.addWidget(self.run_sweep_btn)
        exec_bar.addWidget(self.preview_dorks_btn)
        exec_bar.addStretch()
        layout.addLayout(exec_bar)

    def get_resolved_target_type(self, target_text: str, combo_idx: int) -> str:
        if combo_idx == 1:
            return "DOMAIN"
        elif combo_idx == 2:
            return "EMAIL"
        elif combo_idx == 3:
            return "PERSON"
        elif combo_idx == 4:
            return "KEYWORD"
        else:
            return DorkEngine.detect_target_type(target_text)

    def on_target_input_changed(self):
        target = self.target_scope_input.text().strip()
        combo_idx = self.target_type_combo.currentIndex()
        if not target:
            self.type_badge.setText("Detected: None")
            return

        t_type = self.get_resolved_target_type(target, combo_idx)
        type_names = {
            "DOMAIN": "Domain / Host",
            "EMAIL": "Email Address",
            "PERSON": "Person Name",
            "KEYWORD": "Username / Keyword"
        }
        self.type_badge.setText(f"Type: {type_names.get(t_type, 'General')}")
        if self.builder_radio.isChecked():
            self.compile_form_to_query()

    def apply_domain_preset(self):
        domain_cats = {"basic_info", "files", "directories", "login_pages", "vulnerabilities",
                       "credentials", "backup_files", "subdomains", "technologies", "cloud_storage", "code_repos"}
        for cat_id, cb in self.category_checkboxes:
            cb.setChecked(cat_id in domain_cats)

    def apply_email_preset(self):
        email_cats = {"basic_info", "files", "directories", "login_pages", "vulnerabilities",
                      "credentials", "backup_files", "social_media", "email_harvest", "person_search", "code_repos"}
        for cat_id, cb in self.category_checkboxes:
            cb.setChecked(cat_id in email_cats)

    def apply_person_preset(self):
        person_cats = {"basic_info", "files", "directories", "login_pages", "vulnerabilities",
                       "credentials", "social_media", "email_harvest", "person_search", "code_repos"}
        for cat_id, cb in self.category_checkboxes:
            cb.setChecked(cat_id in person_cats)

    def apply_username_preset(self):
        user_cats = {"basic_info", "files", "login_pages", "vulnerabilities",
                     "credentials", "social_media", "email_harvest", "person_search", "code_repos"}
        for cat_id, cb in self.category_checkboxes:
            cb.setChecked(cat_id in user_cats)

    def populate_templates(self):
        self.all_templates = []
        for section, items in DorkEngine.TEMPLATES.items():
            for title, query in items:
                self.all_templates.append((section, title, query))
        self.filter_templates()

    def filter_templates(self):
        filter_text = self.tmpl_filter_input.text().strip().lower()
        self.template_combo.blockSignals(True)
        self.template_combo.clear()
        self.template_combo.addItem("-- Select Pre-Configured Recipe --", "")

        current_section = ""
        for section, title, query in self.all_templates:
            if not filter_text or filter_text in section.lower() or filter_text in title.lower() or filter_text in query.lower():
                if section != current_section and not filter_text:
                    current_section = section
                label = f"[{section}] {title}" if filter_text else f"{title}"
                self.template_combo.addItem(label, query)

        self.template_combo.blockSignals(False)

    def on_template_selected(self, index: int):
        if index <= 0:
            return
        query = self.template_combo.currentData()
        if not query:
            return

        target = self.target_scope_input.text().strip()
        if target:
            combo_idx = self.target_type_combo.currentIndex()
            t_type = self.get_resolved_target_type(target, combo_idx)
            if t_type == "DOMAIN":
                clean_domain = DorkEngine.clean_target_domain(target)
                if clean_domain and "site:" not in query:
                    final_query = f"site:{clean_domain} {query}"
                else:
                    final_query = query
            else:
                final_query = f'"{target}" {query}'
        else:
            final_query = query

        self.query_editor.setText(final_query)

    def insert_token(self, token: str):
        cursor = self.query_editor.textCursor()
        cursor.insertText(token)
        self.query_editor.setTextCursor(cursor)
        self.query_editor.setFocus()

    def on_query_changed(self):
        query = self.query_editor.toPlainText()
        analysis = DorkEngine.analyze_query(query)

        self.char_count_label.setText(f"{analysis['chars']} chars | {analysis['words']} words")

        # Update Complexity Badge
        comp = analysis['complexity']
        if comp == "Advanced":
            self.complexity_badge.setText("Complexity: High")
            self.complexity_badge.setStyleSheet("color: #f85149; font-size: 12px; font-weight: bold;")
        elif comp == "Moderate":
            self.complexity_badge.setText("Complexity: Medium")
            self.complexity_badge.setStyleSheet("color: #d29922; font-size: 12px; font-weight: bold;")
        elif comp == "Simple":
            self.complexity_badge.setText("Complexity: Low")
            self.complexity_badge.setStyleSheet("color: #7ee787; font-size: 12px; font-weight: bold;")
        else:
            self.complexity_badge.setText("Complexity: Empty")
            self.complexity_badge.setStyleSheet("color: #8b949e; font-size: 12px; font-weight: bold;")

        # Update Operators
        if analysis["operators"]:
            self.detected_ops_label.setText(f"Operators: {', '.join(analysis['operators'])}")
        else:
            self.detected_ops_label.setText("Operators: None")

        # Update Plain-English Explanation
        self.explainer_label.setText(f"Plain English: {analysis['explanation']}")

    def run_api_search(self):
        query = self.query_editor.toPlainText().strip()
        if not query:
            QMessageBox.warning(self, "Empty Query", "Please enter a valid search query.")
            return
        self.on_run_api_search(query, "Manual Search")

    def run_browser_search(self):
        query = self.query_editor.toPlainText().strip()
        if not query:
            QMessageBox.warning(self, "Empty Query", "Please enter a valid search query.")
            return
        self.bookmarks_mgr.add_history(query, 0, mode="Browser")
        encoded = urllib.parse.quote_plus(query)
        search_url = f"https://www.google.com/search?q={encoded}"
        QDesktopServices.openUrl(QUrl(search_url))
        window = self.window()
        if hasattr(window, "show_toast"):
            window.show_toast("Opening query in default web browser...")

    def save_as_bookmark(self):
        query = self.query_editor.toPlainText().strip()
        if not query:
            QMessageBox.warning(self, "Empty Query", "Cannot bookmark an empty query.")
            return
        title = self.template_combo.currentText()
        if not title or title.startswith("--"):
            title = f"Dork: {query[:30]}"
        self.bookmarks_mgr.add_bookmark(title=title, query=query, category="Custom")
        window = self.window()
        if hasattr(window, "show_toast"):
            window.show_toast("Query bookmarked successfully.")

    def copy_query_to_clipboard(self):
        query = self.query_editor.toPlainText().strip()
        if query:
            QApplication.clipboard().setText(query)
            window = self.window()
            if hasattr(window, "show_toast"):
                window.show_toast("Query copied to clipboard.")

    def clear_editor(self):
        self.query_editor.clear()
        self.form_title_input.clear()
        self.form_url_input.clear()
        self.form_text_input.clear()
        self.form_exact_input.clear()
        self.form_exclude_input.clear()
        for btn in self.filetype_buttons.values():
            btn.setChecked(False)

    def set_active_query(self, query: str):
        self.query_editor.setText(query)

    def get_selected_categories(self) -> List[str]:
        return [cat_id for cat_id, cb in self.category_checkboxes if cb.isChecked()]

    def run_auto_sweep(self):
        target = self.target_scope_input.text().strip()
        if not target:
            QMessageBox.warning(self, "Missing Target", "Please enter a target (domain, email, person name, or username).")
            return
        selected = self.get_selected_categories()
        if not selected:
            QMessageBox.warning(self, "No Categories", "Please select at least one reconnaissance category.")
            return

        combo_idx = self.target_type_combo.currentIndex()
        t_type = self.get_resolved_target_type(target, combo_idx)
        self.on_run_batch_recon(target, selected, t_type)

    def preview_dork_queries(self):
        target = self.target_scope_input.text().strip()
        if not target:
            QMessageBox.warning(self, "Missing Target", "Please enter a target to generate queries.")
            return
        selected = self.get_selected_categories()
        if not selected:
            QMessageBox.warning(self, "No Categories", "Please select at least one category to preview.")
            return

        combo_idx = self.target_type_combo.currentIndex()
        t_type = self.get_resolved_target_type(target, combo_idx)
        dorks = DorkEngine.generate_dorks(target, selected, target_type=t_type)

        preview_text = f"Generated {len(dorks)} Dork Queries for target: {target} (Type: {t_type})\n\n"
        for idx, (cat, q) in enumerate(dorks, 1):
            preview_text += f"[{idx}] ({cat})\n    {q}\n\n"

        preview_dialog = QMessageBox(self)
        preview_dialog.setWindowTitle("Generated Dorks Preview")
        preview_dialog.setText(f"Previewing {len(dorks)} generated queries (Target Type: {t_type}):")
        preview_dialog.setDetailedText(preview_text)
        preview_dialog.exec()
