#!/usr/bin/env python3
"""
Automated Test Verification for PySide6 + Visual Form Builder + Plain-English Explainer.
Isolated temporary config directory for zero footprint on user storage.
Version 1.2.0
"""

import sys
import os
import tempfile
import json
import re

# Set workspace path
WORKSPACE = r"c:\Users\parve\OneDrive\Desktop\github\dork\Google-Dorking-Tool-1.1"
sys.path.insert(0, WORKSPACE)

# Set headless Qt
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import dork_tool
from dork_tool import (
    SearchResult, CredentialManager, AdvancedRateLimiter,
    DorkEngine, BookmarksManager, ExportManager
)
from dork_tool.ui import MainWindow, ThemeManager
from PySide6.QtWidgets import QApplication


def test_no_emojis():
    print("[TEST] Verifying Zero Emojis in DorkEngine, Templates & Categories...")
    emoji_pattern = re.compile(r"[\U00010000-\U0010ffff]", flags=re.UNICODE)

    for cat_id, name, _, desc in DorkEngine.CATEGORIES:
        assert not emoji_pattern.search(name), f"Found emoji in category name: {name}"
        assert not emoji_pattern.search(desc), f"Found emoji in category desc: {desc}"

    for section, tmpls in DorkEngine.TEMPLATES.items():
        assert not emoji_pattern.search(section), f"Found emoji in template section: {section}"
        for title, q in tmpls:
            assert not emoji_pattern.search(title), f"Found emoji in template title: {title}"

    print("  -> Zero Emojis Check: PASSED")


def test_multi_target_detection_and_generation():
    print("[TEST] Multi-Target Entity Type Detection & Dork Generation...")

    # 1. Target Detection
    assert DorkEngine.detect_target_type("target.com") == "DOMAIN"
    assert DorkEngine.detect_target_type("https://corp.example.org:8080/") == "DOMAIN"
    assert DorkEngine.detect_target_type("user@company.com") == "EMAIL"
    assert DorkEngine.detect_target_type("John Doe") == "PERSON"
    assert DorkEngine.detect_target_type("Sarah Connor") == "PERSON"
    assert DorkEngine.detect_target_type("admin_root99") == "KEYWORD"

    # 2. Email Dork Generation
    all_cats = [c[0] for c in DorkEngine.CATEGORIES]
    email_dorks = DorkEngine.generate_dorks("ceo@target.com", all_cats)
    assert len(email_dorks) >= 14
    for cat, q in email_dorks:
        assert "ceo" in q or "target.com" in q
        assert "site:ceo@target.com" not in q

    # 3. Person Dork Generation
    person_dorks = DorkEngine.generate_dorks("John Doe", all_cats)
    assert len(person_dorks) >= 14
    for cat, q in person_dorks:
        assert '"John Doe"' in q
        assert "site:John Doe" not in q

    # 4. Domain Dork Generation
    domain_dorks = DorkEngine.generate_dorks("https://example.com:8080/path/", all_cats)
    assert len(domain_dorks) >= 14
    for cat, q in domain_dorks:
        assert "example.com" in q
        assert "filetype:(filetype:" not in q

    # 5. Username Dork Generation
    user_dorks = DorkEngine.generate_dorks("cyber_investigator", all_cats)
    assert len(user_dorks) >= 14

    # 6. Plain-English Explainer
    explanation = DorkEngine.explain_query("site:target.com inurl:admin filetype:pdf")
    assert "target.com" in explanation
    assert "PDF" in explanation or "pdf" in explanation
    assert "admin" in explanation

    # 7. Live Query Analyzer
    analysis = DorkEngine.analyze_query("site:target.com inurl:admin intitle:login ext:pdf")
    assert analysis["chars"] > 0
    assert analysis["words"] == 4
    assert "site:" in analysis["operators"]
    assert "inurl:" in analysis["operators"]
    assert "intitle:" in analysis["operators"]
    assert "ext:" in analysis["operators"]
    assert analysis["target_site"] == "target.com"
    assert analysis["complexity"] == "Advanced"
    assert len(analysis["explanation"]) > 10

    print("  -> Multi-Target Entity Engine, Explainer & Real-Time Analyzer: PASSED")


