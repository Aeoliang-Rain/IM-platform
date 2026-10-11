param([int]$Port=9467)
$ErrorActionPreference='Stop'
$path='H:\.codex\toolchains\client-gui\installed\im-client-storage.exe'
if(Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue){throw 'Diagnostic port already occupied'}
$p=@(Get-Process im-client-storage -ErrorAction SilentlyContinue|Where-Object Path -eq $path);if($p.Count -gt 1){throw 'At most one owned fixture PID required'}
$old=if($p.Count){$p[0].Id}else{0};$all=@(Get-CimInstance Win32_Process);$family=if($old){@($old)}else{@()}
do{$found=@($all|Where-Object {$family -contains $_.ParentProcessId -and $family -notcontains $_.ProcessId}|ForEach-Object ProcessId);$family+=$found}while($found.Count)
if($old){Stop-Process -Id $old}
for($i=0;$i -lt 50;$i++){if(!@($family|Where-Object {Get-Process -Id $_ -ErrorAction SilentlyContinue}).Count){break};Start-Sleep -Milliseconds 200}
if(@($family|Where-Object {Get-Process -Id $_ -ErrorAction SilentlyContinue}).Count){throw 'Old exact owned process family did not exit'}
$original=[Environment]::GetEnvironmentVariable('WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS','Process')
try{
 $env:WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS="--remote-debugging-address=127.0.0.1 --remote-debugging-port=$Port"
 $new=Start-Process -FilePath $path -WindowStyle Hidden -PassThru
}finally{[Environment]::SetEnvironmentVariable('WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS',$original,'Process')}
try{
 for($i=0;$i -lt 100;$i++){$listen=@(Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue);if($listen.Count){break};Start-Sleep -Milliseconds 100}
 if(!$listen.Count -or @($listen|Where-Object LocalAddress -ne '127.0.0.1').Count){throw 'Only actual loopback debug listener permitted'}
 $newFamily=@($new.Id);$all=@(Get-CimInstance Win32_Process);do{$found=@($all|Where-Object {$newFamily -contains $_.ParentProcessId -and $newFamily -notcontains $_.ProcessId}|ForEach-Object ProcessId);$newFamily+=$found}while($found.Count)
 if(@($listen|Where-Object {$newFamily -notcontains $_.OwningProcess}).Count){throw 'Debug listener is outside exact owned process family'}
 @{actualUTC=[DateTime]::UtcNow.ToString('o');oldPID=$old;oldFamily=$family;oldFamilyExited=$true;newPID=$new.Id;ownedFamily=$newFamily;port=$Port;actualListener=@($listen|Select-Object LocalAddress,LocalPort,OwningProcess);flags="--remote-debugging-address=127.0.0.1 --remote-debugging-port=$Port";parentEnvironmentRestored=([Environment]::GetEnvironmentVariable('WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS','Process') -eq $original)}|ConvertTo-Json -Depth 6
}catch{Stop-Process -Id $new.Id -ErrorAction SilentlyContinue;throw}
