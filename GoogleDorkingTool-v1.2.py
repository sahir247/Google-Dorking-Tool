#!/usr/bin/env python3
"""
Google Dorking Tool v1.2 - Advanced OSINT & Penetration Testing Suite
Top-level versioned launcher.
"""

import sys
import os

# Add package directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import main

if __name__ == "__main__":
    main()
