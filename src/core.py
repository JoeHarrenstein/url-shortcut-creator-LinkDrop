"""
LinkDrop Core Module

Provides core functionality for creating .url shortcut files:
- URL validation
- .url file creation with optional icon
- Favicon fetching from multiple sources
"""

import os
import re
from pathlib import Path
from urllib.parse import urlparse
from typing import Optional, Tuple
from dataclasses import dataclass

import requests
from PIL import Image
from io import BytesIO


def get_icon_cache_dir() -> str:
    """
    Get the icon cache directory path.

    Returns:
        Path to %LOCALAPPDATA%\\LinkDrop\\icons\\
    """
    local_app_data = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
    cache_dir = os.path.join(local_app_data, 'LinkDrop', 'icons')
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


@dataclass
class ShortcutResult:
    """Result of a shortcut creation operation."""
    success: bool
    file_path: Optional[str] = None
    icon_path: Optional[str] = None
    error: Optional[str] = None


def is_likely_url(text: str) -> bool:
    """
    Check if text looks like a URL (for clipboard auto-detection).

    More strict than validate_url() - requires explicit http(s):// prefix
    or a recognizable domain pattern with common TLD.

    Args:
        text: Text to check

    Returns:
        True if text appears to be a URL
    """
    if not text or not text.strip():
        return False

    text = text.strip()

    # Must not contain spaces or newlines (URLs don't have these)
    if ' ' in text or '\n' in text or '\t' in text:
        return False

    # Accept if it starts with http:// or https://
    if text.startswith(('http://', 'https://')):
        return True

    # Accept if it looks like a domain with common TLD
    common_tlds = (
        '.com', '.org', '.net', '.io', '.co', '.edu', '.gov', '.mil',
        '.dev', '.app', '.ai', '.info', '.biz', '.me', '.tv', '.us',
        '.uk', '.ca', '.de', '.fr', '.au', '.jp', '.cn', '.in', '.br',
        '.xyz', '.tech', '.online', '.site', '.store', '.cloud', '.so',
        '.gg', '.ly', '.to', '.fm', '.am', '.be', '.it', '.es', '.nl'
    )

    # Check if text contains a TLD (case insensitive)
    text_lower = text.lower()
    for tld in common_tlds:
        # TLD should be followed by nothing, /, :, or ?
        tld_pos = text_lower.find(tld)
        if tld_pos > 0:  # Must have something before the TLD
            after_tld = text_lower[tld_pos + len(tld):]
            if not after_tld or after_tld[0] in ('/', ':', '?', '#'):
                return True

    return False


def validate_url(url: str) -> Tuple[bool, str]:
    """
    Validate a URL string.

    Args:
        url: The URL to validate

    Returns:
        Tuple of (is_valid, error_message_or_normalized_url)
    """
    if not url or not url.strip():
        return False, "URL cannot be empty"

    url = url.strip()

    # Add https:// if no scheme provided
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', url):
        url = 'https://' + url

    try:
        parsed = urlparse(url)

        # Must have a scheme and netloc (domain)
        if not parsed.scheme:
            return False, "URL must have a scheme (http:// or https://)"

        if parsed.scheme not in ('http', 'https'):
            return False, f"Unsupported scheme: {parsed.scheme}"

        if not parsed.netloc:
            return False, "URL must have a domain"

        # Basic domain validation
        domain = parsed.netloc.split(':')[0]  # Remove port if present
        if not domain or domain.startswith('.') or domain.endswith('.'):
            return False, "Invalid domain format"

        return True, url

    except Exception as e:
        return False, f"Invalid URL format: {e}"


def sanitize_filename(name: str) -> str:
    """
    Sanitize a string for use as a filename.

    Args:
        name: The proposed filename

    Returns:
        A safe filename string
    """
    # Remove or replace invalid Windows filename characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')

    # Remove control characters
    name = ''.join(c for c in name if ord(c) >= 32)

    # Trim whitespace and dots from ends
    name = name.strip(' .')

    # Ensure we have something left
    if not name:
        name = "shortcut"

    # Limit length (Windows max is 255, but leave room for extension)
    if len(name) > 200:
        name = name[:200]

    return name


