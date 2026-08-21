# Google Dorking Tool v1.2

A PySide6 desktop application for building, explaining, running, filtering, and exporting Google dork queries for authorized OSINT and security assessment workflows.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](./LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![UI: PySide6](https://img.shields.io/badge/GUI-PySide6%20(Qt6)-green)](https://doc.qt.io/qtforpython/)
[![Security: Fernet AES](https://img.shields.io/badge/Security-Fernet_AES--128-success)](https://cryptography.io/)

This project is intended for security professionals, penetration testers, OSINT investigators, and students working on systems they own or are explicitly authorized to assess.

## Current maintenance status

Recent fixes and cleanup:

- Fixed automated batch sweep result duplication by treating worker updates as cumulative result sets.
- Added CSV formula-injection protection for exports opened in Excel or similar spreadsheet tools.
- Counted API credential validation requests against the local quota tracker.
- Added `pyproject.toml` so the release build workflow has packaging metadata.
- Added standard GitHub issue templates under `.github/ISSUE_TEMPLATE/`.
- Updated this README to match the current modular implementation.

## Features

- Multi-target query generation for:
  - domains and hostnames
  - email addresses
  - person names
  - usernames and keywords
- Automatic target type detection with manual override.
- Visual dork builder for `site:`, `intitle:`, `inurl:`, `intext:`, exact phrases, exclusions, and file types.
- Curated OSINT/security dork templates.
- Plain-English query explanation and live query complexity analysis.
- Automated target sweep using Google Custom Search API.
- Direct browser search mode that does not require API credentials.
- Results explorer with filtering, category chips, pagination, context menu actions, and link opening.
- Export formats:
  - CSV with UTF-8 BOM and formula-injection hardening
  - JSON
  - styled HTML report
  - Markdown
  - plain text
- Local bookmarks and search history.
- Encrypted local API credential storage using Fernet when `cryptography` is available.
- Daily API quota tracking with UTC-day rollover.
- Dark and light QSS themes.

## Project layout

```text
Google-Dorking-Tool-1.1/
├── main.py                         # Standard application entry point
├── GoogleDorkingTool-v1.2.py        # Windows-friendly versioned launcher
├── requirements.txt                 # Runtime dependencies
├── pyproject.toml                   # Packaging/build metadata
├── run.bat                          # Windows launcher
├── install_requirements.bat         # Windows dependency installer
├── dork_tool/
│   ├── engine.py                    # Dork generation, target detection, query analysis
│   ├── workers.py                   # Background Google Custom Search API workers
│   ├── models.py                    # SearchResult dataclass
│   ├── exporter.py                  # CSV/JSON/HTML/Markdown/TXT exports
│   ├── security.py                  # API credential storage and validation
│   ├── rate_limiter.py              # Daily quota and request throttling
│   ├── bookmarks.py                 # Bookmark/history persistence
│   └── ui/                          # PySide6 UI tabs and styles
└── scratch/test_modular_pyside6.py   # Local verification script
```

## Installation

### Option A: Windows launcher

1. Double-click `install_requirements.bat`.
2. Double-click `run.bat`.

### Option B: PowerShell or terminal

```powershell
python -m pip install -r requirements.txt
python main.py
```

You can also run the versioned launcher:

```powershell
python GoogleDorkingTool-v1.2.py
```

### Option C: Install as a local package

```powershell
python -m pip install .
google-dorking-tool
```

## API setup

The in-app automated search mode uses the Google Custom Search JSON API.

1. Create or select a Google Cloud project.
2. Enable the Custom Search API.
3. Create an API key.
4. Create a Programmable Search Engine and copy its Search Engine ID / CX.
5. Open the app's `Credentials & Quota` tab and save both values.

Environment variables take precedence over saved credentials:

```powershell
$env:GOOGLE_API_KEY = "your-api-key"
$env:GOOGLE_CSE_ID = "your-cse-id"
python main.py
```

Direct browser mode does not need API credentials.

## Local data storage

The app stores local state under the current user's home directory:

```text
~/.google_dorking_tool/
├── master.key       # Fernet key generated locally
├── creds.dat        # encrypted credentials, or base64 fallback if cryptography is unavailable
├── quota.json       # local daily request counter
├── bookmarks.json   # saved dork bookmarks
└── history.json     # recent execution history
```

Important security note: `creds.dat` is encrypted, but the encryption key is stored locally as `master.key`. This prevents casual plaintext exposure; it is not a replacement for operating-system account security or a dedicated secrets manager.

## Testing and verification

A local verification script is available:

```powershell
python scratch/test_modular_pyside6.py
```

It checks target detection, dork generation, query explanation, the visual form builder, QSS loading, and all export formats. It runs Qt in offscreen mode, but it still instantiates app managers and may create files under `~/.google_dorking_tool/`.

## Packaging

The repository now includes `pyproject.toml`, so the GitHub release workflow can build distributions with:

```powershell
python -m pip install build
python -m build
```

The package includes the `dork_tool` modules plus QSS and Qt Designer assets.

## Legal and ethical use

Use this tool only for authorized security assessments, penetration testing, research, and education. Do not use it to target systems, organizations, or people without explicit permission and a lawful basis.

## License

This project is licensed under the [GNU Affero General Public License v3.0](./LICENSE).
