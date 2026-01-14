# LinkDrop - URL Shortcut Creator

## Project Overview

A Windows desktop utility that creates `.url` shortcut files for quick access to web resources. Designed for teams using shared network drives who need fast access to project-related web pages (Notion, Monday.com, SharePoint, etc.) without creating wrapper documents.

## Current State

The existing PowerShell script (`Create-URLShortcut.ps1`) provides basic functionality:
- Prompts for shortcut name and URL
- Opens Windows Save dialog
- Creates standard `.url` file format

## Target Features

### Core Functionality
1. **URL Shortcut Creation** - Create `.url` files with proper Windows format
2. **Favicon Fetching** - Automatically download and embed the website's favicon as the shortcut icon
3. **Description/Notes Field** - Add comments that appear in Windows file properties
4. **Batch Creation** - Create multiple shortcuts at once from a list of URLs
5. **Default Save Locations** - Remember last-used folder and allow setting favorites

### Two User Interfaces

#### 1. Full Desktop Application (GUI)
- Launched from desktop shortcut or taskbar pin
- Full-featured interface with:
  - Single URL entry mode
  - Batch mode (paste multiple URLs, one per line)
  - Notes/description field for each shortcut
  - Folder browser with recent/favorite locations
  - Settings panel for defaults
  - Option to fetch favicon (checkbox, default on)

#### 2. Context Menu Quick-Create
- Right-click in any folder → "Create URL Shortcut" or "LinkDrop Here"
- Minimal popup window:
  - Shortcut name field
  - URL field
  - Optional notes field (collapsed by default)
  - Create button
- Saves directly to the folder where user right-clicked (no save dialog)
- Fast and lightweight

### Technical Requirements

#### .url File Format
Standard Windows URL shortcut format:
```ini
[InternetShortcut]
URL=https://example.com
IconIndex=0
IconFile=C:\path\to\favicon.ico
; Comment line for notes (optional)
```

#### Favicon Handling
- Fetch favicon from `https://domain.com/favicon.ico` or parse HTML for `<link rel="icon">`
- Fall back to Google's favicon service: `https://www.google.com/s2/favicons?domain=example.com&sz=64`
- Save `.ico` file alongside `.url` file or in app cache folder
- Reference icon path in the `.url` file's `IconFile` field

#### Context Menu Registry Entry
Add entry at: `HKEY_CLASSES_ROOT\Directory\Background\shell\LinkDrop`
- Pass current folder path as argument to the quick-create executable
- Should include the app icon in the context menu

#### Configuration Storage
JSON config file for:
- Default save location
- Recent folders list (last 5-10)
- Favorite/pinned folders
- Default settings (auto-fetch favicon, etc.)

## Project Structure

```
linkdrop/
├── src/
│   ├── __init__.py
│   ├── core.py              # Core logic: create .url, fetch favicon, validate URL
│   ├── gui_main.py          # Full desktop application GUI
│   ├── gui_quick.py         # Minimal context menu popup
│   ├── config.py            # Config management (load/save JSON)
│   └── registry.py          # Windows registry helpers for context menu
├── assets/
│   ├── icon.ico             # App icon (convert from provided PNG)
│   └── icon.png             # Source icon
├── scripts/
│   ├── install_context_menu.py    # Add context menu entry (run as admin)
│   ├── uninstall_context_menu.py  # Remove context menu entry
│   └── build.py                   # PyInstaller build script
├── config.json              # User configuration (created on first run)
├── requirements.txt         # Python dependencies
├── README.md                # User documentation
├── CLAUDE.md                # Project context for Claude Code
└── original/
    └── Create-URLShortcut.ps1  # Original script for reference
```

## Dependencies

```
# requirements.txt
requests          # For favicon fetching
Pillow            # For icon processing/conversion
pyinstaller       # For building .exe (dev dependency)
```

Using tkinter for GUI (included with Python, no extra install).

## Build Outputs

Two executables via PyInstaller:
1. `LinkDrop.exe` - Full application
2. `LinkDropQuick.exe` - Context menu launcher (accepts folder path as argument)

Or single exe with command-line flag to switch modes.

## User Workflows

### Workflow 1: Desktop App - Single Shortcut
1. User launches LinkDrop from desktop/taskbar
2. Enters shortcut name: "Project Tracker"
3. Pastes URL: "https://notion.so/myteam/project-tracker"
4. Optionally adds note: "Q2 2025 project status"
5. Clicks Browse or uses recent folder dropdown
6. Clicks Create
7. App fetches favicon, creates .url file with icon

### Workflow 2: Desktop App - Batch Mode
1. User launches LinkDrop, clicks "Batch Mode" tab
2. Pastes list:
   ```
   Project Tracker | https://notion.so/project | Main dashboard
   Client Portal | https://client.example.com | Login required
   Budget Sheet | https://docs.google.com/spreadsheets/d/xxx
   ```
3. Format: `Name | URL | Notes (optional)` - one per line
4. Selects destination folder
5. Clicks "Create All"
6. Progress indicator shows each being created

### Workflow 3: Context Menu Quick-Create
1. User is browsing to `\\server\Projects\ClientABC\`
2. Right-clicks in empty space → selects "LinkDrop Here"
3. Small popup appears
4. Enters name: "Client Portal"
5. Pastes URL
6. Clicks Create (or presses Enter)
7. Shortcut appears in folder immediately
8. Popup closes

## UI Design Notes

### Full App
- Clean, modern Windows aesthetic
- Not overly complex - this is a utility, not a full application
- Tabs or toggle for Single/Batch mode
- Recent folders as dropdown, not a full tree browser

### Quick Popup
- Minimal and fast to load
- ~300x200 pixels
- Just the essentials: name, URL, create button
- Expandable "Options" section for notes
- Enter key submits, Escape closes

## Installation

### For Development
```bash
cd linkdrop
pip install -r requirements.txt
python src/gui_main.py  # Run full app
python src/gui_quick.py "C:\Test\Folder"  # Run quick mode
```

### For Distribution
1. Run `python scripts/build.py` to create executables
2. Run `python scripts/install_context_menu.py` as administrator to add context menu
3. Create desktop shortcut to `LinkDrop.exe`

## Testing Notes

- Test on network paths (UNC paths like `\\server\share\folder`)
- Test favicon fetch failure gracefully (use default icon)
- Test with very long URLs
- Test batch mode with malformed lines
- Test context menu on both local and network folders

## Original PowerShell Script Reference

The original script demonstrates:
- Basic .url file format
- Windows Forms Save dialog integration
- Input validation pattern
- Loop for creating multiple shortcuts

See `original/Create-URLShortcut.ps1`
