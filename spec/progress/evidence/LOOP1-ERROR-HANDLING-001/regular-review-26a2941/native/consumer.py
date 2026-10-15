from pathlib import Path
import subprocess,hashlib,json
root=Path('H:/.codex/worktrees/err/IM-platform');out=Path(__file__).parent
fixture=out.parent.parent/'regular-review-a292-recovery2/fixture'
proof=[]
for rel in ['clients/desktop/src/application/ui/native.ts','clients/desktop/src/application/ui/workspace.ts']:
 a=(root/rel).read_bytes();b=(fixture/rel).read_bytes();assert a==b
 proof.append({'path':rel,'current_sha256':hashlib.sha256(a).hexdigest(),'oldfixture_equal':True})
proof.append({'compiled_build':str(fixture/'clients/desktop/dist'),'provenance':'Existing locked exact source strict TypeScript build in prior controls.py/controls-history.json; source byte-equivalence newly verified. Not new candidate native runtime.'})
(out/'consumer-binding.json').write_text(json.dumps(proof,indent=2),'utf-8')
p=subprocess.run(['H:/node.js/node.exe',str(out/'appearance-consumer.mjs'),str(fixture/'clients/desktop/dist')],capture_output=True)
(out/'consumer.stdout').write_bytes(p.stdout);(out/'consumer.stderr').write_bytes(p.stderr)
print(p.stdout.decode('utf-8'));print(p.stderr.decode('utf-8'));p.check_returncode()
