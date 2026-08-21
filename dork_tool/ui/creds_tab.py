"""
Credentials and Quota Management Tab Widget (PySide6).
Clean form layout, API connection validation, and daily quota monitoring wrapped in QScrollArea.
"""

from typing import Callable
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGroupBox, QFormLayout, QProgressBar, QMessageBox, QFrame, QScrollArea
)
from PySide6.QtCore import Qt

from ..security import CredentialManager
from ..rate_limiter import AdvancedRateLimiter


class CredentialsTab(QWidget):
    """
    Credentials Tab for Fernet AES-encrypted storage and Quota monitoring with smooth scrolling.
    """

    def __init__(self, cred_mgr: CredentialManager,
                 rate_limiter: AdvancedRateLimiter,
                 on_credentials_changed: Callable[[], None],
                 parent=None):
        super().__init__(parent)
        self.cred_mgr = cred_mgr
        self.rate_limiter = rate_limiter
        self.on_credentials_changed = on_credentials_changed

        self.init_ui()
        self.load_current_creds()
        self.refresh_quota()

    def init_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # 1. API Credentials Box
        cred_box = QGroupBox("Google Custom Search API Configuration")
        cred_layout = QFormLayout(cred_box)
        cred_layout.setContentsMargins(16, 16, 16, 16)
        cred_layout.setSpacing(12)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter Google Cloud API Key (e.g. AIzaSy...)")
        self.api_key_input.setEchoMode(QLineEdit.Password)

        self.cse_id_input = QLineEdit()
        self.cse_id_input.setPlaceholderText("Enter Search Engine ID / CX (e.g. 017576...:sul9q1akysi)")

        # Show/Hide Password Toggle
        toggle_layout = QHBoxLayout()
        self.toggle_echo_btn = QPushButton("Show Key")
        self.toggle_echo_btn.setCheckable(True)
        self.toggle_echo_btn.toggled.connect(self.toggle_key_visibility)
        toggle_layout.addWidget(self.api_key_input)
        toggle_layout.addWidget(self.toggle_echo_btn)

        cred_layout.addRow("API Key:", toggle_layout)
        cred_layout.addRow("Search Engine CX ID:", self.cse_id_input)

        # Action Buttons Bar
        btn_bar = QHBoxLayout()
        self.save_btn = QPushButton("Save Credentials (AES-128 Encrypted)")
        self.save_btn.setObjectName("primaryBtn")
        self.save_btn.clicked.connect(self.save_credentials)

        self.test_btn = QPushButton("Test API Connection")
        self.test_btn.setObjectName("browserBtn")
        self.test_btn.clicked.connect(self.test_credentials)

        self.clear_btn = QPushButton("Clear Credentials")
        self.clear_btn.setObjectName("dangerBtn")
        self.clear_btn.clicked.connect(self.clear_credentials)

        btn_bar.addWidget(self.save_btn)
        btn_bar.addWidget(self.test_btn)
        btn_bar.addWidget(self.clear_btn)
        btn_bar.addStretch()

        cred_layout.addRow("", btn_bar)
        layout.addWidget(cred_box)

        # 2. Daily Quota Meter Box
        quota_box = QGroupBox("Daily API Rate Limiting & Quota Tracker")
        q_layout = QVBoxLayout(quota_box)
        q_layout.setContentsMargins(16, 16, 16, 16)
        q_layout.setSpacing(10)

        self.quota_status_label = QLabel("Daily Requests: 0 / 100")
        self.quota_status_label.setStyleSheet("font-weight: 600; font-size: 14px;")

        self.quota_progress = QProgressBar()
        self.quota_progress.setRange(0, 100)
        self.quota_progress.setValue(0)

        q_btn_bar = QHBoxLayout()
        self.reset_quota_btn = QPushButton("Reset Quota Counter")
        self.reset_quota_btn.clicked.connect(self.reset_quota)

        quota_info = QLabel("Free tier resets daily at 00:00 UTC. Custom Search allows 100 free requests per day.")
        quota_info.setStyleSheet("color: #8b949e; font-size: 12px;")

        q_btn_bar.addWidget(self.reset_quota_btn)
        q_btn_bar.addWidget(quota_info)
        q_btn_bar.addStretch()

        q_layout.addWidget(self.quota_status_label)
        q_layout.addWidget(self.quota_progress)
        q_layout.addLayout(q_btn_bar)
        layout.addWidget(quota_box)

        # 3. Setup Instructions Frame
        guide_box = QGroupBox("Setup Instructions")
        g_layout = QVBoxLayout(guide_box)
        g_layout.setContentsMargins(16, 16, 16, 16)

        instructions = (
            "1. Google Cloud Console: Create a project and enable 'Custom Search API'.\n"
            "2. API Key: Generate an API Key under APIs & Services > Credentials.\n"
            "3. Programmable Search Engine: Create a search engine at cse.google.com, enable 'Search the entire web', and copy Search Engine ID (CX).\n"
            "4. Zero-API Mode: You can use 'Open in Browser (Direct)' at any time without configuring API keys or consuming quota limits."
        )
        instr_label = QLabel(instructions)
        instr_label.setStyleSheet("color: #8b949e; line-height: 1.5;")
        g_layout.addWidget(instr_label)
        layout.addWidget(guide_box)

        layout.addStretch()

        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

    def toggle_key_visibility(self, checked: bool):
        if checked:
            self.api_key_input.setEchoMode(QLineEdit.Normal)
            self.toggle_echo_btn.setText("Hide Key")
        else:
            self.api_key_input.setEchoMode(QLineEdit.Password)
            self.toggle_echo_btn.setText("Show Key")

    def load_current_creds(self):
        k, c = self.cred_mgr.load()
        if k:
            self.api_key_input.setText(k)
        if c:
            self.cse_id_input.setText(c)

    def save_credentials(self):
        k = self.api_key_input.text().strip()
        c = self.cse_id_input.text().strip()
        if not k or not c:
            QMessageBox.warning(self, "Incomplete Credentials", "Please provide both API Key and Search Engine ID.")
            return
        if self.cred_mgr.save(k, c):
            QMessageBox.information(self, "Credentials Saved", "API credentials securely encrypted and stored locally.")
            self.on_credentials_changed()
        else:
            QMessageBox.critical(self, "Save Error", "Failed to encrypt and save credentials.")

    def test_credentials(self):
        k = self.api_key_input.text().strip()
        c = self.cse_id_input.text().strip()
        if not k or not c:
            QMessageBox.warning(self, "Credentials Required", "Enter API Key and CSE ID to test connection.")
            return
        can_req, quota_msg = self.rate_limiter.can_request()
        if not can_req:
            QMessageBox.warning(self, "Daily Quota Exceeded", quota_msg)
            return
        self.rate_limiter.throttle()
        valid, msg = CredentialManager.validate(k, c)
        self.rate_limiter.record_request()
        self.refresh_quota()
        if valid:
            QMessageBox.information(self, "API Test Succeeded", msg)
        else:
            QMessageBox.critical(self, "API Test Failed", msg)

    def clear_credentials(self):
        reply = QMessageBox.question(self, "Confirm Clear", "Delete all saved local credentials?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.cred_mgr.clear()
            self.api_key_input.clear()
            self.cse_id_input.clear()
            self.on_credentials_changed()
            QMessageBox.information(self, "Cleared", "Credentials successfully deleted.")

    def refresh_quota(self):
        used, limit, rem = self.rate_limiter.get_stats()
        self.quota_status_label.setText(f"Daily Requests: {used} / {limit} ({rem} remaining)")
        self.quota_progress.setMaximum(limit)
        self.quota_progress.setValue(used)

    def reset_quota(self):
        self.rate_limiter.reset()
        self.refresh_quota()
        QMessageBox.information(self, "Quota Reset", "Daily quota tracker counter reset to 0.")

