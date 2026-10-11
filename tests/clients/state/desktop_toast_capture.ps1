param([string]$Output='spec/progress/evidence/LOOP1-CLIENT-STATE-001/fix-b/own-os-notification.png',[switch]$NotificationCenter)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing,UIAutomationClient,UIAutomationTypes
Add-Type 'using System;using System.Runtime.InteropServices;public class OwnToastCapture{[DllImport("user32.dll")]public static extern bool SetProcessDPIAware();[DllImport("user32.dll")]public static extern void keybd_event(byte key,byte scan,uint flags,UIntPtr extra);[DllImport("user32.dll")]public static extern bool SetForegroundWindow(IntPtr h);[DllImport("user32.dll")]public static extern IntPtr SendMessageTimeout(IntPtr h,uint m,IntPtr w,IntPtr l,uint f,uint t,out IntPtr r);}'
if(-not [OwnToastCapture]::SetProcessDPIAware()){throw 'Own toast geometry DPI failed'}
$manager=[Windows.UI.Notifications.ToastNotificationManager,Windows.UI.Notifications,ContentType=WindowsRuntime]
if($manager::CreateToastNotifier('im.platform.desktop').Setting.ToString() -ne 'Enabled'){throw 'Owned notifications disabled; no global settings mutation authorized'}
$before=@($manager::History.GetHistory('im.platform.desktop')).Count
function ToggleCenter{
$condition=New-Object System.Windows.Automation.AndCondition (New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::ClassNameProperty),'SystemTray.OmniButton'),(New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::AutomationIdProperty),'SystemTrayIcon')
$clock=[System.Windows.Automation.AutomationElement]::RootElement.FindAll([System.Windows.Automation.TreeScope]::Descendants,$condition)
if($clock.Count -ne 1){throw 'Unique actual standard taskbar notification center entry required'}
([System.Windows.Automation.InvokePattern]$clock[0].GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)).Invoke()
}
$triggerUTC=$null;$owned=$null
if($NotificationCenter){ToggleCenter;Start-Sleep -Milliseconds 300}else{
& ($PSScriptRoot+'/desktop_window.ps1') -Action click -Name '⚙ Settings' -Output ($Output+'.settings.png') | Out-Null
$owned=@(Get-Process im-client-storage|Where-Object {$_.Path -eq 'H:\.codex\toolchains\client-gui\installed\im-client-storage.exe'})
if($owned.Count -ne 1 -or $owned[0].MainWindowHandle -eq 0){throw 'Exact installed own app window required for trigger'}
[void][OwnToastCapture]::SetForegroundWindow($owned[0].MainWindowHandle);[IntPtr]$reply=[IntPtr]::Zero;[void][OwnToastCapture]::SendMessageTimeout($owned[0].MainWindowHandle,0x003d,[IntPtr]::Zero,[IntPtr](-4),2,3000,[ref]$reply)
Start-Sleep -Milliseconds 150
$root=[System.Windows.Automation.AutomationElement]::FromHandle($owned[0].MainWindowHandle)
$buttons=$root.FindAll([System.Windows.Automation.TreeScope]::Descendants,(New-Object System.Windows.Automation.AndCondition (New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::NameProperty),'Test notification'),(New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::ControlTypeProperty),([System.Windows.Automation.ControlType]::Button))))
if($buttons.Count -ne 1 -or -not $buttons[0].Current.IsEnabled){throw 'Unique enabled actual own Test notification button required'}
$triggerUTC=[DateTime]::UtcNow.ToString('o')
([System.Windows.Automation.InvokePattern]$buttons[0].GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)).Invoke()

}
try {
$condition=New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::NameProperty),'Your workspace notifications are ready.'
$target=$null
$deadline=[DateTime]::UtcNow.AddSeconds(15)
while([DateTime]::UtcNow -lt $deadline){
 $bodies=[System.Windows.Automation.AutomationElement]::RootElement.FindAll([System.Windows.Automation.TreeScope]::Descendants,$condition)
 foreach($body in $bodies){
  if($body.Current.IsOffscreen){continue}
  $node=$body
  while($node){
   $r=$node.Current.BoundingRectangle
   if(-not $r.IsEmpty -and $r.Width -ge 300 -and $r.Width -le 800 -and $r.Height -ge 90 -and $r.Height -le 500){
    $all=$node.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition)
    $names=@($all|Where-Object {$_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Text}|ForEach-Object {$_.Current.Name})
    if($names -contains 'IM+' -and $names -contains 'Your workspace notifications are ready.'){$target=$node;break}
   }
   $node=[System.Windows.Automation.TreeWalker]::ControlViewWalker.GetParent($node)
  }
 }
 if($target){break};Start-Sleep -Milliseconds 100
}
if(-not $target){throw 'Readable precisely owned IM+ OS toast not exposed; own History is insufficient'}
$r=$target.Current.BoundingRectangle
$bitmap=New-Object System.Drawing.Bitmap ([int]$r.Width),([int]$r.Height)
$g=[System.Drawing.Graphics]::FromImage($bitmap)
try{$g.CopyFromScreen([int]$r.Left,[int]$r.Top,0,0,$bitmap.Size)}finally{$g.Dispose()}
$full=[IO.Path]::GetFullPath($Output);$bitmap.Save($full,[System.Drawing.Imaging.ImageFormat]::Png);$bitmap.Dispose()
$meta=@{capturedUTC=[DateTime]::UtcNow.ToString('o');triggerUTC=$triggerUTC;installedPid=$(if($owned){$owned[0].Id}else{$null});AppUserModelId='im.platform.desktop';actualOSSurface=$true;entry=$(if($NotificationCenter){'Standard Windows Notification Center; exact known own title/body card only'}else{'Installed actual Test notification UI; exact owned title/body region only'});bounds=$r.ToString();ownTitle='IM+';ownBody='Your workspace notifications are ready.';beforeOwnedHistoryCount=$before;afterOwnedHistoryCount=@($manager::History.GetHistory('im.platform.desktop')).Count;otherAppHistoryAccess=$false;globalSettingsMutation=$false;theme='OS native';fontSize='OS native';density='OS native';language='en'}|ConvertTo-Json
[IO.File]::WriteAllText($full+'.json',$meta,(New-Object Text.UTF8Encoding $false));$meta

}finally{if($NotificationCenter){ToggleCenter}}
