"""
LinkDrop Build Script

Builds the LinkDrop executables using PyInstaller:
- LinkDrop.exe (full application)
- LinkDropQuick.exe (context menu popup)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def check_pyinstaller() -> bool:
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False


def convert_icon(project_root: Path) -> Path | None:
    """
    Convert PNG icon to ICO if needed.

    Returns path to .ico file or None if not available.
    """
    assets_dir = project_root / "assets"

    # Prefer LinkDrop.ico if it exists
    linkdrop_ico = assets_dir / "LinkDrop.ico"
    if linkdrop_ico.exists():
        return linkdrop_ico

    ico_path = assets_dir / "icon.ico"
    png_path = assets_dir / "icon.png"

    # Check alternate spelling
    if not assets_dir.exists():
        assets_dir = project_root / "assests"
        ico_path = assets_dir / "icon.ico"
        png_path = None
        # Look for any PNG in this folder
        if assets_dir.exists():
            for f in assets_dir.iterdir():
                if f.suffix.lower() == '.png':
                    png_path = f
                    break

    if ico_path.exists():
        return ico_path

    if png_path and png_path.exists():
        print(f"Converting {png_path.name} to icon.ico...")
        try:
            from PIL import Image

            img = Image.open(png_path)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            # Create multiple sizes for ICO
            sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            icons = []
            for size in sizes:
                resized = img.resize(size, Image.Resampling.LANCZOS)
                icons.append(resized)

            # Ensure assets directory exists (correct spelling)
            proper_assets = project_root / "assets"
            proper_assets.mkdir(exist_ok=True)
            ico_path = proper_assets / "icon.ico"

            icons[0].save(
                ico_path,
                format='ICO',
                sizes=[s for s in sizes],
                append_images=icons[1:]
            )
            print(f"Created {ico_path}")
            return ico_path

        except Exception as e:
            print(f"Warning: Could not convert icon: {e}")
            return None

    print("Warning: No icon found in assets folder")
    return None


def build_executable(
    script_path: Path,
    name: str,
    icon_path: Path | None,
    dist_dir: Path,
    onefile: bool = True,
    windowed: bool = True,
    console: bool = False,
    uac_admin: bool = False
) -> bool:
    """
    Build a single executable using PyInstaller.

    Args:
        script_path: Path to the Python script
        name: Output executable name (without .exe)
        icon_path: Path to icon file (optional)
        dist_dir: Output directory
        onefile: Create single-file executable
        windowed: Hide console window (GUI app)
        console: Show console window
        uac_admin: Request admin privileges via UAC

    Returns:
        True if build succeeded
    """
    print(f"\nBuilding {name}.exe...")
    print("-" * 40)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        f"--name={name}",
        f"--distpath={dist_dir}",
        f"--workpath={dist_dir / 'build'}",
        f"--specpath={dist_dir / 'build'}",
    ]

    if onefile:
        cmd.append("--onefile")

    if windowed and not console:
        cmd.append("--windowed")
    elif console:
        cmd.append("--console")

    if uac_admin:
        cmd.append("--uac-admin")

    if icon_path and icon_path.exists():
        cmd.append(f"--icon={icon_path}")
        # Bundle the icon file so it can be used at runtime
        cmd.append(f"--add-data={icon_path};.")

    cmd.append(str(script_path))

    try:
        result = subprocess.run(cmd, check=True)
        print(f"Successfully built {name}.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building {name}.exe: {e}")
        return False


def main():
    print("=" * 50)
    print("LinkDrop Build Script")
    print("=" * 50)

    project_root = get_project_root()
    print(f"Project root: {project_root}")

    # Check PyInstaller
    if not check_pyinstaller():
        print("\nError: PyInstaller is not installed.")
        print("Install it with: pip install pyinstaller")
        sys.exit(1)

    # Setup directories
    dist_dir = project_root / "dist"
    dist_dir.mkdir(exist_ok=True)

    src_dir = project_root / "src"

    # Convert icon
    icon_path = convert_icon(project_root)

    # Copy icon to dist for context menu registration and runtime access
    if icon_path and icon_path.exists():
        shutil.copy(icon_path, dist_dir / "icon.ico")
        # Also copy as LinkDrop.ico for the title bar icon
        shutil.copy(icon_path, dist_dir / "LinkDrop.ico")

    # Build main application
    main_script = src_dir / "gui_main.py"
    if not main_script.exists():
        print(f"Error: {main_script} not found")
        sys.exit(1)

    success1 = build_executable(
        script_path=main_script,
        name="LinkDrop",
        icon_path=icon_path,
        dist_dir=dist_dir,
        onefile=True,
        windowed=True
    )

    # Build quick popup
    quick_script = src_dir / "gui_quick.py"
    if not quick_script.exists():
        print(f"Error: {quick_script} not found")
        sys.exit(1)

    success2 = build_executable(
        script_path=quick_script,
        name="LinkDropQuick",
        icon_path=icon_path,
        dist_dir=dist_dir,
        onefile=True,
        windowed=True
    )

    # Build unified installer (with UAC auto-elevation)
    install_script = project_root / "scripts" / "install_linkdrop.py"
    uninstall_script = project_root / "scripts" / "uninstall_linkdrop.py"

    success3 = True
    success4 = True

    if install_script.exists():
        success3 = build_executable(
            script_path=install_script,
            name="Install_LinkDrop",
            icon_path=icon_path,
            dist_dir=dist_dir,
            onefile=True,
            windowed=False,
            console=True,
            uac_admin=True  # Auto-request admin privileges
        )

    if uninstall_script.exists():
        success4 = build_executable(
            script_path=uninstall_script,
            name="Uninstall_LinkDrop",
            icon_path=icon_path,
            dist_dir=dist_dir,
            onefile=True,
            windowed=False,
            console=True,
            uac_admin=True  # Auto-request admin privileges
        )

    # Summary
    print()
    print("=" * 50)
    print("Build Summary")
    print("=" * 50)

    if success1:
        main_exe = dist_dir / "LinkDrop.exe"
        print(f"LinkDrop.exe: {main_exe}")
        if main_exe.exists():
            size_mb = main_exe.stat().st_size / (1024 * 1024)
            print(f"  Size: {size_mb:.1f} MB")

    if success2:
        quick_exe = dist_dir / "LinkDropQuick.exe"
        print(f"LinkDropQuick.exe: {quick_exe}")
        if quick_exe.exists():
            size_mb = quick_exe.stat().st_size / (1024 * 1024)
            print(f"  Size: {size_mb:.1f} MB")

    if success3:
        install_exe = dist_dir / "Install_LinkDrop.exe"
        print(f"Install_LinkDrop.exe: {install_exe}")
        if install_exe.exists():
            size_mb = install_exe.stat().st_size / (1024 * 1024)
            print(f"  Size: {size_mb:.1f} MB")

    if success4:
        uninstall_exe = dist_dir / "Uninstall_LinkDrop.exe"
        print(f"Uninstall_LinkDrop.exe: {uninstall_exe}")
        if uninstall_exe.exists():
            size_mb = uninstall_exe.stat().st_size / (1024 * 1024)
            print(f"  Size: {size_mb:.1f} MB")

    all_success = success1 and success2 and success3 and success4

    if all_success:
        print()
        print("Build complete!")
        print()
        print("Distribution files in dist/ folder:")
        print("  - LinkDrop.exe          (main application)")
        print("  - LinkDropQuick.exe     (context menu popup)")
        print("  - Install_LinkDrop.exe  (double-click to install)")
        print("  - Uninstall_LinkDrop.exe (double-click to uninstall)")
        print("  - LinkDrop.ico          (application icon)")
        return 0
    else:
        print()
        print("Build failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
