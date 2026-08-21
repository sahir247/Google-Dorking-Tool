"""
Google Dorking Tool - Advanced OSINT & Penetration Testing Suite
Version: 1.2.0
"""

__version__ = "1.2.0"
__author__ = "OSINT Security Community"

from .models import SearchResult
from .security import CredentialManager
from .rate_limiter import AdvancedRateLimiter
from .engine import DorkEngine
from .bookmarks import BookmarksManager
from .exporter import ExportManager

__all__ = [
    "SearchResult",
    "CredentialManager",
    "AdvancedRateLimiter",
    "DorkEngine",
    "BookmarksManager",
    "ExportManager",
]
