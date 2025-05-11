import sys
import json
import os
import csv
import requests
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTextEdit, QComboBox, QGroupBox, QGridLayout,
                            QScrollArea, QFrame, QSplitter, QFileDialog,
                            QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem,
                            QHeaderView, QProgressBar, QCheckBox)
from PyQt5.QtCore import Qt, QSize, QUrl
from PyQt5.QtGui import QFont, QIcon, QDesktopServices

class GoogleDorkingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Google CSE credentials
        self.api_key = 'your_api_key'
        self.cse_id = 'your_cse_id'       
        
        # Store search results
        self.current_results = []
        self.current_page = 1
        self.results_per_page = 10
        self.total_results = 0
        
        self.setWindowTitle('Advanced Google Dorking Tool')
        self.setGeometry(100, 100, 1200, 800)
        
        self.init_ui()
        
    def init_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Title
        title_label = QLabel('Advanced Google Dorking Tool')
        title_label.setFont(QFont('Arial', 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Mode selector
        mode_layout = QHBoxLayout()
        mode_label = QLabel('Mode:')
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(['Manual Dorking', 'Auto Dorking'])
        self.mode_combo.currentIndexChanged.connect(self.toggle_dorking_mode)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()
        main_layout.addLayout(mode_layout)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.search_tab = QWidget()
        self.results_tab = QWidget()
        self.help_tab = QWidget()
        
        self.tabs.addTab(self.search_tab, "Search")
        self.tabs.addTab(self.results_tab, "Results")
        self.tabs.addTab(self.help_tab, "Help & Info")
        
        main_layout.addWidget(self.tabs)
        
        # Setup search tab
        self.setup_search_tab()
        
        # Setup results tab
        self.setup_results_tab()
        
        # Setup help tab
        self.setup_help_tab()
        
        # Status bar with progress
        status_layout = QHBoxLayout()
        self.status_label = QLabel('Ready')
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        status_layout.addWidget(self.status_label, 4)
        status_layout.addWidget(self.progress_bar, 1)
        
        main_layout.addLayout(status_layout)
        
        self.setCentralWidget(main_widget)
    
    def toggle_dorking_mode(self, index):
        # Toggle between manual and auto dorking modes
        if index == 0:  # Manual
            self.auto_dork_group.setVisible(False)
            self.manual_dork_group.setVisible(True)
        else:  # Auto
            self.auto_dork_group.setVisible(True)
            self.manual_dork_group.setVisible(False)
    
    def setup_search_tab(self):
        search_layout = QVBoxLayout(self.search_tab)
        
        # Auto dorking section
        self.auto_dork_group = QGroupBox('Auto Dorking')
        auto_dork_layout = QGridLayout()
        
        # Target input
        auto_dork_layout.addWidget(QLabel('Target Name/Domain:'), 0, 0)
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText('Enter target name, domain, or IP...')
        auto_dork_layout.addWidget(self.target_input, 0, 1, 1, 2)
        
        # Dork categories
        auto_dork_layout.addWidget(QLabel('Dork Categories:'), 1, 0)
        self.categories_layout = QGridLayout()
        
        # Create checkboxes for different dork categories
        self.category_checks = {}
        categories = [
            ('basic_info', 'Basic Information', True),
            ('files', 'Sensitive Files', True),
            ('directories', 'Exposed Directories', True),
            ('login_pages', 'Login Pages', True),
            ('vulnerabilities', 'Potential Vulnerabilities', True),
            ('technologies', 'Technologies', True),
            ('social_media', 'Social Media', True),
            ('email', 'Email Addresses', True),
            ('subdomains', 'Subdomains', True),
            ('person_search', 'Person Search', True),
            ('profiles', 'Profile Pages', True),
            ('images', 'Images', True),
            ('news', 'News Articles', True),
            ('academic', 'Academic/Publications', True)
        ]
        
        row, col = 0, 0
        for i, (cat_id, cat_name, default) in enumerate(categories):
            checkbox = QCheckBox(cat_name)
            checkbox.setChecked(default)
            self.category_checks[cat_id] = checkbox
            self.categories_layout.addWidget(checkbox, row, col)
            col += 1
            if col > 2:  # 3 columns
                col = 0
                row += 1
        
        auto_dork_layout.addLayout(self.categories_layout, 1, 1, 3, 2)
        
        # Auto dork button
        self.auto_dork_btn = QPushButton('Generate & Run Dorks')
        self.auto_dork_btn.clicked.connect(self.run_auto_dorks)
        self.auto_dork_btn.setMinimumHeight(40)
        auto_dork_layout.addWidget(self.auto_dork_btn, 4, 0, 1, 3)
        
        self.auto_dork_group.setLayout(auto_dork_layout)
        search_layout.addWidget(self.auto_dork_group)
        
        # Manual search section
        self.manual_dork_group = QGroupBox('Search Options')
        search_options_layout = QGridLayout()
        
        # Search query
        search_options_layout.addWidget(QLabel('Search Query:'), 0, 0)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Enter your search query...')
        search_options_layout.addWidget(self.search_input, 0, 1, 1, 3)
        
        # Dork operators section
        search_options_layout.addWidget(QLabel('Dork Operators:'), 1, 0)
        
        # Operator type
        self.operator_combo = QComboBox()
        self.operator_combo.addItems([
            'site:', 'inurl:', 'intext:', 'filetype:', 
            'intitle:', 'link:', 'cache:', 'info:', 'related:',
            'before:', 'after:', 'allintext:', 'allinurl:', 'allintitle:',
            'ext:', 'OR', 'AND', '-', '"exact phrase"'
        ])
        search_options_layout.addWidget(self.operator_combo, 1, 1)
        
        # Operator value
        self.operator_value = QLineEdit()
        self.operator_value.setPlaceholderText('Operator value...')
        search_options_layout.addWidget(self.operator_value, 1, 2)
        
        # Add operator button
        add_operator_btn = QPushButton('Add to Query')
        add_operator_btn.clicked.connect(self.add_operator)
        search_options_layout.addWidget(add_operator_btn, 1, 3)
        
        # Common dork templates
        search_options_layout.addWidget(QLabel('Common Dorks:'), 2, 0)
        self.templates_combo = QComboBox()
        self.templates_combo.addItems([
            'Select a template...',
            'Find exposed documents (filetype:pdf | filetype:doc | filetype:xlsx site:example.com)',
            'Find login pages (inurl:login | inurl:signin | intitle:Login)',
            'Find vulnerable pages (inurl:php?id= | inurl:index.php?id=)',
            'Find exposed directories (intitle:"Index of" | intitle:"Directory Listing")',
            'Find config files (filetype:xml | filetype:conf | filetype:cnf | filetype:reg)',
            'Find database files (filetype:sql | filetype:db | filetype:dbf)',
            'Find backup files (filetype:bak | filetype:backup | filetype:old)',
            'Find exposed credentials (intext:username filetype:log | intext:password filetype:log)',
            'Find vulnerable servers (intitle:"Apache HTTP Server" intext:"error")',
            'Find WordPress sites (inurl:wp-content | inurl:wp-includes)',
            'Find exposed .git directories (inurl:/.git intitle:Index of)',
            'Find exposed .env files (intitle:index.of intext:.env)',
            'Find Jenkins instances (intitle:"Dashboard [Jenkins]")',
            'Find open Elasticsearch instances (intitle:"elasticsearch dashboards")',
            'Find open MongoDB instances (intitle:"MongoDB Status")'
        ])
        self.templates_combo.currentIndexChanged.connect(self.apply_template)
        search_options_layout.addWidget(self.templates_combo, 2, 1, 1, 3)
        
        # Advanced options
        search_options_layout.addWidget(QLabel('Results Per Page:'), 3, 0)
        self.results_count_combo = QComboBox()
        self.results_count_combo.addItems(['10', '20', '50', '100'])
        search_options_layout.addWidget(self.results_count_combo, 3, 1)
        
        # Safe search option
        self.safe_search = QCheckBox('Safe Search')
        self.safe_search.setChecked(True)
        search_options_layout.addWidget(self.safe_search, 3, 2)
        
        # Search controls
        button_layout = QHBoxLayout()
        
        self.search_button = QPushButton('Search')
        self.search_button.clicked.connect(self.perform_search)
        self.search_button.setMinimumHeight(40)
        button_layout.addWidget(self.search_button)
        
        self.clear_button = QPushButton('Clear')
        self.clear_button.clicked.connect(self.clear_search)
        self.clear_button.setMinimumHeight(40)
        button_layout.addWidget(self.clear_button)
        
        save_query_btn = QPushButton('Save Query')
        save_query_btn.clicked.connect(self.save_query)
        button_layout.addWidget(save_query_btn)
        
        load_query_btn = QPushButton('Load Query')
        load_query_btn.clicked.connect(self.load_query)
        button_layout.addWidget(load_query_btn)
        
        search_options_layout.addLayout(button_layout, 4, 0, 1, 4)
        
        self.manual_dork_group.setLayout(search_options_layout)
        search_layout.addWidget(self.manual_dork_group)
        
        # Quick results preview
        preview_group = QGroupBox('Results Preview')
        preview_layout = QVBoxLayout()
        
        self.results_preview = QTextEdit()
        self.results_preview.setReadOnly(True)
        preview_layout.addWidget(self.results_preview)
        
        preview_group.setLayout(preview_layout)
        search_layout.addWidget(preview_group)
    
    def setup_results_tab(self):
        results_layout = QVBoxLayout(self.results_tab)
        
        # Results table
        self.results_table = QTableWidget(0, 4)
        self.results_table.setHorizontalHeaderLabels(['Title', 'URL', 'Description', 'Actions'])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        results_layout.addWidget(self.results_table)
        
        # Pagination controls
        pagination_layout = QHBoxLayout()
        
        self.prev_page_btn = QPushButton('Previous Page')
        self.prev_page_btn.clicked.connect(self.previous_page)
        self.prev_page_btn.setEnabled(False)
        pagination_layout.addWidget(self.prev_page_btn)
        
        self.page_label = QLabel('Page 1')
        pagination_layout.addWidget(self.page_label)
        
        self.next_page_btn = QPushButton('Next Page')
        self.next_page_btn.clicked.connect(self.next_page)
        self.next_page_btn.setEnabled(False)
        pagination_layout.addWidget(self.next_page_btn)
        
        results_layout.addLayout(pagination_layout)
        
        # Export controls
        export_layout = QHBoxLayout()
        
        export_csv_btn = QPushButton('Export to CSV')
        export_csv_btn.clicked.connect(lambda: self.export_results('csv'))
        export_layout.addWidget(export_csv_btn)
        
        export_json_btn = QPushButton('Export to JSON')
        export_json_btn.clicked.connect(lambda: self.export_results('json'))
        export_layout.addWidget(export_json_btn)
        
        export_txt_btn = QPushButton('Export to TXT')
        export_txt_btn.clicked.connect(lambda: self.export_results('txt'))
        export_layout.addWidget(export_txt_btn)
        
        results_layout.addLayout(export_layout)
    
    def setup_help_tab(self):
        help_layout = QVBoxLayout(self.help_tab)
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <h2>Google Dorking Guide</h2>
        <p>Google Dorking (also known as Google Hacking) is a technique that uses advanced search operators to find specific information indexed by Google.</p>
        
        <h3>Common Operators:</h3>
        <ul>
            <li><b>site:</b> - Limits results to a specific domain (e.g., site:example.com)</li>
            <li><b>inurl:</b> - Searches for a specific text in URLs (e.g., inurl:admin)</li>
            <li><b>intitle:</b> - Searches for specific text in the page title (e.g., intitle:login)</li>
            <li><b>intext:</b> - Searches for specific text in the content of the page (e.g., intext:password)</li>
            <li><b>filetype:</b> - Searches for specific file types (e.g., filetype:pdf)</li>
            <li><b>ext:</b> - Same as filetype: (e.g., ext:pdf)</li>
            <li><b>-</b> - Excludes results containing specific terms (e.g., admin -login)</li>
            <li><b>OR</b> - Shows results with either term (e.g., admin OR administrator)</li>
            <li><b>AND</b> - Shows results with both terms (e.g., admin AND password)</li>
            <li><b>"exact phrase"</b> - Searches for an exact phrase (e.g., "index of admin")</li>
        </ul>
        
        <h3>Advanced Operators:</h3>
        <ul>
            <li><b>allintext:</b> - All terms must appear in the text of the page</li>
            <li><b>allinurl:</b> - All terms must appear in the URL</li>
            <li><b>allintitle:</b> - All terms must appear in the title</li>
            <li><b>before:</b> - Results from before a specific date (e.g., before:2020-01-01)</li>
            <li><b>after:</b> - Results from after a specific date (e.g., after:2020-01-01)</li>
        </ul>
        
        <h3>Security Considerations:</h3>
        <p>Google Dorking can be used for legitimate security research, but it can also be misused. Always ensure you have permission to test systems you don't own.</p>
        <p>This tool is provided for educational purposes only. The user is responsible for how they use this information.</p>
        
        <h3>About This Tool:</h3>
        <p>This Advanced Google Dorking Tool uses the Google Custom Search Engine API to perform searches with Google Dork operators.</p>
        <p>Features include:</p>
        <ul>
            <li>Pre-defined dork templates for common security searches</li>
            <li>Ability to save and load search queries</li>
            <li>Export results in multiple formats</li>
            <li>Pagination support for viewing large result sets</li>
        </ul>
        """)
        
        help_layout.addWidget(help_text)
    
    def add_operator(self):
        operator = self.operator_combo.currentText()
        value = self.operator_value.text().strip()
        
        if value:
            current_text = self.search_input.text()
            if current_text and not current_text.endswith(' '):
                current_text += ' '
                
            # Special handling for exact phrase
            if operator == '"exact phrase"':
                self.search_input.setText(current_text + f'"{value}"')
            else:
                self.search_input.setText(current_text + operator + value)
                
            self.operator_value.clear()
        else:
            self.status_label.setText('Please enter a value for the operator')
    
    def apply_template(self, index):
        if index > 0:  # Skip the first item which is just a label
            template = self.templates_combo.currentText()
            # Extract the actual dork part (everything inside the parentheses)
            if '(' in template and ')' in template:
                dork = template.split('(')[1].split(')')[0]
                self.search_input.setText(dork)
            self.templates_combo.setCurrentIndex(0)  # Reset to default
    
    def perform_search(self):
        query = self.search_input.text().strip()
        
        if not query:
            self.status_label.setText('Please enter a search query')
            return
            
        self.status_label.setText('Searching...')
        self.results_preview.clear()
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(10)
        
        # Update results per page
        self.results_per_page = int(self.results_count_combo.currentText())
        self.current_page = 1
        
        # Store the current query for reference
        self.current_query = query
        
        try:
            # Perform the Google CSE search
            url = 'https://www.googleapis.com/customsearch/v1'
            params = {
                'key': self.api_key,
                'cx': self.cse_id,
                'q': query,
                'num': self.results_per_page,
                'start': 1,  # First page
                'safe': 'active' if self.safe_search.isChecked() else 'off'
            }
            
            self.progress_bar.setValue(30)
            response = requests.get(url, params=params)
            data = response.json()
            self.progress_bar.setValue(70)
            
            if 'error' in data:
                error_message = data['error']['message']
                self.results_preview.append(f'Error: {error_message}')
                self.status_label.setText(f'Search failed: {error_message}')
                self.progress_bar.setVisible(False)
                return
            
            # Store results
            self.current_results = data.get('items', [])
            self.total_results = int(data.get('searchInformation', {}).get('totalResults', 0))
            
            # Update results preview
            if self.current_results:
                self.results_preview.append(f'Found {self.total_results} results (showing page {self.current_page}):\n')
                
                for i, item in enumerate(self.current_results, 1):
                    self.results_preview.append(f'{i}. {item.get("title", "No title")}')
                    self.results_preview.append(f'URL: {item.get("link", "No link")}')
                    if 'snippet' in item:
                        self.results_preview.append(f'Description: {item.get("snippet", "No description")}')
                    self.results_preview.append('\n' + '-'*80 + '\n')
                
                # Update results tab
                self.update_results_table()
                
                # Update pagination controls
                self.update_pagination_controls()
                
                self.status_label.setText(f'Search completed: {self.total_results} results found')
                
                # Switch to results tab
                self.tabs.setCurrentIndex(1)
            else:
                self.results_preview.append('No results found for your query.')
                self.status_label.setText('Search completed: No results found')
                
                # Clear results table
                self.results_table.setRowCount(0)
                self.prev_page_btn.setEnabled(False)
                self.next_page_btn.setEnabled(False)
                
            self.progress_bar.setValue(100)
            self.progress_bar.setVisible(False)
                
        except Exception as e:
            self.results_preview.append(f'Error performing search: {str(e)}')
            self.status_label.setText('Search failed due to an error')
            self.progress_bar.setVisible(False)
    
    def update_results_table(self):
        # Clear existing rows
        self.results_table.setRowCount(0)
        
        # Add new rows
        for i, item in enumerate(self.current_results):
            row_position = self.results_table.rowCount()
            self.results_table.insertRow(row_position)
            
            # Title
            title_item = QTableWidgetItem(item.get('title', 'No title'))
            title_item.setToolTip(item.get('title', 'No title'))
            self.results_table.setItem(row_position, 0, title_item)
            
            # URL
            url_item = QTableWidgetItem(item.get('link', 'No link'))
            url_item.setToolTip(item.get('link', 'No link'))
            self.results_table.setItem(row_position, 1, url_item)
            
            # Description
            desc_item = QTableWidgetItem(item.get('snippet', 'No description'))
            desc_item.setToolTip(item.get('snippet', 'No description'))
            self.results_table.setItem(row_position, 2, desc_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            # Open URL button
            open_btn = QPushButton('Open')
            open_btn.setMaximumWidth(60)
            open_btn.clicked.connect(lambda checked, url=item.get('link'): QDesktopServices.openUrl(QUrl(url)))
            actions_layout.addWidget(open_btn)
            
            # Copy URL button
            copy_btn = QPushButton('Copy URL')
            copy_btn.setMaximumWidth(80)
            copy_btn.clicked.connect(lambda checked, url=item.get('link'): self.copy_to_clipboard(url))
            actions_layout.addWidget(copy_btn)
            
            self.results_table.setCellWidget(row_position, 3, actions_widget)
    
    def update_pagination_controls(self):
        total_pages = max(1, (self.total_results + self.results_per_page - 1) // self.results_per_page)
        
        self.page_label.setText(f'Page {self.current_page} of {total_pages}')
        self.prev_page_btn.setEnabled(self.current_page > 1)
        self.next_page_btn.setEnabled(self.current_page < total_pages and self.current_page * self.results_per_page < 100)  # Google API limit
    
    def previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_page()
    
    def next_page(self):
        total_pages = max(1, (self.total_results + self.results_per_page - 1) // self.results_per_page)
        if self.current_page < total_pages and self.current_page * self.results_per_page < 100:  # Google API limit
            self.current_page += 1
            self.load_page()
    
    def load_page(self):
        query = self.search_input.text().strip()
        start_index = (self.current_page - 1) * self.results_per_page + 1
        
        self.status_label.setText(f'Loading page {self.current_page}...')
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(20)
        
        try:
            # Perform the Google CSE search for the specific page
            url = 'https://www.googleapis.com/customsearch/v1'
            params = {
                'key': self.api_key,
                'cx': self.cse_id,
                'q': query,
                'num': self.results_per_page,
                'start': start_index,
                'safe': 'active' if self.safe_search.isChecked() else 'off'
            }
            
            self.progress_bar.setValue(50)
            response = requests.get(url, params=params)
            data = response.json()
            self.progress_bar.setValue(80)
            
            if 'error' in data:
                error_message = data['error']['message']
                QMessageBox.warning(self, 'Error', f'Failed to load page: {error_message}')
                self.status_label.setText(f'Failed to load page: {error_message}')
                self.progress_bar.setVisible(False)
                return
            
            # Update current results
            self.current_results = data.get('items', [])
            
            # Update results table
            self.update_results_table()
            
            # Update pagination controls
            self.update_pagination_controls()
            
            self.status_label.setText(f'Page {self.current_page} loaded')
            self.progress_bar.setValue(100)
            self.progress_bar.setVisible(False)
            
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to load page: {str(e)}')
            self.status_label.setText('Failed to load page due to an error')
            self.progress_bar.setVisible(False)
    
    def copy_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.status_label.setText('URL copied to clipboard')
    
    def save_query(self):
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, 'Warning', 'No query to save')
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, 'Save Query', '', 'Text Files (*.txt);;All Files (*)'
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(query)
                self.status_label.setText(f'Query saved to {file_path}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to save query: {str(e)}')
    
    def load_query(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Load Query', '', 'Text Files (*.txt);;All Files (*)'
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    query = f.read().strip()
                self.search_input.setText(query)
                self.status_label.setText(f'Query loaded from {file_path}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to load query: {str(e)}')
    
    def export_results(self, format_type):
        if not self.current_results:
            QMessageBox.warning(self, 'Warning', 'No results to export')
            return
        
        # Get file path
        if format_type == 'csv':
            file_path, _ = QFileDialog.getSaveFileName(
                self, 'Export Results', '', 'CSV Files (*.csv);;All Files (*)'
            )
        elif format_type == 'json':
            file_path, _ = QFileDialog.getSaveFileName(
                self, 'Export Results', '', 'JSON Files (*.json);;All Files (*)'
            )
        else:  # txt
            file_path, _ = QFileDialog.getSaveFileName(
                self, 'Export Results', '', 'Text Files (*.txt);;All Files (*)'
            )
        
        if not file_path:
            return
            
        try:
            if format_type == 'csv':
                self.export_to_csv(file_path)
            elif format_type == 'json':
                self.export_to_json(file_path)
            else:  # txt
                self.export_to_txt(file_path)
                
            self.status_label.setText(f'Results exported to {file_path}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to export results: {str(e)}')
    
    def export_to_csv(self, file_path):
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Title', 'URL', 'Description'])
            
            for item in self.current_results:
                writer.writerow([
                    item.get('title', 'No title'),
                    item.get('link', 'No link'),
                    item.get('snippet', 'No description')
                ])
    
    def export_to_json(self, file_path):
        export_data = []
        
        for item in self.current_results:
            export_data.append({
                'title': item.get('title', 'No title'),
                'url': item.get('link', 'No link'),
                'description': item.get('snippet', 'No description')
            })
            
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
    
    def export_to_txt(self, file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f'Google Dork Search Results\n')
            f.write(f'Query: {self.search_input.text()}\n')
            f.write(f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'Total Results: {self.total_results}\n\n')
            
            for i, item in enumerate(self.current_results, 1):
                f.write(f'{i}. {item.get("title", "No title")}\n')
                f.write(f'URL: {item.get("link", "No link")}\n')
                f.write(f'Description: {item.get("snippet", "No description")}\n\n')
                f.write('-' * 80 + '\n\n')
    
    def run_auto_dorks(self):
        target = self.target_input.text().strip()
        if not target:
            QMessageBox.warning(self, 'Warning', 'Please enter a target name or domain')
            return
        
        # Generate dorks based on selected categories
        dorks = self.generate_dorks(target)
        if not dorks:
            QMessageBox.warning(self, 'Warning', 'No dork categories selected')
            return
        
        # Clear previous results
        self.clear_search()
        
        # Show generated dorks
        self.results_preview.append(f'Generated {len(dorks)} dorks for target: {target}\n')
        for i, dork in enumerate(dorks, 1):
            self.results_preview.append(f'{i}. {dork}\n')
        
        # Run the first dork
        self.search_input.setText(dorks[0])
        self.perform_search()
        
        # Store the remaining dorks for later use
        self.remaining_dorks = dorks[1:]
        
        # Add a button to run the next dork if there are more
        if self.remaining_dorks:
            next_dork_btn = QPushButton('Run Next Dork')
            next_dork_btn.clicked.connect(self.run_next_dork)
            # Add to the results tab
            self.results_tab.layout().addWidget(next_dork_btn)
    
    def run_next_dork(self):
        if not self.remaining_dorks:
            return
        
        # Get the next dork
        next_dork = self.remaining_dorks.pop(0)
        
        # Run it
        self.search_input.setText(next_dork)
        self.perform_search()
        
        # Update the button text or remove it if no more dorks
        if not self.remaining_dorks:
            # Find and remove the button
            for i in range(self.results_tab.layout().count()):
                widget = self.results_tab.layout().itemAt(i).widget()
                if isinstance(widget, QPushButton) and widget.text() == 'Run Next Dork':
                    widget.setVisible(False)
                    break
    
    def generate_dorks(self, target):
        dorks = []
        
        # Determine if target is a domain, name, or something else
        is_domain = '.' in target and not target.startswith('www.')
        # Check if it's likely a person's name (contains space and no special chars)
        is_person = ' ' in target and all(c.isalpha() or c.isspace() for c in target)
        
        if is_domain and not target.startswith('http'):
            domain = target
        elif is_domain and target.startswith('http'):
            # Extract domain from URL
            from urllib.parse import urlparse
            domain = urlparse(target).netloc
        else:
            domain = None
        
        # Basic Information
        if self.category_checks['basic_info'].isChecked():
            if domain:
                dorks.append(f'site:{domain}')
                dorks.append(f'info:{domain}')
            dorks.append(f'"{target}"')
        
        # Files
        if self.category_checks['files'].isChecked():
            file_types = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'log', 'bak', 'backup', 'sql', 'csv']
            if domain:
                dorks.append(f'site:{domain} filetype:({" | ".join([f"filetype:{ft}" for ft in file_types])})')
            else:
                dorks.append(f'"{target}" filetype:({" | ".join([f"filetype:{ft}" for ft in file_types])})')
        
        # Directories
        if self.category_checks['directories'].isChecked():
            dir_queries = ['intitle:"Index of"', 'intitle:"Directory Listing"']
            if domain:
                for query in dir_queries:
                    dorks.append(f'site:{domain} {query}')
            else:
                for query in dir_queries:
                    dorks.append(f'{query} "{target}"')
        
        # Login Pages
        if self.category_checks['login_pages'].isChecked():
            login_queries = ['inurl:login', 'inurl:signin', 'intitle:login', 'intitle:"sign in"', 'inurl:auth']
            if domain:
                for query in login_queries:
                    dorks.append(f'site:{domain} {query}')
            else:
                for query in login_queries:
                    dorks.append(f'{query} "{target}"')
        
        # Potential Vulnerabilities
        if self.category_checks['vulnerabilities'].isChecked():
            vuln_queries = [
                'inurl:php?id=', 'inurl:index.php?id=', 'inurl:view.php?id=',
                'intext:"sql syntax near"', 'intext:"syntax error has occurred"',
                'intext:"incorrect syntax near"', 'intext:"unexpected end of SQL command"',
                'intext:"Warning: mysql_fetch_array()"', 'intext:"Warning: mysql_connect()"',
                'intext:"Warning: pg_connect()"', 'intext:"error occurred while establishing a connection"'
            ]
            if domain:
                for query in vuln_queries:
                    dorks.append(f'site:{domain} {query}')
            else:
                for query in vuln_queries[:4]:  # Only use the first few for non-domain targets
                    dorks.append(f'{query} "{target}"')
        
        # Technologies
        if self.category_checks['technologies'].isChecked():
            tech_queries = [
                'intext:"powered by"', 'intext:"built with"', 'intext:"running on"',
                'inurl:wp-content', 'inurl:wp-includes', # WordPress
                'inurl:administrator/index.php', # Joomla
                'inurl:sites/all/modules', # Drupal
                'intext:"powered by vBulletin"', # vBulletin
                'inurl:phpMyAdmin', 'inurl:phpmyadmin',
                'inurl:cpanel', 'inurl:webmail'
            ]
            if domain:
                for query in tech_queries:
                    dorks.append(f'site:{domain} {query}')
            else:
                for query in tech_queries[:3]:  # Only use the first few for non-domain targets
                    dorks.append(f'{query} "{target}"')
        
        # Social Media
        if self.category_checks['social_media'].isChecked():
            social_sites = ['facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com', 'youtube.com', 'pinterest.com', 'reddit.com', 'quora.com', 'medium.com', 'tumblr.com']
            for site in social_sites:
                dorks.append(f'site:{site} "{target}"')
            
            # Additional social media specific searches for people
            if is_person:
                name_parts = target.split()
                if len(name_parts) >= 2:
                    first_name = name_parts[0]
                    last_name = name_parts[-1]
                    dorks.append(f'site:linkedin.com/in/ "{first_name}*{last_name}"')
                    dorks.append(f'site:twitter.com "{first_name} {last_name}"')
                    dorks.append(f'site:facebook.com "{first_name} {last_name}"')
                    dorks.append(f'site:instagram.com "{first_name}{last_name}" OR "{first_name}.{last_name}" OR "{first_name}_{last_name}"')
        
        # Email Addresses
        if self.category_checks['email'].isChecked():
            if domain:
                dorks.append(f'intext:"@{domain}"')
            else:
                common_emails = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'protonmail.com', 'icloud.com', 'aol.com', 'mail.com']
                email_query = ' OR '.join([f'intext:"@{domain}"' for domain in common_emails])
                dorks.append(f'intext:"{target}" ({email_query})')
                
                # For person names, try common email formats
                if is_person:
                    name_parts = target.split()
                    if len(name_parts) >= 2:
                        first_name = name_parts[0].lower()
                        last_name = name_parts[-1].lower()
                        email_patterns = [
                            f'"{first_name}.{last_name}@"',
                            f'"{first_name}_{last_name}@"',
                            f'"{first_name}{last_name}@"',
                            f'"{first_name[0]}{last_name}@"',
                            f'"{last_name}.{first_name}@"'
                        ]
                        dorks.append(' OR '.join(email_patterns))
        
        # Subdomains
        if self.category_checks['subdomains'].isChecked() and domain:
            dorks.append(f'site:*.{domain} -site:www.{domain}')
        
        # Person Search (specialized for individuals)
        if self.category_checks['person_search'].isChecked() and is_person:
            name_parts = target.split()
            if len(name_parts) >= 2:
                first_name = name_parts[0]
                last_name = name_parts[-1]
                
                # Bio searches
                dorks.append(f'"about {first_name} {last_name}" OR "biography {first_name} {last_name}"')
                dorks.append(f'"profile {first_name} {last_name}" OR "resume {first_name} {last_name}"')
                
                # Contact information
                dorks.append(f'"{first_name} {last_name}" (phone OR contact OR email OR address)')
                
                # Professional information
                dorks.append(f'"{first_name} {last_name}" (CV OR resume OR "curriculum vitae")')
                dorks.append(f'"{first_name} {last_name}" (job OR position OR career OR company OR employer)')
                
                # Educational background
                dorks.append(f'"{first_name} {last_name}" (university OR college OR school OR degree OR graduate OR alumni)')
        
        # Profile Pages
        if self.category_checks['profiles'].isChecked():
            profile_sites = ['about.me', 'gravatar.com', 'github.com', 'stackoverflow.com', 'behance.net', 'dribbble.com', 'flickr.com', 'vimeo.com', 'soundcloud.com', 'last.fm', 'goodreads.com']
            for site in profile_sites:
                dorks.append(f'site:{site} "{target}"')
        
        # Images
        if self.category_checks['images'].isChecked():
            dorks.append(f'intext:"{target}" (filetype:jpg OR filetype:png OR filetype:gif)')
            dorks.append(f'intext:"{target}" site:imgur.com OR site:flickr.com OR site:500px.com')
            if is_person:
                dorks.append(f'"{target}" (photo OR picture OR image OR portrait)')
        
        # News Articles
        if self.category_checks['news'].isChecked():
            news_sites = ['nytimes.com', 'cnn.com', 'bbc.com', 'washingtonpost.com', 'theguardian.com', 'reuters.com', 'bloomberg.com', 'forbes.com', 'timesofindia.indiatimes.com', 'hindustantimes.com', 'ndtv.com', 'indianexpress.com']
            news_query = ' OR '.join([f'site:{site}' for site in news_sites])
            dorks.append(f'"{target}" ({news_query})')
            dorks.append(f'"{target}" (news OR article OR interview OR press)')
        
        # Academic/Publications
        if self.category_checks['academic'].isChecked():
            academic_sites = ['scholar.google.com', 'researchgate.net', 'academia.edu', 'ssrn.com', 'ieee.org', 'springer.com', 'jstor.org', 'arxiv.org']
            academic_query = ' OR '.join([f'site:{site}' for site in academic_sites])
            dorks.append(f'"{target}" ({academic_query})')
            dorks.append(f'"{target}" (paper OR publication OR research OR thesis OR dissertation OR journal)')
            dorks.append(f'author:"{target}"')
        
        return dorks
    
    def clear_search(self):
        self.search_input.clear()
        self.results_preview.clear()
        self.results_table.setRowCount(0)
        self.current_results = []
        self.current_page = 1
        self.total_results = 0
        self.prev_page_btn.setEnabled(False)
        self.next_page_btn.setEnabled(False)
        self.status_label.setText('Ready')
        
        # Remove any dynamic buttons
        for i in range(self.results_tab.layout().count()):
            widget = self.results_tab.layout().itemAt(i).widget()
            if isinstance(widget, QPushButton) and widget.text() == 'Run Next Dork':
                widget.setVisible(False)
                break


def main():
    app = QApplication(sys.argv)
    window = GoogleDorkingApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()