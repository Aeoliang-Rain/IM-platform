$ErrorActionPreference='Stop'
$taskRoot='H:\.codex\worktrees\u\IM-platform'
$script=Join-Path $taskRoot 'tests\clients\ui-ref\windows_fixture_trust.ps1'
$receipt='C:\Users\21441\.codex\visualizations\2026\10\11\01a129aa-d2ed-7350-8f8d-efb0ecc85664\windows-trust'
function Digest([string]$path){$h=[Security.Cryptography.SHA256]::Create();try{[BitConverter]::ToString($h.ComputeHash([IO.File]::ReadAllBytes($path))).Replace('-','').ToLowerInvariant()}finally{$h.Dispose()}}
if((Digest $script) -ne 'f2c6dbbda8db82ccf90f97ad0c8eccfedb308054da24e4dccb2d88e9d22d5074'){throw 'Frozen exact rollback script hash mismatch'}
if((Digest (Join-Path $receipt 'root-baseline.json')) -ne 'a23b249ba45e0eec9f736bc47353485dc12592f09d6441902ec08a91c93f4f40'){throw 'Immutable original root baseline hash mismatch'}
$raw=Join-Path $receipt 'elevated-rollback-original.txt'
$result=Join-Path $receipt 'elevated-rollback-exit.json'
if((Test-Path -LiteralPath $raw) -or (Test-Path -LiteralPath $result)){throw 'Never overwrite elevated rollback originals'}
$exitCode=1
try{
 & $script -Action rollback -ReceiptDirectory $receipt *> $raw
 $exitCode=0
}catch{
 $_|Out-String|Add-Content -LiteralPath $raw -Encoding UTF8
}finally{
 [IO.File]::WriteAllText($result,(@{actualUTC=[DateTime]::UtcNow.ToString('o');PID=$PID;exitCode=$exitCode;exactScript=$script;exactScriptSHA256=(Digest $script);baselineSHA256=(Digest (Join-Path $receipt 'root-baseline.json'));authorization='Human permits actual pinned LM/CU temporary lease and automatic exact owned removal';scope='Only exact727E/DERa804, LM then CU, complete original sets compared by frozen script'}|ConvertTo-Json),[Text.UTF8Encoding]::new($false))
}
exit $exitCode
