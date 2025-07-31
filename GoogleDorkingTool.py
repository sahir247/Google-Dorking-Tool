#!/usr/bin/env python3
"""
Key Features
------------
1. 🔐 Secure Credential Management (Fernet encryption, validation dialog)
2. 🌐 Google Custom Search API with AdvancedRateLimiter (burst & RPS control)
3. 🗂️ Multi-Tab Interface: Search, Results, Help & Info
4. 🤖 Auto-Dorking with 14 categories & intelligent query generation
5. 🛠️ Manual Dork Builder with 19+ operators & template library
6. 🖥️ Responsive GUI via QThread-based GoogleSearchWorker
7. 📊 Results Pagination, Preview, and Export (CSV, JSON, TXT)
8. 💾 Query Save / Load for re-usability
9. 🔍 Site-Specific Search toggle & SafeSearch option
10. 📚 Built-in Help & Documentation pane

Developed for security researchers and penetration testers.
Use responsibly and comply with all relevant laws.
"""

import sys
import os
import json
import csv
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional

import requests
from cryptography.fernet import Fernet

from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QMutex, QMutexLocker, QUrl
)
from PyQt5.QtGui import QFont, QIcon, QDesktopServices
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QComboBox, QGroupBox, QGridLayout,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar,
    QCheckBox, QFileDialog, QMessageBox, QDialog, QDialogButtonBox,
    QFormLayout
)

# --------------------------- Data Classes ----------------------------------

class SearchResult:
    """Container for a single search result"""
    def __init__(self, title: str, url: str, description: str,
                 timestamp: str = "", dork: str = "", category: str = ""):
        self.title = title
        self.url = url
        self.description = description
        self.timestamp = timestamp or datetime.now().isoformat(timespec='seconds')
        self.dork = dork
        self.category = category

# ------------------------ Credential Management ---------------------------

class CredentialManager:
    """Encrypts and stores API credentials locally"""
    def __init__(self):
        self.dir = Path.home() / '.google_dorking_tool'
        self.dir.mkdir(exist_ok=True)
        self.key_file = self.dir / '.key'
        self.cred_file = self.dir / 'creds.dat'
        self.key = self._load_or_create_key()

    def _load_or_create_key(self) -> bytes:
        if self.key_file.exists():
            return self.key_file.read_bytes()
        key = Fernet.generate_key()
        self.key_file.write_bytes(key)
        if os.name != 'nt':
            self.key_file.chmod(0o600)
        return key

    def save(self, api_key: str, cse_id: str) -> bool:
        data = {
            'api_key': api_key,
            'cse_id': cse_id,
            'saved': datetime.now().isoformat()
        }
        try:
            token = Fernet(self.key).encrypt(json.dumps(data).encode())
            self.cred_file.write_bytes(token)
            if os.name != 'nt':
                self.cred_file.chmod(0o600)
            return True
        except Exception as e:
            print(e)
            return False

    def load(self) -> Optional[Dict[str, str]]:
        if not self.cred_file.exists():
            return None
        try:
            token = self.cred_file.read_bytes()
            data = json.loads(Fernet(self.key).decrypt(token).decode())
            return data
        except Exception as e:
            print(e)
            return None

    def validate(self, api_key: str, cse_id: str) -> Tuple[bool, str]:
        url = 'https://www.googleapis.com/customsearch/v1'
        try:
            r = requests.get(url, params={'key': api_key, 'cx': cse_id, 'q': 'test', 'num': 1}, timeout=10)
            if r.status_code == 200:
                return True, 'Credentials valid!'
            return False, f'HTTP {r.status_code}: {r.text[:60]}'
        except Exception as e:
            return False, str(e)

# --------------------------- Rate Limiter ---------------------------------

class AdvancedRateLimiter:
    def __init__(self, rps: float = 1.0, daily: int = 100):
        self.rps = rps
        self.daily = daily
        self.day = datetime.utcnow().date()
        self.count_today = 0
        self.last = 0.0
        self.lock = QMutex()

    def wait(self):
        with QMutexLocker(self.lock):
            now = time.time()
            if datetime.utcnow().date() != self.day:
                self.day = datetime.utcnow().date()
                self.count_today = 0
            if self.count_today >= self.daily:
                raise RuntimeError('Daily quota exceeded')
            delta = now - self.last
            min_interval = 1.0 / self.rps
            if delta < min_interval:
                time.sleep(min_interval - delta)
            self.last = time.time()
            self.count_today += 1

