$ErrorActionPreference='Stop';Add-Type -AssemblyName UIAutomationClient,UIAutomationTypes
$p=@(Get-Process im-client-storage|Where-Object {$_.Path -eq 'H:\.codex\toolchains\client-gui\installed\im-client-storage.exe'});if($p.Count -ne 1){throw 'Unique own app required'}
$r=[System.Windows.Automation.AutomationElement]::FromHandle($p[0].MainWindowHandle);$nodes=$r.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition)
$names=@('Friends','Chat',([char]0x2699+' Settings'),'Search','Add friend');$result=@();foreach($name in $names){$matches=@($nodes|Where-Object {$_.Current.Name -eq $name -and $_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Button});$result+=@{name=$name;count=$matches.Count;enabled=@($matches|ForEach-Object {$_.Current.IsEnabled})}}
$result|ConvertTo-Json -Depth 4
if(@($result|Where-Object {$_.count -ne 1}).Count -ne 0){throw 'Actual current control uniqueness failed'}