"""
Data models for the Google Dorking Tool.
Version 1.2.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any


@dataclass
class SearchResult:
    """Represents an individual search result item."""
    title: str
    link: str
    snippet: str
    category: str = "Manual"
    query: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "link": self.link,
            "snippet": self.snippet,
            "category": self.category,
            "query": self.query,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchResult":
        return cls(
            title=data.get("title", "No Title"),
            link=data.get("link", "No Link"),
            snippet=data.get("snippet", ""),
            category=data.get("category", "Manual"),
            query=data.get("query", ""),
            timestamp=data.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
