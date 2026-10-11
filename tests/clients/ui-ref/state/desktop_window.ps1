param([string]$Action='observe',[string]$Name='',[string]$Value='',[int]$TargetPid=0,[long]$Hwnd=0,[string]$Output='spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/screens/desktop-initial.png')
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing,UIAutomationClient,UIAutomationTypes
Add-Type @"
using System; using System.Runtime.InteropServices;
public class StateWin { [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h); [DllImport("user32.dll")] public static extern IntPtr SendMessageTimeout(IntPtr h,uint m,IntPtr w,IntPtr l,uint f,uint t,out IntPtr r); public delegate bool Callback(IntPtr h,IntPtr p); [DllImport("user32.dll")] public static extern bool EnumWindows(Callback c,IntPtr p); [DllImport("user32.dll",CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h,System.Text.StringBuilder s,int n); public static IntPtr OwnedWindow(uint pid){IntPtr found=IntPtr.Zero;int count=0;EnumWindows(delegate(IntPtr h,IntPtr p){uint owner;GetWindowThreadProcessId(h,out owner);if(owner==pid){var name=new System.Text.StringBuilder(256);GetWindowText(h,name,256);if(name.ToString()=="IM+ \u00b7 PlugWorldIM"){found=h;count++;}}return true;},IntPtr.Zero);if(count!=1)throw new Exception("Unique actual owned window required: "+count);return found;} [DllImport("user32.dll")] public static extern bool SetProcessDPIAware(); [StructLayout(LayoutKind.Sequential)] public struct R { public int l,t,r,b; } [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h,out uint p); [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h,out R r); [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int n); [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h,IntPtr dc,uint flags); [DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y); [DllImport("user32.dll")] public static extern void mouse_event(uint flags,uint x,uint y,uint data,UIntPtr extra); [StructLayout(LayoutKind.Sequential)] public struct P {public int x,y;} [DllImport("user32.dll")] public static extern IntPtr WindowFromPoint(P p); [DllImport("user32.dll")] public static extern IntPtr GetAncestor(IntPtr h,uint f); [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow(); [StructLayout(LayoutKind.Sequential)] public struct M {public int size;public R monitor,work;public uint flags;} [DllImport("user32.dll")] public static extern IntPtr MonitorFromWindow(IntPtr h,uint f); [DllImport("user32.dll")] public static extern bool GetMonitorInfo(IntPtr h,ref M m); [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h,IntPtr after,int x,int y,int w,int height,uint flags); }
"@
$dpiAware=[StateWin]::SetProcessDPIAware();if(-not $dpiAware){throw 'Own capture DPI awareness failed'}
Add-Type 'using System;using System.Runtime.InteropServices; public class UiRefZ { [DllImport("user32.dll")] public static extern int GetWindowLong(IntPtr h,int n); }'
if($TargetPid -eq 0){$owned=@(Get-Process im-client-storage -ErrorAction SilentlyContinue | Where-Object {$_.Path -eq 'H:\.codex\toolchains\client-gui\installed\im-client-storage.exe'});if($owned.Count -ne 1){throw 'Unique installed owned client process required'};$TargetPid=$owned[0].Id}
if($Hwnd -eq 0){$Hwnd=[StateWin]::OwnedWindow([uint32]$TargetPid).ToInt64()}
$p=Get-Process -Id $TargetPid
if($p.Path -ne 'H:\.codex\toolchains\client-gui\installed\im-client-storage.exe'){throw 'Target process ownership mismatch'}
[uint32]$owner=0;[void][StateWin]::GetWindowThreadProcessId([IntPtr]$Hwnd,[ref]$owner)
if($owner -ne $TargetPid){throw 'Window ownership mismatch'}
[void][StateWin]::ShowWindow([IntPtr]$Hwnd,5)
$originalTopmost=(([UiRefZ]::GetWindowLong([IntPtr]$Hwnd,-20) -band 8) -ne 0)
[void][StateWin]::SetWindowPos([IntPtr]$Hwnd,[IntPtr](-1),0,0,0,0,19)
try {
[void][StateWin]::SetForegroundWindow([IntPtr]$Hwnd);[IntPtr]$accessibilityReply=[IntPtr]::Zero;[void][StateWin]::SendMessageTimeout([IntPtr]$Hwnd,0x003d,[IntPtr]::Zero,[IntPtr](-4),2,3000,[ref]$accessibilityReply)
Start-Sleep -Milliseconds 150
$root=[System.Windows.Automation.AutomationElement]::FromHandle([IntPtr]$Hwnd)
function CachedSnapshot($tree){
 $cache=New-Object System.Windows.Automation.CacheRequest
 foreach($property in @([System.Windows.Automation.AutomationElement]::NameProperty,[System.Windows.Automation.AutomationElement]::ControlTypeProperty,[System.Windows.Automation.AutomationElement]::BoundingRectangleProperty,[System.Windows.Automation.AutomationElement]::IsEnabledProperty,[System.Windows.Automation.AutomationElement]::IsOffscreenProperty)){$cache.Add($property)}
 $active=$cache.Activate()
 try{$items=$tree.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition)}finally{$active.Dispose()}
 return @($items|ForEach-Object {[pscustomobject]@{Current=$_.Cached;element=$_}})
}
$visibleTargets=@()
if($Action -eq 'reach-message'){
 function MessageGeometry {
  $tree=[System.Windows.Automation.AutomationElement]::FromHandle([IntPtr]$Hwnd)
  $all=CachedSnapshot $tree
  $texts=@($Name);if($Value -and $Value -notin @('SENDING','FAILED','SENT')){$texts+=@($Value)}
  $heading=@($all|Where-Object {$_.Current.Name -match '^(Connected · Messages sync automatically|Offline · Showing saved history)$'})
  $composer=@($all|Where-Object {$_.Current.Name -eq 'Message' -and $_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Edit})
  if($heading.Count -ne 1 -or $composer.Count -ne 1){throw 'Actual message pane heading/composer must be unique'}
  $h=$heading[0].Current.BoundingRectangle;$c=$composer[0].Current.BoundingRectangle
  $send=@($all|Where-Object {$_.Current.Name -eq 'Send ↑' -and $_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Button})
  if($send.Count -ne 1){throw 'Actual composer Send control must be unique'}
  $panes=@($all|Where-Object {$_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Group -and -not $_.Current.BoundingRectangle.IsEmpty -and $_.Current.BoundingRectangle.Top -ge $h.Bottom -and $_.Current.BoundingRectangle.Bottom -le $c.Top -and $_.Current.BoundingRectangle.Height -gt 100 -and $_.Current.BoundingRectangle.Left -le $c.Left -and $_.Current.BoundingRectangle.Right -ge $send[0].Current.BoundingRectangle.Right})
  if($panes.Count -ne 1){throw 'Unique actual UIA message scroll viewport required'}
  $pane=$panes[0].Current.BoundingRectangle
  $clip=@{left=$pane.Left;right=$pane.Right;top=$pane.Top;bottom=$pane.Bottom}
  $targets=@()
  foreach($text in $texts){
   $body=@($all|Where-Object {$_.Current.Name -eq $text -and $_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Text})
   if($body.Count -ne 1){throw 'Unique controlled message body required'}
   $br=$body[0].Current.BoundingRectangle
   $states=@($all|Where-Object {$_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Text -and $_.Current.Name -in @('Sending…','Failed','Sent') -and $_.Current.BoundingRectangle.Top -ge $br.Bottom -and $_.Current.BoundingRectangle.Top -lt $br.Bottom+110} | Sort-Object {$_.Current.BoundingRectangle.Top})
   if($states.Count -eq 0){throw 'Adjacent actual delivery label absent'}
   $state=$states[0];$sr=$state.Current.BoundingRectangle
   $expect=@{SENDING='Sending…';FAILED='Failed';SENT='Sent'}[$Value]
   if($expect -and -not $state.Current.Name.EndsWith($expect)){throw 'Actual visible delivery state differs from requested checkpoint'}
   $retry=$null
   if($state.Current.Name.EndsWith('Failed')){
    $buttons=@($all|Where-Object {$_.Current.Name -eq 'Retry' -and $_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Button -and $_.Current.BoundingRectangle.Top -ge $br.Bottom -and $_.Current.BoundingRectangle.Top -lt $br.Bottom+110} | Sort-Object {$_.Current.BoundingRectangle.Top})
    if($buttons.Count -eq 0){throw 'Actual adjacent Retry absent'};$retry=$buttons[0]
   }
   $rects=@($br,$sr);if($retry){$rects+=@($retry.Current.BoundingRectangle)}
   $inside=$true;foreach($rect in $rects){if($rect.IsEmpty -or $rect.Left -lt $clip.left -or $rect.Right -gt $clip.right -or $rect.Top -lt $clip.top -or $rect.Bottom -gt $clip.bottom){$inside=$false}}
   $targets+=@{body=$body[0].element;state=$state.element;retry=$(if($retry){$retry.element}else{$null});rects=$rects;inside=$inside;text=$text}
  }
  return @{clip=$clip;targets=$targets;tree=$tree;pane=$panes[0].element}
 }
 for($attempt=0;$attempt -lt 80;$attempt++){
  $g=MessageGeometry
  if(@($g.targets|Where-Object {-not $_.inside}).Count -eq 0){break}
  $target=@($g.targets|Where-Object {-not $_.inside})[0]
  $pattern=$null
  if($g.pane.TryGetCurrentPattern([System.Windows.Automation.ScrollPattern]::Pattern,[ref]$pattern)){
   $amount=if($target.rects[0].Top -lt $g.clip.top){[System.Windows.Automation.ScrollAmount]::LargeDecrement}else{[System.Windows.Automation.ScrollAmount]::LargeIncrement}
   ([System.Windows.Automation.ScrollPattern]$pattern).Scroll([System.Windows.Automation.ScrollAmount]::NoAmount,$amount)
  }else{
   # A real wheel input message targets only the native child under the owned viewport.
   $x=[int](($g.clip.left+$g.clip.right)/2);$y=[int](($g.clip.top+$g.clip.bottom)/2)
   $point=New-Object StateWin+P;$point.x=$x;$point.y=$y;$child=[StateWin]::WindowFromPoint($point)
   if([StateWin]::GetAncestor($child,2).ToInt64() -ne $Hwnd){throw 'Own scroll input point occluded; no input sent'}
   $delta=if($target.rects[0].Top -lt $g.clip.top){480}else{-480};[IntPtr]$reply=[IntPtr]::Zero
   [void][StateWin]::SendMessageTimeout($child,0x020a,[IntPtr]([int64]$delta*65536),[IntPtr]([int64]$x+[int64]$y*65536),2,1000,[ref]$reply)
  }
  Start-Sleep -Milliseconds 80
 }
 $g=MessageGeometry
 if(@($g.targets|Where-Object {-not $_.inside}).Count){
  $diagnostic=@{actualUTC=[DateTime]::UtcNow.ToString('o');clip=$g.clip;targets=@($g.targets|ForEach-Object {@{text=$_.text;inside=$_.inside;rectangles=@($_.rects|ForEach-Object {$_.ToString()})}})}|ConvertTo-Json -Depth 6
  [IO.File]::WriteAllText([IO.Path]::GetFullPath($Output)+'.geometry-fail.json',$diagnostic,(New-Object Text.UTF8Encoding $false))
  throw 'Target body/state/Retry clipped outside actual message pane'
 }
 $monitor=New-Object StateWin+M;$monitor.size=[Runtime.InteropServices.Marshal]::SizeOf($monitor)
 if(-not [StateWin]::GetMonitorInfo([StateWin]::MonitorFromWindow([IntPtr]$Hwnd,2),[ref]$monitor)){throw 'Own monitor physical bounds unavailable'}
 foreach($target in $g.targets){foreach($rect in $target.rects){
  if($rect.Left -lt $monitor.monitor.l -or $rect.Right -gt $monitor.monitor.r -or $rect.Top -lt $monitor.monitor.t -or $rect.Bottom -gt $monitor.monitor.b){throw 'Selected target outside actual physical monitor'}
  $points=@(@(($rect.Left+1),($rect.Top+1)),@(($rect.Right-1),($rect.Top+1)),@(($rect.Left+1),($rect.Bottom-1)),@(($rect.Right-1),($rect.Bottom-1)),@(($rect.Left+$rect.Width/2),($rect.Top+$rect.Height/2)))
  foreach($point in $points){$hit=New-Object StateWin+P;$hit.x=[int]$point[0];$hit.y=[int]$point[1];$hitChild=[StateWin]::WindowFromPoint($hit);$hitRoot=[StateWin]::GetAncestor($hitChild,2);if($hitRoot.ToInt64() -ne $Hwnd){
   [uint32]$hitPid=0;[void][StateWin]::GetWindowThreadProcessId($hitRoot,[ref]$hitPid)
   $diagnostic=@{actualUTC=[DateTime]::UtcNow.ToString('o');targetHwnd=$Hwnd;targetRoot=[StateWin]::GetAncestor([IntPtr]$Hwnd,2).ToInt64();targetPid=$TargetPid;point=@{x=$hit.x;y=$hit.y};hitChild=$hitChild.ToInt64();hitRoot=$hitRoot.ToInt64();hitRootPid=$hitPid;otherWindowTitlesOrContentRead=$false}|ConvertTo-Json
   [IO.File]::WriteAllText([IO.Path]::GetFullPath($Output)+'.occlusion-fail.json',$diagnostic,(New-Object Text.UTF8Encoding $false))
   throw 'Selected target occluded by another native window'
  }}
 }}
 foreach($target in $g.targets){$visibleTargets+=@{text=$target.text;body=$target.body.Current.BoundingRectangle.ToString();state=$target.state.Current.Name;stateBounds=$target.state.Current.BoundingRectangle.ToString();retryBounds=$(if($target.retry){$target.retry.Current.BoundingRectangle.ToString()}else{$null});clip=$g.clip;boundsChecked=$true;physicalMonitorChecked=$true;occlusionChecked=$true;foregroundAtCapture=([StateWin]::GetForegroundWindow().ToInt64() -eq $Hwnd)}}
}elseif($Action -eq 'reach'){
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
}elseif($Action -eq 'click-conversation'){
 $all=$root.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition)
 $matches=@($all|Where-Object {$_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Button -and $_.Current.Name.Contains($Name)})
 if($matches.Count -ne 1 -or -not $matches[0].Current.IsEnabled){throw 'Unique enabled actual fixture conversation required'}
 ([System.Windows.Automation.InvokePattern]$matches[0].GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)).Invoke();Start-Sleep -Milliseconds 700
}elseif($Action -eq 'retry'){
 $b=$root.FindAll([System.Windows.Automation.TreeScope]::Descendants,(New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::NameProperty),$Name));if($b.Count -ne 1){throw 'Unique controlled message body required'}
 $body=$b[0].Current.BoundingRectangle;if($body.IsEmpty){throw 'Current message body geometry unavailable'}
 $choices=$root.FindAll([System.Windows.Automation.TreeScope]::Descendants,(New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::NameProperty),'Retry'))
 $nearest=@($choices | Where-Object {$_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Button -and -not $_.Current.BoundingRectangle.IsEmpty -and $_.Current.BoundingRectangle.Top -ge $body.Bottom} | Sort-Object {$_.Current.BoundingRectangle.Top})
 if($nearest.Count -eq 0){throw 'Current message Retry below body unavailable'};$retry=$nearest[0];if(-not $retry.Current.IsEnabled){throw 'Current controlled Retry disabled'}
 $retry.SetFocus();Start-Sleep -Milliseconds 300;if($retry.Current.IsOffscreen){throw 'Retry remains offscreen'};([System.Windows.Automation.InvokePattern]$retry.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)).Invoke();Start-Sleep -Milliseconds 700
}elseif($Action -eq 'range'){
 $expectedMin=if($Name -eq 'font'){14}else{0.8};$expectedMax=if($Name -eq 'font'){22}else{1.2}
 if($Name -notin @('font','density')){throw 'Only observed appearance controls allowed'}
 $sliders=$root.FindAll([System.Windows.Automation.TreeScope]::Descendants,(New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::ControlTypeProperty),([System.Windows.Automation.ControlType]::Slider)))
 $matching=@($sliders|Where-Object { $rp=[System.Windows.Automation.RangeValuePattern]$_.GetCurrentPattern([System.Windows.Automation.RangeValuePattern]::Pattern);[Math]::Abs($rp.Current.Minimum-$expectedMin) -lt 0.001 -and [Math]::Abs($rp.Current.Maximum-$expectedMax) -lt 0.001})
 if($matching.Count -ne 1){throw 'Unique observed appearance slider required'}
 ([System.Windows.Automation.RangeValuePattern]$matching[0].GetCurrentPattern([System.Windows.Automation.RangeValuePattern]::Pattern)).SetValue([double]$Value)
 Start-Sleep -Milliseconds 700
}elseif($Action -eq 'wait-sync-idle'){
 $clock=[Diagnostics.Stopwatch]::StartNew();$syncWait=$null
 do{
  $idle=$root.FindAll([System.Windows.Automation.TreeScope]::Descendants,(New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::NameProperty),'Up to date'))
  $ready=if($Name){$root.FindAll([System.Windows.Automation.TreeScope]::Descendants,(New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::NameProperty),$Name))}else{$null}
  if($idle.Count -eq 1 -and -not $idle[0].Current.IsOffscreen -and (!$Name -or ($ready.Count -eq 1 -and -not $ready[0].Current.IsOffscreen))){$syncWait=@{observedUTC=[DateTime]::UtcNow.ToString('o');elapsedMilliseconds=$clock.ElapsedMilliseconds;syncHeader='Up to date';requiredConnectionHeader=$Name;pollMilliseconds=40};break}
  Start-Sleep -Milliseconds 40
 }while($clock.ElapsedMilliseconds -lt 30000)
 if(!$syncWait){throw 'Actual visible Sync idle/required connection header not observed within 30s'}
}elseif($Action -ne 'observe'){
 $type=if($Action -eq 'fill'){[System.Windows.Automation.ControlType]::Edit}else{[System.Windows.Automation.ControlType]::Button}
 $condition=New-Object System.Windows.Automation.AndCondition (New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::NameProperty),$Name),(New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::ControlTypeProperty),$type)
 $matches=$root.FindAll([System.Windows.Automation.TreeScope]::Descendants,$condition)
 if($matches.Count -ne 1){throw "Unique observed UI control required: $Name ($($matches.Count))"}
 $n=$matches[0];if(-not $n.Current.IsEnabled){throw 'Observed control disabled'}
 if($Action -eq 'fill'){([System.Windows.Automation.ValuePattern]$n.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)).SetValue($Value)}
 elseif($Action -eq 'click'){
  $invoke=$null;$toggle=$null
  if($n.TryGetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern,[ref]$invoke)){([System.Windows.Automation.InvokePattern]$invoke).Invoke()}
  elseif($n.TryGetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern,[ref]$toggle)){([System.Windows.Automation.TogglePattern]$toggle).Toggle()}
  else{throw 'Actual observed button lacks supported Invoke/Toggle pattern'}
 }
 else{throw 'Unknown actual UI action'}
 Start-Sleep -Milliseconds 700
}
$r=New-Object StateWin+R;[void][StateWin]::GetWindowRect([IntPtr]$Hwnd,[ref]$r)
$bitmap=New-Object System.Drawing.Bitmap ($r.r-$r.l),($r.b-$r.t)
$graphics=[System.Drawing.Graphics]::FromImage($bitmap);$dc=$graphics.GetHdc()
try {if(-not [StateWin]::PrintWindow([IntPtr]$Hwnd,$dc,2)){throw 'PrintWindow failed'}} finally {$graphics.ReleaseHdc($dc);$graphics.Dispose()}
$full=[IO.Path]::GetFullPath($Output);[void][IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($full));$bitmap.Save($full,[System.Drawing.Imaging.ImageFormat]::Png);$bitmap.Dispose()
$root=[System.Windows.Automation.AutomationElement]::FromHandle([IntPtr]$Hwnd)
$all=CachedSnapshot $root
$nodes=@();foreach($n in $all){$c=$n.Current;$nodes+=@{name=$c.Name;type=$c.ControlType.ProgrammaticName;bounds=$c.BoundingRectangle.ToString();enabled=$c.IsEnabled;offscreen=$c.IsOffscreen}}
$result=@{pid=$TargetPid;hwnd=$Hwnd;path=$p.Path;visibleTargets=$visibleTargets;syncWait=$syncWait;capturedUTC=[DateTime]::UtcNow.ToString("o");window=@{left=$r.l;top=$r.t;width=$r.r-$r.l;height=$r.b-$r.t};nodes=$nodes}|ConvertTo-Json -Depth 5

