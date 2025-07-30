# Google Dorking Tool v1.1 - Source Code Documentation

## Overview
`GoogleDorkingTool-v1.1.py` is an advanced Python-based application that provides a secure, modern graphical user interface for performing advanced Google searches using specialized search operators (Google dorks). This tool is designed for security researchers, penetration testers, and OSINT investigators with enhanced security features, encrypted credential management, and a comprehensive multi-tab interface.

## Technical Requirements
- Python 3.7 or higher
- PyQt5 for the advanced GUI components
- Requests library for API communication
- Cryptography library for secure credential storage

## Installation for Development
```bash
# Clone the repository
git clone https://github.com/sahir247/Google-Dorking-Tool.git

# Install dependencies using the automated installer
install_requirements.bat

# Or install manually
pip install PyQt5 requests cryptography
```

## API Configuration
The tool uses Google's Custom Search Engine (CSE) API with secure credential management. Unlike v1.0, API credentials are no longer hardcoded:

1. **Secure Configuration via UI**:
   - Open the Credentials tab in the application
   - Enter your Google API Key and CSE ID
   - Click Save (credentials are encrypted using Fernet encryption)
   - Credentials are stored locally in `~/.google_dorking_tool/creds.dat`

2. **To obtain these credentials**:
   - Google API Key: Create one at [Google Cloud Console](https://console.developers.google.com/apis/credentials)
   - Custom Search Engine ID: Set up at [Google Custom Search Engine](https://cse.google.com/cse/all)

## Code Structure

### Main Components
- **GoogleDorkingApp Class**: The main application class inheriting from QMainWindow with enhanced security
- **CredentialManager Class**: Handles secure encryption/decryption of API credentials
- **AdvancedRateLimiter Class**: Manages API rate limiting and daily quotas
- **GoogleSearchWorker Class**: QThread-based worker for non-blocking search operations
- **SearchResult Class**: Data container for search results with metadata

### UI Architecture
- **Multi-tab Interface**: Search, Results, Help, Credentials tabs
- **Mode Selector**: Toggle between Manual and Auto dorking modes
- **Progress Tracking**: Real-time search progress with status updates
- **Responsive Design**: Non-blocking UI with threaded operations

### Key Features Implemented

1. **Enhanced Security & Credential Management**:
   - Fernet encryption for API credentials
   - Local encrypted storage in user home directory
   - Real-time credential validation
   - No hardcoded API keys in source code

2. **Advanced Dual-mode Operation**:
   - **Manual Dorking**: Custom search queries with 19+ operators and templates
   - **Auto Dorking**: Intelligent query generation with 14 categories

3. **Auto Dorking Categories** (Enhanced from v1.0):
   - Basic Information
   - Sensitive Files (PDF, DOC, XLSX)
   - Exposed Directories
   - Login Pages
   - Potential Vulnerabilities
   - Technologies (WordPress detection)
   - Social Media Presence
   - Email Addresses
   - Subdomains
   - Person Search
   - Profile Pages
   - Images
   - News Articles
   - Academic/Publications

4. **Advanced Manual Dorking Tools** (New in v1.1):
   - 19+ Google search operators support
   - Operator insertion helper with value input
   - 9 predefined query templates
   - Site-specific search toggle
   - SafeSearch option

5. **Enhanced Results Management**:
   - Multi-tab interface with dedicated Results tab
   - Paginated results display (10/20/50/100 per page)
   - Export to CSV, JSON, and TXT formats
   - Sortable results table with clickable links
   - Real-time search progress tracking
   - Copy URL functionality
   - Open links directly in browser

6. **Performance & Rate Limiting** (New in v1.1):
   - Advanced rate limiter with burst control
   - Daily quota management (100 requests/day default)
   - Thread-based search operations for non-blocking UI
   - Progress tracking during searches

7. **Built-in Help System** (Enhanced):
   - Comprehensive user guide
   - API setup instructions with clickable links
   - Google dork operators reference
   - Educational warnings and responsible use guidelines

## Function Documentation

### Core Classes

#### `GoogleDorkingApp(QMainWindow)`
Main application class with enhanced security and modern UI.

**Key Methods:**
- `__init__(self)`: Initializes app with credential manager and rate limiter
- `_build_ui(self)`: Sets up multi-tab interface
- `_build_search_tab(self)`: Creates search interface with dual modes
- `_build_results_tab(self)`: Creates results table with pagination
- `_build_help_tab(self)`: Provides comprehensive help system
- `_build_cred_tab(self)`: Secure credential management interface

#### `CredentialManager`
Handles secure credential storage and validation.

**Key Methods:**
- `save(api_key, cse_id)`: Encrypts and saves credentials locally
- `load()`: Decrypts and loads stored credentials
- `validate(api_key, cse_id)`: Validates credentials with Google API

#### `AdvancedRateLimiter`
Manages API rate limiting and quota enforcement.

**Key Methods:**
- `wait()`: Enforces rate limits before API calls
- Daily quota tracking and burst control

#### `GoogleSearchWorker(QThread)`
Thread-based worker for non-blocking search operations.

**Key Methods:**
- `run()`: Executes search queries in background thread
- Emits progress signals and results

### Enhanced Functions

#### `_execute_queries(self, queries)`
Executes multiple search queries using the threaded worker with progress tracking.

#### `_run_auto(self)`
Enhanced auto-dorking with category selection and intelligent query generation.

#### `_run_manual(self)`
Manual dorking with operator helpers and template support.

#### `_export(self, format)`
Enhanced export functionality supporting CSV, JSON, and TXT formats.

#### `_populate_table(self)`
Populates results table with pagination support.

#### `_save_query(self)` / `_load_query(self)`
Enhanced query save/load functionality.

## What's New in v1.1

### Security Enhancements
- **Encrypted credential storage** using Fernet encryption
- **API credential validation** with real-time feedback
- **Secure local storage** in user home directory
- **No hardcoded credentials** in source code

### UI/UX Improvements
- **Multi-tab interface** replacing single window design
- **Mode selector** for Manual vs Auto dorking
- **Progress tracking** with real-time status updates
- **Responsive design** with non-blocking operations

### Feature Additions
- **Advanced rate limiting** with daily quota management
- **Enhanced manual dorking** with 19+ operators
- **Query templates** for common scenarios
- **Thread-based operations** for better performance
- **Comprehensive help system** with setup guides

### Technical Improvements
- **Modular architecture** with separate classes
- **Type hints** throughout codebase
- **Exception handling** and error reporting
- **Cross-platform compatibility** improvements

## Building from Source

### Create Standalone Executable
```bash
# Install PyInstaller
pip install pyinstaller

# Create executable with resources
python -m PyInstaller --onefile --windowed --add-data "github-mark.png;." --name "GoogleDorkingTool-v1.1" GoogleDorkingTool-v1.1.py

# The executable will be in the dist/ directory
```

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run from source
python GoogleDorkingTool-v1.1.py
```

## Architecture Improvements

### Security Architecture
- **Credential Manager**: Centralized, encrypted credential handling
- **Rate Limiter**: API quota management and burst control
- **Validation**: Real-time API credential validation

### Performance Architecture
- **Threading**: Non-blocking UI with QThread workers
- **Pagination**: Efficient results display with configurable page sizes
- **Caching**: Improved performance with session management

### UI Architecture
- **Multi-tab Design**: Organized interface with dedicated sections
- **Progress Tracking**: Real-time feedback during operations
- **Help System**: Built-in documentation and guides

## Contributing
Contributions to improve the Google Dorking Tool v1.1 are welcome:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature-branch`)
3. Make your changes and commit (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Submit a pull request

## Security Considerations
This tool is meant for educational purposes and legitimate security testing only. Version 1.1 includes enhanced security features:
- Encrypted credential storage
- Rate limiting to prevent abuse
- Educational warnings and responsible use guidelines
- Always obtain proper authorization before testing systems you do not own

## License
This project is licensed for Educational Use Only. This tool is meant for educational purposes and legitimate security testing only. The developers are not responsible for any misuse or damage caused by this tool.

## Version History
- **v1.1** (July 2025): Major security and feature update with encrypted credentials, multi-tab UI, rate limiting
- **v1.0** (Previous): Basic dorking functionality with hardcoded credentials

## Contact & Support
For support, issues, or suggestions:
- **GitHub**: [sahir247/Google-Dorking-Tool](https://github.com/sahir247/Google-Dorking-Tool)
- **Issues**: Create an issue on the repository
- **Discussions**: Use GitHub Discussions for questions

---

**Developed by:** [sahir247](https://github.com/sahir247)  
**Platform:** Windows (Executable) / Cross-platform (Python)  
**Status:** Active Development
