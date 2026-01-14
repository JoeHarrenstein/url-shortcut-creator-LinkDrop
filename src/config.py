"""
LinkDrop Configuration Management

Handles loading/saving user preferences to JSON config file.
"""

import os
import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict


CONFIG_FILENAME = "linkdrop_config.json"
MAX_RECENT_FOLDERS = 10


def get_config_path() -> Path:
    """Get the path to the config file in user's app data."""
    app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
    config_dir = Path(app_data) / 'LinkDrop'
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / CONFIG_FILENAME


@dataclass
class Config:
    """Application configuration."""
    default_folder: str = ""
    recent_folders: list[str] = field(default_factory=list)
    favorite_folders: list[str] = field(default_factory=list)
    fetch_favicon_default: bool = True
    last_window_x: Optional[int] = None
    last_window_y: Optional[int] = None

    def add_recent_folder(self, folder: str) -> None:
        """Add a folder to recent list, moving it to front if already present."""
        folder = os.path.normpath(folder)

        # Remove if already in list
        if folder in self.recent_folders:
            self.recent_folders.remove(folder)

        # Add to front
        self.recent_folders.insert(0, folder)

        # Trim to max size
        self.recent_folders = self.recent_folders[:MAX_RECENT_FOLDERS]

    def add_favorite_folder(self, folder: str) -> None:
        """Add a folder to favorites."""
        folder = os.path.normpath(folder)
        if folder not in self.favorite_folders:
            self.favorite_folders.append(folder)

    def remove_favorite_folder(self, folder: str) -> None:
        """Remove a folder from favorites."""
        folder = os.path.normpath(folder)
        if folder in self.favorite_folders:
            self.favorite_folders.remove(folder)

    def get_initial_folder(self) -> str:
        """Get the best initial folder to show."""
        # Try default folder first
        if self.default_folder and os.path.isdir(self.default_folder):
            return self.default_folder

        # Try most recent folder
        for folder in self.recent_folders:
            if os.path.isdir(folder):
                return folder

        # Fall back to desktop
        return os.path.join(os.path.expanduser("~"), "Desktop")


def load_config() -> Config:
    """Load configuration from file, returning defaults if not found."""
    config_path = get_config_path()

    if not config_path.exists():
        return Config()

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return Config(
            default_folder=data.get('default_folder', ''),
            recent_folders=data.get('recent_folders', []),
            favorite_folders=data.get('favorite_folders', []),
            fetch_favicon_default=data.get('fetch_favicon_default', True),
            last_window_x=data.get('last_window_x'),
            last_window_y=data.get('last_window_y')
        )
    except (json.JSONDecodeError, IOError):
        return Config()


def save_config(config: Config) -> bool:
    """Save configuration to file."""
    config_path = get_config_path()

    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(config), f, indent=2)
        return True
    except IOError:
        return False


if __name__ == "__main__":
    # Test config
    print(f"Config path: {get_config_path()}")

    config = load_config()
    print(f"Loaded config: {config}")

    config.add_recent_folder(r"C:\Test\Folder")
    config.add_recent_folder(r"C:\Another\Folder")
    print(f"After adding recent: {config.recent_folders}")

    save_config(config)
    print("Config saved")

    reloaded = load_config()
    print(f"Reloaded: {reloaded}")
