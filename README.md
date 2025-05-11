# Google-Dorking-tool
## Overview
The Google Dorking Tool is an advanced application that leverages Google's search capabilities to find specific information using specialized search operators (Google dorks). This tool provides both manual and automated dorking capabilities with a user-friendly interface.

## Features

### Two Operating Modes
- **Manual Dorking**: Create custom search queries using Google dork operators
- **Auto Dorking**: Automatically generate and run multiple dork queries based on a target name or domain

### Auto Dorking Categories
- **Basic Information**: General searches about the target
- **Sensitive Files**: Find documents and files related to the target
- **Exposed Directories**: Discover open directories
- **Login Pages**: Find login portals
- **Potential Vulnerabilities**: Search for common vulnerability indicators
- **Technologies**: Identify technologies used by the target
- **Social Media**: Find profiles across major social platforms
- **Email Addresses**: Discover email addresses related to the target
- **Subdomains**: Find subdomains of a target domain
- **Person Search**: Specialized queries for finding information about individuals
- **Profile Pages**: Search professional and personal profile sites
- **Images**: Find photos and images
- **News Articles**: Search major news sites
- **Academic/Publications**: Find research papers and academic profiles

### Results Management
- Table view with clickable links
- Pagination support
- Export to CSV, JSON, and TXT formats
- Copy URL functionality
- Open links directly in browser

### Additional Features
- Save and load search queries
- Pre-defined dork templates
- Comprehensive help section with Google dorking guide

## Installation

### Option 1: Run the Executable
1. Navigate to the `dist` folder
2. Double-click `dork.exe` to run the application

### Option 2: Install Using Setup Script
1. Run `setup.bat` as administrator
2. The script will:
   - Copy the application to Program Files
   - Create desktop and Start Menu shortcuts
   - Create an uninstaller

### Option 3: Run from Source
If you prefer to run from source code:
1. Ensure Python 3.8+ is installed
2. Install required packages: `pip install PyQt5 requests`
3. Run the script: `python dork.py`

## Usage

### Manual Dorking
1. Select "Manual Dorking" from the mode dropdown
2. Enter your search query or use the dork operators to build one
3. Click "Search" to execute the query
4. View results in the Results tab

### Auto Dorking
1. Select "Auto Dorking" from the mode dropdown
2. Enter a target name or domain in the input field
3. Select which categories of dorks you want to generate
4. Click "Generate & Run Dorks"
5. The tool will show all generated dorks and run the first one
6. Use the "Run Next Dork" button to cycle through the remaining dorks

### Person Search Example
To search for information about a person:
1. Select "Auto Dorking" mode
2. Enter the person's full name (e.g., "John Smith")
3. Ensure person-specific categories are selected (Person Search, Social Media, etc.)
4. Click "Generate & Run Dorks"
5. The tool will generate specialized queries to find information about the individual

## Google Dork Operators

### Common Operators
- `site:` - Limits results to a specific domain (e.g., site:example.com)
- `inurl:` - Searches for specific text in URLs (e.g., inurl:admin)
- `intitle:` - Searches for specific text in page titles (e.g., intitle:login)
- `intext:` - Searches for specific text in page content (e.g., intext:password)
- `filetype:` - Searches for specific file types (e.g., filetype:pdf)
- `ext:` - Same as filetype: (e.g., ext:pdf)
- `-` - Excludes results containing specific terms (e.g., admin -login)
- `OR` - Shows results with either term (e.g., admin OR administrator)
- `AND` - Shows results with both terms (e.g., admin AND password)
- `"exact phrase"` - Searches for an exact phrase (e.g., "index of admin")

### Advanced Operators
- `allintext:` - All terms must appear in the text of the page
- `allinurl:` - All terms must appear in the URL
- `allintitle:` - All terms must appear in the title
- `before:` - Results from before a specific date (e.g., before:2020-01-01)
- `after:` - Results from after a specific date (e.g., after:2020-01-01)

## Security Considerations
Google Dorking can be used for legitimate security research, but it can also be misused. Always ensure you have permission to test systems you don't own. This tool is provided for educational purposes only. The user is responsible for how they use this information.

## Uninstallation
If installed using the setup script:
1. Go to the installation directory (typically Program Files\Google Dorking Tool)
2. Run "Uninstall Google Dorking Tool" shortcut

## Troubleshooting
- **API Errors**: The tool uses Google's Custom Search API which has daily query limits. If you encounter API errors, you may have reached these limits.
- **No Results**: Some queries may not return results. Try modifying your search terms or using different operators.
- **Performance Issues**: When generating many dorks in Auto mode, the application may take a moment to process. This is normal behavior.

## License
This project is licensed under the MIT License - a permissive open-source license that allows nearly unrestricted use, modification, and distribution of the code.
Feel free to use it in your own projects! See the LICENSE file for more details.

## Contributing

We welcome contributions! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch (git checkout -b feature-branch).
3. Make your changes and commit (git commit -am 'Add new feature').
4. Push to the branch (git push origin feature-branch).
5. Open a pull request.

## Credits
This tool was developed as an educational resource for security researchers, penetration testers, and IT professionals to understand the power and risks of Google dorking techniques.

## Disclaimer
This tool is meant for educational purposes and legitimate security testing only. The developers are not responsible for any misuse or damage caused by this tool. Always obtain proper authorization before performing security tests on systems you do not own.