def fetch_favicon(url: str) -> Optional[str]:
    """
    Fetch a favicon for a URL and cache it as an .ico file.

    Icons are cached in %LOCALAPPDATA%\\LinkDrop\\icons\\ using the domain
    name as the filename (e.g., notion.so.ico). Cached icons are reused
    for subsequent requests to the same domain.

    Tries multiple sources in order:
    1. Direct /favicon.ico from the domain
    2. Google Favicon service (more reliable)

    Args:
        url: The website URL

    Returns:
        Path to the cached .ico file, or None if fetching failed
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        base_url = f"{parsed.scheme}://{domain}"
    except Exception:
        return None

    # Build cache path using domain name
    cache_dir = get_icon_cache_dir()
    icon_filename = sanitize_filename(domain) + ".ico"
    icon_path = os.path.join(cache_dir, icon_filename)

    # Return cached icon if it already exists
    if os.path.exists(icon_path):
        return icon_path

    # Request timeout and headers
    timeout = 5
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    # Try direct favicon.ico first
    try:
        response = requests.get(
            f"{base_url}/favicon.ico",
            timeout=timeout,
            headers=headers,
            allow_redirects=True
        )
        if response.status_code == 200 and len(response.content) > 0:
            if _save_as_ico(response.content, icon_path):
                return icon_path
    except requests.RequestException:
        pass

    # Fallback to Google's favicon service (request largest available size)
    try:
        google_favicon_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=256"
        response = requests.get(
            google_favicon_url,
            timeout=timeout,
            headers=headers,
            allow_redirects=True
        )
        if response.status_code == 200 and len(response.content) > 0:
            if _save_as_ico(response.content, icon_path):
                return icon_path
    except requests.RequestException:
        pass

    return None


def _save_as_ico(image_data: bytes, output_path: str) -> bool:
    """
    Convert image data to .ico format and save it.

    Args:
        image_data: Raw image bytes
        output_path: Path to save the .ico file

    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if it's already an ICO file
        if image_data[:4] == b'\x00\x00\x01\x00':
            with open(output_path, 'wb') as f:
                f.write(image_data)
            return True

        # Convert other formats to ICO using Pillow
        img = Image.open(BytesIO(image_data))

        # Convert to RGBA if needed
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Resize to standard icon sizes (include larger sizes for high-DPI displays)
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        icons = []
        for size in sizes:
            # Only create sizes up to the source image size to avoid upscaling
            if img.width >= size[0] and img.height >= size[1]:
                resized = img.resize(size, Image.Resampling.LANCZOS)
                icons.append(resized)

        # Ensure we have at least one size
        if not icons:
            # Source is smaller than 16x16, resize to smallest
            resized = img.resize((16, 16), Image.Resampling.LANCZOS)
            icons.append(resized)

        # Save as ICO with multiple sizes
        icons[0].save(
            output_path,
            format='ICO',
            sizes=[(s.width, s.height) for s in icons],
            append_images=icons[1:]
        )
        return True

    except Exception:
        return False


