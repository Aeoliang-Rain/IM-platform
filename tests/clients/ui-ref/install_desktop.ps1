param([ValidateSet('install','restore')][string]$Action='install')
$ErrorActionPreference='Stop'
$target='H:/.codex/toolchains/client-gui/installed'
$private='C:/Users/21441/.codex/visualizations/2026/10/11/01a129aa-d2ed-7350-8f8d-efb0ecc85664/ui-ref-runtime/desktop-before'
$setup='H:/.codex/toolchains/client-gui/target/x86_64-pc-windows-msvc/release/bundle/nsis/IM Plus_0.1.0_x64-setup.exe'
if(Get-Process im-client-storage -ErrorAction SilentlyContinue){throw 'Existing app must be stopped by exact owned PID before install/restore'}
if($Action -eq 'install'){
 if(Test-Path -LiteralPath $private){throw 'Never overwrite original installation snapshot'}
 New-Item -ItemType Directory -Path $private|Out-Null
 $files=@(Get-ChildItem -LiteralPath $target -File)
 $original=@($files|ForEach-Object{[pscustomobject]@{name=$_.Name;sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash}})
 foreach($file in $files){Copy-Item -LiteralPath $file.FullName -Destination (Join-Path $private $file.Name)}
 $original|ConvertTo-Json|Set-Content (Join-Path $private 'original.json') -Encoding utf8
 $head=git rev-parse HEAD;$clock=[DateTime]::UtcNow
 $installer=Start-Process -FilePath $setup -ArgumentList @('/S','/D=H:\.codex\toolchains\client-gui\installed') -WindowStyle Hidden -PassThru
 $installer.WaitForExit();if($installer.ExitCode -ne 0){throw 'Owned installer failed'}
 [pscustomobject]@{actualSourceHead=$head;actualUTC=$clock.ToString('o');installer=$setup;installerSHA256=(Get-FileHash $setup).Hash;installerPID=$installer.Id;exit=$installer.ExitCode;installedSHA256=(Get-FileHash ($target+'/im-client-storage.exe')).Hash;original=$original;dataOperation='No AppData/preferences/credential/database deletion'}|ConvertTo-Json -Depth 8|Set-Content 'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/desktop-install.json' -Encoding utf8
}else{
 $original=Get-Content (Join-Path $private 'original.json') -Raw|ConvertFrom-Json
 foreach($file in $original){$saved=Join-Path $private $file.name;if((Get-FileHash $saved).Hash -ne $file.sha256){throw 'Original snapshot changed'};Copy-Item -LiteralPath $saved -Destination (Join-Path $target $file.name) -Force}
 foreach($file in $original){if((Get-FileHash (Join-Path $target $file.name)).Hash -ne $file.sha256){throw 'Original install restore failed'}}
 [pscustomobject]@{actualUTC=[DateTime]::UtcNow.ToString('o');original=$original;restored=$true;dataOperation='No AppData/preferences/credential/database deletion'}|ConvertTo-Json -Depth 8|Set-Content 'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/desktop-install-restored.json' -Encoding utf8
}
Write-Output ('PASS actual NSIS '+$Action)
