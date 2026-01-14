# CLAUDE.md - LinkDrop Project Context

## What This Project Is

LinkDrop is a Windows desktop utility for creating `.url` shortcut files. It's designed for teams using shared network drives who need quick access to web-based project resources (Notion, Monday.com, SharePoint, etc.).

## Key Files

- `PROJECT_SPEC.md` - Full project specification with features, workflows, and technical details
- `original/Create-URLShortcut.ps1` - The original PowerShell script this is based on
- `assets/icon.png` - App icon to convert to .ico

## Tech Stack

- **Python 3.x** with **tkinter** for GUI (no external GUI framework needed)
- **requests** for fetching favicons
- **Pillow** for icon processing
- **PyInstaller** for building executables

## Architecture

Two entry points, one core:

1. `src/core.py` - All the actual work (URL validation, .url file creation, favicon fetching)
2. `src/gui_main.py` - Full desktop app with batch mode, settings, folder browser
3. `src/gui_quick.py` - Minimal popup for context menu (receives folder path as CLI argument)

## .url File Format

```ini
[InternetShortcut]
URL=https://example.com
IconIndex=0
IconFile=C:\path\to\icon.ico
```

## Context Menu Integration

Registry key at `HKEY_CLASSES_ROOT\Directory\Background\shell\LinkDrop\command` should invoke:
```
"C:\path\to\LinkDropQuick.exe" "%V"
```
Where `%V` is the current folder path.

## Commands to Remember

```bash
# Run full app during development
python src/gui_main.py

# Run quick popup with test folder
python src/gui_quick.py "C:\Users\joeh\Desktop"

# Build executables
python scripts/build.py

# Install context menu (requires admin)
python scripts/install_context_menu.py
```

## Important Behaviors

1. **Favicon fetching should fail gracefully** - If we can't get a favicon, just create the shortcut without an icon. Don't error out.

2. **Support UNC paths** - Network paths like `\\server\share\folder` must work. This is a primary use case.

3. **Quick popup must be FAST** - Minimal startup time. Users right-click expecting immediate response.

4. **Batch format** - `Name | URL | Notes` with pipe delimiter, notes optional. One entry per line.

## Development Order Suggestion

1. Get `core.py` working first with basic .url creation
2. Build `gui_quick.py` - simpler, proves the concept
3. Add favicon fetching to core
4. Build `gui_main.py` with full features
5. Registry/context menu setup scripts
6. PyInstaller build configuration
