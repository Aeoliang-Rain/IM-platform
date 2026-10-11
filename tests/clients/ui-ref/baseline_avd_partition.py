"""Narrow partition repair of newly created owned factory fixture, not old AVD."""
from pathlib import Path
import json, hashlib, datetime
root=Path(__file__).resolve().parents[3]
private=Path('C:/Users/21441/.codex/visualizations/2026/10/11/01a129aa-d2ed-7350-8f8d-efb0ecc85664/ui-ref-runtime/baseline-avd')
created=json.loads((root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/baseline-avd-created.json').read_text())
assert Path(created['directory']).resolve()==private.resolve() and created['serial']=='emulator-5592'
config=private/'avds/IMUIRefBaseline34.avd/config.ini'
original=config.read_bytes();backup=private/'config-original-before-byte-size-repair.ini';assert not backup.exists();backup.write_bytes(original)
text=original.decode();assert text.count('disk.dataPartition.size = 6442450944')==1
new=text.replace('disk.dataPartition.size = 6442450944','disk.dataPartition.size = 2146435072').encode();config.write_bytes(new)
sha=lambda b:hashlib.sha256(b).hexdigest()
receipt={'actualUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'config':str(config),'backup':str(backup),'originalSHA256':sha(original),'newSHA256':sha(config.read_bytes()),'changedField':'disk.dataPartition.size','originalValue':'6442450944','newValue':'2146435072','qualification':'Only task-owned new factory userdata size2047MiB in bytes; SDK/API34/image unchanged. Original unknown AVD userdata untouched. Emulator normalized unsupported2047M back to6GiB; prior attempt retained.'}
target=root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/baseline-avd-byte-size-repair.json';assert not target.exists();target.write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS owned factory partition config repair; original config preserved')
