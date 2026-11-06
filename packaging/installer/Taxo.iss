#define MyAppName "Taxo"
#ifndef MyAppVersion
  #error "MyAppVersion must be supplied by the build workflow"
#endif
#ifndef SourceBundle
  #error "SourceBundle must be supplied by the build workflow"
#endif
#ifndef OutputBase
  #error "OutputBase must be supplied by the build workflow"
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
