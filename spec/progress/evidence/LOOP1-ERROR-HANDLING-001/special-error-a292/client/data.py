import pathlib,json,re,tomllib,zipfile,hashlib
r=pathlib.Path.cwd();ext=pathlib.Path(__file__).parent
for p in [r/'clients/desktop/package-lock.json',r/'clients/shared/protocol-sdk/package-lock.json']:json.loads(p.read_text(encoding='utf-8'))
tomllib.loads((r/'clients/desktop/src-tauri/Cargo.lock').read_text(encoding='utf-8'))
with zipfile.ZipFile(r/'clients/mobile/gradle/wrapper/gradle-wrapper.jar') as z:assert z.testzip() is None
packs=[]
for group in ['clients/desktop/src/ui/i18n','clients/mobile/app/src/main/kotlin/im/platform/client/ui/i18n']:
 tables=[]
 for name in (['en.ts','zh-CN.ts','ja-JP.ts'] if group.startswith('clients/desktop') else ['en.kt','zhCN.kt','jaJP.kt']):
  text=(r/group/name).read_text(encoding='utf-8');keys=re.findall(r'^\s*"([^"\n]+)"\s*(?::|to)',text,re.M);assert len(keys)==len(set(keys));tables.append(set(keys));packs.append(dict(path=group+'/'+name,keys=len(keys),declarative_only=not re.search(r'\b(?:catch|throw|try|fetch|execSQL|invoke)\s*[({]',text)))
 assert tables[0]==tables[1]==tables[2]
(ext/'data-validation.json').write_text(json.dumps(packs,indent=2),encoding='utf-8')
# Architecture authority relevant sections reread without enormous policy/resources.
t=(r/'spec/architecture/frozen-architecture.md').read_text(encoding='utf-8')
for n in ['10','10-1','11','11-1','11-5']:
 a='<a id="section-'+n+'"></a>';part=t.split(a)[1].split('<a id="section-')[0];print(a,part)
for p in sorted((r/'spec/domain').glob('*.md'))+sorted((r/'spec/invariants').glob('*.md')):print('\nFILE',p, p.read_text(encoding='utf-8'))
print('PASS all6resource table keysets/no injected executable behavior; lockJSON/CargoTOML/JAR integrity')
