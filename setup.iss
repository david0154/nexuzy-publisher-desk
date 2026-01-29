; Inno Setup Script for Nexuzy Publisher Desk
; Complete AI-Powered News Publishing Platform with All Models

#define MyAppName "Nexuzy Publisher Desk"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "David Studioz"
#define MyAppURL "https://github.com/david0154/nexuzy-publisher-desk"
#define MyAppExeName "NexuzyPublisher.exe"

[Setup]
AppId={{NEXUZY-PUBLISHER-DESK-2026}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=Output
OutputBaseFilename=NexuzyPublisherSetup
Compression=lzma2/ultra64
SolidCompression=yes
SetupIconFile=resources\icon.ico
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "dist\NexuzyPublisher\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "models\david-ai-writer-7b.gguf"; DestDir: "{app}\models"; Flags: ignoreversion; Check: FileExists('models\david-ai-writer-7b.gguf')
Source: "models\nllb-200-distilled-600M\*"; DestDir: "{app}\models\nllb-200-distilled-600M"; Flags: ignoreversion recursesubdirs; Check: DirExists('models\nllb-200-distilled-600M')
Source: "models\vision-watermark-detector\*"; DestDir: "{app}\models\vision-watermark-detector"; Flags: ignoreversion recursesubdirs; Check: DirExists('models\vision-watermark-detector')
Source: "models\all-MiniLM-L6-v2\*"; DestDir: "{app}\models\all-MiniLM-L6-v2"; Flags: ignoreversion recursesubdirs; Check: DirExists('models\all-MiniLM-L6-v2')

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