[IO.File]::WriteAllText($full+'.json',$result,(New-Object Text.UTF8Encoding $false)); ($nodes | Where-Object {$_.name}) | ConvertTo-Json -Depth 4
if($Action -eq 'wait-sync-idle' -and (!@($nodes|Where-Object {$_.name -eq 'Up to date' -and -not $_.offscreen}).Count -or ($Name -and !@($nodes|Where-Object {$_.name -eq $Name -and -not $_.offscreen}).Count) -or @($nodes|Where-Object name -eq 'Syncing…').Count)){throw 'Captured actual UIA state changed before strict idle/connection sidecar; original preserved'}
} finally {
 [void][StateWin]::SetWindowPos([IntPtr]$Hwnd,[IntPtr]($(if($originalTopmost){-1}else{-2})),0,0,0,0,19)
 $restoredTopmost=(([UiRefZ]::GetWindowLong([IntPtr]$Hwnd,-20) -band 8) -ne 0)
 [IO.File]::WriteAllText([IO.Path]::GetFullPath($Output)+'.zorder.json',(@{pid=$TargetPid;path=$p.Path;actualUTC=[DateTime]::UtcNow.ToString('o');beforeTopmost=$originalTopmost;temporaryTopmost=$true;afterTopmost=$restoredTopmost;restored=($restoredTopmost -eq $originalTopmost)}|ConvertTo-Json),(New-Object Text.UTF8Encoding $false))
 if($restoredTopmost -ne $originalTopmost){throw 'Owned fixture z-order restoration failed'}
}
