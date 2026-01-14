"""
LinkDrop Main Application

Full desktop GUI for creating URL shortcuts with batch mode support.
Uses CustomTkinter for modern dark mode appearance.
"""

import sys
import os
import ctypes
import threading
import customtkinter as ctk

# Add parent directory to path for imports when running as script
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core import create_url_shortcut, validate_url, ShortcutResult
from src.config import Config, load_config, save_config

# App colors
TEAL_ACCENT = "#4ecdc4"
TEAL_HOVER = "#5fe0d7"
DARK_BG = "#2a2d3e"
DARKER_BG = "#252836"


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


class BatchRow(ctk.CTkFrame):
    """A single row in the batch entry table."""

    def __init__(self, parent, on_delete, row_num):
        super().__init__(parent, fg_color="transparent")
        self.on_delete = on_delete
        self.row_num = row_num

        self.grid_columnconfigure(0, weight=3)  # URL gets more space
        self.grid_columnconfigure(1, weight=2)  # Name

        # URL entry (first - for paste and auto-fill flow)
        self.url_entry = ctk.CTkEntry(self, placeholder_text="URL", height=32)
        self.url_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5), pady=2)

        # Name entry
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Name", height=32)
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=(5, 5), pady=2)

        # Delete button
        self.delete_btn = ctk.CTkButton(
            self,
            text="×",
            width=30,
            height=32,
            fg_color=("#c0c0c0", "#3a3d4e"),
            hover_color=("#ff6b6b", "#ff6b6b"),
            text_color=("#333333", "#ffffff"),
            command=self._delete
        )
        self.delete_btn.grid(row=0, column=2, padx=(0, 0), pady=2)

    def _delete(self):
        self.on_delete(self)

    def get_data(self):
        """Return (name, url) tuple."""
        return (
            self.name_entry.get().strip(),
            self.url_entry.get().strip()
        )

    def is_valid(self):
        """Check if row has valid data."""
        name, url = self.get_data()
        return bool(name and url)


