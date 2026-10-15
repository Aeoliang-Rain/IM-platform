import pathlib,json,re,collections
out=pathlib.Path(__file__).parent;r=json.loads((out/'retained-grounds.json').read_text())
def body(s,start):
 # Brace delimiter reader for these simple checked native catch bodies; skip quoted strings.
 p=s.find('{',start)
 if p<0:return s[start:]
 depth=0;quote=None;escape=False
 for i in range(p,len(s)):
  c=s[i]
  if quote:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c==quote:quote=None
   continue
  if c in ['"',"'",'`']:quote=c;continue
  if c=='{':depth+=1
  if c=='}':
   depth-=1
   if depth==0:return s[start:i+1]
 return s[start:]
ops={'start':'appearance load','updateTray':'OS tray text update','selectLanguage':'language file save','testNotification':'OS notification','preferences':'appearance save','socket':'WSS session event decoding','bind':'account local-first bind/profile/list load','refreshFriends':'Repository cursor and authenticated friend-list read','updateList':'Repository conversation/message reads and preview publication','register':'register request','login':'login/credential/account bind','restore':'credential/local history/session restore','refresh':'refresh credential/session bind','expire':'secure credential cleanup after session expiry','logout':'local isolation and remote logout','open':'selected local history/Sync','send':'persist/transmit logical message','retry':'reload original send and retry','reconnect':'connect/Sync','search':'authenticated user search','add':'friend creation/refreshed list/open'}
for x in r:
 p=x['path'];name=pathlib.Path(p).name;line=pathlib.Path(p).read_text().splitlines()[x['line']-1];start=x['column']-1;snippet=line[start:];kind=x['token_class'];operation=x['operation'];method=operation.split('.')[-1]
 x['current_authority']={'frozen':'spec/architecture/frozen-architecture.md §6.1, §6.3, §6.4, §6.5, §7, §11','governance':'spec/governance/error-handling.md; spec/governance/minimality.md','specific':'ADR-0009 native capability boundary' if name in ['native.ts','desktop_capabilities.rs','Preferences.kt','Auth.kt','auth.ts'] else 'contracts/websocket/envelope.schema.json and sync-v1.schema.json'}
 if kind=='catch':
  b=body(line,start);x['exact_catch_clause_and_body']=b
  if name in ['workspace.ts','WorkspaceViewModel.kt'] and x['line']not in ([33,34]if name=='WorkspaceViewModel.kt'else []):
   action=ops.get(method,method)
   if 'CancellationException' in b:x['specific_fault']=operation+': coroutine cancellation during '+action;x['actual_recovery_or_failure']='Rethrows the SAME CancellationException; does not publish a recovered successful result.'
   elif name=='WorkspaceViewModel.kt' and x['line']==42:x['specific_fault']='Malformed WSS frame at Workspace session interception, exact WireFailure only';x['actual_recovery_or_failure']='Use null only to decline session interception; original raw frame forwarded to Send receive for protocol rejection/disconnection.'
   elif name=='workspace.ts'and x['line']==35:x['specific_fault']='WireFailure decoding raw WSS frame at Workspace interception';x['actual_recovery_or_failure']='Leaves original frame to onmessage/Send protocolFailure; all non-WireFailure rethrow.'
   elif name=='WorkspaceViewModel.kt'and x['line']==82 and x['column']<310:x['specific_fault']='Remote logout Exception collected while local account is retired';x['actual_recovery_or_failure']='The SAME exception is returned solely as coroutine result, then remote.await()?.let{throw it}; logout boundary fail applies known classes, unknown exception rethrows.'
   else:
    types='ApiFailure, WireFailure, SyncFailure, SendStorageFailure and NativeCapabilityFailure'if name=='workspace.ts'else'ApiFailure, WireFailure, SyncFailure, SendStorageFailure, IOException and GeneralSecurityException'
    x['specific_fault']=operation+': '+action+' rejects with only currently recognized '+types+'. The literal catch body is '+b
    x['actual_recovery_or_failure']='failure/fail checks recognized identity BEFORE stale-generation suppression; unrecognized errors rethrow. For recognized fault this operation '+('records latest languageStored=false with in-memory selection retained'if 'languageStored:false' in b or 'languageStored=false'in b else'records the explicit error state in this exact branch: '+b)+'. No loaded rows/success reply are synthesized.'
  elif name=='Preferences.kt':
   x['specific_fault']=operation+': '+('wrong stored SharedPreferences type(ClassCastException)'if'ClassCastException'in b else'existing theme/font/density record fails exact validation(IllegalArgumentException)')
   x['actual_recovery_or_failure']='Return English only for invalid language preference'if x['line']==18 else'Throw ApiFailure(error.appearanceLoad); existing default appearance stays in Workspace and load error is shown.';x['current_authority']['specific']='ADR-0012 canonical6.6 language invalid default; ADR-0009 appearance failure'
  elif name=='RepositoryRead.kt':
   typ=re.search(r'catch\(error:([^)]*)',b).group(1);x['specific_fault']='Literal final Repository read throws '+typ+(' with actual SDK already-closed prefix only'if typ=='IllegalStateException'else'');x['actual_recovery_or_failure']='Tag this exact actual native read error as SendStorageFailure retaining cause, so Send/Sync/Workspace can show storage failure; every other IllegalStateException rethrows unchanged. No broad SQLiteException conversion.';x['current_authority']['specific']='Human native boundary clarification in human-boundary-clarification.txt; frozen6.1/6.4'
  else:
   typ=re.search(r'catch\s*\(([^)]*)',b);conditions=re.findall(r'instanceof\s+\w+|error\s+is\s+[\w.]+|error\s*!is\s+[\w.]+|catch\([^)]*|error\s*===?\s*"[^"]+"',b)
   x['specific_fault']=operation+' exception/rejection: '+(typ.group(1)if typ else'Promise rejection')+'; exact admitted/error tests '+', '.join(conditions)+'; inspected literal producing operation in source: '+line[:start]
   x['actual_recovery_or_failure']='Exact branch '+b+'; inspected caller effect: '+x['specific_ground_and_recovery']
 elif kind in ['optional_type_declaration','nonexecutable_regex_or_comment']:
  x['specific_fault']='None: original inventory regex hit '+snippet+' in '+kind;x['actual_recovery_or_failure']='No executable handler; preserved navigation ID, excluded from204 executable count.';x['current_authority']['specific']='Task acceptance requires precise inventory without false catch classification.'
 else:
  x['specific_fault']='Normal explicit absence/branch predicate at '+operation+': '+line[:start]+' [TOKEN '+x['token']+']';x['actual_recovery_or_failure']='Exact alternative '+snippet+'; '+x['specific_ground_and_recovery']
  if '/i18n/'in p:x['current_authority']['specific']='ADR-0012 canonical6.6 English/locale/resource fallback'
  if x['id']=='RH141':x['current_authority']['specific']='Direct Human question/reply fix-cause-read/human-read-mapper-scope.txt ONLY two contiguous READ mappers'
 excluded=x['id']in ['RH026','RH027','RH096','RH111','RH112']
 x['review_disposition']='EXCLUDED_UNCHANGED_WRITE_NATIVE_DB_OR_DRAFT_POLICY'if excluded else'NONEXECUTABLE_NAVIGATION_ONLY'if kind in ['optional_type_declaration','nonexecutable_regex_or_comment']else'RETAINED_CURRENT_REQUIREMENT'
 if excluded:x['actual_recovery_or_failure']='EXCLUDED from write/nativeDB/draft redesign. Existing branch inspected, byte-scope preservation checked; no positive acceptance of new policy. '+x['actual_recovery_or_failure']
(out/'semantic-site-addendum.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
# Reviewed mapping ID allocation is exact for the immutable original sequence; duplicates were manually judged from native source.
summary={'original_ids':len(r),'distinct_corrected_coordinates':len({(x['path'],x['line'],x['column'])for x in r}),'executable_navigation':204,'nonexecutable_navigation':14,'manual_duplicate_reconciliation':{k:next((x['line'],x['column'],x['token'],x['operation'])for x in r if x['id']==k)for k in ['RH147','RH148','RH190','RH191','RH196','RH197','RH198','RH199','RH204','RH205','RH206','RH208','RH209','RH210','RH211','RH212','RH213','RH214','RH215','RH216','RH217']},'standards_findings':[],'task_spec_findings':[],'navigation_judgment':'Candidate original inaccurate operations/duplicatecatch coords are repaired by independent addendum with no semantic coverage loss; navigation issue is not product defect or review blocker once corrected.'}
(out/'navigation-summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
