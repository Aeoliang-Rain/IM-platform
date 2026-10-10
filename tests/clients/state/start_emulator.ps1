$ErrorActionPreference='Stop'
$stateRuntime='H:/IM-platform/.git/worktrees/IM-platform43/state-runtime'
$stateAdb='H:/Android/platform-tools/adb.exe'
$stateExisting=& $stateAdb devices -l
if($stateExisting -match 'emulator-'){throw 'Existing emulator requires owner lease'}
$env:ANDROID_USER_HOME='H:/IM-platform/.git/worktrees/IM-platform4/send-runtime/android-user'
$env:ANDROID_AVD_HOME='H:/IM-platform/.git/worktrees/IM-platform4/send-runtime/avd-home'
$stateProcess=Start-Process -FilePath H:/Android/emulator/emulator.exe -ArgumentList @('-avd','IMClientSend34','-port','5590','-memory','2048','-gpu','swiftshader_indirect','-no-snapshot-load','-no-snapshot-save','-no-window','-no-audio') -WindowStyle Hidden -RedirectStandardOutput ($stateRuntime+'/emulator.stdout.txt') -RedirectStandardError ($stateRuntime+'/emulator.stderr.txt') -PassThru
$stateProcess.Id | Set-Content -LiteralPath ($stateRuntime+'/emulator.pid')
Write-Output ('Started owned IMClientSend34 process '+$stateProcess.Id+'; no wipe; no snapshots')
