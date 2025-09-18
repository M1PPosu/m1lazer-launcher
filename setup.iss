#define MyAppName "M1Lazer"
#define MyAppVersion "1.1"
#define MyAppPublisher "M1PPosu"
#define MyAppURL "https://m1pposu.dev/"
#define MyAppExeName "m1lazer.exe"

[Setup]
; IMPORTANT: Replace relevant file paths in this file so they point to your M1Lazer source code folder.
AppId={{8FC16274-DA5A-4A1A-9FD6-5C3EB6F63F96}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
LicenseFile=C:\Users\gamepc\Pictures\m1lazer-launcher-main\LICENSE
OutputDir=C:\Users\gamepc\Videos
OutputBaseFilename=m1lazer-setup
SetupIconFile=C:\Users\gamepc\Pictures\m1lazer-launcher-main\assets\icon.ico
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Users\gamepc\Pictures\m1lazer-launcher-main\dist\m1lazer\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\gamepc\Pictures\m1lazer-launcher-main\dist\m1lazer\_internal\*"; \
DestDir: "{app}\_internal"; \
Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "schtasks.exe"; \
    Parameters: "/Create /F /RL HIGHEST /SC ONLOGON /TN ""M1LazerCleanup"" /TR """"{app}\{#MyAppExeName}"" cleanup"""; \
    Flags: runhidden; \
    StatusMsg: "Configuring auto-cleanup script..."

[UninstallRun]
Filename: "schtasks.exe"; \
    Parameters: "/Delete /F /TN ""M1LazerCleanup"""; \
    Flags: runhidden; \