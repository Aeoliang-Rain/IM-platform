param([switch]$VerifyOnly)
$ErrorActionPreference='Stop'
$path='H:\.codex\toolchains\client-gui\installed\im-client-storage.exe'
if(Get-NetTCPConnection -State Listen -LocalPort 9467 -ErrorAction SilentlyContinue){throw 'Diagnostic listener must be closed before formal run'}
if([Environment]::GetEnvironmentVariable('WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS','Process')){throw 'Formal process must have no additional WebView arguments'}
$existing=@(Get-Process im-client-storage -ErrorAction SilentlyContinue|Where-Object Path -eq $path)
if($VerifyOnly){if($existing.Count -ne 1){throw 'Unique exact already-started owned fixture required'};$p=$existing[0]}else{if($existing.Count){throw 'Exact owned fixture already running; do not duplicate'};$p=Start-Process -FilePath $path -WindowStyle Hidden -PassThru}
Start-Sleep -Seconds 3
if($p.HasExited){throw 'Formal fixture exited during startup'}
$all=@(Get-CimInstance Win32_Process);$family=@($p.Id)
do{$found=@($all|Where-Object {$family -contains $_.ParentProcessId -and $family -notcontains $_.ProcessId}|ForEach-Object ProcessId);$family+=$found}while($found.Count)
if(@($all|Where-Object {$family -contains $_.ProcessId -and $_.CommandLine -match 'remote-debugging'}).Count){throw 'Formal owned process family has diagnostic flags'}
if(Get-NetTCPConnection -State Listen -LocalPort 9467 -ErrorAction SilentlyContinue){throw 'Formal startup opened a diagnostic listener'}
$hasher=[Security.Cryptography.SHA256]::Create();try{$hash=[BitConverter]::ToString($hasher.ComputeHash([IO.File]::ReadAllBytes($path))).Replace('-','').ToLowerInvariant()}finally{$hasher.Dispose()}
@{actualUTC=[DateTime]::UtcNow.ToString('o');PID=$p.Id;path=$path;sha256=$hash;ownedFamily=$family;additionalBrowserArguments=$null;diagnosticFlags=$false;diagnosticListener=$false;captureHEAD=(git rev-parse HEAD);verifyExisting=$VerifyOnly.IsPresent}|ConvertTo-Json -Depth 4
