param([switch]$Exercise,[string]$Output='spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/screens/desktop-native/tray-probe.json')
$ErrorActionPreference='Stop'
Add-Type -AssemblyName UIAutomationClient,UIAutomationTypes,System.Drawing
Add-Type 'using System;using System.Runtime.InteropServices;public class StateTray { [DllImport("user32.dll")]public static extern bool SetProcessDPIAware(); [DllImport("user32.dll",CharSet=CharSet.Unicode)]public static extern IntPtr FindWindow(string cls,string title); }' 
if(-not [StateTray]::SetProcessDPIAware()){throw 'Own tray geometry DPI awareness failed'}
$p=@(Get-Process im-client-storage|Where-Object {$_.Path -eq 'H:\.codex\toolchains\client-gui\installed\im-client-storage.exe'});if($p.Count -ne 1){throw 'Unique installed owner required'}
$name='IM+ '+[char]0x00b7+' Your workspace'
$match=[System.Windows.Automation.AutomationElement]::RootElement.FindFirst([System.Windows.Automation.TreeScope]::Descendants,(New-Object System.Windows.Automation.AndCondition (New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::NameProperty),$name),(New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::ControlTypeProperty),([System.Windows.Automation.ControlType]::Button))))
if($null -eq $match){
 $taskbar=[System.Windows.Automation.AutomationElement]::FromHandle([StateTray]::FindWindow('Shell_TrayWnd',$null))
 $elements=$taskbar.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition)
 $expand=@($elements|Where-Object {$_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Button -and ($_.Current.AutomationId -match 'Chevron' -or $_.Current.Name -match 'hidden|隐藏')})
 if($expand.Count -ne 1){throw ('Unique system tray overflow control required: '+$expand.Count)}
 Write-Output ('Observed overflow: '+$expand[0].Current.Name+' id='+$expand[0].Current.AutomationId)
 ([System.Windows.Automation.InvokePattern]$expand[0].GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)).Invoke();Start-Sleep -Milliseconds 350
 $match=[System.Windows.Automation.AutomationElement]::RootElement.FindFirst([System.Windows.Automation.TreeScope]::Descendants,(New-Object System.Windows.Automation.AndCondition (New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::NameProperty),$name),(New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::ControlTypeProperty),([System.Windows.Automation.ControlType]::Button))))
 if($null -eq $match){throw 'Owned tray tooltip still not exposed after actual overflow'}
}
$c=$match.Current;$result=@{ownedClientPid=$p[0].Id;name=$c.Name;type=$c.ControlType.ProgrammaticName;bounds=$c.BoundingRectangle.ToString();offscreen=$c.IsOffscreen;enabled=$c.IsEnabled;patterns=@($match.GetSupportedPatterns()|ForEach-Object {$_.ProgrammaticName})}|ConvertTo-Json -Depth 4
[IO.File]::WriteAllText([IO.Path]::GetFullPath($Output),$result,(New-Object Text.UTF8Encoding $false));$result
if($Exercise){
 Add-Type 'using System;using System.Runtime.InteropServices;public class StateTrayActions { [StructLayout(LayoutKind.Sequential)]public struct Rect {public int L,T,R,B;}[DllImport("user32.dll")]public static extern bool GetWindowRect(IntPtr h,out Rect r);[DllImport("user32.dll")]public static extern bool PrintWindow(IntPtr h,IntPtr dc,uint f); [StructLayout(LayoutKind.Sequential)]public struct Point {public int X,Y;} [DllImport("user32.dll")]public static extern bool GetCursorPos(out Point p);[DllImport("user32.dll")]public static extern IntPtr WindowFromPoint(Point p);[DllImport("user32.dll")]public static extern uint GetWindowThreadProcessId(IntPtr h,out uint p);[DllImport("user32.dll",CharSet=CharSet.Unicode)]public static extern int GetClassName(IntPtr h,System.Text.StringBuilder s,int n);[DllImport("user32.dll")]public static extern IntPtr FindWindow(string cls,string title); [DllImport("user32.dll")]public static extern bool SetCursorPos(int x,int y);[DllImport("user32.dll")]public static extern void mouse_event(uint f,uint x,uint y,uint d,UIntPtr e);[DllImport("user32.dll")]public static extern bool IsWindowVisible(IntPtr h); }'
 $window=$p[0].MainWindowHandle;if($window -eq 0){throw 'Own client window required'}
 Add-Type -AssemblyName Accessibility
 Add-Type -ReferencedAssemblies ([Accessibility.IAccessible].Assembly.Location) -TypeDefinition 'using System;using System.Runtime.InteropServices;public class StateMenuAccessibility { [DllImport("oleacc.dll")]static extern int AccessibleObjectFromWindow(IntPtr h,uint id,ref Guid iid,out Accessibility.IAccessible a);public static Accessibility.IAccessible Get(IntPtr h){var iid=new Guid("618736E0-3C3D-11CF-810C-00AA00389B71");Accessibility.IAccessible a;Marshal.ThrowExceptionForHR(AccessibleObjectFromWindow(h,0xfffffffc,ref iid,out a));return a;}public static string[] Describe(IntPtr h){var a=Get(h);var lines=new string[a.accChildCount];for(int i=1;i<=lines.Length;i++)lines[i-1]=i+" name="+a.get_accName(i)+" action="+a.get_accDefaultAction(i)+" role="+a.get_accRole(i);return lines;}public static string Invoke(IntPtr h,string name){var a=Get(h);int found=0,count=0;for(int i=1;i<=a.accChildCount;i++)if(a.get_accName(i)==name){found=i;count++;}if(count!=1||Convert.ToInt32(a.get_accRole(found))!=12||(Convert.ToInt32(a.get_accState(found))&1)!=0||a.get_accDefaultAction(found)!="Execute")throw new Exception("Unique observed enabled menu action required");int x,y,w,z;a.accLocation(out x,out y,out w,out z,found);a.accDoDefaultAction(found);return x+","+y+","+w+","+z;} }'
 $results=@()
 foreach($action in @('Hide window','Open IM+')){
  $icon=[System.Windows.Automation.AutomationElement]::RootElement.FindFirst([System.Windows.Automation.TreeScope]::Descendants,(New-Object System.Windows.Automation.AndCondition (New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::NameProperty),$name),(New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::ControlTypeProperty),([System.Windows.Automation.ControlType]::Button))))
  if($null -eq $icon -or $icon.Current.IsOffscreen){
   $taskbar=[System.Windows.Automation.AutomationElement]::FromHandle([StateTray]::FindWindow('Shell_TrayWnd',$null))
   $elements=$taskbar.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition)
   $expand=@($elements|Where-Object {$_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Button -and ($_.Current.AutomationId -match 'Chevron' -or $_.Current.Name -match 'hidden|隐藏')})
   if($expand.Count -ne 1){throw 'Unique actual overflow required'}
   ([System.Windows.Automation.InvokePattern]$expand[0].GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)).Invoke();Start-Sleep -Milliseconds 350
   $icon=[System.Windows.Automation.AutomationElement]::RootElement.FindFirst([System.Windows.Automation.TreeScope]::Descendants,(New-Object System.Windows.Automation.AndCondition (New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::NameProperty),$name),(New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::ControlTypeProperty),([System.Windows.Automation.ControlType]::Button))))
  }
  if($null -eq $icon -or $icon.Current.IsOffscreen){throw 'Actual owned tray icon must be visible'}
  $r=$icon.Current.BoundingRectangle;if($r.IsEmpty){throw 'Own tray bounds missing'}
  if(-not [StateTrayActions]::SetCursorPos([int]($r.X+$r.Width/2),[int]($r.Y+$r.Height/2))){throw 'Own icon pointer positioning failed'}
  $point=New-Object StateTrayActions+Point;[void][StateTrayActions]::GetCursorPos([ref]$point);$hit=[StateTrayActions]::WindowFromPoint($point);[uint32]$hitPid=0;[void][StateTrayActions]::GetWindowThreadProcessId($hit,[ref]$hitPid);$cls=New-Object Text.StringBuilder 256;[void][StateTrayActions]::GetClassName($hit,$cls,256);Write-Output ('Actual pointer '+$point.X+','+$point.Y+' hitClass='+$cls.ToString()+' hitPID='+$hitPid+' iconProviderPID='+$icon.Current.ProcessId)
  if($hitPid -ne $icon.Current.ProcessId){throw 'Actual pointer does not hit observed own tray provider'}
  [StateTrayActions]::mouse_event(8,0,0,0,[UIntPtr]::Zero);[StateTrayActions]::mouse_event(16,0,0,0,[UIntPtr]::Zero);Start-Sleep -Milliseconds 350
  $menu=[StateTrayActions]::FindWindow('#32768',$null);if($menu -ne [IntPtr]::Zero){[uint32]$menuPid=0;[void][StateTrayActions]::GetWindowThreadProcessId($menu,[ref]$menuPid);Write-Output ('Actual native menu HWND='+$menu.ToInt64()+' PID='+$menuPid);if($menuPid -eq $p[0].Id){$menuTree=[System.Windows.Automation.AutomationElement]::FromHandle($menu);$menuNodes=@($menuTree.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition)|ForEach-Object {@{name=$_.Current.Name;type=$_.Current.ControlType.ProgrammaticName;pid=$_.Current.ProcessId;bounds=$_.Current.BoundingRectangle.ToString()}});$menuNodes|ConvertTo-Json -Depth 4|Write-Output}}
  if($menu -ne [IntPtr]::Zero -and $menuPid -eq $p[0].Id){
   [StateMenuAccessibility]::Describe($menu)|Write-Output
   $rect=New-Object StateTrayActions+Rect;if(-not [StateTrayActions]::GetWindowRect($menu,[ref]$rect)){throw 'Own menu bounds unavailable'}
   $image=New-Object Drawing.Bitmap ($rect.R-$rect.L),($rect.B-$rect.T);$graphics=[Drawing.Graphics]::FromImage($image);$dc=$graphics.GetHdc()
   try{if(-not [StateTrayActions]::PrintWindow($menu,$dc,2)){throw 'Own actual menu capture failed'}}finally{$graphics.ReleaseHdc($dc);$graphics.Dispose()}
   try{$image.Save([IO.Path]::GetFullPath($Output+'.menu-'+$action.Replace(' ','-')+'.png'),[Drawing.Imaging.ImageFormat]::Png)}finally{$image.Dispose()}
  }
  $item=[System.Windows.Automation.AutomationElement]::RootElement.FindFirst([System.Windows.Automation.TreeScope]::Descendants,(New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::NameProperty),$action))
  if($null -eq $item){
   if($menu -eq [IntPtr]::Zero -or $menuPid -ne $p[0].Id){throw 'Own actual native popup required'}
   $menuBounds=[StateMenuAccessibility]::Invoke($menu,$action);$entry='actual MSAA accDoDefaultAction'
  }else{
   if($item.Current.ProcessId -ne $p[0].Id -or -not $item.Current.IsEnabled){throw 'Actual menu item owner mismatch'}
   $menuBounds=$item.Current.BoundingRectangle.ToString();([System.Windows.Automation.InvokePattern]$item.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)).Invoke();$entry='actual UIA Invoke'
  }
  Start-Sleep -Milliseconds 500
  $visible=[StateTrayActions]::IsWindowVisible($window);if($visible -ne ($action -eq 'Open IM+')){throw 'Actual tray action window result failed'}
  $results+=@{action=$action;actualEntry=$entry;ownerPid=$p[0].Id;menuBounds=$menuBounds;windowVisibleAfter=$visible}
 }
 $proof=@{clientPid=$p[0].Id;hwnd=$window.ToInt64();actualActions=$results}|ConvertTo-Json -Depth 4
 [IO.File]::WriteAllText([IO.Path]::GetFullPath($Output+'.actions.json'),$proof,(New-Object Text.UTF8Encoding $false));$proof
}
