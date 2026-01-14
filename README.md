# LinkDrop

[![GitHub release](https://img.shields.io/github/v/release/JoeHarrenstein/url-shortcut-creator-LinkDrop)](https://github.com/JoeHarrenstein/url-shortcut-creator-LinkDrop/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows-blue)](https://github.com/JoeHarrenstein/url-shortcut-creator-LinkDrop)
[![Python](https://img.shields.io/badge/python-3.10+-green)](https://www.python.org/)

A Windows desktop utility for creating `.url` shortcut files with automatic favicon fetching. Perfect for teams using shared network drives who need quick access to web-based project resources.

## Features

- **Single Mode** - Create one shortcut at a time with a clean, simple interface
- **Batch Mode** - Create multiple shortcuts at once
- **Favicon Fetching** - Automatically downloads and applies website icons
- **Right-Click Integration** - "LinkDrop Here" context menu option in Windows Explorer
- **Dark Mode UI** - Modern interface using CustomTkinter
- **UNC Path Support** - Works with network paths (`\\server\share\folder`)

## Screenshots

### Main Application - Single Mode
![Single Mode](screenshots/Main%20App%20-%20Single%20Mode.png)

### Main Application - Batch Mode
![Batch Mode](screenshots/Main%20App%20-%20Batch%20Mode.png)

### Right-Click Context Menu
![Context Menu](screenshots/Context%20Menu.png)

### Quick Popup
![Quick Popup](screenshots/Quick%20popup.png)

## Installation

### Option 1: Download Release (Recommended)

1. Download the latest release ZIP from the [Releases page](https://github.com/JoeHarrenstein/url-shortcut-creator-LinkDrop/releases)
2. Extract to a folder (e.g., `C:\Program Files\LinkDrop`)
3. Run `Install_LinkDrop.exe`
4. Click "Yes" on the UAC prompt

This will:
- Add "LinkDrop Here" to your right-click context menu
- Create a Desktop shortcut
- Add LinkDrop to your Start Menu

### Option 2: Build from Source

```bash
# Clone the repository
git clone https://github.com/JoeHarrenstein/url-shortcut-creator-LinkDrop.git
cd url-shortcut-creator-LinkDrop

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/gui_main.py

# Or build executables
python scripts/build.py
```

## Usage

### Right-Click Context Menu (Fastest)

1. Open any folder in Windows Explorer
2. Right-click on empty space
3. Select "LinkDrop Here"
4. Enter URL and name
5. Click "Create"

### Desktop Application

1. Launch LinkDrop from Desktop or Start Menu
2. Enter URL (name auto-fills from domain)
3. Choose save location
4. Click "Create Shortcut"

### Batch Mode

1. Open LinkDrop and click the "Batch" tab
2. Enter URL and Name for each row
3. Click "+ Add Row" for more entries
4. Click "Create All"

## Requirements

- Windows 10/11
- Python 3.10+ (for building from source)

## Dependencies

- `customtkinter` - Modern dark-mode UI
- `requests` - Favicon fetching
- `Pillow` - Icon processing
- `pywin32` - Windows shortcut creation
- `pyinstaller` - Building executables

## Project Structure

```
├── src/
│   ├── core.py          # URL validation, .url file creation, favicon fetching
│   ├── gui_main.py      # Full desktop application
│   ├── gui_quick.py     # Minimal popup for context menu
│   ├── config.py        # Configuration settings
│   └── theme.py         # UI theming
├── scripts/
│   ├── build.py         # PyInstaller build script
│   ├── install_linkdrop.py    # Unified installer
│   └── uninstall_linkdrop.py  # Unified uninstaller
├── assets/
│   └── LinkDrop.ico     # Application icon
└── dist/
    └── README.txt       # Distribution readme
```

## Uninstalling

Run `Uninstall_LinkDrop.exe` to remove:
- Right-click context menu entry
- Desktop shortcut
- Start Menu folder

Then delete the installation folder.

## License

MIT License - Feel free to use and modify.
