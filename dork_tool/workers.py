"""
PySide6 QThread Background Search Workers.
Version 1.2.0 - With robust exception and cancellation handling.
"""

import requests
from typing import List, Tuple
from PySide6.QtCore import QThread, Signal
from .models import SearchResult
from .rate_limiter import AdvancedRateLimiter


class GoogleSearchWorker(QThread):
    """
    Background worker thread for executing Google Custom Search API requests with pagination.
    """
    result_ready = Signal(list, int, str)  # List[SearchResult], total_results, query
    progress_update = Signal(int, str)     # percentage (0-100), status_message
    error_occurred = Signal(str)           # error_message
    finished_search = Signal()

    def __init__(self, api_key: str, cse_id: str, query: str,
                 num_results: int = 10, start_index: int = 1,
                 rate_limiter: AdvancedRateLimiter = None,
                 category: str = "Manual"):
        super().__init__()
        self.api_key = api_key
        self.cse_id = cse_id
        self.query = query
        self.num_results = min(max(num_results, 1), 100)
        self.start_index = max(start_index, 1)
        self.rate_limiter = rate_limiter or AdvancedRateLimiter()
        self.category = category
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        try:
            if not self.api_key or not self.cse_id:
                self.error_occurred.emit("API Key and CSE ID are required. Configure them in the Credentials tab.")
                return

            if not self.query.strip():
                self.error_occurred.emit("Search query cannot be empty.")
                return

            results: List[SearchResult] = []
            total_fetched = 0
            total_available = 0
            current_start = self.start_index

            self.progress_update.emit(10, f"Initializing search for: '{self.query[:40]}...'")

            while total_fetched < self.num_results and not self._is_cancelled:
                if current_start > 91:
                    break

                can_req, msg = self.rate_limiter.can_request()
                if not can_req:
                    self.error_occurred.emit(msg)
                    break

                self.rate_limiter.throttle()

                batch_size = min(10, self.num_results - total_fetched)
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    "key": self.api_key,
                    "cx": self.cse_id,
                    "q": self.query,
                    "num": batch_size,
                    "start": current_start
                }

                self.progress_update.emit(
                    min(90, int(15 + (total_fetched / self.num_results) * 75)),
                    f"Fetching results {current_start} - {current_start + batch_size - 1}..."
                )

                try:
                    response = requests.get(url, params=params, timeout=12)
                    self.rate_limiter.record_request()

                    if response.status_code == 200:
                        data = response.json()
                        search_info = data.get("searchInformation", {})
                        total_available = int(search_info.get("totalResults", "0"))
                        items = data.get("items", [])

                        if not items:
                            break

                        for item in items:
                            results.append(SearchResult(
                                title=item.get("title", "No Title"),
                                link=item.get("link", ""),
                                snippet=item.get("snippet", ""),
                                category=self.category,
                                query=self.query
                            ))

                        total_fetched += len(items)
                        current_start += len(items)

                        if len(items) < batch_size:
                            break

                    elif response.status_code == 400:
                        self.error_occurred.emit("HTTP 400: Invalid Request or invalid CSE ID.")
                        break
                    elif response.status_code == 403:
                        self.error_occurred.emit("HTTP 403: Forbidden - Custom Search API not enabled or daily quota exceeded.")
                        break
                    elif response.status_code == 429:
                        self.error_occurred.emit("HTTP 429: Rate limited by Google. Please wait a moment.")
                        break
                    else:
                        self.error_occurred.emit(f"API Error {response.status_code}: {response.text[:120]}")
                        break

                except requests.exceptions.Timeout:
                    self.error_occurred.emit("Search request timed out. Please check your network connection.")
                    break
                except requests.exceptions.RequestException as e:
                    self.error_occurred.emit(f"Network error: {str(e)}")
                    break

            if self._is_cancelled:
                self.progress_update.emit(100, "Search cancelled by user.")
            else:
                self.progress_update.emit(100, f"Search complete: {len(results)} items collected.")
                self.result_ready.emit(results, total_available, self.query)

        except Exception as e:
            self.error_occurred.emit(f"Unexpected worker error: {str(e)}")
        finally:
            self.finished_search.emit()


class AutoDorkBatchWorker(QThread):
    """
    Background worker thread for batch executing multiple dork queries in sequence.
    """
    category_started = Signal(str, str, int, int)  # category, query, index, total
    results_updated = Signal(list)                 # cumulative List[SearchResult]
    progress_update = Signal(int, str)             # percentage (0-100), message
    error_occurred = Signal(str)
    batch_finished = Signal(list)                  # final List[SearchResult]

    def __init__(self, api_key: str, cse_id: str, dork_list: List[Tuple[str, str]],
                 rate_limiter: AdvancedRateLimiter = None, max_per_dork: int = 5):
        super().__init__()
        self.api_key = api_key
        self.cse_id = cse_id
        self.dork_list = dork_list
        self.rate_limiter = rate_limiter or AdvancedRateLimiter()
        self.max_per_dork = max_per_dork
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        all_results: List[SearchResult] = []
        try:
            if not self.api_key or not self.cse_id:
                self.error_occurred.emit("API Key and CSE ID are required. Configure them in the Credentials tab.")
                return

            seen_links = set()
            total_dorks = len(self.dork_list)

            for idx, (cat_name, query) in enumerate(self.dork_list, start=1):
                if self._is_cancelled:
                    break

                can_req, msg = self.rate_limiter.can_request()
                if not can_req:
                    self.error_occurred.emit(msg)
                    break

                self.category_started.emit(cat_name, query, idx, total_dorks)
                pct = int((idx / total_dorks) * 100)
                self.progress_update.emit(pct, f"[{idx}/{total_dorks}] Running {cat_name}: {query[:35]}...")

                self.rate_limiter.throttle()

                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    "key": self.api_key,
                    "cx": self.cse_id,
                    "q": query,
                    "num": min(self.max_per_dork, 10),
                    "start": 1
                }

                try:
                    resp = requests.get(url, params=params, timeout=12)
                    self.rate_limiter.record_request()

                    if resp.status_code == 200:
                        data = resp.json()
                        items = data.get("items", [])
                        for item in items:
                            link = item.get("link", "")
                            if link and link not in seen_links:
                                seen_links.add(link)
                                sr = SearchResult(
                                    title=item.get("title", "No Title"),
                                    link=link,
                                    snippet=item.get("snippet", ""),
                                    category=cat_name,
                                    query=query
                                )
                                all_results.append(sr)
                        self.results_updated.emit(list(all_results))

                    elif resp.status_code == 429:
                        self.error_occurred.emit("HTTP 429: Rate limit hit. Cooling down...")
                    elif resp.status_code in (400, 403):
                        self.error_occurred.emit(f"HTTP {resp.status_code}: Error with API keys or permissions.")
                        break
                except Exception as e:
                    self.error_occurred.emit(f"Error executing dork: {str(e)}")

            if self._is_cancelled:
                self.progress_update.emit(100, f"Batch sweep cancelled by user. Aggregated {len(all_results)} results.")
            else:
                self.progress_update.emit(100, f"Reconnaissance completed: {len(all_results)} findings.")

        except Exception as e:
            self.error_occurred.emit(f"Unexpected batch worker error: {str(e)}")
        finally:
            self.batch_finished.emit(all_results)
