param([switch]$Exercise,[string]$Output='spec/progress/evidence/LOOP1-CLIENT-STATE-001/screens/desktop-native/tray-probe.json')
$ErrorActionPreference='Stop'
Add-Type -AssemblyName UIAutomationClient,UIAutomationTypes
Add-Type 'using System;using System.Runtime.InteropServices;public class StateTray { [DllImport("user32.dll",CharSet=CharSet.Unicode)]public static extern IntPtr FindWindow(string cls,string title); }' 
$p=@(Get-Process im-client-storage|Where-Object {$_.Path -eq 'H:\.codex\toolchains\client-gui\installed\im-client-storage.exe'});if($p.Count -ne 1){throw 'Unique installed owner required'}
$name='IM+ '+[char]0x00b7+' Your workspace'
$match=[System.Windows.Automation.AutomationElement]::RootElement.FindFirst([System.Windows.Automation.TreeScope]::Descendants,(New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::NameProperty),$name))
if($null -eq $match){
 $taskbar=[System.Windows.Automation.AutomationElement]::FromHandle([StateTray]::FindWindow('Shell_TrayWnd',$null))
 $elements=$taskbar.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition)
 $expand=@($elements|Where-Object {$_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Button -and ($_.Current.AutomationId -match 'Chevron' -or $_.Current.Name -match 'hidden|隐藏')})
 if($expand.Count -ne 1){throw ('Unique system tray overflow control required: '+$expand.Count)}
 Write-Output ('Observed overflow: '+$expand[0].Current.Name+' id='+$expand[0].Current.AutomationId)
 ([System.Windows.Automation.InvokePattern]$expand[0].GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)).Invoke();Start-Sleep -Milliseconds 350
 $match=[System.Windows.Automation.AutomationElement]::RootElement.FindFirst([System.Windows.Automation.TreeScope]::Descendants,(New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::NameProperty),$name))
 if($null -eq $match){throw 'Owned tray tooltip still not exposed after actual overflow'}
}
$c=$match.Current;$result=@{ownedClientPid=$p[0].Id;name=$c.Name;type=$c.ControlType.ProgrammaticName;bounds=$c.BoundingRectangle.ToString();offscreen=$c.IsOffscreen;enabled=$c.IsEnabled;patterns=@($match.GetSupportedPatterns()|ForEach-Object {$_.ProgrammaticName})}|ConvertTo-Json -Depth 4
[IO.File]::WriteAllText([IO.Path]::GetFullPath($Output),$result,(New-Object Text.UTF8Encoding $false));$result
if($Exercise){
 Add-Type 'using System;using System.Runtime.InteropServices;public class StateTrayActions { [DllImport("user32.dll")]public static extern bool SetCursorPos(int x,int y);[DllImport("user32.dll")]public static extern void mouse_event(uint f,uint x,uint y,uint d,UIntPtr e);[DllImport("user32.dll")]public static extern bool IsWindowVisible(IntPtr h); }'
 $window=$p[0].MainWindowHandle;if($window -eq 0){throw 'Own client window required'}
 $results=@()
 foreach($action in @('Hide window','Open IM+')){
  $icon=[System.Windows.Automation.AutomationElement]::RootElement.FindFirst([System.Windows.Automation.TreeScope]::Descendants,(New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::NameProperty),$name))
  if($null -eq $icon -or $icon.Current.IsOffscreen){
   $taskbar=[System.Windows.Automation.AutomationElement]::FromHandle([StateTray]::FindWindow('Shell_TrayWnd',$null))
   $elements=$taskbar.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition)
   $expand=@($elements|Where-Object {$_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Button -and ($_.Current.AutomationId -match 'Chevron' -or $_.Current.Name -match 'hidden|隐藏')})
   if($expand.Count -ne 1){throw 'Unique actual overflow required'}
   ([System.Windows.Automation.InvokePattern]$expand[0].GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)).Invoke();Start-Sleep -Milliseconds 350
   $icon=[System.Windows.Automation.AutomationElement]::RootElement.FindFirst([System.Windows.Automation.TreeScope]::Descendants,(New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::NameProperty),$name))
  }
  if($null -eq $icon -or $icon.Current.IsOffscreen){throw 'Actual owned tray icon must be visible'}
  $r=$icon.Current.BoundingRectangle;if($r.IsEmpty){throw 'Own tray bounds missing'}
  if(-not [StateTrayActions]::SetCursorPos([int]($r.X+$r.Width/2),[int]($r.Y+$r.Height/2))){throw 'Own icon pointer positioning failed'}
  [StateTrayActions]::mouse_event(8,0,0,0,[UIntPtr]::Zero);[StateTrayActions]::mouse_event(16,0,0,0,[UIntPtr]::Zero);Start-Sleep -Milliseconds 350
  $item=[System.Windows.Automation.AutomationElement]::RootElement.FindFirst([System.Windows.Automation.TreeScope]::Descendants,(New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::NameProperty),$action))
  if($null -eq $item -or $item.Current.ProcessId -ne $p[0].Id -or -not $item.Current.IsEnabled){throw 'Actual menu item owner mismatch or unavailable'}
  $menuBounds=$item.Current.BoundingRectangle.ToString()
  ([System.Windows.Automation.InvokePattern]$item.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)).Invoke();Start-Sleep -Milliseconds 500
  $visible=[StateTrayActions]::IsWindowVisible($window);if($visible -ne ($action -eq 'Open IM+')){throw 'Actual tray action window result failed'}
  $results+=@{action=$action;ownerPid=$p[0].Id;menuBounds=$menuBounds;windowVisibleAfter=$visible}
 }
 $proof=@{clientPid=$p[0].Id;hwnd=$window.ToInt64();actualActions=$results}|ConvertTo-Json -Depth 4
 [IO.File]::WriteAllText([IO.Path]::GetFullPath($Output+'.actions.json'),$proof,(New-Object Text.UTF8Encoding $false));$proof
}
