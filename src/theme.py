"""
LinkDrop Theme Module

Provides dark/light mode support following Windows system settings.
"""

import tkinter as tk
from tkinter import ttk


# Color schemes
DARK_THEME = {
    'bg': '#1a1f2e',              # Dark blue-gray background
    'fg': '#e0e6ed',              # Soft white text
    'bg_secondary': '#242b3d',    # Slightly lighter panels
    'bg_entry': '#2a3245',        # Entry field background
    'fg_secondary': '#b8c5d6',    # Secondary text
    'fg_dim': '#6b7a94',          # Dimmed/hint text
    'accent': '#4ecdc4',          # Teal accent for buttons
    'accent_hover': '#5fe0d7',    # Lighter teal for hover
    'accent_pressed': '#3db8b0',  # Darker teal for pressed
    'border': '#3d4659',          # Subtle borders
    'select_bg': '#3d5a80',       # Selection background
    'select_fg': '#ffffff',       # Selection text
}

LIGHT_THEME = {
    'bg': '#f5f7fa',
    'fg': '#1a1f2e',
    'bg_secondary': '#ffffff',
    'bg_entry': '#ffffff',
    'fg_secondary': '#4a5568',
    'fg_dim': '#718096',
    'accent': '#3d9be9',
    'accent_hover': '#2d8bd9',
    'accent_pressed': '#1d7bc9',
    'border': '#e2e8f0',
    'select_bg': '#3d9be9',
    'select_fg': '#ffffff',
}


def is_windows_dark_mode() -> bool:
    """
    Detect if Windows is using dark mode.

    Returns:
        True if dark mode is enabled, False otherwise
    """
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        )
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return value == 0  # 0 = dark mode, 1 = light mode
    except Exception:
        return False  # Default to light mode if detection fails


def get_theme() -> dict:
    """Get the appropriate theme based on system settings."""
    if is_windows_dark_mode():
        return DARK_THEME
    return LIGHT_THEME


