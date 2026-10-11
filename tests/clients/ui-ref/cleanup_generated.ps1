$ErrorActionPreference='Stop'
$root='H:\.codex\worktrees\u\IM-platform'
if((git rev-parse --show-toplevel).Replace('/','\') -ne $root){throw 'Exact assigned Git root required'}
$private='C:\Users\21441\.codex\visualizations\2026\10\11\01a129aa-d2ed-7350-8f8d-efb0ecc85664\ui-ref-runtime'
$evidence=Join-Path $root 'spec\progress\evidence\LOOP1-CLIENT-UI-REF-001'
$relative=@('clients\web\dist','clients\web\node_modules','clients\desktop\dist','clients\desktop\node_modules','clients\desktop\src-tauri\gen','clients\mobile\app\build','clients\mobile\.gradle','clients\mobile\.kotlin','tests\clients\ui-ref\.runtime\baseline-avd')
$targets=@($relative|ForEach-Object{Join-Path $root $_})
$failed=Join-Path $private 'baseline-avd';$created=Get-Content (Join-Path $evidence 'baseline-avd-created.json') -Raw|ConvertFrom-Json
if([IO.Path]::GetFullPath($created.directory) -ne [IO.Path]::GetFullPath($failed)){throw 'Exact created failed factory path required'}
$targets+=$failed
# Validate every resolved target before any deletion. Do not follow reparse points.
foreach($target in $targets){
 if(!(Test-Path -LiteralPath $target)){continue}
 $resolved=(Resolve-Path -LiteralPath $target).Path
 if($resolved -ne [IO.Path]::GetFullPath($target)){throw 'Resolved target differs from explicit owned path'}
 if($target -ne $failed -and !$resolved.StartsWith($root+'\')){throw 'Generated target outside assigned worktree'}
 if(@(Get-ChildItem -LiteralPath $resolved -Force -Recurse|Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}).Count){throw 'Do not recursively remove linked data'}
 if($target -ne $failed -and (git ls-files -- ($target.Substring($root.Length+1))).Length){throw 'Tracked data cannot be generated cleanup'}
}
function Digest([string]$path){$h=[Security.Cryptography.SHA256]::Create();try{[BitConverter]::ToString($h.ComputeHash([IO.File]::ReadAllBytes($path))).Replace('-','').ToLowerInvariant()}finally{$h.Dispose()}}
$crashes=Join-Path $private 'gradle-crash-originals';if(Test-Path -LiteralPath $crashes){throw 'Never overwrite crash originals'};New-Item -ItemType Directory -Path $crashes|Out-Null
$crashNames=@('hs_err_pid57924.log','hs_err_pid60832.log','replay_pid57924.log','replay_pid60832.log');$archived=@()
foreach($name in $crashNames){$source=Join-Path $root ('clients\mobile\'+$name);if(!(Test-Path -LiteralPath $source)){throw 'Expected owned build crash original missing'};$hash=Digest $source;$destination=Join-Path $crashes $name;Copy-Item -LiteralPath $source -Destination $destination;if((Digest $destination) -ne $hash){throw 'Crash original archive mismatch'};$archived+=@{original=$source;archive=$destination;SHA256=$hash}}
$removed=@()
foreach($target in $targets){$existed=Test-Path -LiteralPath $target;if($existed){Remove-Item -LiteralPath $target -Recurse -Force};if(Test-Path -LiteralPath $target){throw 'Owned generated cleanup incomplete'};$removed+=@{path=$target;existedBefore=$existed;absentAfter=$true}}
foreach($name in $crashNames){Remove-Item -LiteralPath (Join-Path $root ('clients\mobile\'+$name))}
$output=Join-Path $evidence 'generated-cleanup.json';if(Test-Path -LiteralPath $output){throw 'Never overwrite cleanup receipt'}
[IO.File]::WriteAllText($output,(@{actualUTC=[DateTime]::UtcNow.ToString('o');actualHEAD=(git rev-parse HEAD);removed=$removed;privateCrashArchives=$archived;qualification='Only new task-owned generated build/runtime directories and archived crash files removed; explicit resolved roots checked first, no tracked files/reparse points, no original AVD/unknown userdata or credential content copied.'}|ConvertTo-Json -Depth 5),[Text.UTF8Encoding]::new($false))
Write-Output 'PASS exact owned generated directories and archived crash files cleaned'
