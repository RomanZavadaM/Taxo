#define MyAppName "Taxo"
#define MyAppVersion "8.64"
#define MyAppPublisher "RomanZavadaM"
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
OutputDir=..\release_out
OutputBaseFilename=Taxo_v8_64_Setup_Windows_x64
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\Taxo.exe
CloseApplications=yes
RestartApplications=no
ChangesAssociations=no
SetupLogging=yes

[Languages]
Name: "ukrainian"; MessagesFile: "compiler:Languages\Ukrainian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Створити ярлик на робочому столі"; GroupDescription: "Додаткові ярлики:"; Flags: checkedonce

[Files]
Source: "..\dist\Taxo\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Taxo"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{autodesktop}\Taxo"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Запустити Taxo"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Навмисно НЕ видаляємо %USERPROFILE%\Documents\DriverWorktime.
Type: filesandordirs; Name: "{app}"
