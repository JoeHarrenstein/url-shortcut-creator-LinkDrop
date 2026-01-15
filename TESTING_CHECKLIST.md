# LinkDrop v1.2 Testing Checklist

## Pre-Testing Setup
- [x] Fresh install completed via `LinkDrop-Setup-1.2.exe`
- [x] Previous version uninstalled (if applicable)

---

## 1. Installation Verification

### Add/Remove Programs
- [x] Open **Windows Settings → Apps → Installed Apps**
- [x] Search for "LinkDrop"
- [x] Verify LinkDrop appears in the list with correct version

### Desktop Shortcut
- [x] Check Desktop for "LinkDrop" shortcut
- [x] Verify icon displays correctly (teal/cyan LinkDrop icon)
- [x] Double-click to confirm it launches the app

### Start Menu
- [x] Click Start and search for "LinkDrop"
- [x] Verify LinkDrop appears in search results
- [x] Click to confirm it launches

### Context Menu
- [x] Open any folder in Windows Explorer
- [x] Right-click on empty space (not on a file)
- [x] Verify "LinkDrop Here" appears in context menu
- [x] Verify LinkDrop icon shows next to menu item


---

## 2. Main Application (LinkDrop.exe)

### Window & UI
- [x] App opens without errors
- [x] Window title shows "LinkDrop - URL Shortcut Creator"
- [x] LinkDrop icon appears in title bar and taskbar
- [x] Dark mode theme displays correctly
- [x] "Single" and "Batch" tabs are visible

### Single Mode - Basic Functionality
- [x] URL field accepts input
- [x] Shortcut Name field accepts input
- [x] "Fetch website favicon" toggle works
- [x] "Clear" button clears both fields
- [x] "Browse..." button opens folder picker
- [x] Recent dropdown shows previously used folders

### Single Mode - Create Shortcut
- [x] Enter URL: `https://google.com`
- [x] Enter Name: `Google`
- [x] Select a save location
- [x] Click "Create Shortcut"
- [x] Verify .url file created in selected folder
- [x] Double-click the .url file to verify it opens the website
- [x] Check if favicon was downloaded (shortcut should have Google icon)

### Single Mode - Auto-Fill Name
- [x] Clear both fields
- [x] Paste `https://github.com` into URL field (Ctrl+V)
- [x] Verify Name field auto-fills with "Github"

### Single Mode - Clipboard Auto-Detect
- [x] Close LinkDrop
- [x] Copy a URL to clipboard: `https://microsoft.com`
- [x] Open LinkDrop
- [x] Verify URL field auto-fills with the copied URL
- [x] Verify Name field auto-fills with "Microsoft"

### Single Mode - File Path Rejection
- [x] Close LinkDrop
- [x] Copy a file path to clipboard: `C:\Users\joeh\Documents`
- [x] Open LinkDrop
- [x] Verify URL field stays EMPTY (file paths should be ignored)

### Batch Mode
- [x] Switch to "Batch" tab
- [x] Verify 3 empty rows displayed by default
- [x] Click "+ Add Row" to add more rows
- [x] Click "×" button to delete a row
- [x] Enter test data in multiple rows:
  - Row 1: URL: `https://youtube.com` | Name: `YouTube`
  - Row 2: URL: `https://amazon.com` | Name: `Amazon`
- [x] Toggle "Fetch favicons"
- [x] Click "Create All"
- [x] Verify progress bar appears during creation
- [x] Verify both .url files created
- [x] "Clear All" button resets to 3 empty rows

---

## 3. Quick Popup (LinkDropQuick.exe)

### Launch via Context Menu
- [x] Navigate to Desktop or any folder
- [x] Right-click on empty space
- [x] Click "LinkDrop Here"
- [x] Verify quick popup opens

### Quick Popup UI
- [x] Window title shows "LinkDrop"
- [x] Window stays on top of other windows
- [x] URL field is focused and ready for input
- [x] Name field has "Auto-fills from URL" placeholder

### Quick Popup - Create Shortcut
- [x] Enter URL: `https://reddit.com`
- [x] Verify Name auto-fills when pasting URL
- [x] Enter Name: `Reddit` (or accept auto-fill)
- [x] Press Enter or click "Create"
- [x] Verify popup closes after creation
- [x] Verify .url file created in the folder you right-clicked in

### Quick Popup - Clipboard Auto-Detect
- [x] Copy `https://twitter.com` to clipboard
- [x] Right-click in a folder → "LinkDrop Here"
- [x] Verify URL auto-fills from clipboard
- [x] Verify Name auto-fills with "Twitter"

### Quick Popup - Cancel
- [x] Open quick popup via context menu
- [x] Press Escape key
- [x] Verify popup closes without creating file
- [x] Re-open and click "Cancel" button
- [x] Verify same behavior

---

## 4. Remember Last Location

- [x] Open LinkDrop main app
- [x] Browse to a specific folder (e.g., `C:\Users\joeh\Desktop\TestFolder`)
- [x] Create a shortcut there
- [x] Close LinkDrop completely
- [x] Re-open LinkDrop
- [x] Verify "Save Location" shows the previously used folder

---

## 5. Favicon Fetching

### Successful Favicon
- [x] Create shortcut for `https://google.com` with favicon enabled
- [x] Check the created .url file's icon (should show Google "G")
- [x] Create shortcut for `https://github.com` with favicon enabled
- [x] Check icon (should show GitHub octocat)

### Favicon Fallback (Google Service)
- [x] Create shortcut for a less common site that might block direct favicon
- [x] Verify icon still downloads via Google's fallback service

### Favicon Disabled
- [x] Turn OFF "Fetch website favicon" toggle
- [x] Create a shortcut
- [x] Verify shortcut uses default Windows icon (no custom favicon)

---

## 6. Edge Cases

### Invalid URL Handling
- [x] Try creating shortcut with empty URL - should not proceed
- [x] Try creating shortcut with empty Name - should not proceed
- [x] Try creating shortcut with invalid URL (e.g., "not a url") - should fail gracefully

### Special Characters in Name
- [x] Create shortcut with name containing spaces: `My Test Site`
- [x] Verify file created as `My Test Site.url`

### UNC/Network Paths (if available)
- [x] Browse to a network location (e.g., `\\server\share\folder`)
- [x] Create a shortcut there
- [x] Verify it works on network drives

---

## 7. Uninstall Verification

- [x] Open **Windows Settings → Apps → Installed Apps**
- [x] Find LinkDrop and click Uninstall
- [x] Confirm uninstall
- [x] Verify:
  - [x] LinkDrop removed from Apps list
  - [x] Desktop shortcut removed
  - [x] Start Menu entry removed
  - [x] Context menu "LinkDrop Here" removed (may need Explorer restart)

---

## Test Results Summary

| Category | Pass | Fail | Notes |
|----------|------|------|-------|
| Installation | | | |
| Main App - Single Mode | | | |
| Main App - Batch Mode | | | |
| Quick Popup | | | |
| Clipboard Auto-Detect | | | |
| Remember Location | | | |
| Favicon Fetching | | | |
| Edge Cases | | | |
| Uninstall | | | |

---

## Notes / Issues Found

### Resolved in v1.2

1. **[FIXED]** Batch mode Name column now auto-populates from URL (like Single mode)
2. **[FIXED]** Added duplicate file warning dialog when overwriting existing shortcuts
3. **[FIXED]** Clipboard auto-detect now only accepts valid URLs (rejects random text)
4. **[IMPROVED]** Icons now fetch at higher resolution (256px) for better quality
5. **[FIXED]** Clipboard no longer populates fields with non-URL data