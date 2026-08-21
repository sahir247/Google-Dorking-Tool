# Google Dorking Tool v1.2.0 - Standalone Windows Executable (.exe)

**Release:** `v1.2.0`  
**Binary Name:** `GoogleDorkingTool-v1.2.exe`  
**Target Platform:** Windows 10 / 11 (64-bit)  
**Distribution Type:** Portable Standalone Executable (Zero-Install, No Python Required)  
**License:** GNU Affero General Public License v3.0 (AGPLv3)

---

## 🚀 Quick Download & Run (No Python Required)

1. **Download:** Grab `GoogleDorkingTool-v1.2.exe` from the [GitHub Releases](https://github.com/sahir247/Google-Dorking-Tool/releases/tag/v1.2.0) page.
2. **Launch:** Double-click `GoogleDorkingTool-v1.2.exe` to run immediately.
   - *No Python installation or command-line setup required.*
   - *All Qt6 libraries, cryptography engines, and QSS stylesheets are self-contained.*

---

## 🔒 Binary Integrity & Checksums

Verify the authenticity and integrity of your downloaded `.exe` binary:

| Property | Specification |
| :--- | :--- |
| **File Name** | `GoogleDorkingTool-v1.2.exe` |
| **File Size** | ~53.5 MB |
| **Architecture** | Windows x86_64 (64-bit Intel/AMD) |
| **SHA-256 Checksum** | `DAFA24FBC8FEA88E2D201930CEBACE3CB4BA5144C848318DF7D52E1104C2A3DF` |

### Verify Checksum in PowerShell:
```powershell
Get-FileHash -Algorithm SHA256 .\GoogleDorkingTool-v1.2.exe
```

---

## 🌟 Executable Highlights & Capabilities

### 1. 📋 Visual Dork Form Builder (Zero Syntax Errors)
- Never memorize complex boolean syntax again. Fill in guided fields:
  - **In Title (`intitle:`)**: `admin, dashboard, login`
  - **In URL (`inurl:`)**: `portal, auth, wp-login`
  - **In Page Content (`intext:`)**: `password, confidential, API_KEY`
  - **Exact Phrase (`" "`)**: `"Index of /"`
  - **Exclusions (`-`)**: `github.com, stackoverflow.com`
- **Clickable File Extension Pills**: One-click toggles for `PDF`, `DOCX`, `XLSX`, `SQL`, `ENV`, `LOG`, `BAK`, `CONF`, `YML`, and `JSON`.

### 2. 🎯 Multi-Target Entity OSINT Support
- **Domain Recon** (`target.com`): Subdomain enumeration, open directories, database dumps, cloud storage, and SQLi error discovery.
- **Email OSINT** (`user@target.com`): Credential leaks, breach dumps, pastebins, employee rosters, and documents.
- **Person OSINT** (`"John Doe"`): Resumes/CVs, social media footprints, court records, and conference presentations.
- **Username OSINT** (`cyber_user`): GitHub/GitLab repositories, forum accounts, Docker registries, and leak combos.

### 3. 💬 Real-Time Plain-English Query Explainer
- Deconstructs your Google Dork queries in real time and displays a plain English translation directly below the editor.
- Displays live metrics: Character Count, Word Count, Complexity Rating (`Low`, `Medium`, `High`), and Detected Operators.

### 4. 🌐 Dual Search Execution
- **In-App Google Custom Search API**: Automated batch sweeps, real-time result tables, pagination, and multi-format exports.
- **Direct Browser Mode (Zero-API)**: One-click query launch in your default browser with **zero API keys and no daily quota limits**.

### 5. 🛡️ Enterprise Security & Quota Protection
- **Fernet AES-128 Encrypted Vault**: API credentials are encrypted locally in `~/.google_dorking_tool/creds.dat`.
- **Token-Bucket Throttling**: Enforces request delays to prevent HTTP 429 rate limit bans.
- **Daily Quota Meter**: Tracks daily requests with automatic UTC midnight resets.
- **CSV Formula Injection (DDE) Defense**: Sanitizes spreadsheet control characters to protect exported data.

### 6. 📊 5 Export Formats & Results Explorer
- Instant search filtering and dynamic category breakdown chips.
- Export findings into **CSV (Excel UTF-8 BOM)**, **JSON**, **Styled Dark HTML Executive Report**, **Markdown**, and **Plain Text**.

### 7. 🎨 Cyber Obsidian Dark & Clean Light QSS Themes
- Full hardware-accelerated dark and light themes. Toggle anytime via `Ctrl+L`.
- **Zero Emojis**: Clean, professional layout for security audits and penetration test reports.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Ctrl+Enter` | Execute Search (from query editor) |
| `Ctrl+1` – `Ctrl+5` | Switch between tabs (Search, Results, Saved, Credentials, Guide) |
| `Ctrl+L` | Toggle Dark / Light Theme |
| `Ctrl+F` | Focus active tab's search / filter input |
| `F5` | Refresh data and quota display |

---

## 🛡️ Antivirus & Windows SmartScreen Notice

Because `GoogleDorkingTool-v1.2.exe` is a standalone binary generated with PyInstaller and is not code-signed with an expensive EV certificate:
- **Windows SmartScreen** may display *"Windows protected your PC"*.
- **To Run:** Click **"More info"** and then select **"Run anyway"**.
- The entire project is 100% open-source and can be independently inspected and compiled directly from source code.

---

## ⚙️ Building the Executable from Source

If you prefer building the `.exe` yourself:

```powershell
# 1. Clone repository
git clone https://github.com/sahir247/Google-Dorking-Tool.git
cd Google-Dorking-Tool

# 2. Install dependencies & PyInstaller
python -m pip install -r requirements.txt pyinstaller

# 3. Compile standalone executable
pyinstaller --noconfirm --onefile --windowed --name "GoogleDorkingTool-v1.2" --add-data "dork_tool/ui/styles;dork_tool/ui/styles" --add-data "dork_tool/ui/designer;dork_tool/ui/designer" main.py
```
The compiled binary will be placed in `dist/GoogleDorkingTool-v1.2.exe`.

---

## ⚖️ License & Ethical Disclaimer
- **License:** [GNU Affero General Public License v3.0 (AGPLv3)](./LICENSE)
- **Legal Notice:** This tool is strictly intended for authorized security evaluations, educational research, and penetration testing on assets you own or have explicit authorization to assess.
