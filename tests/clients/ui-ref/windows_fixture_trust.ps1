param([ValidateSet('inspect','baseline','verify-manual','verify-approved','rollback')][string]$Action='inspect',[Parameter(Mandatory=$true)][string]$ReceiptDirectory,[string]$CertificatePath='H:/IM-platform/.git/worktrees/IM-platform43/state-runtime/tls-state-week2/ca.der')
$ErrorActionPreference='Stop'
$fixtureCertificate=$CertificatePath
$expectedThumbprint='727E5D6BB4D072F9A76BFBC8FA81A6159A047D5C'
$expectedHash='a8042057db2373aa63b5b46c860c61614ba0e4bd6627f1acd3244dcf22d1c2f5'
$certificate=[Security.Cryptography.X509Certificates.X509Certificate2]::new($fixtureCertificate)
function Digest([byte[]]$bytes){[BitConverter]::ToString([Security.Cryptography.SHA256]::Create().ComputeHash($bytes)).Replace('-','').ToLower()}
if($certificate.Thumbprint -ne $expectedThumbprint -or (Digest $certificate.RawData) -ne $expectedHash -or $certificate.NotAfter.ToUniversalTime() -le [DateTime]::UtcNow){throw 'Exact valid fixture certificate required'}
function Snapshot([string]$location){
 $read=[Security.Cryptography.X509Certificates.X509Store]::new('Root',$location);$read.Open([Security.Cryptography.X509Certificates.OpenFlags]::ReadOnly)
 try{@($read.Certificates|ForEach-Object{[pscustomobject]@{thumbprint=$_.Thumbprint;derSHA256=(Digest $_.RawData)}}|Sort-Object thumbprint)}finally{$read.Close()}
}
function Save([string]$name,$value){$file=Join-Path $ReceiptDirectory $name;if(Test-Path -LiteralPath $file){throw 'Never overwrite original trust receipt'};[IO.File]::WriteAllText($file,($value|ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false))}
$userBefore=Snapshot 'CurrentUser';$machineBefore=Snapshot 'LocalMachine'
if($Action -eq 'inspect'){
 [pscustomobject]@{action='inspect';certificatePath=$fixtureCertificate;thumbprint=$expectedThumbprint;derSHA256=$expectedHash;notAfterUTC=$certificate.NotAfter.ToUniversalTime().ToString('o');notBeforeUTC=$certificate.NotBefore.ToUniversalTime().ToString('o');currentUserAlreadyContains=@($userBefore.thumbprint).Contains($expectedThumbprint);machineAlreadyContains=@($machineBefore.thumbprint).Contains($expectedThumbprint);scope='CurrentUser Root only; LocalMachine read-only';mutation='none'}|ConvertTo-Json
 exit
}
New-Item -ItemType Directory -Path $ReceiptDirectory -Force|Out-Null
if($Action -eq 'baseline'){
 if(@($userBefore.thumbprint).Contains($expectedThumbprint)){throw 'Collision: do not own an existing certificate'}
 Save 'root-baseline.json' ([pscustomobject]@{actualUTC=[DateTime]::UtcNow.ToString('o');currentUser=$userBefore;localMachine=$machineBefore;ownedCertificate=$expectedThumbprint;certificateDERHash=$expectedHash})
}elseif($Action -in @('verify-manual','verify-approved')){
 $baseline=Get-Content (Join-Path $ReceiptDirectory 'root-baseline.json') -Raw|ConvertFrom-Json
 if($baseline.ownedCertificate -ne $expectedThumbprint -or @($baseline.currentUser.thumbprint).Contains($expectedThumbprint)){throw 'Manual import baseline mismatch'}
 if(!@($userBefore.thumbprint).Contains($expectedThumbprint)){throw 'Manual certificate import not yet present'}
 $expectedUser=@($baseline.currentUser|ForEach-Object{$_.thumbprint+':'+$_.derSHA256})+@($expectedThumbprint+':'+$expectedHash)
 $actualUser=@($userBefore|ForEach-Object{$_.thumbprint+':'+$_.derSHA256})
 $expectedMachine=@($baseline.localMachine|ForEach-Object{$_.thumbprint+':'+$_.derSHA256});$actualMachine=@($machineBefore|ForEach-Object{$_.thumbprint+':'+$_.derSHA256})
 if($Action -eq 'verify-approved'){$expectedMachine+=@($expectedThumbprint+':'+$expectedHash)}
 if((Compare-Object $expectedUser $actualUser) -or (Compare-Object $expectedMachine $actualMachine)){throw 'Root delta exceeds exact manually imported certificate'}
 Save ('root-'+$Action+'-observed.json') ([pscustomobject]@{actualUTC=[DateTime]::UtcNow.ToString('o');currentUser=$userBefore;localMachine=$machineBefore;ownedCertificate=$expectedThumbprint;method='Human manual import; subsequent explicit Human approval permits exact observed machine/user-view lease and automatic exact owned removal; physical HKCU duplication unknown; import process/command unavailable'})
}else{
 $baseline=Get-Content (Join-Path $ReceiptDirectory 'root-baseline.json') -Raw|ConvertFrom-Json
 if($baseline.ownedCertificate -ne $expectedThumbprint -or $baseline.certificateDERHash -ne $expectedHash -or @($baseline.currentUser.thumbprint).Contains($expectedThumbprint)){throw 'Rollback baseline ownership mismatch'}
 if(@($baseline.localMachine.thumbprint).Contains($expectedThumbprint)){throw 'Rollback cannot own baseline machine certificate'}
 # Remove machine certificate first: CurrentUser can include inherited machine roots.
 foreach($location in @('LocalMachine','CurrentUser')){
  if(!@(Snapshot $location|Where-Object thumbprint -eq $expectedThumbprint).Count){continue}
  $store=[Security.Cryptography.X509Certificates.X509Store]::new('Root',$location);$store.Open([Security.Cryptography.X509Certificates.OpenFlags]::ReadWrite)
  try{foreach($owned in @($store.Certificates|Where-Object Thumbprint -eq $expectedThumbprint)){if((Digest $owned.RawData) -ne $expectedHash){throw 'Owned certificate bytes changed'};$store.Remove($owned)}}finally{$store.Close()}
 }
 $after=Snapshot 'CurrentUser';$machineAfter=Snapshot 'LocalMachine'
 $expectedUser=@($baseline.currentUser|ForEach-Object{$_.thumbprint+':'+$_.derSHA256});$actualUser=@($after|ForEach-Object{$_.thumbprint+':'+$_.derSHA256})
 $expectedMachine=@($baseline.localMachine|ForEach-Object{$_.thumbprint+':'+$_.derSHA256});$actualMachine=@($machineAfter|ForEach-Object{$_.thumbprint+':'+$_.derSHA256})
 if((Compare-Object $expectedUser $actualUser) -or (Compare-Object $expectedMachine $actualMachine)){throw 'Exact full original root set not restored; do not remove other certificates'}
 Save 'root-rollback.json' ([pscustomobject]@{actualUTC=[DateTime]::UtcNow.ToString('o');currentUser=$after;localMachine=$machineAfter;exactFullSetRestored=$true;ownedCertificatePresent=$false})
}
Write-Output ('PASS exact fixture trust '+$Action)