# -------------------------- Worker Thread ---------------------------------

class GoogleSearchWorker(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, api_key: str, cse_id: str, queries: List[Tuple[str, str]], limiter: AdvancedRateLimiter):
        super().__init__()
        self.api_key = api_key
        self.cse_id = cse_id
        self.queries = queries  # list of (query, category)
        self.limiter = limiter
        self.session = requests.Session()

    def run(self):
        results = []
        total = len(self.queries)
        for idx, (query, category) in enumerate(self.queries):
            try:
                self.limiter.wait()
            except Exception as e:
                self.error.emit(str(e))
                return
            try:
                url = 'https://www.googleapis.com/customsearch/v1'
                resp = self.session.get(url, params={
                    'key': self.api_key,
                    'cx': self.cse_id,
                    'q': query,
                    'num': 10,
                    'safe': 'off'
                }, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                for item in data.get('items', []):
                    results.append(SearchResult(
                        title=item.get('title', ''),
                        url=item.get('link', ''),
                        description=item.get('snippet', ''),
                        dork=query,
                        category=category
                    ))
            except Exception as e:
                self.error.emit(f'Query "{query}" failed: {e}')
                return
            self.progress.emit(int((idx + 1)/total*100))
        self.finished.emit(results)

# ---------------------------- Main GUI ------------------------------------

class GoogleDorkingApp(QMainWindow):
    CATEGORY_MAP = [
        ('basic_info', 'Basic Information', '"{target}"'),
        ('files', 'Sensitive Files', 'filetype:pdf | filetype:doc | filetype:xlsx {target}'),
        ('directories', 'Exposed Directories', 'intitle:"index of" {target}'),
        ('login_pages', 'Login Pages', '(inurl:login | inurl:signin | intitle:Login) {target}'),
        ('vulnerabilities', 'Potential Vulnerabilities', '(inurl:php?id= | inurl:index.php?id=) {target}'),
        ('technologies', 'Technologies', 'inurl:wp-content | inurl:wp-includes {target}'),
        ('social_media', 'Social Media', 'site:twitter.com {target}'),
        ('email', 'Email Addresses', '"@{target}"'),
        ('subdomains', 'Subdomains', 'site:*.{target} -www'),
        ('person_search', 'Person Search', '{target} "curriculum vitae"'),
        ('profiles', 'Profile Pages', '{target} "profile"'),
        ('images', 'Images', 'site:{target} filetype:png | filetype:jpg'),
        ('news', 'News Articles', 'site:news {target}'),
        ('academic', 'Academic/Publications', '{target} filetype:pdf')
    ]

    OPERATORS = ['site:', 'inurl:', 'intext:', 'filetype:', 'intitle:', 'link:', 'cache:', 'info:',
                 'related:', 'before:', 'after:', 'allintext:', 'allinurl:', 'allintitle:', 'ext:',
                 'OR', 'AND', '-']

    TEMPLATES = [
        'Find exposed documents (filetype:pdf | filetype:doc | filetype:xlsx site:example.com)',
        'Find login pages (inurl:login | inurl:signin | intitle:Login)',
        'Find vulnerable pages (inurl:php?id= | inurl:index.php?id=)',
        'Find exposed directories (intitle:"Index of" | intitle:"Directory Listing")',
        'Find config files (filetype:xml | filetype:conf | filetype:cnf | filetype:reg)',
        'Find database files (filetype:sql | filetype:db | filetype:dbf)',
        'Find backup files (filetype:bak | filetype:backup | filetype:old)',
        'Find exposed credentials (intext:username filetype:log | intext:password filetype:log)',
        'Find Jenkins instances (intitle:"Dashboard [Jenkins]")'
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Google Dorking Tool v1.1')
        self.setGeometry(100, 100, 1200, 800)
        self.cred_mgr = CredentialManager()
        creds = self.cred_mgr.load() or {}
        self.api_key = creds.get('api_key', '')
        self.cse_id = creds.get('cse_id', '')
        self.limiter = AdvancedRateLimiter()
        self.current_results: List[SearchResult] = []
        self.current_page = 1
        self.per_page = 10
        self._build_ui()

    # -------------------- UI Builders ----------------------

    def _build_ui(self):
        central = QWidget()
        layout = QVBoxLayout(central)
        self.setCentralWidget(central)

        # Mode selector
        mode_layout = QHBoxLayout()
        mode_label = QLabel('Mode:')
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(['Manual Dorking', 'Auto Dorking'])
        self.mode_combo.currentIndexChanged.connect(self._toggle_mode)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        # Tabs
        self.tabs = QTabWidget()
        self.search_tab = QWidget()
        self.results_tab = QWidget()
        self.help_tab = QWidget()
        self.cred_tab = QWidget()
        self.tabs.addTab(self.search_tab, 'Search')
        self.tabs.addTab(self.results_tab, 'Results')
        self.tabs.addTab(self.help_tab, 'Help & Info')
        self.tabs.addTab(self.cred_tab, 'API Credentials')
        layout.addWidget(self.tabs)

        # Add Configure API Credentials button to the top right
        cred_btn_layout = QHBoxLayout()
        cred_btn_layout.addStretch()
        self.cred_tab_btn = QPushButton('Configure API Credentials')
        cred_btn_layout.addWidget(self.cred_tab_btn)
        layout.insertLayout(0, cred_btn_layout)
        self.cred_tab_btn.clicked.connect(lambda: self.tabs.setCurrentWidget(self.cred_tab))

        self._build_search_tab()
        self._build_results_tab()
        self._build_help_tab()
        self._build_cred_tab()

        # Status
        status_layout = QHBoxLayout()
        self.status_label = QLabel('Ready')
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.progress)
        layout.addLayout(status_layout)

    def _build_search_tab(self):
        layout = QVBoxLayout(self.search_tab)

        # Auto group
        self.auto_group = QGroupBox('Auto Dorking')
        auto_layout = QGridLayout()
        auto_layout.addWidget(QLabel('Target:'), 0, 0)
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText('example.com or keyword')
        auto_layout.addWidget(self.target_input, 0, 1, 1, 2)

        auto_layout.addWidget(QLabel('Categories:'), 1, 0)
        self.category_checks: Dict[str, QCheckBox] = {}
        row = 1
        col = 1
        for cat_id, cat_name, _ in self.CATEGORY_MAP:
            cb = QCheckBox(cat_name)
            cb.setChecked(True)
            self.category_checks[cat_id] = cb
            auto_layout.addWidget(cb, row, col)
            col += 1
            if col > 3:
                col = 1
                row += 1
        self.run_auto_btn = QPushButton('Generate & Run Dorks')
        auto_layout.addWidget(self.run_auto_btn, row+1, 0, 1, 3)
        self.run_auto_btn.clicked.connect(self._run_auto)
        self.auto_group.setLayout(auto_layout)
        layout.addWidget(self.auto_group)

        # Manual group
        self.manual_group = QGroupBox('Manual Dorking')
        man_layout = QGridLayout()
        man_layout.addWidget(QLabel('Query:'), 0, 0)
        self.query_input = QLineEdit()
        man_layout.addWidget(self.query_input, 0, 1, 1, 3)

        man_layout.addWidget(QLabel('Operator:'), 1, 0)
        self.op_combo = QComboBox(); self.op_combo.addItems(self.OPERATORS)
        man_layout.addWidget(self.op_combo, 1, 1)
        self.op_value = QLineEdit(); self.op_value.setPlaceholderText('value')
        man_layout.addWidget(self.op_value, 1, 2)
        add_op_btn = QPushButton('Add'); add_op_btn.clicked.connect(self._add_operator)
        man_layout.addWidget(add_op_btn, 1, 3)

        man_layout.addWidget(QLabel('Template:'), 2, 0)
        self.tpl_combo = QComboBox(); self.tpl_combo.addItems(['Select...'] + self.TEMPLATES)
        man_layout.addWidget(self.tpl_combo, 2, 1, 1, 3)
        self.tpl_combo.currentIndexChanged.connect(self._apply_template)

        man_layout.addWidget(QLabel('Results per page:'), 3, 0)
        self.per_page_combo = QComboBox(); self.per_page_combo.addItems(['10','20','50','100'])
        man_layout.addWidget(self.per_page_combo, 3, 1)
        self.safe_cb = QCheckBox('Safe Search'); self.safe_cb.setChecked(True)
        man_layout.addWidget(self.safe_cb, 3, 2)

        self.site_cb = QCheckBox('Site specific')
        self.site_cb.toggled.connect(lambda b: self.site_input.setEnabled(b))
        man_layout.addWidget(self.site_cb, 4, 0)
        self.site_input = QLineEdit(); self.site_input.setEnabled(False)
        self.site_input.setPlaceholderText('example.com')
        man_layout.addWidget(self.site_input, 4, 1, 1, 2)

        # Control buttons
        ctrl_layout = QHBoxLayout()
        self.search_btn = QPushButton('Search'); ctrl_layout.addWidget(self.search_btn)
        self.clear_btn = QPushButton('Clear'); ctrl_layout.addWidget(self.clear_btn)
        self.saveq_btn = QPushButton('Save Query'); ctrl_layout.addWidget(self.saveq_btn)
        self.loadq_btn = QPushButton('Load Query'); ctrl_layout.addWidget(self.loadq_btn)
        man_layout.addLayout(ctrl_layout, 5, 0, 1, 4)

        self.manual_group.setLayout(man_layout)
        layout.addWidget(self.manual_group)

        self.preview = QTextEdit(); self.preview.setReadOnly(True)
        layout.addWidget(self.preview)

        # Connections
        self.search_btn.clicked.connect(self._run_manual)
        self.clear_btn.clicked.connect(self.query_input.clear)
        self.saveq_btn.clicked.connect(self._save_query)
        self.loadq_btn.clicked.connect(self._load_query)

        # Initially show manual group, hide auto if selected
        self._toggle_mode(0)

    def _build_results_tab(self):
        layout = QVBoxLayout(self.results_tab)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(['Title', 'URL', 'Description', 'Category'])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        layout.addWidget(self.table)

        # Pagination & export
        btn_layout = QHBoxLayout()
        self.prev_btn = QPushButton('Prev'); self.prev_btn.clicked.connect(lambda: self._change_page(-1))
        self.next_btn = QPushButton('Next'); self.next_btn.clicked.connect(lambda: self._change_page(1))
        self.page_lbl = QLabel('Page 1')
        btn_layout.addWidget(self.prev_btn); btn_layout.addWidget(self.page_lbl); btn_layout.addWidget(self.next_btn)
        btn_layout.addStretch()
        self.export_csv = QPushButton('CSV'); self.export_csv.clicked.connect(lambda: self._export('csv'))
        self.export_json = QPushButton('JSON'); self.export_json.clicked.connect(lambda: self._export('json'))
        self.export_txt = QPushButton('TXT'); self.export_txt.clicked.connect(lambda: self._export('txt'))
        btn_layout.addWidget(self.export_csv); btn_layout.addWidget(self.export_json); btn_layout.addWidget(self.export_txt)
        layout.addLayout(btn_layout)

        self._update_pagination()

    def _build_help_tab(self):
        """Creates and adds a Help tab with documentation/instructions, clickable links, and a clickable GitHub logo."""
        self.help_tab = QWidget()
        layout = QVBoxLayout(self.help_tab)
        github_logo_path = 'file:///C:/Users/LENOVO/Downloads/github-mark.png'
        help_html = f'''
        <h2>Comprehensive Google Dorking Tool - Help</h2>
        <p style="color:#b22222;"><b>⚠️ WARNING: This tool is for educational and authorized security research purposes only. The developer is not responsible for misuse. Use responsibly and comply with all laws and terms of service.</b></p>
        <h3>User Guide</h3>
        <ol>
            <li><b>Configure API Credentials:</b> Enter your Google API Key and Custom Search Engine (CSE) ID in the Credentials tab.</li>
            <li><b>Manual Dorking:</b> Go to the Manual Dorking tab to enter custom queries. Use operators to refine your search.</li>
            <li><b>Auto Dorking:</b> Enter a domain or keyword, select categories, and let the tool generate dorks automatically.</li>
            <li><b>View Results:</b> Check the Results tab for search results. You can paginate and export results as CSV, JSON, or TXT.</li>
            <li><b>Save/Load Queries:</b> Save your favorite queries for later, or load previous ones.</li>
        </ol>
        <h3>How to Get API Key & CSE ID</h3>
        <ul>
            <li><b>API Key:</b> Visit <a href="https://console.developers.google.com/apis/credentials">Google Cloud Console</a>, create a project, enable the Custom Search API, and generate an API key.</li>
            <li><b>CSE ID:</b> Go to <a href="https://cse.google.com/cse/all">Google Custom Search Engine</a>, create a new search engine (set it to search the entire web), and copy the CSE ID.</li>
        </ul>
        <p>For more details, see the <a href="https://developers.google.com/custom-search/v1/overview">Google Custom Search API Documentation</a>.</p>
        <h3>Contact Developer</h3>
        <p align="center">
            <a href="https://github.com/sahir247/Google-Dorking-Tool">
                <img src="{github_logo_path}" alt="GitHub" width="48" style="vertical-align:middle;">
            </a>
        </p>
        '''
        help_label = QLabel()
        help_label.setText(help_html)
        help_label.setOpenExternalLinks(True)
        help_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        help_label.setWordWrap(True)
        layout.addWidget(help_label)
        self.tabs.addTab(self.help_tab, 'Help')

        # Remove duplicate Help/Info tab if it exists
        for i in range(self.tabs.count()-1):
            if self.tabs.tabText(i).lower() in ('help', 'help & info', 'help/info', 'info'):
                self.tabs.removeTab(i)
                break

    def _build_cred_tab(self):
        layout = QVBoxLayout(self.cred_tab)
        cred_box = QGroupBox('Google API Credentials')
        cred_layout = QFormLayout()
        self.api_key_input = QLineEdit(); self.api_key_input.setPlaceholderText('API Key')
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.cse_id_input = QLineEdit(); self.cse_id_input.setPlaceholderText('CSE ID')
        self.save_cred_btn = QPushButton('Save')
        self.cred_status = QLabel('')
        self.cred_status.setStyleSheet('color: #006600')
        cred_layout.addRow('API Key:', self.api_key_input)
        cred_layout.addRow('CSE ID:', self.cse_id_input)
        cred_layout.addRow(self.save_cred_btn, self.cred_status)
        cred_box.setLayout(cred_layout)
        layout.addWidget(cred_box)
        layout.addStretch()
        creds = self.cred_mgr.load() or {}
        self.api_key_input.setText(creds.get('api_key', ''))
        self.cse_id_input.setText(creds.get('cse_id', ''))
        def save_creds():
            api = self.api_key_input.text().strip()
            cse = self.cse_id_input.text().strip()
            ok, msg = self.cred_mgr.validate(api, cse)
            if ok:
                self.cred_mgr.save(api, cse)
                self.cred_status.setText('Saved!')
                self.cred_status.setStyleSheet('color: #006600')
                self.api_key = api
                self.cse_id = cse
            else:
                self.cred_status.setText(msg)
                self.cred_status.setStyleSheet('color: #990000')
        self.save_cred_btn.clicked.connect(save_creds)

    def _toggle_mode(self, idx: int):
        is_manual = idx == 0
        self.manual_group.setVisible(is_manual)
        self.auto_group.setVisible(not is_manual)

    # ------------------ Manual Functions -------------------

    def _add_operator(self):
        op = self.op_combo.currentText()
        val = self.op_value.text().strip()
        if op and val:
            snippet = f' {op}{val} '
            self.query_input.insert(snippet)
            self.op_value.clear()

    def _apply_template(self, idx: int):
        if idx > 0:
            self.query_input.setText(self.TEMPLATES[idx-1])
            self.tpl_combo.setCurrentIndex(0)

    def _save_query(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Save Query', 'query.txt', 'Text (*.txt)')
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.query_input.text())

    def _load_query(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Load Query', '', 'Text (*.txt)')
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                self.query_input.setText(f.read())

    # ------------------ Auto Dorking -----------------------

    def _run_auto(self):
        target = self.target_input.text().strip()
        if not target:
            QMessageBox.warning(self, 'Input missing', 'Enter a target keyword or domain')
            return
        queries = []
        for cat_id, cat_name, pattern in self.CATEGORY_MAP:
            if self.category_checks[cat_id].isChecked():
                q = pattern.replace('{target}', target)
                queries.append((q, cat_name))
        if not queries:
            QMessageBox.warning(self, 'No categories', 'Select at least one category')
            return
        self._execute_queries(queries)

    # ------------------ Manual Search ---------------------

    def _run_manual(self):
        q = self.query_input.text().strip()
        if not q:
            QMessageBox.warning(self, 'Input missing', 'Enter a query')
            return
        if self.site_cb.isChecked() and self.site_input.text().strip():
            site = self.site_input.text().strip().replace('http://','').replace('https://','').strip('/')
            q = f'site:{site} {q}'
        queries = [(q, 'Manual')]
        self._execute_queries(queries)

    # ------------------ Execution -------------------------

    def _execute_queries(self, queries: List[Tuple[str,str]]):
        if not self.api_key or not self.cse_id:
            QMessageBox.warning(self, 'Credentials', 'Configure API credentials first')
            self._show_cred_dialog()
            return
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.status_label.setText('Searching...')
        self.worker = GoogleSearchWorker(self.api_key, self.cse_id, queries, self.limiter)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_error(self, msg: str):
        self.status_label.setText('Error')
        self.progress.setVisible(False)
        QMessageBox.critical(self, 'Error', msg)

    def _on_finished(self, results: List[SearchResult]):
        self.current_results = results
        self.current_page = 1
        self._populate_table()
        self.status_label.setText(f'Completed. {len(results)} results')
        self.progress.setVisible(False)

    # ----------------- Table & Pagination -----------------

    def _populate_table(self):
        start = (self.current_page-1)*self.per_page
        end = start + self.per_page
        subset = self.current_results[start:end]
        self.table.setRowCount(len(subset))
        for r, res in enumerate(subset):
            self.table.setItem(r, 0, QTableWidgetItem(res.title))
            self.table.setItem(r, 1, QTableWidgetItem(res.url))
            self.table.setItem(r, 2, QTableWidgetItem(res.description))
            self.table.setItem(r, 3, QTableWidgetItem(res.category))
        self._update_pagination()

    def _change_page(self, delta: int):
        max_page = max(1, (len(self.current_results)+self.per_page-1)//self.per_page)
        self.current_page = max(1, min(max_page, self.current_page+delta))
        self._populate_table()

    def _update_pagination(self):
        max_page = max(1, (len(self.current_results)+self.per_page-1)//self.per_page)
        self.page_lbl.setText(f'Page {self.current_page}/{max_page}')
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < max_page)

    # ------------------- Export ---------------------------

    def _export(self, fmt: str):
        if not self.current_results:
            return
        fname, _ = QFileDialog.getSaveFileName(self, 'Export', f'results.{fmt}', f'{fmt.upper()} (*.{fmt})')
        if not fname:
            return
        try:
            if fmt == 'csv':
                with open(fname, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Title','URL','Description','Category','Timestamp'])
                    for res in self.current_results:
                        writer.writerow([res.title, res.url, res.description, res.category, res.timestamp])
            elif fmt == 'json':
                with open(fname, 'w', encoding='utf-8') as f:
                    json.dump([res.__dict__ for res in self.current_results], f, indent=2)
            elif fmt == 'txt':
                with open(fname, 'w', encoding='utf-8') as f:
                    for res in self.current_results:
                        f.write(f"{res.title}\n{res.url}\n{res.description}\n[{res.category}] {res.timestamp}\n\n")
            QMessageBox.information(self, 'Export', 'Export successful')
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))
            QMessageBox.information(self, 'Export', 'Export successful')
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    # ------------------ Credential Dialog -----------------

    def _show_cred_dialog(self):
        dlg = CredentialDialog(self, self.cred_mgr)
        if dlg.exec_() == QDialog.Accepted:
            creds = self.cred_mgr.load() or {}
            self.api_key = creds.get('api_key','')
            self.cse_id = creds.get('cse_id','')

# ------------------ Credential Dialog GUI ----------------

class CredentialDialog(QDialog):
    def __init__(self, parent, cred_mgr: CredentialManager):
        super().__init__(parent)
        self.mgr = cred_mgr
        self.setWindowTitle('API Credentials')
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.key_in = QLineEdit(); self.key_in.setEchoMode(QLineEdit.Password)
        self.cse_in = QLineEdit()
        form.addRow('API Key:', self.key_in)
        form.addRow('CSE ID:', self.cse_in)
        layout.addLayout(form)
        self.valid_lbl = QLabel('')
        layout.addWidget(self.valid_lbl)
        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(self._save)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
        creds = self.mgr.load()
        if creds:
            self.key_in.setText(creds.get('api_key',''))
            self.cse_in.setText(creds.get('cse_id',''))

    def _save(self):
        key = self.key_in.text().strip()
        cse = self.cse_in.text().strip()
        ok, msg = self.mgr.validate(key, cse)
        self.valid_lbl.setText(msg)
        if not ok:
            return
        if self.mgr.save(key, cse):
            self.accept()
        else:
            QMessageBox.critical(self, 'Error', 'Save failed')

# ---------------------------- Main ----------------------------------------

def main():
    app = QApplication(sys.argv)
    window = GoogleDorkingApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
