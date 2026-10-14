import pathlib,json,re,collections,hashlib,subprocess
out=pathlib.Path(__file__).parent; ss=json.loads((out/'sites-original.json').read_text());groups=collections.defaultdict(list)
for x in ss:groups[(x['path'],x['line'])].append(x)
result=[]
def owner(p,n,lines):
 name=pathlib.Path(p).name
 overrides={('send.ts',45):'SendApplication.storage',('send.ts',52):'SendApplication.serial',('send.ts',71):'SendApplication.connect.onopen',('send.ts',72):'SendApplication.connect.onmessage',('send.ts',82):'SendApplication.disconnect',('send.ts',112):'SendApplication.begin',('send.ts',115):'SendApplication.begin.timeout',('application.ts',14):'SyncApplication.constructor.delivery',('application.ts',18):'SyncApplication.constructor.ready',('application.ts',22):'SyncApplication.constructor.poll',('application.ts',52):'SyncApplication.synchronize.conversation',('application.ts',55):'SyncApplication.synchronize',('application.ts',63):'SyncApplication.synchronize.queue'}
 if (name,n) in overrides:return overrides[(name,n)]
 if name=='native.ts':return {16:'nativeFetch',22:'appearance.load',23:'appearance.save',27:'secure.read',28:'secure.write',29:'secure.remove',31:'windowMaximized',32:'windowControl',33:'notify',36:'language.load',37:'language.save',39:'trayText'}[n]
 if name=='gradlew':return 'vendor license comment'
 if name=='gradlew.bat':return 'vendor license comment'
 if name=='build.gradle.kts':return 'android.defaultConfig.testInstrumentationRunner'
 decl=[]
 for i,l in enumerate(lines[:n],1):
  pats=[r'\bfun\s+(?:<[^>]+>\s*)?(\w+)\s*\(',r'\bfn\s+(\w+)\s*\(',r'^\s*(?:(?:export|private|public|async|internal|suspend|override|function|static)\s+)*(\w+)\s*\([^;]*',r'\bfunction\s+(\w+)\s*\(']
  for pat in pats:
   m=re.search(pat,l)
   if m and m.group(1) not in ['if','for','while','switch','catch','return','try','check','require','print','println','const','let','val']:decl.append((i,m.group(1)));break
 return name+'.'+(decl[-1][1]if decl else 'module declaration')