def create_url_shortcut(
    name: str,
    url: str,
    save_dir: str,
    notes: Optional[str] = None,
    fetch_icon: bool = True
) -> ShortcutResult:
    """
    Create a Windows .url shortcut file.

    Args:
        name: The shortcut name (will be sanitized and used as filename)
        url: The target URL
        save_dir: Directory to save the shortcut (supports UNC paths)
        notes: Optional notes/description
        fetch_icon: Whether to fetch and embed the favicon

    Returns:
        ShortcutResult with success status and file paths
    """
    # Validate URL
    is_valid, result = validate_url(url)
    if not is_valid:
        return ShortcutResult(success=False, error=result)

    normalized_url = result

    # Validate save directory
    if not save_dir:
        return ShortcutResult(success=False, error="Save directory cannot be empty")

    # Normalize path (works with both local and UNC paths)
    save_dir = os.path.normpath(save_dir)

    if not os.path.isdir(save_dir):
        return ShortcutResult(success=False, error=f"Directory does not exist: {save_dir}")

    # Sanitize filename
    safe_name = sanitize_filename(name)
    if not safe_name:
        return ShortcutResult(success=False, error="Invalid shortcut name")

    # Build file path
    shortcut_path = os.path.join(save_dir, f"{safe_name}.url")

    # Fetch favicon if requested (cached in %LOCALAPPDATA%\LinkDrop\icons\)
    icon_path = None
    if fetch_icon:
        icon_path = fetch_favicon(normalized_url)

    # Build .url file content
    lines = ["[InternetShortcut]", f"URL={normalized_url}"]

    if icon_path:
        lines.append("IconIndex=0")
        lines.append(f"IconFile={icon_path}")

    # Notes stored as Comment field (shows in some Windows versions)
    if notes and notes.strip():
        # Single line for Comment field, replace newlines with spaces
        comment = ' '.join(notes.strip().split())
        lines.append(f"Comment={comment}")

    content = '\n'.join(lines) + '\n'

    # Write the file
    try:
        with open(shortcut_path, 'w', encoding='ascii', errors='replace') as f:
            f.write(content)
    except OSError as e:
        return ShortcutResult(success=False, error=f"Failed to write file: {e}")

    return ShortcutResult(
        success=True,
        file_path=shortcut_path,
        icon_path=icon_path
    )


def parse_batch_line(line: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Parse a single line from batch input.

    Format: Name | URL | Notes (notes optional)

    Args:
        line: A single line of batch input

    Returns:
        Tuple of (name, url, notes) or (None, None, None) if invalid
    """
    line = line.strip()
    if not line or line.startswith('#'):
        return None, None, None

    parts = [p.strip() for p in line.split('|')]

    if len(parts) < 2:
        return None, None, None

    name = parts[0] if parts[0] else None
    url = parts[1] if parts[1] else None
    notes = parts[2] if len(parts) > 2 and parts[2] else None

    if not name or not url:
        return None, None, None

    return name, url, notes


def create_batch_shortcuts(
    batch_text: str,
    save_dir: str,
    fetch_icons: bool = True
) -> list[ShortcutResult]:
    """
    Create multiple shortcuts from batch text input.

    Args:
        batch_text: Multi-line text with format "Name | URL | Notes" per line
        save_dir: Directory to save all shortcuts
        fetch_icons: Whether to fetch favicons

    Returns:
        List of ShortcutResult for each processed line
    """
    results = []

    for line in batch_text.split('\n'):
        name, url, notes = parse_batch_line(line)

        if name and url:
            result = create_url_shortcut(
                name=name,
                url=url,
                save_dir=save_dir,
                notes=notes,
                fetch_icon=fetch_icons
            )
            results.append(result)

    return results


if __name__ == "__main__":
    # Simple test
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Testing in: {tmpdir}")

        # Test URL validation
        print("\n--- URL Validation Tests ---")
        test_urls = [
            "https://example.com",
            "example.com",
            "http://test.org/path?query=1",
            "",
            "not a url at all",
            "ftp://invalid.scheme.com"
        ]
        for test_url in test_urls:
            valid, result = validate_url(test_url)
            print(f"  '{test_url}' -> valid={valid}, result='{result}'")

        # Test shortcut creation
        print("\n--- Shortcut Creation Test ---")
        result = create_url_shortcut(
            name="Test Shortcut",
            url="https://example.com",
            save_dir=tmpdir,
            notes="This is a test note",
            fetch_icon=True
        )
        print(f"  Result: success={result.success}")
        if result.success:
            print(f"  File: {result.file_path}")
            print(f"  Icon: {result.icon_path}")
            with open(result.file_path, 'r') as f:
                print(f"  Content:\n{f.read()}")
        else:
            print(f"  Error: {result.error}")

        # Test batch creation
        print("\n--- Batch Creation Test ---")
        batch = """
        Google | https://google.com | Search engine
        GitHub | https://github.com
        # This is a comment
        Invalid line without pipe
        """
        results = create_batch_shortcuts(batch, tmpdir, fetch_icons=False)
        for r in results:
            print(f"  {r.file_path}: success={r.success}")
