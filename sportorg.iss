; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "SportOrg"
#define MyAppVersion "v1.6.0"
#define MyVersionInfoVersion "1.6.0.0"
#define MyAppPublisher "Danil Akhtarov, Sergei Kobelev"
#define MyAppURL "https://sportorg.readthedocs.io"
#define MyAppExeName "SportOrg.exe"

#define BuildDir "build/exe.win32-3.8" ; !!replace with your build path!!
#define AdditionalLib32 "data/additional_lib_32" ; !!replace with your lib path!!

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{0C7DBB23-2F49-410E-B92E-47CC79ED9801}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
VersionInfoVersion={#MyVersionInfoVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\{#MyAppName}
DisableProgramGroupPage=yes
OutputBaseFilename={#MyAppName}-{#MyAppVersion}
Compression=lzma
SolidCompression=yes
LicenseFile=LICENSE
SetupIconFile="img\icon\sportorg.ico"

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#BuildDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

Source: "{#AdditionalLib32}\*"; DestDir: {sys}; Flags: onlyifdoesntexist
; Taken here for Win7: http://www.skaip.su/na-kompyutere-otsutstvuet-api-ms-win-crt-runtime-l1-1-0-dll

; Source: "vc_redist\vc_redist.x86.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall;

[Dirs]
Name: "{app}\log"; Permissions: everyone-full
Name: "{app}\templates"; Permissions: everyone-full
Name: "{app}\example"; Permissions: everyone-full
Name: "{app}\data"; Permissions: everyone-full
; NOTE: to allow start by non-privileged user from Program Files

[Icons]
Name: "{commonprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent


; Replaced with direct DLL copy, also requires KB2999226 update, which is plarform-depended (Vista, Win7, Win8, Win8.1, WinR8...)

; Python starting from 3.5 requires the VC 2015 redistributables so run the installer if this
; or a later 2015 version is not already present
; https://wiki.python.org/moin/WindowsCompilers#Which_Microsoft_Visual_C.2B-.2B-_compiler_to_use_with_a_specific_Python_version_.3F
;
; Filename: "{tmp}\vc_redist.x86.exe"; Parameters: "/install /passive"; StatusMsg: "Installing VS C++ 2015 Redistributable"; Check: not VCinstalled

[Code]
function VCinstalled: Boolean;
 // Function for Inno Setup Compiler
 // Returns True if same or later Microsoft Visual C++ 2015 Redistributable is installed, otherwise False.
 var
  major: Cardinal;
  minor: Cardinal;
  bld: Cardinal;
  rbld: Cardinal;
  key: String;
 begin
  Result := False;
  key := 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x86';
  if RegQueryDWordValue(HKEY_LOCAL_MACHINE, key, 'Major', major) then begin
    if RegQueryDWordValue(HKEY_LOCAL_MACHINE, key, 'Minor', minor) then begin
      if RegQueryDWordValue(HKEY_LOCAL_MACHINE, key, 'Bld', bld) then begin
        if RegQueryDWordValue(HKEY_LOCAL_MACHINE, key, 'RBld', rbld) then begin
            Log('VC 2015 Redist Major is: ' + IntToStr(major) + ' Minor is: ' + IntToStr(minor) + ' Bld is: ' + IntToStr(bld) + ' Rbld is: ' + IntToStr(rbld));
            // Version info was found. Return true if later or equal to our 14.0.24212.00 redistributable
            // Note brackets required because of weird operator precendence
            Result := (major >= 14) and (minor >= 0) and (bld >= 24212) and (rbld >= 0)
        end;
      end;
    end;
  end;
 end;
