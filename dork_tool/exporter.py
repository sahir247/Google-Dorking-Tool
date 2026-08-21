"""
Multi-Format Export Manager: CSV, JSON, HTML, TXT, Markdown.
Professional styling with zero emojis.
Version 1.2.0
"""

import csv
import json
import html
from datetime import datetime
from typing import List
from .models import SearchResult


class ExportManager:
    """
    Exports search results into multiple structured and report formats.
    """

    @staticmethod
    def _safe_csv_cell(value) -> str:
        """
        Prevents spreadsheet formula injection when CSVs are opened in Excel or
        similar spreadsheet tools. Cells beginning with formula-control
        characters are prefixed with a single quote.
        """
        text = "" if value is None else str(value)
        stripped = text.lstrip()
        if text.startswith(("\t", "\r", "\n")) or stripped.startswith(("=", "+", "-", "@")):
            return "'" + text
        return text

    @staticmethod
    def export_csv(filepath: str, results: List[SearchResult]) -> bool:
        try:
            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Title", "URL", "Snippet", "Category", "Query", "Timestamp"])
                for r in results:
                    writer.writerow([
                        ExportManager._safe_csv_cell(r.title),
                        ExportManager._safe_csv_cell(r.link),
                        ExportManager._safe_csv_cell(r.snippet),
                        ExportManager._safe_csv_cell(r.category),
                        ExportManager._safe_csv_cell(r.query),
                        ExportManager._safe_csv_cell(r.timestamp),
                    ])
            return True
        except Exception as e:
            print(f"[ERROR] CSV Export failed: {e}")
            return False

    @staticmethod
    def export_json(filepath: str, results: List[SearchResult]) -> bool:
        try:
            data = {
                "generated_at": datetime.now().isoformat(),
                "total_results": len(results),
                "results": [r.to_dict() for r in results]
            }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[ERROR] JSON Export failed: {e}")
            return False

    @staticmethod
    def export_txt(filepath: str, results: List[SearchResult], query: str = "") -> bool:
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("=" * 80 + "\n")
                f.write("GOOGLE DORKING TOOL - RECONNAISSANCE REPORT\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Active Query: {query}\n")
                f.write(f"Total Results: {len(results)}\n")
                f.write("=" * 80 + "\n\n")

                for idx, r in enumerate(results, start=1):
                    f.write(f"[{idx}] {r.title}\n")
                    f.write(f"URL:      {r.link}\n")
                    f.write(f"Category: {r.category}\n")
                    f.write(f"Snippet:  {r.snippet}\n")
                    f.write("-" * 80 + "\n")
            return True
        except Exception as e:
            print(f"[ERROR] TXT Export failed: {e}")
            return False

    @staticmethod
    def export_markdown(filepath: str, results: List[SearchResult], query: str = "") -> bool:
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("# Google Dorking Reconnaissance Report\n\n")
                f.write(f"- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"- **Query:** `{query}`\n")
                f.write(f"- **Total Results:** {len(results)}\n\n")
                f.write("| # | Title | URL | Category | Snippet |\n")
                f.write("|---|-------|-----|----------|---------|\n")

                for idx, r in enumerate(results, start=1):
                    clean_title = r.title.replace("|", "-").replace("\n", " ")
                    clean_snippet = r.snippet.replace("|", "-").replace("\n", " ")
                    f.write(f"| {idx} | {clean_title} | [{r.link}]({r.link}) | {r.category} | {clean_snippet} |\n")
            return True
        except Exception as e:
            print(f"[ERROR] Markdown Export failed: {e}")
            return False

    @staticmethod
    def export_html(filepath: str, results: List[SearchResult], query: str = "") -> bool:
        try:
            cards_html = ""
            for idx, r in enumerate(results, start=1):
                safe_title = html.escape(r.title)
                safe_link = html.escape(r.link)
                safe_snippet = html.escape(r.snippet)
                safe_cat = html.escape(r.category)
                safe_time = html.escape(r.timestamp)

                cards_html += f"""
                <div class="result-card">
                    <div class="card-header">
                        <span class="badge category">{safe_cat}</span>
                        <span class="result-index">#{idx}</span>
                    </div>
                    <h3 class="title"><a href="{safe_link}" target="_blank" rel="noopener noreferrer">{safe_title}</a></h3>
                    <div class="url-link">{safe_link}</div>
                    <p class="snippet">{safe_snippet}</p>
                    <div class="card-footer">
                        <span class="timestamp">{safe_time}</span>
                        <a class="open-btn" href="{safe_link}" target="_blank" rel="noopener noreferrer">Open Link &rarr;</a>
                    </div>
                </div>
                """

            safe_query = html.escape(query)
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google Dorking OSINT Report - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        :root {{
            --bg: #0d1117;
            --surface: #161b22;
            --border: #30363d;
            --primary: #58a6ff;
            --accent: #1f6feb;
            --text: #c9d1d9;
            --text-heading: #f0f6fc;
            --muted: #8b949e;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding: 32px 16px;
        }}
        .container {{ max-width: 1100px; margin: 0 auto; }}
        header {{
            background-color: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
        }}
        h1 {{ color: var(--text-heading); font-size: 24px; margin-bottom: 8px; }}
        .meta-bar {{ display: flex; flex-wrap: wrap; gap: 16px; font-size: 14px; color: var(--muted); }}
        .meta-item strong {{ color: var(--primary); }}
        .result-card {{
            background-color: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 18px 20px;
            margin-bottom: 16px;
            transition: transform 0.15s, border-color 0.15s;
        }}
        .result-card:hover {{
            border-color: var(--primary);
            transform: translateY(-2px);
        }}
        .card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
        .badge {{
            display: inline-block;
            font-size: 12px;
            font-weight: 600;
            padding: 2px 10px;
            border-radius: 20px;
            background-color: #21262d;
            color: var(--primary);
            border: 1px solid var(--border);
        }}
        .result-index {{ font-size: 13px; font-weight: bold; color: var(--muted); }}
        .title {{ font-size: 17px; margin-bottom: 4px; }}
        .title a {{ color: var(--primary); text-decoration: none; }}
        .title a:hover {{ text-decoration: underline; }}
        .url-link {{
            font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
            font-size: 13px;
            color: #7ee787;
            word-break: break-all;
            margin-bottom: 8px;
        }}
        .snippet {{ font-size: 14px; color: #8b949e; margin-bottom: 12px; }}
        .card-footer {{ display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: var(--muted); }}
        .open-btn {{
            color: var(--primary);
            text-decoration: none;
            font-weight: 600;
            padding: 4px 10px;
            border: 1px solid var(--border);
            border-radius: 6px;
        }}
        .open-btn:hover {{ background-color: var(--border); }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Google Dorking OSINT Report</h1>
            <div class="meta-bar">
                <div class="meta-item">Generated: <strong>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</strong></div>
                <div class="meta-item">Total Findings: <strong>{len(results)}</strong></div>
                {f'<div class="meta-item">Target Query: <strong>{safe_query}</strong></div>' if safe_query else ''}
            </div>
        </header>
        <div class="results-container">
            {cards_html if results else '<p style="text-align:center; padding:40px; color:#8b949e;">No results found.</p>'}
        </div>
    </div>
</body>
</html>
"""
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            return True
        except Exception as e:
            print(f"[ERROR] HTML Export failed: {e}")
            return False

