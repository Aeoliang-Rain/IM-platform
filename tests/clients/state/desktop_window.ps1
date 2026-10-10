param([string]$Action='observe',[string]$Name='',[string]$Value='',[int]$TargetPid=0,[long]$Hwnd=0,[string]$Output='spec/progress/evidence/LOOP1-CLIENT-STATE-001/screens/desktop-initial.png')
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing,UIAutomationClient,UIAutomationTypes
Add-Type @"
using System; using System.Runtime.InteropServices;
public class StateWin { [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h); [DllImport("user32.dll")] public static extern IntPtr SendMessageTimeout(IntPtr h,uint m,IntPtr w,IntPtr l,uint f,uint t,out IntPtr r); public delegate bool Callback(IntPtr h,IntPtr p); [DllImport("user32.dll")] public static extern bool EnumWindows(Callback c,IntPtr p); [DllImport("user32.dll",CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h,System.Text.StringBuilder s,int n); public static IntPtr OwnedWindow(uint pid){IntPtr found=IntPtr.Zero;int count=0;EnumWindows(delegate(IntPtr h,IntPtr p){uint owner;GetWindowThreadProcessId(h,out owner);if(owner==pid){var name=new System.Text.StringBuilder(256);GetWindowText(h,name,256);if(name.ToString()=="IM+ \u00b7 PlugWorldIM"){found=h;count++;}}return true;},IntPtr.Zero);if(count!=1)throw new Exception("Unique actual owned window required: "+count);return found;} [DllImport("user32.dll")] public static extern bool SetProcessDPIAware(); [StructLayout(LayoutKind.Sequential)] public struct R { public int l,t,r,b; } [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h,out uint p); [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h,out R r); [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int n); [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h,IntPtr dc,uint flags); }
"@
$dpiAware=[StateWin]::SetProcessDPIAware();if(-not $dpiAware){throw 'Own capture DPI awareness failed'}
if($TargetPid -eq 0){$owned=@(Get-Process im-client-storage -ErrorAction SilentlyContinue | Where-Object {$_.Path -eq 'H:\.codex\toolchains\client-gui\installed\im-client-storage.exe'});if($owned.Count -ne 1){throw 'Unique installed owned client process required'};$TargetPid=$owned[0].Id}
if($Hwnd -eq 0){$Hwnd=[StateWin]::OwnedWindow([uint32]$TargetPid).ToInt64()}
$p=Get-Process -Id $TargetPid
if($p.Path -ne 'H:\.codex\toolchains\client-gui\installed\im-client-storage.exe'){throw 'Target process ownership mismatch'}
[uint32]$owner=0;[void][StateWin]::GetWindowThreadProcessId([IntPtr]$Hwnd,[ref]$owner)
if($owner -ne $TargetPid){throw 'Window ownership mismatch'}
[void][StateWin]::ShowWindow([IntPtr]$Hwnd,5)
[void][StateWin]::SetForegroundWindow([IntPtr]$Hwnd);[IntPtr]$accessibilityReply=[IntPtr]::Zero;[void][StateWin]::SendMessageTimeout([IntPtr]$Hwnd,0x003d,[IntPtr]::Zero,[IntPtr](-4),2,3000,[ref]$accessibilityReply)
Start-Sleep -Milliseconds 150
$root=[System.Windows.Automation.AutomationElement]::FromHandle([IntPtr]$Hwnd)
if($Action -eq 'reach'){
 function FindOwnedFriendCard($tree){
  $bodies=$tree.FindAll([System.Windows.Automation.TreeScope]::Descendants,(New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::NameProperty),$Name))
  $buttons=$tree.FindAll([System.Windows.Automation.TreeScope]::Descendants,(New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::NameProperty),'Message'))
  $cards=@();foreach($body in $bodies){if($body.Current.ControlType -ne [System.Windows.Automation.ControlType]::Text){continue};$bounds=$body.Current.BoundingRectangle;if($bounds.IsEmpty){continue};$middle=$bounds.Top+$bounds.Height/2
   $same=@($buttons|Where-Object {$_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Button -and -not $_.Current.BoundingRectangle.IsEmpty -and $middle -ge $_.Current.BoundingRectangle.Top -and $middle -le $_.Current.BoundingRectangle.Bottom})
   if($same.Count -eq 1){$cards+=@{body=$body;button=$same[0]}}
  };if($cards.Count -ne 1){throw ('Unique controlled username/Message friend card required: '+$cards.Count)};return $cards[0]
 }
 $card=FindOwnedFriendCard $root;$card.button.SetFocus();Start-Sleep -Milliseconds 300
 $root=[System.Windows.Automation.AutomationElement]::FromHandle([IntPtr]$Hwnd);$current=FindOwnedFriendCard $root
 if($current.body.Current.IsOffscreen -or $current.button.Current.IsOffscreen){throw 'Controlled friend card remains offscreen'}
}elseif($Action -eq 'retry'){
 $b=$root.FindAll([System.Windows.Automation.TreeScope]::Descendants,(New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::NameProperty),$Name));if($b.Count -ne 1){throw 'Unique controlled message body required'}
 $body=$b[0].Current.BoundingRectangle;if($body.IsEmpty){throw 'Current message body geometry unavailable'}
 $choices=$root.FindAll([System.Windows.Automation.TreeScope]::Descendants,(New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::NameProperty),'Retry'))
 $nearest=@($choices | Where-Object {$_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Button -and -not $_.Current.BoundingRectangle.IsEmpty -and $_.Current.BoundingRectangle.Top -ge $body.Bottom} | Sort-Object {$_.Current.BoundingRectangle.Top})
 if($nearest.Count -eq 0){throw 'Current message Retry below body unavailable'};$retry=$nearest[0];if(-not $retry.Current.IsEnabled){throw 'Current controlled Retry disabled'}
 $retry.SetFocus();Start-Sleep -Milliseconds 300;if($retry.Current.IsOffscreen){throw 'Retry remains offscreen'};([System.Windows.Automation.InvokePattern]$retry.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)).Invoke();Start-Sleep -Milliseconds 700
}elseif($Action -ne 'observe'){
 $type=if($Action -eq 'fill'){[System.Windows.Automation.ControlType]::Edit}else{[System.Windows.Automation.ControlType]::Button}
 $condition=New-Object System.Windows.Automation.AndCondition (New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::NameProperty),$Name),(New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::ControlTypeProperty),$type)
 $matches=$root.FindAll([System.Windows.Automation.TreeScope]::Descendants,$condition)
 if($matches.Count -ne 1){throw "Unique observed UI control required: $Name ($($matches.Count))"}
 $n=$matches[0];if(-not $n.Current.IsEnabled){throw 'Observed control disabled'}
 if($Action -eq 'fill'){([System.Windows.Automation.ValuePattern]$n.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)).SetValue($Value)}
 elseif($Action -eq 'click'){([System.Windows.Automation.InvokePattern]$n.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)).Invoke()}
 else{throw 'Unknown actual UI action'}
 Start-Sleep -Milliseconds 700
}
$r=New-Object StateWin+R;[void][StateWin]::GetWindowRect([IntPtr]$Hwnd,[ref]$r)
$bitmap=New-Object System.Drawing.Bitmap ($r.r-$r.l),($r.b-$r.t)
$graphics=[System.Drawing.Graphics]::FromImage($bitmap);$dc=$graphics.GetHdc()
try {if(-not [StateWin]::PrintWindow([IntPtr]$Hwnd,$dc,2)){throw 'PrintWindow failed'}} finally {$graphics.ReleaseHdc($dc);$graphics.Dispose()}
$full=[IO.Path]::GetFullPath($Output);[void][IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($full));$bitmap.Save($full,[System.Drawing.Imaging.ImageFormat]::Png);$bitmap.Dispose()
$root=[System.Windows.Automation.AutomationElement]::FromHandle([IntPtr]$Hwnd)
$all=$root.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition)
$nodes=@();foreach($n in $all){$c=$n.Current;$nodes+=@{name=$c.Name;type=$c.ControlType.ProgrammaticName;bounds=$c.BoundingRectangle.ToString();enabled=$c.IsEnabled;offscreen=$c.IsOffscreen}}
$result=@{pid=$TargetPid;hwnd=$Hwnd;path=$p.Path;window=@{left=$r.l;top=$r.t;width=$r.r-$r.l;height=$r.b-$r.t};nodes=$nodes}|ConvertTo-Json -Depth 5

[IO.File]::WriteAllText($full+'.json',$result,(New-Object Text.UTF8Encoding $false)); ($nodes | Where-Object {$_.name}) | ConvertTo-Json -Depth 4
