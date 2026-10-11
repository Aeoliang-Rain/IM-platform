param([string]$Output='spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/screens/desktop-native/shortcut-proof.json')
$ErrorActionPreference='Stop'
Add-Type @"
using System;using System.Runtime.InteropServices;public class StateShortcut {
[DllImport("user32.dll")]public static extern bool ShowWindow(IntPtr h,int n);
[DllImport("user32.dll")]public static extern bool IsIconic(IntPtr h);
[DllImport("user32.dll")]public static extern bool IsWindowVisible(IntPtr h);
[DllImport("user32.dll")]public static extern void keybd_event(byte k,byte s,uint flags,UIntPtr extra);
}
"@
$p=@(Get-Process im-client-storage|Where-Object {$_.Path -eq 'H:\.codex\toolchains\client-gui\installed\im-client-storage.exe'})
if($p.Count -ne 1){throw 'Unique owned installed process required'}
$window=$p[0].MainWindowHandle;if($window -eq 0){throw 'Owned actual window unavailable'}
[void][StateShortcut]::ShowWindow($window,6);Start-Sleep -Milliseconds 250
$before=[StateShortcut]::IsIconic($window);if(-not $before){throw 'Owned minimize not observed'}
try{[StateShortcut]::keybd_event(0x11,0,0,[UIntPtr]::Zero);[StateShortcut]::keybd_event(0x10,0,0,[UIntPtr]::Zero);[StateShortcut]::keybd_event(0x20,0,0,[UIntPtr]::Zero)}finally{[StateShortcut]::keybd_event(0x20,0,2,[UIntPtr]::Zero);[StateShortcut]::keybd_event(0x10,0,2,[UIntPtr]::Zero);[StateShortcut]::keybd_event(0x11,0,2,[UIntPtr]::Zero)}
Start-Sleep -Milliseconds 800
$after=[StateShortcut]::IsIconic($window);$visible=[StateShortcut]::IsWindowVisible($window)
$hashStream=[IO.File]::OpenRead($p[0].Path);try{$hash=[BitConverter]::ToString([Security.Cryptography.SHA256]::Create().ComputeHash($hashStream)).Replace('-','')}finally{$hashStream.Dispose()}
$result=@{pid=$p[0].Id;path=$p[0].Path;hwnd=$window.ToInt64();installedSha256=$hash;shortcut='Ctrl+Shift+Space';minimizedBefore=$before;minimizedAfter=$after;visibleAfter=$visible}|ConvertTo-Json
[IO.File]::WriteAllText([IO.Path]::GetFullPath($Output),$result,(New-Object Text.UTF8Encoding $false));$result
if($after -or -not $visible){throw 'Actual global shortcut did not restore owned window'}