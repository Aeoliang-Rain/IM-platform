$ErrorActionPreference='Stop'
$stateInstall='H:/.codex/toolchains/client-gui/installed'
$stateSetup='H:/.codex/toolchains/client-gui/target/x86_64-pc-windows-msvc/release/bundle/nsis/IM Plus_0.1.0_x64-setup.exe'
$statePrivate='H:/IM-platform/.git/worktrees/IM-platform43/state-runtime/desktop-before'
if((Get-FileHash ($stateInstall+'/im-client-storage.exe') -Algorithm SHA256).Hash -ne '6707F9D5D5B1C1D2FC195B5C9EF91F11FA86B195E20F83B0DC046864AE9F8B8C'){throw 'Prior accepted exact installed hash changed'}
if(Get-Process im-client-storage -ErrorAction SilentlyContinue){throw 'Existing app owner lease required'}
if(Test-Path -LiteralPath $statePrivate){throw 'Never replace prior installed snapshot'}
New-Item -ItemType Directory -Path $statePrivate | Out-Null
Copy-Item -LiteralPath ($stateInstall+'/im-client-storage.exe') -Destination ($statePrivate+'/im-client-storage.exe')
Copy-Item -LiteralPath ($stateInstall+'/uninstall.exe') -Destination ($statePrivate+'/uninstall.exe')
$stateBefore=(Get-FileHash ($stateInstall+'/im-client-storage.exe') -Algorithm SHA256).Hash
$stateStart=[DateTime]::UtcNow
$stateInstaller=Start-Process -FilePath $stateSetup -ArgumentList @('/S','/D=H:\.codex\toolchains\client-gui\installed') -WindowStyle Hidden -PassThru
$stateInstaller.WaitForExit();if($stateInstaller.ExitCode -ne 0){throw ('Installer actual exit '+$stateInstaller.ExitCode)}
[pscustomobject]@{kind='preliminary task-owned actual NSIS install';installer=$stateSetup;installerSHA256=(Get-FileHash $stateSetup -Algorithm SHA256).Hash;installerPid=$stateInstaller.Id;installerExit=$stateInstaller.ExitCode;elapsedSeconds=([DateTime]::UtcNow-$stateStart).TotalSeconds;installed=$stateInstall+'/im-client-storage.exe';previousAcceptedSHA256=$stateBefore;installedSHA256=(Get-FileHash ($stateInstall+'/im-client-storage.exe') -Algorithm SHA256).Hash;dataOperation='No AppData/preferences/credential/database deletion or copy'} | ConvertTo-Json | Set-Content spec/progress/evidence/LOOP1-CLIENT-STATE-001/desktop-install-preliminary.json -Encoding utf8
Get-Content spec/progress/evidence/LOOP1-CLIENT-STATE-001/desktop-install-preliminary.json
