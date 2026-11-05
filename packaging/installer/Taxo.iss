#define MyAppName "Taxo"
#ifndef MyAppVersion
  #define MyAppVersion "10.10-r6"
#endif
#ifndef SourceBundle
  #define SourceBundle "Taxo_v10_10_candidate_r6_Windows_x64"
#endif
#ifndef OutputBase
  #define OutputBase "Taxo_v10_10_candidate_r6_Setup_Windows_x64"
#endif
#define MyAppPublisher "Roman Zavada"
#define MyAppExeName "Taxo.exe"

[Setup]
AppId={{5D5D4FC7-9FE8-4B24-94EE-7B0F1EDB8560}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} v{#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Taxo
DefaultGroupName=Taxo
DisableProgramGroupPage=yes
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\..\release_out
OutputBaseFilename={#OutputBase}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\Taxo.exe
CloseApplications=yes
RestartApplications=no
ChangesAssociations=no
SetupLogging=yes
VersionInfoCopyright=Copyright (C) 2026 Roman Zavada. All rights reserved.

[Languages]
Name: "ukrainian"; MessagesFile: "compiler:Languages\Ukrainian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Створити ярлик на робочому столі"; GroupDescription: "Додаткові ярлики:"; Flags: checkedonce

[Files]
Source: "..\..\dist\{#SourceBundle}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Taxo"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{autodesktop}\Taxo"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Запустити Taxo"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Навмисно НЕ видаляємо робоче сховище Taxo / DriverWorktime.
Type: filesandordirs; Name: "{app}"
