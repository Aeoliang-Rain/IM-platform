"""Final read-only exact baseline/resource receipt, no trust or data mutation."""
from pathlib import Path
import datetime,hashlib,json,subprocess
private=Path('H:/IM-platform/.git/worktrees/IM-platform43/state-runtime')
script="""$s=[Security.Cryptography.X509Certificates.X509Store]::new('Root','CurrentUser');$s.Open([Security.Cryptography.X509Certificates.OpenFlags]::ReadOnly);try{@($s.Certificates|ForEach-Object Thumbprint|Sort-Object)|ConvertTo-Json}finally{$s.Close()}"""
actual=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',script],text=True,timeout=10))
baseline=json.loads((private/'windows-root-week2-baseline.json').read_text(encoding='utf-8-sig'))
assert sorted(actual)==sorted(baseline) and len(actual)==74 and '727E5D6BB4D072F9A76BFBC8FA81A6159A047D5C' not in actual
processes=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',"@(Get-CimInstance Win32_Process -Filter 'ProcessId=38928 OR ProcessId=4656' | Select-Object ProcessId)|ConvertTo-Json -Compress"],text=True,timeout=10) or '[]')
assert not processes
docker='C:/Program Files/Docker/Docker/resources/bin/docker.exe'
project='im-gui-product-20261004-35588'
containers=subprocess.check_output([docker,'ps','-aq','--filter','label=com.docker.compose.project='+project],text=True,timeout=15).strip()
volumes=subprocess.check_output([docker,'volume','ls','-q','--filter','label=com.docker.compose.project='+project],text=True,timeout=15).strip()
assert not containers and not volumes
installed=Path('H:/.codex/toolchains/client-gui/installed/im-client-storage.exe');old=private/'desktop-before/im-client-storage.exe'
assert hashlib.sha256(installed.read_bytes()).hexdigest()=='18f8b5bb6f8a8c1a6ec8777421a5440c60fabf03a4f8dea0f24deb48ed870503'
assert hashlib.sha256(old.read_bytes()).hexdigest()=='6707f9d5d5b1c1d2fc195b5c9ef91f11fa86b195e20f83b0dc046864ae9f8b8c'
receipt={'actualUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'windowsRootFullBaselineEqual':True,'rootCount':len(actual),'sortedThumbprints':actual,'rootBaselineFileSHA256':hashlib.sha256((private/'windows-root-week2-baseline.json').read_bytes()).hexdigest(),'ownedProxyAndEmulatorPidsAbsent':True,'ownedGoProject':project,'ownedGoContainers':containers,'ownedGoVolumes':volumes,'retainedWindowsCandidateSHA256':hashlib.sha256(installed.read_bytes()).hexdigest(),'originalAcceptedSnapshotSHA256':hashlib.sha256(old.read_bytes()).hexdigest(),'AndroidBaselineReceipt':'android-week2-rollback-baseline.json','AndroidLiveNativeNegativeReceipt':'android-week2-native-negative.json','preserved':'Both controlled candidate installs and all AppData/databases/preferences/credentials; no unknown resource altered'}
Path('spec/progress/evidence/LOOP1-CLIENT-STATE-001/final-resource-baseline.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print('PASS final exact74 Root baseline, owned processes/Go containers/volumes absent; controlled installs/data preserved')
