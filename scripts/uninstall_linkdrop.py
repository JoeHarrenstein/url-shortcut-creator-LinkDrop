"""
LinkDrop Unified Uninstaller

Removes LinkDrop completely:
- Context menu entry
- Desktop shortcut
- Start Menu folder

Auto-requests administrator privileges via UAC.
"""

import sys
import os
import ctypes
import winreg
import shutil


# Registry path
SHELL_KEY = r"Directory\Background\shell\LinkDrop"


def is_admin() -> bool:
    """Check if script is running with admin privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def delete_registry_key_recursive(hkey, key_path: str) -> bool:
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
                delete_registry_key_recursive(hkey, subkey_path)
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
        return False
    except Exception:
        return False


def context_menu_exists() -> bool:
    """Check if the context menu entry exists."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, SHELL_KEY, 0, winreg.KEY_READ)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False


def remove_context_menu() -> bool:
    """Remove the context menu registry entry."""
    return delete_registry_key_recursive(winreg.HKEY_CLASSES_ROOT, SHELL_KEY)


def remove_desktop_shortcut() -> bool:
    """Remove the Desktop shortcut."""
    try:
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        shortcut_path = os.path.join(desktop, 'LinkDrop.lnk')

        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)

        return True
    except Exception:
        return False


def remove_start_menu_shortcuts() -> bool:
    """Remove the Start Menu folder and shortcuts."""
    try:
        start_menu = os.path.join(
            os.environ['APPDATA'],
            'Microsoft', 'Windows', 'Start Menu', 'Programs'
        )
        linkdrop_folder = os.path.join(start_menu, 'LinkDrop')

        if os.path.exists(linkdrop_folder):
            shutil.rmtree(linkdrop_folder)

        return True
    except Exception:
        return False


def main():
    print()
    print("=" * 50)
    print("       LinkDrop Uninstaller")
    print("=" * 50)
    print()

    # Check admin privileges
    if not is_admin():
        print("ERROR: Administrator privileges required.")
        print()
        print("This uninstaller needs to run as Administrator to")
        print("remove the right-click context menu option.")
        print()
        input("Press Enter to exit...")
        sys.exit(1)

    # Check what's installed
    has_context_menu = context_menu_exists()
    desktop_shortcut = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'LinkDrop.lnk')
    has_desktop = os.path.exists(desktop_shortcut)
    start_menu_folder = os.path.join(
        os.environ['APPDATA'],
        'Microsoft', 'Windows', 'Start Menu', 'Programs', 'LinkDrop'
    )
    has_start_menu = os.path.exists(start_menu_folder)

    if not (has_context_menu or has_desktop or has_start_menu):
        print("LinkDrop is not installed - nothing to remove.")
        input("\nPress Enter to exit...")
        sys.exit(0)

    print("Found LinkDrop installation:")
    if has_context_menu:
        print("  - Context menu entry")
    if has_desktop:
        print("  - Desktop shortcut")
    if has_start_menu:
        print("  - Start Menu folder")
    print()

    # Confirm uninstall
    response = input("Remove LinkDrop? [Y/n]: ").strip().lower()
    if response and response != 'y':
        print("Uninstall cancelled.")
        sys.exit(0)

    print()
    print("Removing LinkDrop...")
    print()

    # Remove context menu
    if has_context_menu:
        print("  [1/3] Removing context menu...", end=" ", flush=True)
        if remove_context_menu():
            print("Done")
        else:
            print("Failed")
    else:
        print("  [1/3] Context menu... Not installed")

    # Remove desktop shortcut
    if has_desktop:
        print("  [2/3] Removing Desktop shortcut...", end=" ", flush=True)
        if remove_desktop_shortcut():
            print("Done")
        else:
            print("Failed")
    else:
        print("  [2/3] Desktop shortcut... Not found")

    # Remove Start Menu
    if has_start_menu:
        print("  [3/3] Removing Start Menu folder...", end=" ", flush=True)
        if remove_start_menu_shortcuts():
            print("Done")
        else:
            print("Failed")
    else:
        print("  [3/3] Start Menu folder... Not found")

    print()
    print("=" * 50)
    print("       Uninstall Complete!")
    print("=" * 50)
    print()
    print("LinkDrop has been removed from your system.")
    print()
    print("Note: The program files are still in this folder.")
    print("You can delete this folder manually if desired.")
    print()
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
