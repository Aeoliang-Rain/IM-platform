$ErrorActionPreference='Stop'
Add-Type -AssemblyName UIAutomationClient,UIAutomationTypes
Add-Type 'using System;using System.Runtime.InteropServices;public class StateCertConfirm { [StructLayout(LayoutKind.Sequential)]public struct Point {public int X,Y;}[DllImport("user32.dll")]public static extern bool SetProcessDPIAware();[DllImport("user32.dll")]public static extern uint GetWindowThreadProcessId(IntPtr h,out uint p);[DllImport("user32.dll")]public static extern bool SetCursorPos(int x,int y);[DllImport("user32.dll")]public static extern IntPtr WindowFromPoint(Point p);[DllImport("user32.dll")]public static extern void mouse_event(uint f,uint x,uint y,uint d,UIntPtr e);}'
if(-not [StateCertConfirm]::SetProcessDPIAware()){throw 'Own confirmation geometry DPI failed'}
$process=Get-Process -Id 57324;if($process.Path -ne 'C:\WINDOWS\SYSTEM32\certutil.exe'){throw 'Own exact removal process changed'}
$hwnd=[IntPtr]16452796;[uint32]$owner=0;[void][StateCertConfirm]::GetWindowThreadProcessId($hwnd,[ref]$owner);if($owner -ne 57324){throw 'Removal confirmation window owner changed'}
$root=[Windows.Automation.AutomationElement]::FromHandle($hwnd);$all=$root.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)
$text=($all|ForEach-Object {$_.Current.Name}) -join "`n";$compact=[regex]::Replace($text,'\s','')
if(-not $compact.Contains('727E5D6BB4D072F9A76BFBC8FA81A6159A047D5C') -or -not $text.Contains('IM STATE owned fixture 20261010') -or -not $text.Contains(([char]0x5220).ToString()+[char]0x9664)){throw 'Actual confirmation is not the exact approved Root certificate deletion'}
$yes=@($all|Where-Object {$_.Current.Name -eq ([char]0x662f+'(Y)')});if($yes.Count -ne 1 -or -not $yes[0].Current.IsEnabled){throw 'Actual observed confirmation control required'}
$r=$yes[0].Current.BoundingRectangle;$point=New-Object StateCertConfirm+Point;$point.X=[int]($r.X+$r.Width/2);$point.Y=[int]($r.Y+$r.Height/2)
[uint32]$hitOwner=0;[void][StateCertConfirm]::GetWindowThreadProcessId([StateCertConfirm]::WindowFromPoint($point),[ref]$hitOwner);if($hitOwner -ne 57324){throw 'Observed confirmation click target owner mismatch'}
if(-not [StateCertConfirm]::SetCursorPos($point.X,$point.Y)){throw 'Confirmation pointer failed'}
[StateCertConfirm]::mouse_event(2,0,0,0,[UIntPtr]::Zero);[StateCertConfirm]::mouse_event(4,0,0,0,[UIntPtr]::Zero)
@{kind='Actual Windows standard confirmation for already-approved exact Root deletion';pid=57324;hwnd=16452796;thumbprint='727E5D6BB4D072F9A76BFBC8FA81A6159A047D5C';actualText=$text;buttonBounds=$r.ToString();entry='Actual pointer click on reread observed enabled Yes control, owned window/pointer checked';storeRollbackResult='Pending independent post-action store baseline check'}|ConvertTo-Json|Set-Content spec/progress/evidence/LOOP1-CLIENT-STATE-001/windows-week2-removal-confirmation.json -Encoding utf8
