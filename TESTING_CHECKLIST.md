# LinkDrop v1.1 Testing Checklist

## Pre-Testing Setup
- [ ] Fresh install completed via `LinkDrop-Setup-1.1.exe`
- [ ] Previous version uninstalled (if applicable)

---

## 1. Installation Verification

### Add/Remove Programs
- [ ] Open **Windows Settings → Apps → Installed Apps**
- [ ] Search for "LinkDrop"
- [ ] Verify LinkDrop appears in the list with correct version

### Desktop Shortcut
- [ ] Check Desktop for "LinkDrop" shortcut
- [ ] Verify icon displays correctly (teal/cyan LinkDrop icon)
- [ ] Double-click to confirm it launches the app

### Start Menu
- [ ] Click Start and search for "LinkDrop"
- [ ] Verify LinkDrop appears in search results
- [ ] Click to confirm it launches

### Context Menu
- [ ] Open any folder in Windows Explorer
- [ ] Right-click on empty space (not on a file)
- [ ] Verify "LinkDrop Here" appears in context menu
- [ ] Verify LinkDrop icon shows next to menu item

---

## 2. Main Application (LinkDrop.exe)

### Window & UI
- [ ] App opens without errors
- [ ] Window title shows "LinkDrop - URL Shortcut Creator"
- [ ] LinkDrop icon appears in title bar and taskbar
- [ ] Dark mode theme displays correctly
- [ ] "Single" and "Batch" tabs are visible

### Single Mode - Basic Functionality
- [ ] URL field accepts input
- [ ] Shortcut Name field accepts input
- [ ] "Fetch website favicon" toggle works
- [ ] "Clear" button clears both fields
- [ ] "Browse..." button opens folder picker
- [ ] Recent dropdown shows previously used folders

### Single Mode - Create Shortcut
- [ ] Enter URL: `https://google.com`
- [ ] Enter Name: `Google`
- [ ] Select a save location
- [ ] Click "Create Shortcut"
- [ ] Verify .url file created in selected folder
- [ ] Double-click the .url file to verify it opens the website
- [ ] Check if favicon was downloaded (shortcut should have Google icon)

### Single Mode - Auto-Fill Name
- [ ] Clear both fields
- [ ] Paste `https://github.com` into URL field (Ctrl+V)
- [ ] Verify Name field auto-fills with "Github"

### Single Mode - Clipboard Auto-Detect
- [ ] Close LinkDrop
- [ ] Copy a URL to clipboard: `https://microsoft.com`
- [ ] Open LinkDrop
- [ ] Verify URL field auto-fills with the copied URL
- [ ] Verify Name field auto-fills with "Microsoft"

### Single Mode - File Path Rejection
- [ ] Close LinkDrop
- [ ] Copy a file path to clipboard: `C:\Users\joeh\Documents`
- [ ] Open LinkDrop
- [ ] Verify URL field stays EMPTY (file paths should be ignored)

### Batch Mode
- [ ] Switch to "Batch" tab
- [ ] Verify 3 empty rows displayed by default
- [ ] Click "+ Add Row" to add more rows
- [ ] Click "×" button to delete a row
- [ ] Enter test data in multiple rows:
  - Row 1: URL: `https://youtube.com` | Name: `YouTube`
  - Row 2: URL: `https://amazon.com` | Name: `Amazon`
- [ ] Toggle "Fetch favicons"
- [ ] Click "Create All"
- [ ] Verify progress bar appears during creation
- [ ] Verify both .url files created
- [ ] "Clear All" button resets to 3 empty rows

---

## 3. Quick Popup (LinkDropQuick.exe)

### Launch via Context Menu
- [ ] Navigate to Desktop or any folder
- [ ] Right-click on empty space
- [ ] Click "LinkDrop Here"
- [ ] Verify quick popup opens

### Quick Popup UI
- [ ] Window title shows "LinkDrop"
- [ ] Window stays on top of other windows
- [ ] URL field is focused and ready for input
- [ ] Name field has "Auto-fills from URL" placeholder

### Quick Popup - Create Shortcut
- [ ] Enter URL: `https://reddit.com`
- [ ] Verify Name auto-fills when pasting URL
- [ ] Enter Name: `Reddit` (or accept auto-fill)
- [ ] Press Enter or click "Create"
- [ ] Verify popup closes after creation
- [ ] Verify .url file created in the folder you right-clicked in

### Quick Popup - Clipboard Auto-Detect
- [ ] Copy `https://twitter.com` to clipboard
- [ ] Right-click in a folder → "LinkDrop Here"
- [ ] Verify URL auto-fills from clipboard
- [ ] Verify Name auto-fills with "Twitter"

### Quick Popup - Cancel
- [ ] Open quick popup via context menu
- [ ] Press Escape key
- [ ] Verify popup closes without creating file
- [ ] Re-open and click "Cancel" button
- [ ] Verify same behavior

---

## 4. Remember Last Location

- [ ] Open LinkDrop main app
- [ ] Browse to a specific folder (e.g., `C:\Users\joeh\Desktop\TestFolder`)
- [ ] Create a shortcut there
- [ ] Close LinkDrop completely
- [ ] Re-open LinkDrop
- [ ] Verify "Save Location" shows the previously used folder

---

## 5. Favicon Fetching

### Successful Favicon
- [ ] Create shortcut for `https://google.com` with favicon enabled
- [ ] Check the created .url file's icon (should show Google "G")
- [ ] Create shortcut for `https://github.com` with favicon enabled
- [ ] Check icon (should show GitHub octocat)

### Favicon Fallback (Google Service)
- [ ] Create shortcut for a less common site that might block direct favicon
- [ ] Verify icon still downloads via Google's fallback service

### Favicon Disabled
- [ ] Turn OFF "Fetch website favicon" toggle
- [ ] Create a shortcut
- [ ] Verify shortcut uses default Windows icon (no custom favicon)

---

## 6. Edge Cases

### Invalid URL Handling
- [ ] Try creating shortcut with empty URL - should not proceed
- [ ] Try creating shortcut with empty Name - should not proceed
- [ ] Try creating shortcut with invalid URL (e.g., "not a url") - should fail gracefully

### Special Characters in Name
- [ ] Create shortcut with name containing spaces: `My Test Site`
- [ ] Verify file created as `My Test Site.url`

### UNC/Network Paths (if available)
- [ ] Browse to a network location (e.g., `\\server\share\folder`)
- [ ] Create a shortcut there
- [ ] Verify it works on network drives

---

## 7. Uninstall Verification

- [ ] Open **Windows Settings → Apps → Installed Apps**
- [ ] Find LinkDrop and click Uninstall
- [ ] Confirm uninstall
- [ ] Verify:
  - [ ] LinkDrop removed from Apps list
  - [ ] Desktop shortcut removed
  - [ ] Start Menu entry removed
  - [ ] Context menu "LinkDrop Here" removed (may need Explorer restart)

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

(Record any bugs or issues here)

1.
2.
3.
