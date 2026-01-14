"""
LinkDrop Quick Popup

Minimal popup window for context menu integration.
Receives folder path as CLI argument and creates shortcut directly there.
Uses CustomTkinter for modern dark mode appearance.

Usage: python gui_quick.py "C:\\path\\to\\folder"
"""

import sys
import os
import ctypes
import customtkinter as ctk

# Add parent directory to path for imports when running as script
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core import create_url_shortcut, validate_url

# App colors
TEAL_ACCENT = "#4ecdc4"
TEAL_HOVER = "#5fe0d7"


def get_icon_path():
    """Get the path to the application icon, handling both dev and PyInstaller."""
    # Check for bundled resource (PyInstaller --add-data)
    if hasattr(sys, '_MEIPASS'):
        bundled = os.path.join(sys._MEIPASS, 'LinkDrop.ico')
        if os.path.exists(bundled):
            return bundled

    # Check next to executable (for PyInstaller onefile)
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        beside_exe = os.path.join(exe_dir, 'LinkDrop.ico')
        if os.path.exists(beside_exe):
            return beside_exe
        beside_exe = os.path.join(exe_dir, 'icon.ico')
        if os.path.exists(beside_exe):
            return beside_exe

    # Development mode - check assets folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_ico = os.path.join(script_dir, '..', 'assets', 'LinkDrop.ico')
    if os.path.exists(assets_ico):
        return os.path.abspath(assets_ico)

    assets_ico = os.path.join(script_dir, '..', 'assets', 'icon.ico')
    if os.path.exists(assets_ico):
        return os.path.abspath(assets_ico)

    return None


def set_dark_title_bar(window):
    """Set Windows dark mode title bar using DWM API."""
    try:
        window.update()
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(ctypes.c_int(1)),
            ctypes.sizeof(ctypes.c_int)
        )
    except Exception:
        pass


class QuickPopup(ctk.CTk):
    """Minimal popup window for quick shortcut creation."""

    def __init__(self, save_dir: str):
        super().__init__()

        self.save_dir = save_dir

        # Set dark mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.setup_window()
        set_dark_title_bar(self)
        self.create_widgets()
        self.bind_events()

    def setup_window(self):
        """Configure the main window."""
        self.title("LinkDrop")
        self.resizable(False, False)

        # Window size
        width, height = 380, 200

        # Center on screen
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Keep on top
        self.attributes('-topmost', True)

        # Set window icon
        icon_path = get_icon_path()
        if icon_path:
            self.iconbitmap(icon_path)

    def create_widgets(self):
        """Create and layout all widgets."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Main frame
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=0, sticky="nsew", padx=20, pady=15)
        main.grid_columnconfigure(0, weight=1)

        # URL field (first - for paste and auto-fill flow)
        ctk.CTkLabel(main, text="URL:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.url_entry = ctk.CTkEntry(main, placeholder_text="https://example.com")
        self.url_entry.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # Name field (auto-fills from URL)
        ctk.CTkLabel(main, text="Name:").grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.name_entry = ctk.CTkEntry(main, placeholder_text="Auto-fills from URL")
        self.name_entry.grid(row=3, column=0, sticky="ew", pady=(0, 15))

        # Button frame
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.grid(row=4, column=0, sticky="e")

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            width=80,
            fg_color=("#c0c0c0", "#3a3d4e"),
            hover_color=("#a0a0a0", "#4a4d5e"),
            text_color=("#333333", "#ffffff"),
            command=self.destroy
        ).grid(row=0, column=0, padx=(0, 10))

        self.create_btn = ctk.CTkButton(
            btn_frame,
            text="Create",
            width=80,
            fg_color=TEAL_ACCENT,
            hover_color=TEAL_HOVER,
            text_color="#1a1f2e",
            command=self.create_shortcut
        )
        self.create_btn.grid(row=0, column=1)

        # Focus on URL field
        self.url_entry.focus_set()

        # Check clipboard for URL on startup
        self.after(100, self._check_clipboard_for_url)

    def _check_clipboard_for_url(self):
        """Auto-fill URL from clipboard if it contains a valid URL."""
        try:
            clipboard = self.clipboard_get()
            if clipboard and not self.url_entry.get().strip():
                # Check if clipboard looks like a URL
                is_valid, normalized = validate_url(clipboard)
                if is_valid:
                    self.url_entry.insert(0, clipboard.strip())
                    self._check_auto_name()
        except Exception:
            # Clipboard may be empty or contain non-text data
            pass

    def bind_events(self):
        """Bind keyboard shortcuts."""
        self.bind('<Return>', lambda e: self.create_shortcut())
        self.bind('<Escape>', lambda e: self.destroy())
        self.url_entry.bind('<Control-v>', self.on_url_paste)

    def on_url_paste(self, event):
        """When pasting URL, suggest a name if name field is empty."""
        self.after(50, self._check_auto_name)

    def _check_auto_name(self):
        """Auto-fill name from URL domain if name is empty."""
        if self.name_entry.get().strip():
            return

        url = self.url_entry.get().strip()
        if not url:
            return

        try:
            from urllib.parse import urlparse
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            parsed = urlparse(url)
            domain = parsed.netloc
            name = domain.replace('www.', '').split('.')[0].title()
            if name:
                self.name_entry.delete(0, 'end')
                self.name_entry.insert(0, name)
        except Exception:
            pass

    def create_shortcut(self):
        """Validate inputs and create the shortcut."""
        url = self.url_entry.get().strip()
        name = self.name_entry.get().strip()

        # Validate
        if not url:
            self.url_entry.focus_set()
            return

        if not name:
            self.name_entry.focus_set()
            return

        is_valid, msg = validate_url(url)
        if not is_valid:
            self.url_entry.focus_set()
            return

        # Disable button during creation
        self.create_btn.configure(state="disabled")

        # Create shortcut
        result = create_url_shortcut(
            name=name,
            url=url,
            save_dir=self.save_dir,
            fetch_icon=True
        )

        if result.success:
            self.destroy()
        else:
            self.create_btn.configure(state="normal")


def main():
    # Get folder path from command line argument
    if len(sys.argv) < 2:
        save_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        print(f"No folder specified, using: {save_dir}")
    else:
        save_dir = sys.argv[1]

    # Validate folder exists
    if not os.path.isdir(save_dir):
        print(f"Error: Folder not found: {save_dir}")
        sys.exit(1)

    # Run the popup
    app = QuickPopup(save_dir)
    app.mainloop()


if __name__ == "__main__":
    main()
