"""
Main Application Window for Google Dorking Tool v1.2 (PySide6).
Global Keyboard Shortcuts, Toast Notifications, Tabs Orchestration, and Zero Emojis.
Version 1.2.0
"""

from typing import List, Optional
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QProgressBar, QStatusBar, QMessageBox,
    QFrame
)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QKeySequence, QShortcut

from ..models import SearchResult
from ..security import CredentialManager
from ..rate_limiter import AdvancedRateLimiter
from ..bookmarks import BookmarksManager
from ..engine import DorkEngine
from ..workers import GoogleSearchWorker, AutoDorkBatchWorker
from .loader import ThemeManager
from .search_tab import SearchTab
from .results_tab import ResultsTab
from .saved_tab import SavedTab
from .creds_tab import CredentialsTab
from .help_tab import HelpTab


class NonSwitchingTabWidget(QTabWidget):
    """
    QTabWidget subclass that disables accidental tab switching on mouse wheel / swipe events.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tabBar().installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.tabBar() and event.type() == QEvent.Wheel:
            return True
        return False

    def wheelEvent(self, event):
        event.ignore()


class MainWindow(QMainWindow):
    """
    Primary Application Window implementing the multi-tab OSINT reconnaissance interface.
    """

    def __init__(self):
        super().__init__()

        # Backend Managers
        self.cred_mgr = CredentialManager()
        self.rate_limiter = AdvancedRateLimiter(daily_limit=100)
        self.bookmarks_mgr = BookmarksManager()
        self.current_theme = "dark"

        self.api_key, self.cse_id = self.cred_mgr.load()

        # Active worker threads
        self.active_search_worker: Optional[GoogleSearchWorker] = None
        self.active_batch_worker: Optional[AutoDorkBatchWorker] = None

        self.init_window()
        self.init_ui()
        self.init_shortcuts()
        self.apply_theme("dark")
        self.update_quota_display()

    def init_window(self):
        self.setWindowTitle("Google Dorking Tool v1.2 - OSINT & Penetration Testing Suite")
        self.setGeometry(80, 60, 1280, 850)
        self.setMinimumSize(960, 680)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # 1. Header Bar
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("GOOGLE DORKING TOOL v1.2")
        title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #58a6ff; letter-spacing: 1px;")

        self.header_quota_label = QLabel("Daily Quota: Loading...")
        self.header_quota_label.setStyleSheet("color: #8b949e; font-size: 13px;")

        self.theme_btn = QPushButton("Light Theme")
        self.theme_btn.setToolTip("Toggle between Dark and Light interface themes (Ctrl+L)")
        self.theme_btn.clicked.connect(self.toggle_theme)

        self.stop_btn = QPushButton("Stop Search")
        self.stop_btn.setObjectName("dangerBtn")
        self.stop_btn.setVisible(False)
        self.stop_btn.clicked.connect(self.cancel_active_worker)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.header_quota_label)
        header_layout.addSpacing(16)
        header_layout.addWidget(self.stop_btn)
        header_layout.addWidget(self.theme_btn)

        main_layout.addWidget(header_frame)

        # 2. Main Tab Widget
        self.tabs = NonSwitchingTabWidget()

        # Build individual tab views
        self.search_tab = SearchTab(
            on_run_api_search=self.start_api_search,
            on_run_batch_recon=self.start_batch_recon,
            bookmarks_mgr=self.bookmarks_mgr,
            parent=self
        )

        self.results_tab = ResultsTab(parent=self)

        self.saved_tab = SavedTab(
            bookmarks_mgr=self.bookmarks_mgr,
            on_execute_query=self.load_query_in_search_tab,
            parent=self
        )

        self.creds_tab = CredentialsTab(
            cred_mgr=self.cred_mgr,
            rate_limiter=self.rate_limiter,
            on_credentials_changed=self.on_credentials_updated,
            parent=self
        )

        self.help_tab = HelpTab(parent=self)

        self.tabs.addTab(self.search_tab, "Search & Builder")
        self.tabs.addTab(self.results_tab, "Results Explorer")
        self.tabs.addTab(self.saved_tab, "Saved & History")
        self.tabs.addTab(self.creds_tab, "Credentials & Quota")
        self.tabs.addTab(self.help_tab, "Reference Guide")

        main_layout.addWidget(self.tabs)

        # 3. Global Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # 4. Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. Press Ctrl+1 to Ctrl+5 to navigate tabs | Ctrl+Enter to search.")

    def init_shortcuts(self):
        """Initializes application-wide keyboard shortcuts."""
        # Tab navigation shortcuts
        for idx in range(5):
            shortcut = QShortcut(QKeySequence(f"Ctrl+{idx+1}"), self)
            shortcut.activated.connect(lambda i=idx: self.tabs.setCurrentIndex(i))

        # Theme toggle shortcut
        theme_sc = QShortcut(QKeySequence("Ctrl+L"), self)
        theme_sc.activated.connect(self.toggle_theme)

        # Focus filter shortcut
        filter_sc = QShortcut(QKeySequence("Ctrl+F"), self)
        filter_sc.activated.connect(self.focus_current_filter)

        # Refresh shortcut
        refresh_sc = QShortcut(QKeySequence("F5"), self)
        refresh_sc.activated.connect(self.refresh_active_view)

    def focus_current_filter(self):
        current_idx = self.tabs.currentIndex()
        if current_idx == 0:
            self.search_tab.query_editor.setFocus()
        elif current_idx == 1:
            self.results_tab.filter_input.setFocus()
        elif current_idx == 2:
            self.saved_tab.bm_filter_input.setFocus()

    def refresh_active_view(self):
        self.saved_tab.refresh_all()
        self.update_quota_display()
        self.show_toast("Refreshed data.")

    def show_toast(self, message: str, duration_ms: int = 3500):
        """Displays a non-blocking toast status in the status bar."""
        self.status_bar.showMessage(f"[OK] {message}", duration_ms)

    def apply_theme(self, theme_name: str):
        self.current_theme = theme_name
        ThemeManager.apply_theme(self, theme_name)
        if theme_name == "dark":
            self.theme_btn.setText("Light Theme")
        else:
            self.theme_btn.setText("Dark Theme")
        # Update results tab link color
        if hasattr(self, "results_tab"):
            self.results_tab.render_page()

    def toggle_theme(self):
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme(new_theme)
        self.show_toast(f"Switched to {new_theme.capitalize()} theme.")

    def update_quota_display(self):
        used, limit, rem = self.rate_limiter.get_stats()
        self.header_quota_label.setText(f"API Quota: {used}/{limit} requests ({rem} remaining)")
        self.creds_tab.refresh_quota()

    def on_credentials_updated(self):
        self.api_key, self.cse_id = self.cred_mgr.load()
        self.update_quota_display()
        self.show_toast("API credentials reloaded.")

    def load_query_in_search_tab(self, query: str):
        self.search_tab.set_active_query(query)
        self.tabs.setCurrentWidget(self.search_tab)
        self.show_toast("Loaded query into Search Tab.")

    def cancel_active_worker(self):
        if self.active_search_worker and self.active_search_worker.isRunning():
            self.active_search_worker.cancel()
            self.status_bar.showMessage("Cancelling search operation...")
        if self.active_batch_worker and self.active_batch_worker.isRunning():
            self.active_batch_worker.cancel()
            self.status_bar.showMessage("Cancelling batch sweep...")
        self.stop_btn.setVisible(False)

    def start_api_search(self, query: str, category: str = "Manual"):
        if not self.api_key or not self.cse_id:
            reply = QMessageBox.question(
                self, "API Credentials Missing",
                "Google Custom Search API Key and CSE ID are not configured.\n\n"
                "Would you like to open the Credentials tab now?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.tabs.setCurrentWidget(self.creds_tab)
            return

        can_req, msg = self.rate_limiter.can_request()
        if not can_req:
            QMessageBox.warning(self, "Daily Quota Exceeded", msg)
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(10)
        self.stop_btn.setVisible(True)
        self.status_bar.showMessage(f"Searching API: {query[:45]}...")

        self.active_search_worker = GoogleSearchWorker(
            api_key=self.api_key,
            cse_id=self.cse_id,
            query=query,
            num_results=10,
            rate_limiter=self.rate_limiter,
            category=category
        )

        self.active_search_worker.progress_update.connect(self.on_worker_progress)
        self.active_search_worker.result_ready.connect(self.on_search_results_ready)
        self.active_search_worker.error_occurred.connect(self.on_worker_error)
        self.active_search_worker.finished_search.connect(self.on_worker_finished)

        self.active_search_worker.start()

    def start_batch_recon(self, target: str, selected_categories: List[str], target_type: str = "AUTO"):
        if not self.api_key or not self.cse_id:
            reply = QMessageBox.question(
                self, "API Credentials Missing",
                "Google Custom Search API Key and CSE ID are required for automated API sweeps.\n\n"
                "Open Credentials tab now?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.tabs.setCurrentWidget(self.creds_tab)
            return

        dork_list = DorkEngine.generate_dorks(target, selected_categories, target_type=target_type)
        if not dork_list:
            QMessageBox.warning(self, "No Queries", "No queries could be generated for the target.")
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(5)
        self.stop_btn.setVisible(True)
        self.status_bar.showMessage(f"Initiating batch sweep ({len(dork_list)} queries)...")

        # Switch to results tab in anticipation
        self.results_tab.set_results([], query=f"Target: {target}")
        self.tabs.setCurrentWidget(self.results_tab)

        self.active_batch_worker = AutoDorkBatchWorker(
            api_key=self.api_key,
            cse_id=self.cse_id,
            dork_list=dork_list,
            rate_limiter=self.rate_limiter,
            max_per_dork=5
        )

        self.active_batch_worker.progress_update.connect(self.on_worker_progress)
        self.active_batch_worker.results_updated.connect(self.results_tab.update_results)
        self.active_batch_worker.error_occurred.connect(self.on_worker_error)
        self.active_batch_worker.batch_finished.connect(self.on_batch_sweep_finished)

        self.active_batch_worker.start()

    def on_worker_progress(self, percent: int, message: str):
        self.progress_bar.setValue(percent)
        self.status_bar.showMessage(message)
        self.update_quota_display()

    def on_search_results_ready(self, results: List[SearchResult], total_available: int, query: str):
        self.results_tab.set_results(results, query=query)
        self.bookmarks_mgr.add_history(query, len(results), mode="API")
        self.saved_tab.refresh_history()
        self.tabs.setCurrentWidget(self.results_tab)
        self.show_toast(f"Found {len(results)} results for query.")

    def on_batch_sweep_finished(self, results: List[SearchResult]):
        self.progress_bar.setVisible(False)
        self.stop_btn.setVisible(False)
        self.update_quota_display()
        self.show_toast(f"Automated sweep completed with {len(results)} findings.")
        QMessageBox.information(self, "Sweep Complete", f"Reconnaissance completed with {len(results)} findings.")

    def on_worker_error(self, message: str):
        self.status_bar.showMessage(f"Error: {message}")
        QMessageBox.critical(self, "Search Error", message)

    def on_worker_finished(self):
        self.progress_bar.setVisible(False)
        self.stop_btn.setVisible(False)
        self.update_quota_display()

