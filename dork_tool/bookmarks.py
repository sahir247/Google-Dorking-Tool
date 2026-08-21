"""
Bookmarks and History Management for Google Dorking Tool.
Version 1.2.0
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any


class BookmarksManager:
    """
    Manages saved dork bookmarks and search execution history.
    """

    def __init__(self):
        self.config_dir = os.path.join(os.path.expanduser("~"), ".google_dorking_tool")
        self.bookmarks_file = os.path.join(self.config_dir, "bookmarks.json")
        self.history_file = os.path.join(self.config_dir, "history.json")
        self._ensure_files()

    def _ensure_files(self):
        try:
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir, exist_ok=True)
            if not os.path.exists(self.bookmarks_file):
                self._save_json(self.bookmarks_file, self._default_bookmarks())
            if not os.path.exists(self.history_file):
                self._save_json(self.history_file, [])
        except Exception as e:
            print(f"[ERROR] Bookmarks file setup failed: {e}")

    def _save_json(self, filepath: str, data: Any):
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Failed to save {filepath}: {e}")

    def _load_json(self, filepath: str) -> Any:
        if not os.path.exists(filepath):
            return []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def load_bookmarks(self) -> List[Dict[str, Any]]:
        return self._load_json(self.bookmarks_file)

    def add_bookmark(self, title: str, query: str, category: str = "Custom", notes: str = "") -> bool:
        bookmarks = self.load_bookmarks()
        bookmarks.append({
            "title": title.strip(),
            "query": query.strip(),
            "category": category.strip(),
            "notes": notes.strip(),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self._save_json(self.bookmarks_file, bookmarks)
        return True

    def delete_bookmark(self, index: int) -> bool:
        bookmarks = self.load_bookmarks()
        if 0 <= index < len(bookmarks):
            bookmarks.pop(index)
            self._save_json(self.bookmarks_file, bookmarks)
            return True
        return False

    def load_history(self) -> List[Dict[str, Any]]:
        return self._load_json(self.history_file)

    def add_history(self, query: str, results_count: int, mode: str = "API"):
        history = self.load_history()
        history.insert(0, {
            "query": query,
            "results_count": results_count,
            "mode": mode,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        # Keep recent 200 items
        history = history[:200]
        self._save_json(self.history_file, history)

    def clear_history(self) -> bool:
        self._save_json(self.history_file, [])
        return True

    def _default_bookmarks(self) -> List[Dict[str, Any]]:
        return [
            {
                "title": "Exposed Environment Configuration",
                "query": 'filetype:env "DB_PASSWORD" OR "SECRET_KEY"',
                "category": "Credentials",
                "notes": "Searches for exposed .env files with database or secret keys",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "title": "Exposed Git Repositories",
                "query": 'inurl:"/.git" intitle:"Index of /"',
                "category": "Source Code",
                "notes": "Finds publicly accessible .git version control folders",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "title": "Public AWS S3 Buckets",
                "query": 'site:s3.amazonaws.com intext:"Index of"',
                "category": "Cloud",
                "notes": "Finds publicly readable Amazon S3 storage buckets",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "title": "Open Jenkins Dashboards",
                "query": 'intitle:"Dashboard [Jenkins]" "Jenkins"',
                "category": "CI/CD",
                "notes": "Finds unauthenticated Jenkins automation instances",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
