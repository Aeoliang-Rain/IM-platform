$ErrorActionPreference='Stop'
Add-Type -AssemblyName UIAutomationClient,UIAutomationTypes
Add-Type @"
using System;using System.Runtime.InteropServices;
public class UiRefAccess {
 public delegate bool Callback(IntPtr h,IntPtr p);
 [DllImport("user32.dll")]public static extern bool EnumChildWindows(IntPtr h,Callback c,IntPtr p);
 [DllImport("user32.dll")]public static extern IntPtr SendMessageTimeout(IntPtr h,uint m,IntPtr w,IntPtr l,uint f,uint t,out IntPtr r);
 [DllImport("oleacc.dll")]public static extern int AccessibleObjectFromWindow(IntPtr h,uint id,ref Guid iid,[MarshalAs(UnmanagedType.Interface)]out object result);
 public static int Activate(IntPtr h){int count=0;EnumChildWindows(h,delegate(IntPtr child,IntPtr p){IntPtr reply;SendMessageTimeout(child,0x003d,IntPtr.Zero,new IntPtr(-4),2,1000,out reply);SendMessageTimeout(child,0x003d,IntPtr.Zero,new IntPtr(-25),2,1000,out reply);Guid iid=new Guid("618736e0-3c3d-11cf-810c-00aa00389b71");object result;AccessibleObjectFromWindow(child,0xfffffffc,ref iid,out result);if(result!=null&&Marshal.IsComObject(result))Marshal.ReleaseComObject(result);count++;return true;},IntPtr.Zero);return count;}
}
"@
$owned=@(Get-Process im-client-storage -ErrorAction SilentlyContinue|Where-Object Path -eq 'H:\.codex\toolchains\client-gui\installed\im-client-storage.exe')
if($owned.Count -ne 1 -or !$owned[0].MainWindowHandle){throw 'Unique exact owned fixture window required'}
$p=$owned[0];$count=[UiRefAccess]::Activate($p.MainWindowHandle)
Start-Sleep -Milliseconds 1000
$root=[System.Windows.Automation.AutomationElement]::FromHandle($p.MainWindowHandle)
$nodes=$root.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition)
@{actualUTC=[DateTime]::UtcNow.ToString('o');PID=$p.Id;ownedMainWindow=$p.MainWindowHandle.ToInt64();childWindowsRequested=$count;nodeCount=$nodes.Count;method='Standard WM_GETOBJECT/MSAA requests only on children of exact owned native fixture window; no debug flags or business calls';nodes=@($nodes|ForEach-Object {@{name=$_.Current.Name;type=$_.Current.ControlType.ProgrammaticName}})}|ConvertTo-Json -Depth 4
if(!@($nodes|Where-Object {$_.Current.Name -eq 'Username' -and $_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Edit}).Count){throw 'Actual anonymous Username edit not exposed after accessibility request'}
