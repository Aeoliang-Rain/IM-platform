param([string]$Output)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName UIAutomationClient,UIAutomationTypes
$p=@(Get-Process im-client-storage|Where-Object Path -eq 'H:\.codex\toolchains\client-gui\installed\im-client-storage.exe');if($p.Count -ne 1){throw 'Unique exact owned fixture required'}
$root=[System.Windows.Automation.AutomationElement]::FromHandle($p[0].MainWindowHandle)
$all=$root.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition)
$sync=@($all|Where-Object {$_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Text -and $_.Current.Name -in @('Syncing…','Up to date','Sync needs attention','Local history')})
$ready=@($all|Where-Object {$_.Current.Name -eq 'Connected · Messages sync automatically'})
if($sync.Count -ne 1 -or $ready.Count -ne 1){throw 'Unique actual Sync span and Connected header required'}
$clock=[Diagnostics.Stopwatch]::StartNew();$samples=@();$pass=$false
do{$at=$clock.ElapsedMilliseconds;$s=$sync[0].Current;$r=$ready[0].Current;$samples+=@{elapsedMilliseconds=$at;queryMilliseconds=($clock.ElapsedMilliseconds-$at);sync=$s.Name;syncOffscreen=$s.IsOffscreen;connection=$r.Name;connectionOffscreen=$r.IsOffscreen};if($s.Name -eq 'Up to date' -and !$s.IsOffscreen -and $r.Name -eq 'Connected · Messages sync automatically' -and !$r.IsOffscreen){$pass=$true;break};Start-Sleep -Milliseconds 20}while($clock.ElapsedMilliseconds -lt 30000)
if([IO.File]::Exists($Output)){throw 'Do not overwrite original probe'}
$receipt=@{actualUTC=[DateTime]::UtcNow.ToString('o');PID=$p[0].Id;pass=$pass;method='One actual UIA element lookup; each sample reads live Current Name and visibility, never cached property values; read-only diagnostic without debug flags or business calls';samples=$samples}
[IO.File]::WriteAllText($Output,($receipt|ConvertTo-Json -Depth 6),(New-Object Text.UTF8Encoding($false)))
if(!$pass){throw 'Direct actual UIA Connected/idle not observed in30s'}
'PASS direct actual live UIA Connected + idle; '+$Output
