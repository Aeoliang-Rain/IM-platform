param([ValidateSet('install','rollback','inspect')][string]$Action)
$ErrorActionPreference='Stop'
$statePrivate='H:/IM-platform/.git/worktrees/IM-platform43/state-runtime'
$stateMeta=Get-Content ($statePrivate+'/tls-state-week2/public.json') -Raw | ConvertFrom-Json
$stateCA=[System.Security.Cryptography.X509Certificates.X509Certificate2]::new($statePrivate+'/tls-state-week2/ca.der')
$stateExpected='727E5D6BB4D072F9A76BFBC8FA81A6159A047D5C'
if($stateCA.Thumbprint -ne $stateExpected -or $stateCA.NotAfter.ToUniversalTime() -le [DateTime]::UtcNow){throw 'New authorized certificate identity/expiry mismatch'}
$stateHash=[BitConverter]::ToString([Security.Cryptography.SHA256]::Create().ComputeHash([IO.File]::ReadAllBytes($statePrivate+'/tls-state-week2/ca.der'))).Replace('-','').ToLower()
if($stateHash -ne 'a8042057db2373aa63b5b46c860c61614ba0e4bd6627f1acd3244dcf22d1c2f5'){throw 'CA hash mismatch'}
$stateStore=[System.Security.Cryptography.X509Certificates.X509Store]::new('Root','CurrentUser')
$stateStore.Open([System.Security.Cryptography.X509Certificates.OpenFlags]::ReadWrite)
try{
 $stateBefore=@($stateStore.Certificates | ForEach-Object Thumbprint | Sort-Object)
 $stateBaseline=$statePrivate+'/windows-root-week2-baseline.json'
 if($Action -eq 'install'){
  if(Test-Path -LiteralPath $stateBaseline){throw 'Baseline already exists'}
  if($stateBefore -contains $stateExpected){throw 'CA collision'}
  ConvertTo-Json -InputObject $stateBefore | Set-Content -LiteralPath $stateBaseline -Encoding utf8
  $stateStore.Add($stateCA)
 }elseif($Action -eq 'rollback'){
  $stateOriginal=[string[]](Get-Content $stateBaseline -Raw | ConvertFrom-Json)
  if($stateOriginal -contains $stateExpected){throw 'Baseline certificate cannot be removed'}
  foreach($stateOwned in @($stateStore.Certificates | Where-Object Thumbprint -eq $stateExpected)){$stateStore.Remove($stateOwned)}
 }
}finally{$stateStore.Close()}
$stateFresh=[System.Security.Cryptography.X509Certificates.X509Store]::new('Root','CurrentUser');$stateFresh.Open([System.Security.Cryptography.X509Certificates.OpenFlags]::ReadOnly)
try{$stateAfter=@($stateFresh.Certificates | ForEach-Object Thumbprint | Sort-Object)}finally{$stateFresh.Close()}
if($Action -eq 'install' -and -not ($stateAfter -contains $stateExpected)){throw 'Standard import did not persist; no security bypass'}
if($Action -eq 'rollback' -and (Compare-Object $stateOriginal $stateAfter)){throw 'Original Root set not restored'}
[pscustomobject]@{action=$Action;ownCertificatePresent=($stateAfter -contains $stateExpected);certificate=$stateExpected;notAfter=$stateCA.NotAfter.ToUniversalTime().ToString('o');scope='CurrentUser Root';baselineCount=$stateBefore.Count;afterCount=$stateAfter.Count} | ConvertTo-Json
