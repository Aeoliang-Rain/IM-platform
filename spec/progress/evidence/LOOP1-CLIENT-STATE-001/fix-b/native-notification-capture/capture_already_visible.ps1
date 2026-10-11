$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing,System.Windows.Forms,WindowsBase,UIAutomationClient,UIAutomationTypes
Add-Type -Path ($PSScriptRoot+'/notification-native-query.cs')
Add-Type 'using System;using System.Runtime.InteropServices;public static class OwnVisibleNotification{[DllImport("user32.dll")]public static extern bool SetProcessDPIAware();[DllImport("user32.dll")]public static extern IntPtr WindowFromPoint(POINT p);[DllImport("user32.dll")]public static extern IntPtr GetAncestor(IntPtr h,uint f);[StructLayout(LayoutKind.Sequential)]public struct POINT{public int X,Y;public POINT(int x,int y){X=x;Y=y;}}}'
if(-not [OwnVisibleNotification]::SetProcessDPIAware()){throw 'Physical DPI initialization failed'}
$started=[DateTime]::UtcNow;$target=$null;$matches=@();$hostPath=$null
$output='spec/progress/evidence/LOOP1-CLIENT-STATE-001/fix-b/own-os-notification-human-visible.png'
try{
 while(([DateTime]::UtcNow-$started).TotalSeconds -lt 30){
  $matches=@();$queriedMatches=@([OwnSubstringQuery]::Find())
  foreach($match in $queriedMatches){
   if($match['30022']){continue}
   $b=$match['30001'];if($b.Count -ne 4){continue}
   $process=Get-Process -Id ([int]$match['30002'])
   $path=$process.Path
   if($path -ne 'C:\Windows\explorer.exe' -and -not ($path -like 'C:\Windows\SystemApps\*\ShellExperienceHost.exe') -and -not ($path -like 'C:\Windows\SystemApps\*\ShellHost.exe')){continue}
   $matches+=$match
   if($match['30003'] -eq 50007 -and $match['30012'] -eq 'ListViewItem' -and $match['30005'].Contains('IM+') -and $b[2] -ge 300 -and $b[2] -le 800 -and $b[3] -ge 90 -and $b[3] -le 500){
    $target=New-Object System.Windows.Rect $b[0],$b[1],$b[2],$b[3];$hostPath=$path;break
   }
   if($target){break}
  }
  if($target){break};Start-Sleep -Milliseconds 100
 }
 if(-not $target){throw 'No already visible known own OS card exposed; no toggle/trigger performed'}
 $r=$target
 $screen=@([System.Windows.Forms.Screen]::AllScreens|Where-Object {$_.Bounds.Contains([int]$r.Left,[int]$r.Top) -and $_.Bounds.Contains([int]($r.Right-1),[int]($r.Bottom-1))})
 if($screen.Count -ne 1){throw 'Own card must be fully inside one physical monitor'}
 $hitRoots=@()
 foreach($xy in @(@(($r.Left+3),($r.Top+3)),@(($r.Right-3),($r.Top+3)),@(($r.Left+3),($r.Bottom-3)),@(($r.Right-3),($r.Bottom-3)),@(($r.Left+$r.Width/2),($r.Top+$r.Height/2)))){
  $point=New-Object OwnVisibleNotification+POINT ([int]$xy[0]),([int]$xy[1])
  $hitRoots+=([OwnVisibleNotification]::GetAncestor([OwnVisibleNotification]::WindowFromPoint($point),2)).ToInt64()
 }
 if(@($hitRoots|Select-Object -Unique).Count -ne 1 -or $hitRoots[0] -eq 0){throw 'Own OS card is occluded at sampled points'}
 $bitmap=New-Object System.Drawing.Bitmap ([int]$r.Width),([int]$r.Height);$graphics=[System.Drawing.Graphics]::FromImage($bitmap)
 try{$graphics.CopyFromScreen([int]$r.Left,[int]$r.Top,0,0,$bitmap.Size);$bitmap.Save([IO.Path]::GetFullPath($output),[System.Drawing.Imaging.ImageFormat]::Png)}finally{$graphics.Dispose();$bitmap.Dispose()}
 @{capturedUTC=[DateTime]::UtcNow.ToString('o');startedUTC=$started.ToString('o');actualOSSurface=$true;alreadyVisibleOnly=$true;AppUserModelId='im.platform.desktop';AUMIDBinding='notification-own-popup-shortcut.json';ownTitle='IM+';ownBody='Your workspace notifications are ready.';nativeMatchedKnownBody=$matches;OSHostPath=$hostPath;bounds=$r.ToString();sampledHitRootHWND=$hitRoots;theme='OS native';fontSize='OS native';density='OS native';language='en';otherNotificationContentRead=$false;panelToggle=$false;trigger=$false;globalSettingChanged=$false}|ConvertTo-Json -Depth 8|Set-Content -LiteralPath ($output+'.json') -Encoding UTF8
 'PASS actual already-visible own OS card cropped'
}finally{
 @{actualUTC=[DateTime]::UtcNow.ToString('o');startedUTC=$started.ToString('o');knownBodyMatches=$matches;captured=[bool]$target;alreadyVisibleOnly=$true;otherNotificationContentRead=$false;panelToggle=$false;trigger=$false}|ConvertTo-Json -Depth 8|Set-Content -LiteralPath 'spec/progress/evidence/LOOP1-CLIENT-STATE-001/fix-b/notification-already-visible-attempt-native-card.json' -Encoding UTF8
}
