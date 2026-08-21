# Google Dorking Tool v1.2.0 Release Notes

**Release Tag:** `v1.2.0`  
**Release Name:** `Google Dorking Tool v1.2.0 - PySide6, Visual Dork Builder & Multi-Target OSINT Suite`  
**Date:** August 21, 2026  
**License:** GNU Affero General Public License v3.0 (AGPLv3)

---

## 🌟 What's New in Version 1.2.0

Version 1.2.0 is a complete ground-up re-architecture from the legacy monolithic script to a high-performance, modular desktop application powered by **PySide6 (Qt 6.11+)**, **Qt Designer**, and external **QSS Stylesheets**.

### 1. 📋 Interactive Visual Dork Form Builder
- Construct complex Google Dorks without syntax errors or spacing bugs.
- Dedicated input fields for:
  - **In Title (`intitle:`)**: `admin, login, portal`
  - **In URL (`inurl:`)**: `auth, wp-login, .php?id=`
  - **In Page Content (`intext:`)**: `password, confidential, API_KEY`
  - **Exact Phrase (`" "`)**: `"Index of /"`
  - **Exclusions (`-`)**: `github.com, stackoverflow.com`
- **Clickable File Extension Pills**: One-click toggles for `PDF`, `DOCX`, `XLSX`, `SQL`, `ENV`, `LOG`, `BAK`, `CONF`, `YML`, and `JSON`.

---

### 2. 🎯 Multi-Target Entity OSINT Engine
No longer restricted to website domains. Intelligently tailors search syntax to the target entity:
- **Domains & Hostnames** (`target.com`): Subdomain enumeration, open directories, database dumps, cloud buckets, and SQLi error discovery.
- **Email Addresses** (`user@target.com`): Credential leaks, breach databases, pastebins, employee rosters, and sensitive documents.
- **Person Names** (`"John Doe"`): Resumes/CVs, social media footprints, court/legal records, conference presentations, and direct contact lookups.
- **Usernames & Keywords** (`cyber_user`): GitHub/GitLab repositories, developer profiles, Docker hubs, forum accounts, and leak combos.

---

### 3. 💬 Real-Time Plain-English Query Explainer & Complexity Analyzer
- Automatically translates complex search dorks into plain, human-readable sentences directly below the query editor.
- Live telemetry badge displaying token count, character counter, complexity level (`Simple`, `Moderate`, `Advanced`), and detected operator tags.

---

### 4. 🚀 Dual Search Execution Modes
- **Google Custom Search JSON API Mode**: Automated in-app execution, live findings table, dynamic category filtering, pagination, and multi-format reporting.
- **Direct Web Browser Mode (Zero-API)**: Launches queries directly in your default browser. **Requires zero API keys and has no quota limits.**

---

### 5. 🛡️ Security Hardening & Rate Limiting
- **Fernet AES-128 Credential Vault**: Secures API keys and Custom Search IDs locally at `~/.google_dorking_tool/creds.dat`.
- **Token-Bucket Throttling**: 1.2s delay enforcing compliance with Google rate limits.
- **Daily Quota Meter**: Tracks requests against Google's free 100 queries/day tier with UTC midnight auto-reset.
- **CSV Formula Injection (DDE) Defense**: Prefixes formula control characters (`=`, `+`, `-`, `@`) with a single quote to protect spreadsheet applications.
- **HTML XSS Sanitization**: Escapes all crawled titles, URLs, and snippet texts in generated HTML reports.

---

### 6. 📊 Results Explorer & Multi-Format Exporters
- **Dynamic Category Filter Chips**: Instant category breakdown chips (`All`, `Login Pages`, `Credentials`, etc.) with real-time result counts.
- **5 Export Formats**:
  1. **CSV**: Excel-compatible with UTF-8 BOM and formula injection hardening.
  2. **JSON**: Structured JSON with ISO timestamps.
  3. **Styled HTML Report**: Standalone, responsive dark-themed executive dossier.
  4. **Markdown**: GitHub-flavored Markdown tables.
  5. **Plain Text**: Formatted ASCII text report.

---

### 7. 🎨 Cyber Obsidian Dark & Clean Light Themes
- Built with pure Vanilla QSS stylesheets (`dark.qss` and `light.qss`).
- **Zero Emojis**: Professional, clean typography and standard cybersecurity designations.
- **Non-Switching Tabs**: Eliminated accidental tab jumping during mouse wheel or trackpad scrolling.
- **Global Keyboard Shortcuts**:
  - `Ctrl+Enter`: Execute search from query box
  - `Ctrl+1` - `Ctrl+5`: Switch between tabs
  - `Ctrl+F`: Focus search/filter inputs
  - `Ctrl+L`: Toggle Dark / Light theme
  - `F5`: Refresh active data

---

## 📦 Package Layout

```text
Google-Dorking-Tool-1.1/
├── main.py                         # Canonical application entry point
├── GoogleDorkingTool-v1.2.py        # Versioned top-level launcher
├── GoogleDorkingTool-v1.1.py        # Backward compatibility redirect
├── pyproject.toml                   # Standard packaging build metadata
├── requirements.txt                 # Runtime dependencies
├── run.bat                          # Windows one-click launcher
├── install_requirements.bat         # Windows dependency installer
├── README.md                        # Project documentation
├── DOCUMENTATION.md                 # System architecture & technical specification
├── RELEASE.md                       # This release document
├── SECURITY.md                      # Security & vulnerability reporting policy
├── LICENSE                          # AGPLv3 License
├── .github/
│   ├── workflows/python-publish.yml # Automated PyPI build and publish workflow
│   └── ISSUE_TEMPLATE/              # Standard GitHub issue forms
└── dork_tool/                       # Modular Python package
    ├── models.py
    ├── security.py
    ├── rate_limiter.py
    ├── engine.py
    ├── workers.py
    ├── bookmarks.py
    ├── exporter.py
    └── ui/
        ├── loader.py
        ├── main_window.py
        ├── search_tab.py
        ├── results_tab.py
        ├── saved_tab.py
        ├── creds_tab.py
        ├── help_tab.py
        ├── styles/ (dark.qss, light.qss)
        └── designer/ (main_window.ui)
```

---

## 💻 Quick Start & Installation

### Option A: Windows Launcher (One-Click)
1. Double-click `install_requirements.bat`.
2. Double-click `run.bat`.

### Option B: Terminal / PowerShell
```powershell
# Install dependencies
python -m pip install -r requirements.txt

# Run application
python GoogleDorkingTool-v1.2.py
# Or: python main.py
```

### Option C: Install as Package
```powershell
python -m pip install .
google-dorking-tool
```

---

## ⚖️ License & Ethical Use
- **License**: [GNU Affero General Public License v3.0 (AGPLv3)](./LICENSE)
- **Ethical Disclaimer**: This tool is designed strictly for authorized penetration testing, security assessments, and legitimate OSINT research. Always obtain explicit authorization before testing any target.
