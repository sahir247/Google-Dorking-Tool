# Source Code Information

## About the Source Code
The `source code.py` file contains the complete source code for the Google Dorking Tool. This Python script uses PyQt5 for the GUI and the Google Custom Search API for performing searches.

## Requirements
- Python 3.8 or higher
- PyQt5
- Requests library

## Setting Up for Development
1. Clone this repository
2. Install the required dependencies:
   ```
   pip install PyQt5 requests
   ```
3. Open `dork.py` in your preferred Python IDE
4. Replace the placeholder API credentials with your own:
   ```python
   self.api_key = 'your_api_key'  # Replace with your Google API key
   self.cse_id = 'your_cse_id'    # Replace with your Custom Search Engine ID
   ```

## Getting Google API Credentials
To use this tool with full functionality, you'll need:
1. A Google API key: [Get one here](https://console.cloud.google.com/)
2. A Custom Search Engine ID: [Create one here](https://cse.google.com/cse/all)

## Code Structure
- `GoogleDorkingApp` class: Main application class
- `init_ui()`: Sets up the user interface
- `setup_search_tab()`, `setup_results_tab()`, `setup_help_tab()`: UI setup for each tab
- `run_auto_dorks()`: Generates dorks based on selected categories
- `perform_search()`: Executes search queries using the Google API
- `display_results()`: Formats and displays search results

## Contributing
Contributions to improve the Google Dorking Tool are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests with improvements

## Building from Source
To build the executable from source:
1. Install PyInstaller: `pip install pyinstaller`
2. Run: `pyinstaller --onefile --windowed dork.py`
3. The executable will be created in the `dist` folder

## License
This project is licensed under the terms specified in the LICENSE file included in this repository.
