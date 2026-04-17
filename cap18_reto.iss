; cap18_reto.iss - Script CORREGIDO y FUNCIONAL
[Setup]
AppName=AR Catcher
AppVersion=2.0
AppPublisher=TuNombre
DefaultDirName={pf}\AR Catcher
DefaultGroupName=AR Catcher
UninstallDisplayIcon={app}\AR Catcher.exe
Compression=lzma2
SolidCompression=yes
OutputDir=instalador
OutputBaseFilename=AR_Catcher_Setup
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
Source: "dist\AR Catcher\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\AR Catcher"; Filename: "{app}\AR Catcher.exe"
Name: "{group}\Desinstalar AR Catcher"; Filename: "{uninstallexe}"
Name: "{autodesktop}\AR Catcher"; Filename: "{app}\AR Catcher.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear icono en el escritorio"; GroupDescription: "Iconos adicionales:"

[Run]
Filename: "{app}\AR Catcher.exe"; Description: "Ejecutar AR Catcher"; Flags: postinstall nowait skipifsilent