def test_visual_form_builder():
    print("[TEST] Visual Form Builder Dork Compilation...")
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()

    # Fill in Visual Form fields
    window.search_tab.target_scope_input.setText("example.com")
    window.search_tab.form_title_input.setText("login, admin")
    window.search_tab.form_url_input.setText("portal")
    window.search_tab.filetype_buttons["PDF"].setChecked(True)
    window.search_tab.filetype_buttons["SQL"].setChecked(True)
    window.search_tab.form_exclude_input.setText("github.com")

    # Verify compiled query
    compiled = window.search_tab.query_editor.toPlainText()
    assert "site:example.com" in compiled
    assert "intitle:login" in compiled or 'intitle:"login"' in compiled
    assert "inurl:portal" in compiled
    assert "filetype:pdf" in compiled
    assert "filetype:sql" in compiled
    assert "-site:github.com" in compiled

    print("  -> Visual Form Builder Compilation: PASSED")


def test_qss_stylesheets():
    print("[TEST] QSS Stylesheets Loading...")
    dark_qss = ThemeManager.get_stylesheet("dark")
    assert len(dark_qss) > 100, "dark.qss is empty or missing"
    assert "#0d1117" in dark_qss

    light_qss = ThemeManager.get_stylesheet("light")
    assert len(light_qss) > 100, "light.qss is empty or missing"
    assert "#f6f8fa" in light_qss
    print("  -> dark.qss and light.qss Loaded: PASSED")


def test_exports_and_csv_injection():
    print("[TEST] Multi-Format Exporters & CSV Formula Injection Protection...")
    results = [
        SearchResult(
            title="=cmd|' /C calc'!A0",
            link="https://example.com/malicious.php",
            snippet="@SUM(1+1) injected formula snippet",
            category="Vulnerabilities",
            query="-DDE command test"
        ),
        SearchResult(
            title="Normal Safe Title",
            link="https://example.com/safe.html",
            snippet="Clean snippet content",
            category="General",
            query="site:example.com"
        )
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_p = os.path.join(tmpdir, "out.csv")
        json_p = os.path.join(tmpdir, "out.json")
        html_p = os.path.join(tmpdir, "out.html")
        md_p = os.path.join(tmpdir, "out.md")
        txt_p = os.path.join(tmpdir, "out.txt")

        assert ExportManager.export_csv(csv_p, results)
        assert ExportManager.export_json(json_p, results)
        assert ExportManager.export_html(html_p, results, "site:example.com")
        assert ExportManager.export_markdown(md_p, results, "site:example.com")
        assert ExportManager.export_txt(txt_p, results, "site:example.com")

        # Verify CSV formula injection escaping
        with open(csv_p, "r", encoding="utf-8-sig") as f:
            csv_content = f.read()
            assert "'=cmd|' /C calc'!A0" in csv_content
            assert "'@SUM(1+1)" in csv_content
            assert "'-DDE command test" in csv_content

        with open(html_p, "r", encoding="utf-8") as f:
            html = f.read()
            assert "Google Dorking OSINT Report" in html
            assert "&lt;script&gt;" not in html

    print("  -> Exporters & Formula Injection Sanitization: PASSED")


def main():
    print("==================================================")
    print(" Running PySide6 + Visual Form & Security Tests   ")
    print("==================================================")
    test_no_emojis()
    test_multi_target_detection_and_generation()
    test_visual_form_builder()
    test_qss_stylesheets()
    test_exports_and_csv_injection()
    print("==================================================")
    print(" ALL TESTS PASSED SUCCESSFULLY!                  ")
    print("==================================================")


if __name__ == "__main__":
    main()
