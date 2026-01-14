; LinkDrop Inno Setup Script
; Creates a professional Windows installer with Add/Remove Programs support

#define MyAppName "LinkDrop"
#define MyAppVersion "1.1"
#define MyAppPublisher "Joe Harrenstein"
#define MyAppURL "https://github.com/JoeHarrenstein/url-shortcut-creator-LinkDrop"
#define MyAppExeName "LinkDrop.exe"
#define MyAppQuickExeName "LinkDropQuick.exe"

[Setup]
; Application info
AppId={{8A5F3D2E-4B6C-7D8E-9F0A-1B2C3D4E5F6A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE
OutputDir=..\dist
OutputBaseFilename=LinkDrop-Setup-{#MyAppVersion}
SetupIconFile=..\assets\LinkDrop.ico
UninstallDisplayIcon={app}\LinkDrop.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "contextmenu"; Description: "Add ""LinkDrop Here"" to right-click context menu"; GroupDescription: "Context Menu:"; Flags: checkedonce

[Files]
; Main application files
Source: "..\dist\LinkDrop.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\LinkDropQuick.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\LinkDrop.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\README.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\LinkDrop.ico"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"; IconFilename: "{app}\LinkDrop.ico"
; Desktop shortcut (optional)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\LinkDrop.ico"; Tasks: desktopicon

[Registry]
; Context menu - "LinkDrop Here" when right-clicking in folder background
Root: HKCR; Subkey: "Directory\Background\shell\LinkDrop"; ValueType: string; ValueName: ""; ValueData: "LinkDrop Here"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCR; Subkey: "Directory\Background\shell\LinkDrop"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\LinkDrop.ico"; Tasks: contextmenu
Root: HKCR; Subkey: "Directory\Background\shell\LinkDrop\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppQuickExeName}"" ""%V"""; Tasks: contextmenu

[Run]
; Option to launch after install
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up any generated files
Type: filesandordirs; Name: "{localappdata}\LinkDrop"

[Code]
// Show a message after successful installation
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    if WizardIsTaskSelected('contextmenu') then
    begin
      // Context menu was installed
    end;
  end;
end;