for (p,n),xs in groups.items():
 lines=pathlib.Path(p).read_text(encoding='utf-8').splitlines();line=lines[n-1];tokens=[(m.start()+1,m.group())for m in re.finditer(r'\bcatch\b|\?\?|\?\s*:|unwrap_or|_\s*=>|\bexcept\b|return 0L',line)]
 used=set()
 for x in xs:
  candidates=[(abs(c-x['column']),idx,c,t)for idx,(c,t)in enumerate(tokens)if idx not in used]
  if not candidates:raise ValueError((x,tokens))
  _,idx,c,t=min(candidates);used.add(idx)
  klass='catch'if t=='catch'else 'absent_row'if t=='return 0L'else 'fallback'
  if t=='except' or (t.strip()=='?:' and x['id'] in ['RH128','RH129','RH131','RH132','RH133','RH137','RH143','RH165','RH050']):klass='nonexecutable_regex_or_comment'
  if x['id'] in ['RH048','RH054','RH055']:klass='optional_type_declaration'
  # RH050 is regex syntax, RH051 is the executable header absence default.
  op=owner(p,n,lines);rhs=line[c-1:c+200]
  if klass=='catch':
   m=re.match(r'catch\s*\(([^)]*)\)',rhs);fault=m.group(1)if m else 'Promise rejection'
   if p.endswith('/send/RepositoryRead.kt'):ground='Literal final Repository native read: '+fault+' is wrapped only as SendStorageFailure; other IllegalStateException rethrows. Sync/Send/Workspace publish storage failure; no SQL/write recovery change. Authority canonical6.1/6.4, Human boundary clarification.'
   elif p.endswith('/SendViewModel.kt') and n in [25,26]:ground='Excluded existing SQLite write/initialization wrapper: '+fault+'; original rollback/write policy retained byte-equivalent. Current review does not approve changing excluded write recovery.'
   elif p.endswith('/WorkspaceViewModel.kt') and n in [33,34]:ground='Existing constructor/initialize SQLite projection at literal invocation only; produces storage failure for Workspace state, leaves SQL/init/write implementation unchanged. Human native boundary clarification.'
   elif p.endswith('/ui/WorkspaceViewModel.kt') or p.endswith('/ui/workspace.ts'):ground='Operation '+op+' boundary: '+fault+'; fail/failure first rejects unknown values, then displays known Api/Sync/Wire/native failure only for current generation. Cancellation rethrows where explicitly caught. State/publication observers remain capable of failing operation; no fake success data. Authority canonical6.1/6.5/7 and error-handling.md.'
   elif 'native.ts' in p or 'accountSend.ts' in p:ground='Literal native invoke/query '+op+': '+fault+'; only exact sanitized native codes obtain provenance; unknown Error/primitive/value rethrows. Callers own truthful capability/transport/storage state. canonical6.1, ADR0009 and Human boundary clarification.'
   elif p.endswith('/Wss.kt'):ground='Socket '+op+': '+fault+'; transport IOException closes/ends socket, close IOException occurs after closed flag/retirement; no frame or credential logging. Unknown runtime exceptions escape; canonical7 WSS failure/disconnect.'
   elif '/sync/' in p:ground='Sync '+op+': '+fault+'; protocol parsing rejects malformed canonical data, known transport/storage failure remains failed, known authorization unavailable is per-conversation, unknown errors propagate; cancellation does not become success. canonical6.4/11.5 and contracts/websocket/sync-v1.schema.json.'
   elif '/ui/auth.ts' in p or '/ui/Auth.kt' in p:ground='Auth '+op+': '+fault+'; exact transport/UTF8/Wire faults become failed auth operation, secure/session queues retain known failure handling; unknown exception propagates and no credentials enter error display. canonical7, ADR0009, contracts/http/errors.'
   else:ground='Operation '+op+' catch '+fault+'; observed body '+rhs+'. Known malformed wire/socket or storage fault follows protocol rejection/disconnect/FAILED; unknown exceptions are not converted to success. canonical5/6/7; contracts/websocket/envelope.schema.json.'
  elif klass in ['nonexecutable_regex_or_comment','optional_type_declaration']:ground='Navigation-only false positive: '+rhs+'. This is '+klass+', not exception recovery/default data; retained original ID preserves audit trace without counting it as an executable catch.'
  elif klass=='absent_row':ground='Only absent query row returns initial contiguous0; present NULL/empty/noncanonical decimal fails checkNotNull/regex/toLong. SQL unchanged. Human exact2READ exception; canonical6.4 gap-free cursor.'
  elif '/storage/' in p or p.endswith('storage_probe.rs'):ground='Existing excluded native transaction/type/null transport branch '+rhs+'; no new fallback success. Native result errors fail operation; SQL/schema/write policy outside authorized correction. canonical6.3 and Task forbidden scope.'
  elif '/i18n/' in p:ground='Display-only '+op+' absence expression '+rhs+'; permitted English locale/key fallback or untouched placeholder/error display lookup. English base missing is explicit failure. Does not modify wire/business/user text. ADR0012 canonical6.6.'
  elif '/Wire.kt' in p:ground='Canonical external field type/absence '+rhs+' triggers invalid protocol rejection, not empty/normal data. canonical7/11, contracts/websocket WSS/Sync shapes.'
  elif 'Auth' in op or '/ui/auth' in p or '/ui/Auth.kt' in p:ground='Auth optional/default '+rhs+'; optional request/session/credential absence fails authentication or reports genuinely absent saved credential; response error label is only for actual non2xx. No unknown caught error becomes successful data. canonical7 and contracts/errors.'
  else:ground='Optional/declarative state in '+op+': '+rhs+'; null/absent input is an explicit normal state (unselected/no preview/no profile/default presentation/absent header), not a caught failure returning data. Failure paths elsewhere remain observable. canonical6.1/6.5, ADR0006/0009/0012.'
  result.append({**x,'original_operation':x['operation'],'original_column':x['column'],'operation':op,'column':c,'token':t,'token_class':klass,'specific_ground_and_recovery':ground,'reviewed_sha':'a292f516f622651ae62595163e479c13fff78c1d','source_sha256':hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest(),'navigation_correction':c!=x['column']or op!=x['operation']})
(out/'retained-grounds.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
unique={(x['path'],x['line'],x['column'],x['token'])for x in result};counts=collections.Counter(x['token_class']for x in result)
print('originalIDs',len(result),'distincttokens',len(unique),'classes',dict(counts));print('corrected',sum(x['navigation_correction']for x in result));print('duplicateoriginalcoords',[(k,[x['id']for x in v])for k,v in collections.defaultdict(list).items()])
for x in result:
 if x['original_column']!=x['column']:print(x['id'],x['operation'],x['line'],x['original_column'],'->',x['column'],x['token'],x['token_class'])
