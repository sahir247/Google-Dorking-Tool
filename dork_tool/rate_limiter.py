"""
Rate limiting and daily API quota management.
Version 1.2.0
"""

import os
import json
import time
from datetime import datetime, timezone
from typing import Tuple


class AdvancedRateLimiter:
    """
    Enforces inter-request throttling and tracks daily API quotas.
    Quota data is saved to ~/.google_dorking_tool/quota.json
    """

    def __init__(self, daily_limit: int = 100, min_interval: float = 1.2):
        self.daily_limit = daily_limit
        self.min_interval = min_interval
        self.last_request_time: float = 0.0
        self.quota_file = os.path.join(
            os.path.expanduser("~"), ".google_dorking_tool", "quota.json"
        )
        self._ensure_dir()
        self._load_quota()

    def _ensure_dir(self):
        try:
            d = os.path.dirname(self.quota_file)
            if not os.path.exists(d):
                os.makedirs(d, exist_ok=True)
        except Exception:
            pass

    def _get_current_utc_date(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _load_quota(self):
        self.today = self._get_current_utc_date()
        self.requests_today = 0
        if os.path.exists(self.quota_file):
            try:
                with open(self.quota_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("date") == self.today:
                        self.requests_today = data.get("count", 0)
            except Exception:
                self.requests_today = 0

    def _save_quota(self):
        try:
            data = {
                "date": self.today,
                "count": self.requests_today,
                "daily_limit": self.daily_limit,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            with open(self.quota_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def _check_day_rollover(self):
        current_date = self._get_current_utc_date()
        if current_date != self.today:
            self.today = current_date
            self.requests_today = 0
            self._save_quota()

    def can_request(self) -> Tuple[bool, str]:
        """Checks if a new request is permitted under daily quota."""
        self._check_day_rollover()
        if self.requests_today >= self.daily_limit:
            return False, f"Daily quota reached ({self.requests_today}/{self.daily_limit}). Quota resets at 00:00 UTC."
        return True, ""

    def throttle(self):
        """Enforces minimum inter-request delay."""
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()

    def record_request(self):
        """Increments and persists the daily request counter."""
        self._check_day_rollover()
        self.requests_today += 1
        self._save_quota()

    def get_stats(self) -> Tuple[int, int, int]:
        """Returns (used, limit, remaining)."""
        self._check_day_rollover()
        remaining = max(0, self.daily_limit - self.requests_today)
        return self.requests_today, self.daily_limit, remaining

    def reset(self):
        """Manually resets the daily request counter."""
        self.requests_today = 0
        self._save_quota()
