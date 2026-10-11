"""Assemble a post-capture index without rewriting any captured original."""
from pathlib import Path
import subprocess, json, hashlib, datetime, sys, os
root = Path(__file__).resolve().parents[3]
out = root / 'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/screens' / sys.argv[1]
assert out.resolve().parent == (root / 'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/screens').resolve()
raw = (out / 'instrumentation-original.txt').read_text(encoding='utf-8')
assert 'INSTRUMENTATION_RESULT: result=PASS' in raw and 'testTrustRestore=PASS' in raw
proofs = json.loads((out / 'proofs.json').read_text())
assert proofs['newMessageDeliveryEvents'] == 0
binding = json.loads(subprocess.check_output(['node', '--input-type=module', '-e', "import {actualBinding} from './tests/clients/ui-ref/state/android_binding.mjs'; console.log(JSON.stringify(await actualBinding()))"], cwd=root, env=os.environ.copy(), text=True))
after = out / 'source-install-binding-after.json'
assert not after.exists()
after.write_text(json.dumps(binding, indent=2) + '\n', encoding='utf-8')
entries = [{'file': str(p.relative_to(out)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.rglob('*')) if p.is_file()]
target = out / 'manifest.json'
assert not target.exists()
target.write_text(json.dumps({'result': 'PASS', 'task_id': 'LOOP1-CLIENT-UI-REF-001', 'assembledUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'assemblyQualification': 'Post-capture hash index of unchanged originals; actual capture states/times/HEAD are retained in original PNG sidecars and before-install binding.', 'fixture': proofs['fixture'], 'androidBindingAfter': binding, 'windowsTrustQualification': 'Human manually imported exact pinned fixture CA; actual machine/user-view temporary lease approved, cleanup remains separately required.', 'entries': entries}, indent=2) + '\n', encoding='utf-8')
print('PASS full Friends original index:', target)