class LinkDropApp(ctk.CTk):
    """Main LinkDrop application window."""

    def __init__(self):
        super().__init__()

        # Set dark mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.config_data = load_config()
        self.batch_rows = []

        self.setup_window()
        self.create_widgets()
        self.load_initial_state()

        # Set icon and dark title bar after window is ready
        self.after(100, self._finalize_window)

    def _finalize_window(self):
        """Finalize window setup after it's fully created."""
        set_dark_title_bar(self)
        # Re-apply icon after window is fully ready
        icon_path = get_icon_path()
        if icon_path:
            try:
                self.iconbitmap(icon_path)
                self.wm_iconbitmap(icon_path)
            except Exception:
                pass

    def setup_window(self):
        """Configure the main window."""
        self.title("LinkDrop - URL Shortcut Creator")
        self.minsize(600, 550)

        # Window size and position
        width, height = 650, 620

        # Use saved position or center on screen
        if self.config_data.last_window_x is not None and self.config_data.last_window_y is not None:
            x, y = self.config_data.last_window_x, self.config_data.last_window_y
        else:
            screen_w = self.winfo_screenwidth()
            screen_h = self.winfo_screenheight()
            x = (screen_w - width) // 2
            y = (screen_h - height) // 2

        self.geometry(f"{width}x{height}+{x}+{y}")

        # Set window icon
        icon_path = get_icon_path()
        if icon_path:
            self.iconbitmap(icon_path)

        # Handle close
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        """Create all widgets."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Tabview with styled tabs
        self.tabview = ctk.CTkTabview(
            main_frame,
            fg_color=("#e0e0e0", DARK_BG),
            segmented_button_fg_color=("#c0c0c0", "#3a3d4e"),
            segmented_button_selected_color=TEAL_ACCENT,
            segmented_button_selected_hover_color=TEAL_HOVER,
            segmented_button_unselected_color=("#d0d0d0", "#3a3d4e"),
            segmented_button_unselected_hover_color=("#b0b0b0", "#4a4d5e"),
            text_color=("#333333", "#ffffff"),
            text_color_disabled=("#666666", "#888888")
        )
        self.tabview.grid(row=0, column=0, sticky="nsew")

        # Configure tab button font size (make tabs larger)
        self.tabview._segmented_button.configure(font=ctk.CTkFont(size=14, weight="bold"))

        # Add tabs
        self.tab_single = self.tabview.add("  Single  ")
        self.tab_batch = self.tabview.add("  Batch  ")

        self.tab_single.grid_columnconfigure(0, weight=1)
        self.tab_batch.grid_columnconfigure(0, weight=1)
        self.tab_batch.grid_rowconfigure(1, weight=1)

        self.create_single_tab()
        self.create_batch_tab()

        # Folder selection frame
        folder_frame = ctk.CTkFrame(main_frame, fg_color=("#d0d0d0", DARKER_BG), corner_radius=10)
        folder_frame.grid(row=1, column=0, sticky="ew", pady=(15, 0))
        folder_frame.grid_columnconfigure(1, weight=1)

        self.create_folder_selector(folder_frame)

        # Status bar
        self.status_var = ctk.StringVar(value="Ready")
        status_label = ctk.CTkLabel(
            main_frame,
            textvariable=self.status_var,
            anchor="w",
            text_color=("#555555", "#888888")
        )
        status_label.grid(row=2, column=0, sticky="ew", pady=(10, 0))

    def create_single_tab(self):
        """Create the single shortcut tab."""
        tab = self.tab_single

        # URL field (first - for paste and auto-fill flow)
        ctk.CTkLabel(tab, text="URL:").grid(row=0, column=0, sticky="w", pady=(10, 5))
        self.single_url = ctk.CTkEntry(tab, placeholder_text="https://example.com", height=36)
        self.single_url.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.single_url.bind('<Control-v>', lambda e: self.after(50, self._auto_fill_name))

        # Name field (auto-fills from URL)
        ctk.CTkLabel(tab, text="Shortcut Name:").grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.single_name = ctk.CTkEntry(tab, placeholder_text="Auto-fills from URL, or enter a name", height=36)
        self.single_name.grid(row=3, column=0, sticky="ew", pady=(0, 15))

        # Options frame
        options_frame = ctk.CTkFrame(tab, fg_color="transparent")
        options_frame.grid(row=4, column=0, sticky="ew", pady=(0, 15))

        self.single_fetch_icon = ctk.CTkSwitch(
            options_frame,
            text="Fetch website favicon",
            progress_color=TEAL_ACCENT,
            button_color=TEAL_ACCENT,
            button_hover_color=TEAL_HOVER
        )
        self.single_fetch_icon.grid(row=0, column=0, sticky="w")
        if self.config_data.fetch_favicon_default:
            self.single_fetch_icon.select()

        # Button frame
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=5, column=0, sticky="e")

        ctk.CTkButton(
            btn_frame,
            text="Clear",
            width=90,
            height=36,
            fg_color=("#c0c0c0", "#3a3d4e"),
            hover_color=("#a0a0a0", "#4a4d5e"),
            text_color=("#333333", "#ffffff"),
            command=self.clear_single
        ).grid(row=0, column=0, padx=(0, 10))

        self.single_create_btn = ctk.CTkButton(
            btn_frame,
            text="Create Shortcut",
            width=130,
            height=36,
            fg_color=TEAL_ACCENT,
            hover_color=TEAL_HOVER,
            text_color="#1a1f2e",
            command=self.create_single
        )
        self.single_create_btn.grid(row=0, column=1)

    def create_batch_tab(self):
        """Create the batch mode tab with two-column entry."""
        tab = self.tab_batch

        # Header row
        header_frame = ctk.CTkFrame(tab, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(10, 5))
        header_frame.grid_columnconfigure(0, weight=3)  # URL gets more space
        header_frame.grid_columnconfigure(1, weight=2)  # Name

        ctk.CTkLabel(header_frame, text="URL", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=(0, 5)
        )
        ctk.CTkLabel(header_frame, text="Name", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=1, sticky="w", padx=5
        )

        # Scrollable frame for rows
        self.batch_scroll = ctk.CTkScrollableFrame(
            tab,
            fg_color=("#ffffff", "#2a3245"),
            corner_radius=8
        )
        self.batch_scroll.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        self.batch_scroll.grid_columnconfigure(0, weight=1)

        # Add initial rows
        for _ in range(3):
            self.add_batch_row()

        # Bottom controls
        controls_frame = ctk.CTkFrame(tab, fg_color="transparent")
        controls_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        controls_frame.grid_columnconfigure(1, weight=1)

        # Add row button
        ctk.CTkButton(
            controls_frame,
            text="+ Add Row",
            width=100,
            height=32,
            fg_color=("#c0c0c0", "#3a3d4e"),
            hover_color=("#a0a0a0", "#4a4d5e"),
            text_color=("#333333", "#ffffff"),
            command=self.add_batch_row
        ).grid(row=0, column=0, sticky="w")

        # Fetch favicon switch
        self.batch_fetch_icon = ctk.CTkSwitch(
            controls_frame,
            text="Fetch favicons",
            progress_color=TEAL_ACCENT,
            button_color=TEAL_ACCENT,
            button_hover_color=TEAL_HOVER
        )
        self.batch_fetch_icon.grid(row=0, column=1, sticky="e", padx=(10, 0))
        if self.config_data.fetch_favicon_default:
            self.batch_fetch_icon.select()

        # Progress bar (hidden by default)
        self.batch_progress = ctk.CTkProgressBar(tab, progress_color=TEAL_ACCENT, height=8)
        self.batch_progress.set(0)

        # Button frame
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=4, column=0, sticky="e")

        ctk.CTkButton(
            btn_frame,
            text="Clear All",
            width=90,
            height=36,
            fg_color=("#c0c0c0", "#3a3d4e"),
            hover_color=("#a0a0a0", "#4a4d5e"),
            text_color=("#333333", "#ffffff"),
            command=self.clear_batch
        ).grid(row=0, column=0, padx=(0, 10))

        self.batch_create_btn = ctk.CTkButton(
            btn_frame,
            text="Create All",
            width=110,
            height=36,
            fg_color=TEAL_ACCENT,
            hover_color=TEAL_HOVER,
            text_color="#1a1f2e",
            command=self.create_batch
        )
        self.batch_create_btn.grid(row=0, column=1)

    def add_batch_row(self):
        """Add a new row to the batch entry table."""
        row = BatchRow(self.batch_scroll, self.delete_batch_row, len(self.batch_rows))
        row.grid(row=len(self.batch_rows), column=0, sticky="ew", pady=2)
        self.batch_rows.append(row)

    def delete_batch_row(self, row):
        """Delete a row from the batch entry table."""
        if len(self.batch_rows) > 1:
            row.destroy()
            self.batch_rows.remove(row)
            # Re-grid remaining rows
            for i, r in enumerate(self.batch_rows):
                r.grid(row=i, column=0, sticky="ew", pady=2)

    def create_folder_selector(self, parent):
        """Create the folder selection widgets."""
        # Label
        ctk.CTkLabel(parent, text="Save Location", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", padx=15, pady=(10, 5)
        )

        # Folder entry
        self.folder_var = ctk.StringVar()
        self.folder_entry = ctk.CTkEntry(
            parent,
            textvariable=self.folder_var,
            placeholder_text="Select a folder...",
            height=36
        )
        self.folder_entry.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(15, 10), pady=(0, 10))

        # Browse button
        ctk.CTkButton(
            parent,
            text="Browse...",
            width=90,
            height=36,
            fg_color=("#c0c0c0", "#3a3d4e"),
            hover_color=("#a0a0a0", "#4a4d5e"),
            text_color=("#333333", "#ffffff"),
            command=self.browse_folder
        ).grid(row=1, column=2, padx=(0, 15), pady=(0, 10))

        # Recent label
        ctk.CTkLabel(parent, text="Recent:").grid(row=2, column=0, sticky="w", padx=15, pady=(0, 10))

        # Recent dropdown
        self.recent_combo = ctk.CTkComboBox(
            parent,
            values=[],
            state="readonly",
            command=self.on_recent_selected,
            button_color=TEAL_ACCENT,
            button_hover_color=TEAL_HOVER,
            border_color=("#cccccc", "#3d4659"),
            height=36
        )
        self.recent_combo.grid(row=2, column=1, columnspan=2, sticky="ew", padx=(0, 15), pady=(0, 10))

    def load_initial_state(self):
        """Load initial values from config."""
        initial_folder = self.config_data.get_initial_folder()
        self.folder_var.set(initial_folder)
        self.update_recent_folders()

        # Check clipboard for URL on startup
        self.after(100, self._check_clipboard_for_url)

    def _check_clipboard_for_url(self):
        """Auto-fill URL from clipboard if it contains a valid URL."""
        try:
            clipboard = self.clipboard_get()
            if clipboard and not self.single_url.get().strip():
                # Check if clipboard looks like a URL
                is_valid, normalized = validate_url(clipboard)
                if is_valid:
                    self.single_url.insert(0, clipboard.strip())
                    self._auto_fill_name()
        except Exception:
            # Clipboard may be empty or contain non-text data
            pass

    def update_recent_folders(self):
        """Update the recent folders dropdown."""
        valid_recent = [f for f in self.config_data.recent_folders if os.path.isdir(f)]
        self.recent_combo.configure(values=valid_recent)

    def on_recent_selected(self, choice):
        """Handle selection from recent folders dropdown."""
        if choice:
            self.folder_var.set(choice)

    def browse_folder(self):
        """Open folder browser dialog."""
        current = self.folder_var.get()
        initial = current if os.path.isdir(current) else os.path.expanduser("~")

        folder = ctk.filedialog.askdirectory(initialdir=initial, title="Select Save Location")

        if folder:
            self.folder_var.set(folder)
            self.config_data.add_recent_folder(folder)
            self.update_recent_folders()

    def _auto_fill_name(self):
        """Auto-fill name from URL if name is empty."""
        if self.single_name.get().strip():
            return

        url = self.single_url.get().strip()
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
                self.single_name.delete(0, 'end')
                self.single_name.insert(0, name)
        except Exception:
            pass

    def clear_single(self):
        """Clear single tab fields."""
        self.single_url.delete(0, 'end')
        self.single_name.delete(0, 'end')
        self.single_url.focus_set()

    def clear_batch(self):
        """Clear all batch rows."""
        for row in self.batch_rows[:]:
            row.destroy()
        self.batch_rows.clear()
        for _ in range(3):
            self.add_batch_row()

    def create_single(self):
        """Create a single shortcut."""
        name = self.single_name.get().strip()
        url = self.single_url.get().strip()
        folder = self.folder_var.get().strip()

        # Validate
        if not url:
            self.single_url.focus_set()
            return

        if not name:
            self.single_name.focus_set()
            return

        is_valid, msg = validate_url(url)
        if not is_valid:
            self.single_url.focus_set()
            return

        if not folder or not os.path.isdir(folder):
            return

        # Disable button
        self.single_create_btn.configure(state="disabled")
        self.status_var.set("Creating shortcut...")

        # Create in thread
        def do_create():
            result = create_url_shortcut(
                name=name,
                url=url,
                save_dir=folder,
                fetch_icon=self.single_fetch_icon.get()
            )
            self.after(0, lambda: self.on_single_complete(result, folder))

        threading.Thread(target=do_create, daemon=True).start()

    def on_single_complete(self, result: ShortcutResult, folder: str):
        """Handle single shortcut creation completion."""
        self.single_create_btn.configure(state="normal")

        if result.success:
            self.status_var.set(f"Created: {os.path.basename(result.file_path)}")
            self.config_data.add_recent_folder(folder)
            self.update_recent_folders()
            save_config(self.config_data)
            self.clear_single()
        else:
            self.status_var.set("Failed to create shortcut")

    def create_batch(self):
        """Create shortcuts from batch rows."""
        folder = self.folder_var.get().strip()

        if not folder or not os.path.isdir(folder):
            return

        # Get valid rows
        valid_rows = [(r.get_data()) for r in self.batch_rows if r.is_valid()]
        if not valid_rows:
            return

        # Show progress
        self.batch_progress.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        self.batch_progress.set(0)

        self.batch_create_btn.configure(state="disabled")
        self.status_var.set(f"Creating {len(valid_rows)} shortcuts...")

        def do_batch():
            results = []
            for i, (name, url) in enumerate(valid_rows):
                result = create_url_shortcut(
                    name=name,
                    url=url,
                    save_dir=folder,
                    fetch_icon=self.batch_fetch_icon.get()
                )
                results.append((name, result))

                progress = (i + 1) / len(valid_rows)
                self.after(0, lambda p=progress: self.batch_progress.set(p))

            self.after(0, lambda: self.on_batch_complete(results, folder))

        threading.Thread(target=do_batch, daemon=True).start()

    def on_batch_complete(self, results: list, folder: str):
        """Handle batch creation completion."""
        self.batch_create_btn.configure(state="normal")
        self.batch_progress.grid_forget()

        success_count = sum(1 for _, r in results if r.success)
        fail_count = len(results) - success_count

        self.status_var.set(f"Created {success_count} shortcuts, {fail_count} failed")

        self.config_data.add_recent_folder(folder)
        self.update_recent_folders()
        save_config(self.config_data)

        if fail_count == 0:
            self.clear_batch()

    def on_close(self):
        """Handle window close."""
        self.config_data.last_window_x = self.winfo_x()
        self.config_data.last_window_y = self.winfo_y()
        self.config_data.fetch_favicon_default = self.single_fetch_icon.get()
        save_config(self.config_data)
        self.destroy()


def main():
    app = LinkDropApp()
    app.mainloop()


if __name__ == "__main__":
    main()
