$ErrorActionPreference='Stop'
$installed='H:/.codex/toolchains/client-gui/installed/im-client-storage.exe'
$setup='H:/.codex/toolchains/client-gui/target/x86_64-pc-windows-msvc/release/bundle/nsis/IM Plus_0.1.0_x64-setup.exe'
function Hash([string]$p){$sha=[Security.Cryptography.SHA256]::Create();try{([BitConverter]::ToString($sha.ComputeHash([IO.File]::ReadAllBytes($p)))).Replace('-','').ToLowerInvariant()}finally{$sha.Dispose()}}
$prior=Hash $installed
if($prior -ne '7f39c9d1010b0ca70c8cd0971540c1fbdee1f4a8135ecdb18168fb97ffab12e1'){throw 'Exact previous task-owned installed candidate changed'}
$owned=@(Get-Process im-client-storage -ErrorAction SilentlyContinue)
foreach($p in $owned){if($p.Path.Replace('\','/') -ne $installed){throw 'Unknown application process ownership'};Stop-Process -Id $p.Id -ErrorAction Stop}
$start=[DateTime]::UtcNow;$installer=Start-Process -FilePath $setup -ArgumentList @('/S','/D=H:\.codex\toolchains\client-gui\installed') -WindowStyle Hidden -PassThru
if(-not $installer.WaitForExit(60000)){throw ('Owned installer timeout PID '+$installer.Id)}
if($installer.ExitCode -ne 0){throw ('Installer exit '+$installer.ExitCode)}
$app=Start-Process -FilePath $installed -WindowStyle Hidden -PassThru
[pscustomobject]@{source='547514f6c8c8c0c40e27073b67d17bb3f224b6c5';priorInstalledSHA256=$prior;installerSHA256=(Hash $setup);installedSHA256=(Hash $installed);installerExit=$installer.ExitCode;installerPID=$installer.Id;appPID=$app.Id;elapsedSeconds=([DateTime]::UtcNow-$start).TotalSeconds;dataOperation='No application data/preferences/credentials/database deletion or copy; original accepted snapshot preserved'} | ConvertTo-Json | Set-Content spec/progress/evidence/LOOP1-CLIENT-STATE-001/desktop-source547514-install.json -Encoding utf8