def apply_theme(root: tk.Tk, theme: dict = None) -> dict:
    """
    Apply theme to a tkinter root window and configure ttk styles.

    Args:
        root: The tkinter root window
        theme: Optional theme dict, auto-detects if not provided

    Returns:
        The theme dict that was applied
    """
    if theme is None:
        theme = get_theme()

    # Configure root window
    root.configure(bg=theme['bg'])

    # Create and configure ttk style
    style = ttk.Style(root)

    # Use clam theme as base (more customizable than default)
    style.theme_use('clam')

    # Configure common styles
    style.configure(
        '.',
        background=theme['bg'],
        foreground=theme['fg'],
        fieldbackground=theme['bg_entry'],
        troughcolor=theme['bg_secondary'],
        bordercolor=theme['border'],
        lightcolor=theme['bg_secondary'],
        darkcolor=theme['border'],
    )

    # Frame
    style.configure(
        'TFrame',
        background=theme['bg']
    )

    # Label
    style.configure(
        'TLabel',
        background=theme['bg'],
        foreground=theme['fg']
    )

    style.configure(
        'Dim.TLabel',
        background=theme['bg'],
        foreground=theme['fg_dim']
    )

    # Entry
    style.configure(
        'TEntry',
        fieldbackground=theme['bg_entry'],
        foreground=theme['fg'],
        insertcolor=theme['fg'],
        selectbackground=theme['select_bg'],
        selectforeground=theme['select_fg'],
        bordercolor=theme['border'],
    )

    style.map(
        'TEntry',
        fieldbackground=[('focus', theme['bg_entry']), ('!focus', theme['bg_entry'])],
        bordercolor=[('focus', theme['accent']), ('!focus', theme['border'])],
    )

    # Get accent colors (with fallbacks for light theme)
    accent = theme.get('accent', '#4ecdc4')
    accent_hover = theme.get('accent_hover', accent)
    accent_pressed = theme.get('accent_pressed', accent)

    # Button - styled with accent color
    style.configure(
        'TButton',
        background=accent,
        foreground='#1a1f2e',
        bordercolor=accent,
        focuscolor=accent,
        padding=(12, 6),
        relief='flat',
    )

    style.map(
        'TButton',
        background=[('active', accent_hover), ('pressed', accent_pressed), ('disabled', theme['bg_secondary'])],
        foreground=[('disabled', theme['fg_dim'])],
        bordercolor=[('active', accent_hover), ('pressed', accent_pressed)],
    )

    # Secondary button style (less prominent)
    style.configure(
        'Secondary.TButton',
        background=theme['bg_secondary'],
        foreground=theme['fg'],
        bordercolor=theme['border'],
    )

    style.map(
        'Secondary.TButton',
        background=[('active', theme['border']), ('pressed', theme['bg_entry'])],
    )

    # Checkbutton
    style.configure(
        'TCheckbutton',
        background=theme['bg'],
        foreground=theme['fg'],
    )

    style.map(
        'TCheckbutton',
        background=[('active', theme['bg'])],
    )

    # LabelFrame
    style.configure(
        'TLabelframe',
        background=theme['bg'],
        foreground=theme['fg'],
        bordercolor=theme['border'],
    )

    style.configure(
        'TLabelframe.Label',
        background=theme['bg'],
        foreground=theme['fg'],
    )

    # Notebook (tabs)
    style.configure(
        'TNotebook',
        background=theme['bg'],
        bordercolor=theme['border'],
        tabmargins=[2, 5, 2, 0],
    )

    style.configure(
        'TNotebook.Tab',
        background=theme['bg_secondary'],
        foreground=theme['fg'],
        padding=[10, 5],
        bordercolor=theme['border'],
    )

    style.map(
        'TNotebook.Tab',
        background=[('selected', theme['bg']), ('active', theme['bg_secondary'])],
        foreground=[('selected', theme['fg'])],
        expand=[('selected', [1, 1, 1, 0])],
    )

    # Combobox
    style.configure(
        'TCombobox',
        fieldbackground=theme['bg_entry'],
        background=theme['bg_secondary'],
        foreground=theme['fg'],
        arrowcolor=theme['fg'],
        bordercolor=theme['border'],
        selectbackground=theme['select_bg'],
        selectforeground=theme['select_fg'],
    )

    style.map(
        'TCombobox',
        fieldbackground=[('readonly', theme['bg_entry'])],
        selectbackground=[('readonly', theme['select_bg'])],
        selectforeground=[('readonly', theme['select_fg'])],
        bordercolor=[('focus', theme['accent'])],
    )

    # Combobox dropdown listbox (requires option database)
    root.option_add('*TCombobox*Listbox.background', theme['bg_entry'])
    root.option_add('*TCombobox*Listbox.foreground', theme['fg'])
    root.option_add('*TCombobox*Listbox.selectBackground', theme['select_bg'])
    root.option_add('*TCombobox*Listbox.selectForeground', theme['select_fg'])

    # Progressbar
    style.configure(
        'TProgressbar',
        background=theme['accent'],
        troughcolor=theme['bg_secondary'],
        bordercolor=theme['border'],
    )

    # Scrollbar
    style.configure(
        'TScrollbar',
        background=theme['bg_secondary'],
        troughcolor=theme['bg'],
        bordercolor=theme['border'],
        arrowcolor=theme['fg'],
    )

    style.map(
        'TScrollbar',
        background=[('active', theme['fg_dim'])],
    )

    return theme


def style_text_widget(widget: tk.Text, theme: dict):
    """
    Apply theme to a tk.Text widget (not ttk).

    Args:
        widget: The Text widget to style
        theme: The theme dict
    """
    widget.configure(
        bg=theme['bg_entry'],
        fg=theme['fg'],
        insertbackground=theme['fg'],
        selectbackground=theme['select_bg'],
        selectforeground=theme['select_fg'],
        relief='flat',
        borderwidth=1,
        highlightthickness=1,
        highlightbackground=theme['border'],
        highlightcolor=theme['accent'],
    )
