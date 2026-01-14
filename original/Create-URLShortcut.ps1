do {
    # Customize window appearance
    $Host.UI.RawUI.WindowTitle = "Create Web URL Shortcut"
    Clear-Host
    
    Write-Host "=== Create Web URL Shortcut ===`n"
    
    # Prompt user for shortcut name and URL
    $shortcutName = Read-Host "Enter shortcut name (e.g. Notion Portal)"
    
    # Basic validation - exit loop if empty (user can press Ctrl+C)
    if ([string]::IsNullOrWhiteSpace($shortcutName)) {
        Write-Host "Shortcut name cannot be empty. Exiting..." -ForegroundColor Yellow
        break
    }
    
    $url = Read-Host "Enter the full URL (e.g. https://www.notion.so/YourTeamPage)"
    
    # Basic validation for URL
    if ([string]::IsNullOrWhiteSpace($url)) {
        Write-Host "URL cannot be empty. Exiting..." -ForegroundColor Yellow
        break
    }
    
    # Ensure the shortcut ends in .url
    if (-not $shortcutName.EndsWith(".url")) {
        $shortcutName += ".url"
    }
    
    # Load Windows Forms for Save Dialog
    Add-Type -AssemblyName System.Windows.Forms
    
    # Create and configure the Save File Dialog
    $saveDialog = New-Object System.Windows.Forms.SaveFileDialog
    $saveDialog.Filter = "URL Shortcut (*.url)|*.url"
    $saveDialog.Title = "Save URL Shortcut"
    $saveDialog.FileName = $shortcutName
    $saveDialog.InitialDirectory = [Environment]::GetFolderPath("Desktop")
    
    # Show the dialog
    $result = $saveDialog.ShowDialog()
    
    if ($result -eq [System.Windows.Forms.DialogResult]::OK) {
        $fullPath = $saveDialog.FileName
        
        # Create the .url file
        @"
[InternetShortcut]
URL=$url
"@ | Out-File -Encoding ASCII "$fullPath"
    }
    else {
        Write-Host "Save cancelled." -ForegroundColor Yellow
        continue
    }
    
    # Confirm success
    Write-Host "`n--- Shortcut created successfully ---" -ForegroundColor Green
    Write-Host "$fullPath"
    Write-Host "URL: $url" -ForegroundColor Gray
    
    # Prompt to continue or exit
    Write-Host "`nPress Enter to create another shortcut, or Esc to exit..."
    
    # Wait for Enter or Esc
    $key = $null
    do {
        $key = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    } until ($key.VirtualKeyCode -eq 13 -or $key.VirtualKeyCode -eq 27)  # 13 = Enter, 27 = Esc
    
} while ($key.VirtualKeyCode -eq 13)  # Loop if Enter is pressed