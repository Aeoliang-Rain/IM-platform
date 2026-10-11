$ErrorActionPreference='Stop'
$path='H:\.codex\toolchains\client-gui\installed\im-client-storage.exe'
$owned=@(Get-Process im-client-storage -ErrorAction SilentlyContinue|Where-Object Path -eq $path)
if($owned.Count -gt 1){throw 'At most one exact owned fixture required'}
$family=@();if($owned.Count){$family=@($owned[0].Id);$all=@(Get-CimInstance Win32_Process);do{$found=@($all|Where-Object {$family -contains $_.ParentProcessId -and $family -notcontains $_.ProcessId}|ForEach-Object ProcessId);$family+=$found}while($found.Count);Stop-Process -Id $owned[0].Id}
for($i=0;$i -lt 50;$i++){if(!@($family|Where-Object {Get-Process -Id $_ -ErrorAction SilentlyContinue}).Count){break};Start-Sleep -Milliseconds 200}
if(@($family|Where-Object {Get-Process -Id $_ -ErrorAction SilentlyContinue}).Count){throw 'Exact owned process family did not exit'}
@{actualUTC=[DateTime]::UtcNow.ToString('o');path=$path;ownedFamily=$family;allExited=$true;unknownProcessesUntouched=$true}|ConvertTo-Json -Depth 3
