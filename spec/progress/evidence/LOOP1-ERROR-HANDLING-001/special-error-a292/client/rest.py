import pathlib,json,hashlib,subprocess,re
r=pathlib.Path.cwd();ext=pathlib.Path(__file__).parent
i=json.loads((r/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/production-inventory.json').read_text(encoding='utf-8')); fs=[f for f in i['files'] if f['path'].startswith(('clients/shared/','clients/desktop/','clients/mobile/'))]
readparts=['protocol-sdk/src','desktop/src/application','desktop/src-tauri/src','client/send','client/sync','client/ui/WorkspaceViewModel.kt','client/ui/Auth.kt','client/ui/Preferences.kt','desktop/src/ui/components','client/ui/components','i18n/resources.ts','i18n/Resources.kt','client/storage']
for f in fs:
 p=f['path'];b=(r/p).read_bytes()
 if any(x in p for x in readparts):continue
 print('\nFILE',p)
 if b'\0' in b:print('BINARY header',b[:24].hex(),'bytes',len(b));continue
 text=b.decode('utf-8')
 if p.endswith(('package-lock.json','Cargo.lock')):
  print('Lock fully parsed/version identifiers; no executable error handling. Headers',text[:200]);continue
 for n,l in enumerate(text.splitlines(),1):print(f'{n}: {l}')
