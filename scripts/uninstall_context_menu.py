"""
Uninstall LinkDrop Context Menu Entry

Removes the "LinkDrop Here" option from the Windows Explorer right-click menu.

MUST BE RUN AS ADMINISTRATOR.
"""

import sys
import ctypes
import winreg


# Registry path
SHELL_KEY = r"Directory\Background\shell\LinkDrop"


def is_admin() -> bool:
    """Check if script is running with admin privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def delete_key_recursive(hkey, key_path: str) -> bool:
    """
    Recursively delete a registry key and all its subkeys.

    Args:
        hkey: Registry hive (e.g., HKEY_CLASSES_ROOT)
        key_path: Path to the key to delete

    Returns:
        True if successful or key didn't exist
    """
    try:
        # Open the key
        key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_ALL_ACCESS)

        # Enumerate and delete subkeys first
        while True:
            try:
                subkey_name = winreg.EnumKey(key, 0)
                subkey_path = f"{key_path}\\{subkey_name}"
                delete_key_recursive(hkey, subkey_path)
            except OSError:
                # No more subkeys
                break

        winreg.CloseKey(key)

        # Now delete the key itself
        winreg.DeleteKey(hkey, key_path)
        return True

    except FileNotFoundError:
        # Key doesn't exist - that's fine
        return True
    except PermissionError:
        print(f"Error: Permission denied for key: {key_path}")
        return False
    except Exception as e:
        print(f"Error deleting key {key_path}: {e}")
        return False


def check_exists() -> bool:
    """Check if the context menu entry exists."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, SHELL_KEY, 0, winreg.KEY_READ)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False


def main():
    print("=" * 50)
    print("LinkDrop Context Menu Uninstaller")
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

    # Check if entry exists
    if not check_exists():
        print("Context menu entry not found - nothing to uninstall.")
        input("\nPress Enter to exit...")
        sys.exit(0)

    print("Found LinkDrop context menu entry.")
    print()

    # Confirm uninstall
    response = input("Remove context menu entry? [Y/n]: ").strip().lower()
    if response and response != 'y':
        print("Uninstall cancelled.")
        sys.exit(0)

    # Uninstall
    print()
    print("Removing...")

    if delete_key_recursive(winreg.HKEY_CLASSES_ROOT, SHELL_KEY):
        print()
        print("SUCCESS! Context menu entry removed.")
    else:
        print()
        print("Uninstall failed.")
        sys.exit(1)

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
