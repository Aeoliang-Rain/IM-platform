from pathlib import Path
import json,hashlib,subprocess,struct,zipfile,re
r=Path('H:/.codex/worktrees/err/IM-platform');o=Path('C:/Users/21441/.codex/visualizations/2026/10/13/01a1341c-f5bd-7a20-8d63-e5a574250f3c/regular-review-b5ea135/mobile');sha=lambda b:hashlib.sha256(b).hexdigest();d=json.loads((r/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/production-inventory.json').read_text());a=json.loads((o/'report.json').read_text(encoding='utf8'))
for f in a['files']:
 b=(r/f['path']).read_bytes();orig=next(x for x in d['files'] if x['path']==f['path']);f['sha256']=sha(b);f['inventory_hash_matches']=sha(b)==orig['sha256'];base=subprocess.check_output(['git','show','35bd6f5f1091503f95a0282f730ed04233b0b6ea:'+f['path']],cwd=r,stderr=subprocess.DEVNULL) if f['path']!='clients/mobile/app/src/main/kotlin/im/platform/client/send/RepositoryRead.kt' else None;f['baseline_unchanged']=base is not None and base.replace(b'\r\n',b'\n')==b.replace(b'\r\n',b'\n')
for s in a['retained_sites']:s['input_sha256']=sha((r/s['path']).read_bytes())
# Declarative language maps have no executable function/import behavior beyond map declarations.
loc={}
for name in ['en','zhCN','jaJP']:
 p=r/('clients/mobile/app/src/main/kotlin/im/platform/client/ui/i18n/'+name+'.kt');t=p.read_text(encoding='utf8');keys=re.findall(r'^\s*"([^"\n]+)" to ',t,re.M);loc[name]=keys;print(name,len(keys),'duplicates',len(keys)-len(set(keys)))
assert set(loc['en'])==set(loc['zhCN'])==set(loc['jaJP'])
b=(r/'clients/mobile/app/src/main/res/drawable/project_logo.png').read_bytes();print('PNG',b[:8].hex(),struct.unpack('>II',b[16:24]));assert b[:8]==b'\x89PNG\r\n\x1a\n'
with zipfile.ZipFile(r/'clients/mobile/gradle/wrapper/gradle-wrapper.jar') as z:print('JAR entries',len(z.namelist()),'wrapper',any(x.endswith('GradleWrapperMain.class') for x in z.namelist()))
print('missing hash', [f['path'] for f in a['files'] if not f['inventory_hash_matches']])
# Evidence blobs located external immutable implementation run.
h=a['runtime_review']['commands'];roots=[Path('C:/Users/21441/.codex/visualizations/2026/10/13/01a1341c-f5bd-7a20-8d63-e5a574250f3c/fix-send-cleanup')]
for c in h:
 for root in roots:
  matches=list(root.rglob(Path(c['stdout_blob']).name))
  for p in matches:
   b=p.read_bytes();print(c['command_id'],p,sha(b)==c['stdout_sha256']);print(b.decode('utf8')[-2500:])
(o/'report.json').write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf8')
