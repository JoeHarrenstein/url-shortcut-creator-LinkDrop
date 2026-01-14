"""
LinkDrop Unified Installer

Installs LinkDrop with a single click:
- Context menu integration ("LinkDrop Here")
- Desktop shortcut
- Start Menu shortcuts

Auto-requests administrator privileges via UAC.
"""

import sys
import os
import ctypes
import winreg


# Registry paths for context menu
SHELL_KEY = r"Directory\Background\shell\LinkDrop"
COMMAND_KEY = r"Directory\Background\shell\LinkDrop\command"


def is_admin() -> bool:
    """Check if script is running with admin privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def get_install_dir() -> str:
    """Get the directory where the installer is located."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_exe_paths() -> tuple:
    """Get paths to LinkDrop executables."""
    install_dir = get_install_dir()

    main_exe = os.path.join(install_dir, "LinkDrop.exe")
    quick_exe = os.path.join(install_dir, "LinkDropQuick.exe")
    icon_path = os.path.join(install_dir, "LinkDrop.ico")

    return main_exe, quick_exe, icon_path


def create_shortcut(target_path: str, shortcut_path: str, icon_path: str = None,
                    description: str = "", working_dir: str = None) -> bool:
    """
    Create a Windows shortcut (.lnk file).

    Args:
        target_path: Path to the executable
        shortcut_path: Where to save the .lnk file
        icon_path: Optional icon file path
        description: Shortcut description
        working_dir: Working directory for the shortcut

    Returns:
        True if successful
    """
    try:
        import win32com.client

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target_path
        shortcut.Description = description

        if working_dir:
            shortcut.WorkingDirectory = working_dir
        else:
            shortcut.WorkingDirectory = os.path.dirname(target_path)

        if icon_path and os.path.exists(icon_path):
            shortcut.IconLocation = icon_path

        shortcut.save()
        return True

    except ImportError:
        # Fallback to PowerShell if win32com not available
        return create_shortcut_powershell(target_path, shortcut_path, icon_path, description)
    except Exception as e:
        print(f"  Error creating shortcut: {e}")
        return False


def create_shortcut_powershell(target_path: str, shortcut_path: str,
                                icon_path: str = None, description: str = "") -> bool:
    """Create shortcut using PowerShell as fallback."""
    try:
        import subprocess

        ps_script = f'''
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{target_path}"
$Shortcut.WorkingDirectory = "{os.path.dirname(target_path)}"
$Shortcut.Description = "{description}"
'''
        if icon_path and os.path.exists(icon_path):
            ps_script += f'$Shortcut.IconLocation = "{icon_path}"\n'

        ps_script += "$Shortcut.Save()"

        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            text=True
        )
        return result.returncode == 0

    except Exception as e:
        print(f"  Error creating shortcut via PowerShell: {e}")
        return False


def install_context_menu(quick_exe: str, icon_path: str) -> bool:
    """Install the right-click context menu entry."""
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

        # Set icon
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
        command = f'"{quick_exe}" "%V"'
        winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, command)

        winreg.CloseKey(cmd_key)
        return True

    except Exception as e:
        print(f"  Error: {e}")
        return False


def create_desktop_shortcut(main_exe: str, icon_path: str) -> bool:
    """Create a shortcut on the user's Desktop."""
    try:
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        shortcut_path = os.path.join(desktop, 'LinkDrop.lnk')

        return create_shortcut(
            target_path=main_exe,
            shortcut_path=shortcut_path,
            icon_path=icon_path,
            description="Create URL shortcuts quickly"
        )
    except Exception as e:
        print(f"  Error: {e}")
        return False


def create_start_menu_shortcuts(main_exe: str, quick_exe: str, icon_path: str) -> bool:
    """Create Start Menu folder with shortcuts."""
    try:
        # Get Start Menu Programs folder
        start_menu = os.path.join(
            os.environ['APPDATA'],
            'Microsoft', 'Windows', 'Start Menu', 'Programs'
        )

        # Create LinkDrop folder
        linkdrop_folder = os.path.join(start_menu, 'LinkDrop')
        os.makedirs(linkdrop_folder, exist_ok=True)

        # Create main app shortcut
        main_shortcut = os.path.join(linkdrop_folder, 'LinkDrop.lnk')
        success1 = create_shortcut(
            target_path=main_exe,
            shortcut_path=main_shortcut,
            icon_path=icon_path,
            description="Create URL shortcuts quickly"
        )

        # Create uninstaller shortcut if uninstaller exists
        install_dir = get_install_dir()
        uninstall_exe = os.path.join(install_dir, 'Uninstall_LinkDrop.exe')

        if os.path.exists(uninstall_exe):
            uninstall_shortcut = os.path.join(linkdrop_folder, 'Uninstall LinkDrop.lnk')
            create_shortcut(
                target_path=uninstall_exe,
                shortcut_path=uninstall_shortcut,
                icon_path=icon_path,
                description="Remove LinkDrop from your system"
            )

        return success1

    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    print()
    print("=" * 50)
    print("       LinkDrop Installer")
    print("=" * 50)
    print()

    # Check admin privileges
    if not is_admin():
        print("ERROR: Administrator privileges required.")
        print()
        print("This installer needs to run as Administrator to")
        print("add the right-click context menu option.")
        print()
        input("Press Enter to exit...")
        sys.exit(1)

    # Get executable paths
    main_exe, quick_exe, icon_path = get_exe_paths()

    # Verify files exist
    missing = []
    if not os.path.exists(main_exe):
        missing.append("LinkDrop.exe")
    if not os.path.exists(quick_exe):
        missing.append("LinkDropQuick.exe")

    if missing:
        print("ERROR: Missing required files:")
        for f in missing:
            print(f"  - {f}")
        print()
        print("Make sure all files are in the same folder as the installer.")
        input("\nPress Enter to exit...")
        sys.exit(1)

    print("Installing LinkDrop...")
    print()

    # Install context menu
    print("  [1/3] Installing context menu...", end=" ", flush=True)
    if install_context_menu(quick_exe, icon_path):
        print("Done")
    else:
        print("Failed")

    # Create desktop shortcut
    print("  [2/3] Creating Desktop shortcut...", end=" ", flush=True)
    if create_desktop_shortcut(main_exe, icon_path):
        print("Done")
    else:
        print("Failed")

    # Create Start Menu shortcuts
    print("  [3/3] Creating Start Menu shortcuts...", end=" ", flush=True)
    if create_start_menu_shortcuts(main_exe, quick_exe, icon_path):
        print("Done")
    else:
        print("Failed")

    print()
    print("=" * 50)
    print("       Installation Complete!")
    print("=" * 50)
    print()
    print("You can now:")
    print("  - Right-click in any folder -> 'LinkDrop Here'")
    print("  - Launch LinkDrop from your Desktop")
    print("  - Find LinkDrop in your Start Menu")
    print()
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
