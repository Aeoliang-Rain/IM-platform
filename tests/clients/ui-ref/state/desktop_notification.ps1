param([string]$Output='spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/screens/desktop-native/notification-source547514.json')
$ErrorActionPreference='Stop'
$manager=[Windows.UI.Notifications.ToastNotificationManager,Windows.UI.Notifications,ContentType=WindowsRuntime]
$setting=$manager::CreateToastNotifier('im.platform.desktop').Setting.ToString();if($setting -ne 'Enabled'){throw 'Actual owned native notification setting unavailable'}
$before=@($manager::History.GetHistory('im.platform.desktop')).Length
& powershell -NoProfile -File tests/clients/ui-ref/state/desktop_window.ps1 -Action click -Name ([char]0x2699+' Settings') -Output ($Output+'.settings.png') | Out-Null
if($LASTEXITCODE -ne 0){throw 'Actual Settings action failed'}
& powershell -NoProfile -File tests/clients/ui-ref/state/desktop_window.ps1 -Action click -Name 'Test notification' -Output ($Output+'.actual-ui.png') | Out-Null
if($LASTEXITCODE -ne 0){throw 'Actual notification UI action failed'}
$after=$before;for($i=0;$i -lt 10 -and $after -eq $before;$i++){Start-Sleep -Milliseconds 500;$after=@($manager::History.GetHistory('im.platform.desktop')).Length}
if($after -ne $before+1){throw 'Owned native notification history did not gain exactly one actual notification'}
$metadata=@{AppUserModelId='im.platform.desktop';nativeSetting=$setting;before=$before;after=$after;entry='Actual Test notification UI button; no payload/history from other applications read'}|ConvertTo-Json
[IO.File]::WriteAllText([IO.Path]::GetFullPath($Output),$metadata,(New-Object Text.UTF8Encoding $false));$metadata
