"""
Install LinkDrop Context Menu Entry

Adds a "LinkDrop Here" option to the Windows Explorer right-click menu
when clicking in empty folder space.

MUST BE RUN AS ADMINISTRATOR.
"""

import sys
import os
import ctypes
import winreg


# Registry paths
SHELL_KEY = r"Directory\Background\shell\LinkDrop"
COMMAND_KEY = r"Directory\Background\shell\LinkDrop\command"


def is_admin() -> bool:
    """Check if script is running with admin privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def get_exe_path() -> str:
    """Get the path to LinkDropQuick.exe."""
    # When running as compiled exe, check same directory
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        quick_exe = os.path.join(exe_dir, "LinkDropQuick.exe")
        if os.path.exists(quick_exe):
            return quick_exe

    # Check common locations (development mode)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)

    # Check dist folder first (built executable)
    dist_exe = os.path.join(project_dir, "dist", "LinkDropQuick.exe")
    if os.path.exists(dist_exe):
        return dist_exe

    # Fall back to asking user
    print(f"LinkDropQuick.exe not found.")
    print()
    exe_path = input("Enter full path to LinkDropQuick.exe: ").strip().strip('"')

    if not os.path.exists(exe_path):
        print(f"Error: File not found: {exe_path}")
        sys.exit(1)

    return exe_path


def get_icon_path() -> str:
    """Get the path to the app icon."""
    # When running as compiled exe, check same directory
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        icon_path = os.path.join(exe_dir, "LinkDrop.ico")
        if os.path.exists(icon_path):
            return icon_path
        icon_path = os.path.join(exe_dir, "icon.ico")
        if os.path.exists(icon_path):
            return icon_path

    # Development mode
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)

    # Check for LinkDrop.ico in assets folder first
    icon_path = os.path.join(project_dir, "assets", "LinkDrop.ico")
    if os.path.exists(icon_path):
        return icon_path

    # Check for icon.ico in assets folder
    icon_path = os.path.join(project_dir, "assets", "icon.ico")
    if os.path.exists(icon_path):
        return icon_path

    # Check dist folder for LinkDrop.ico
    icon_path = os.path.join(project_dir, "dist", "LinkDrop.ico")
    if os.path.exists(icon_path):
        return icon_path

    # Check dist folder for icon.ico
    icon_path = os.path.join(project_dir, "dist", "icon.ico")
    if os.path.exists(icon_path):
        return icon_path

    return ""


def install_context_menu(exe_path: str, icon_path: str = "") -> bool:
    """
    Install the context menu registry entries.

    Args:
        exe_path: Full path to LinkDropQuick.exe
        icon_path: Optional path to icon file

    Returns:
        True if successful
    """
    try:
        # Create the shell key
        key = winreg.CreateKeyEx(
            winreg.HKEY_CLASSES_ROOT,
            SHELL_KEY,
            0,
            winreg.KEY_WRITE
        )

        # Set display name
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "LinkDrop Here")

        # Set icon if available
        if icon_path and os.path.exists(icon_path):
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon_path)

        winreg.CloseKey(key)

        # Create the command key
        cmd_key = winreg.CreateKeyEx(
            winreg.HKEY_CLASSES_ROOT,
            COMMAND_KEY,
            0,
            winreg.KEY_WRITE
        )

        # Set the command - %V is the current folder path
        command = f'"{exe_path}" "%V"'
        winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, command)

        winreg.CloseKey(cmd_key)

        return True

    except PermissionError:
        print("Error: Permission denied. Please run as Administrator.")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    print("=" * 50)
    print("LinkDrop Context Menu Installer")
    print("=" * 50)
    print()

    # Check admin
    if not is_admin():
        print("ERROR: This script must be run as Administrator.")
        print()
        print("Right-click on Command Prompt or PowerShell and select")
        print("'Run as administrator', then run this script again.")
        input("\nPress Enter to exit...")
        sys.exit(1)

    # Get executable path
    exe_path = get_exe_path()
    print(f"Using executable: {exe_path}")

    # Get icon path
    icon_path = get_icon_path()
    if icon_path:
        print(f"Using icon: {icon_path}")
    else:
        print("No icon found (context menu will use default icon)")

    print()

    # Confirm installation
    response = input("Install context menu entry? [Y/n]: ").strip().lower()
    if response and response != 'y':
        print("Installation cancelled.")
        sys.exit(0)

    # Install
    print()
    print("Installing...")

    if install_context_menu(exe_path, icon_path):
        print()
        print("SUCCESS! Context menu installed.")
        print()
        print("You can now right-click in any folder and select 'LinkDrop Here'")
        print("to quickly create URL shortcuts.")
    else:
        print()
        print("Installation failed.")
        sys.exit(1)

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
