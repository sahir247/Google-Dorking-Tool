# Google Dorking Tool - Source Code Documentation

## Overview
`source code.py` is a Python-based application that provides a graphical user interface for performing advanced Google searches using specialized search operators (Google dorks). This tool is designed for security researchers, penetration testers, and IT professionals to demonstrate the power and risks of Google dorking techniques.

## Technical Requirements
- Python 3.8 or higher
- PyQt5 for the GUI components
- Requests library for API communication

## Installation for Development
```bash
# Clone the repository
git clone https://github.com/sahir247/google-dorking-tool.git

# Install dependencies
pip install PyQt5 requests
```

## API Configuration
The tool uses Google's Custom Search Engine (CSE) API. To use the application:

1. Replace the placeholder API credentials in the source code:
```python
self.api_key = 'your_api_key'  # Replace with your Google API key
self.cse_id = 'your_cse_id'    # Replace with your Custom Search Engine ID
```

2. To obtain these credentials:
   - Google API Key: Create one at [Google Cloud Console](https://console.cloud.google.com/)
   - Custom Search Engine ID: Set up at [Google Programmable Search Engine](https://programmablesearchengine.google.com/about/)

## Code Structure

### Main Components
- **GoogleDorkingApp Class**: The main application class that inherits from QMainWindow
- **UI Setup Methods**: `init_ui()`, `setup_search_tab()`, `setup_results_tab()`, `setup_help_tab()`
- **Search Functionality**: `perform_search()`, `run_auto_dorks()`, `generate_dorks()`
- **Results Management**: `update_results_table()`, `export_results()`

### Key Features Implemented
1. **Dual-mode Operation**:
   - Manual Dorking: Custom search queries using Google dork operators
   - Auto Dorking: Automatically generate and run multiple dork queries

2. **Auto Dorking Categories**:
   - Basic Information
   - Sensitive Files
   - Exposed Directories
   - Login Pages
   - Potential Vulnerabilities
   - Technologies
   - Social Media
   - Email Addresses
   - Subdomains
   - Person Search
   - Profile Pages
   - Images
   - News Articles
   - Academic/Publications

3. **Results Management**:
   - Table view with clickable links
   - Pagination support
   - Export to CSV, JSON, and TXT formats
   - Copy URL functionality
   - Open links directly in browser

4. **Additional Features**:
   - Save and load search queries
   - Pre-defined dork templates
   - Comprehensive help section

## Function Documentation

### Core Functions

#### `__init__(self)`
Initializes the application, sets up API credentials, and configures the main window.

#### `init_ui(self)`
Sets up the main user interface including title, mode selector, tabs, and status bar.

#### `setup_search_tab(self)`
Creates the search interface with both manual and auto dorking options.

#### `setup_results_tab(self)`
Creates the results table and export options.

#### `setup_help_tab(self)`
Provides documentation on Google dorking techniques.

#### `perform_search(self)`
Executes the search query using the Google CSE API and displays results.

#### `generate_dorks(self, target)`
Creates specialized search queries based on the target and selected categories.

#### `run_auto_dorks(self)`
Generates and executes multiple dork queries automatically.

### Utility Functions

#### `export_to_csv/json/txt(self, file_path)`
Exports search results to various file formats.

#### `save_query(self)` / `load_query(self)`
Saves and loads search queries to/from files.

#### `update_results_table(self)`
Populates the results table with search findings.

#### `update_pagination_controls(self)`
Manages pagination for search results.

## Building from Source
To build an executable:

```bash
# Install PyInstaller
pip install pyinstaller

# Create a single executable
pyinstaller --onefile --windowed dork.py

# The executable will be in the dist/ directory
```

## Contributing
Contributions to improve the Google Dorking Tool are welcome:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Security Considerations
This tool is meant for educational purposes and legitimate security testing only. Always obtain proper authorization before performing security tests on systems you do not own.

## License
This project is open source, available under the terms specified in the LICENSE file included in this repository.

