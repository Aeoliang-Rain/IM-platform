from pathlib import Path
import hashlib,json,subprocess,re,tomllib,zipfile
root=Path('H:/.codex/worktrees/err/IM-platform'); out=Path(__file__).parent
sha='26a2941024c561d711d0d572b82f0f0f7a46d984'; base='35bd6f5f1091503f95a0282f730ed04233b0b6ea'
def git(*a): return subprocess.check_output(['git','-C',str(root),*a])
assert git('rev-parse','HEAD').decode().strip()==sha
assert not git('status','--porcelain').strip()
inventory=json.loads((root/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/fix-outbox-mixed/production-hashes.json').read_text('utf-8'))
nav=json.loads((root/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/fix-outbox-mixed/current-navigation.json').read_text('utf-8'))['records']
def scope(p):return p.startswith('clients/mobile/') or p.startswith('clients/desktop/src-tauri/')
meaning={
'RepositoryRead.kt':'Only literal final Repository reads: five physical SDK SQLite failure types and direct closed-object error acquire cause-preserving SendStorageFailure. Generic SQLiteException/schema errors, invalid mapper content/overflow and callback errors escape unchanged; no SQL/writes here.',
'SendViewModel.kt':'Account-fixed send state. Persist-before-send and SENT terminal use existing Repo writes (excluded). Two direct messages reads use repositoryRead. Network send IOException retires/fails attempt; WireFailure rejects frame; typed storage catch publishes error then rejects operation. Background only known tagged failure is consumed after observable failure. Delivery observers propagate. UUID/text/session/generation/ambiguous RID checks have present ACK/account authority.',
'Wire.kt':'External schema validation: UUID/content/timestamp/positive exact integer/object keys/page consistency/request correlation checks reject malformed wire. Numeric/date conversion catches operate on validated external lexemes. No unknown application callbacks or fake successful page.',
'Wss.kt':'Standard verified TLS/hostname WSS with bounded handshake/frame sizes, masking/client frames, strict UTF8. IOException closes and notifies ended; unknown throwable escapes. Actual production open/message handlers only enqueue Send operations; delivered user callbacks run later outside this IO catch. Absent socket fails explicitly. Close IO on already retired socket does not claim readiness.',
'Https.kt':'HTTPS only, no redirect, Bearer bytes and bounded no-store JSON response. URI/encoding defects reject protocol; SDK IOException rejects transport; cancellation rethrows; unknown Exception identity resumes failure or throws after inactive continuation. Finally disconnects native connection; no fake empty page.',
'SyncViewModel.kt':'Account/session/Repo equivalence, generation cancellation and complete user/conversation pagination. Reads only through repositoryRead, writes through Send merge. 403 unavailable records conversation then continues other authorized conversations. Known auth stops/disconnects; other known failures publish failed and throw; unknown propagates before active-state discard. Enqueue consumes only known failed kinds, not arbitrary exceptions.',
'Auth.kt':'Native HTTPS credential lifecycle with secure refresh slot, generation checks, app-owned metadata. Unknown schema/cast/crypto/state error propagates. Narrow wire/UTF8/IO failures become user-facing API failure; no credentials logged or plaintext fallback. 204 is existing logout no-content contract, not failed request fallback. Credential accept error clears in-memory session and rethrows; refresh expiry cleans session; logout performs local clear then actual remote request.',
'Preferences.kt':'Keystore AES/GCM ciphertext plus AAD slot; credential reads decrypt or fail, commit failure throws, no plaintext downgrade. Appearance invalid/cast is explicit failure. Language missing/invalid/type mismatch defaults en exactly under Frozen6.6/ADR12; failed save remains IOException.',
'WorkspaceViewModel.kt':'Main StateFlow assembly; failure helper checks known ApiFailure/SyncFailure/WireFailure/tagged storage/IO/security before retired-result suppression, unknown rethrows. Literal native read boundary preserves original schema/mapper/observer errors. Async logout retains failure object for await after stop. Account/generation/revision guards discard stale known results; empty list/preview defaults represent legitimate unselected/no-message UI. Search completion only after success. Existing writes/draft handling excluded.',
'Resources.kt':'Pure locale translation mapping: invalid locale/missing localized text falls back English under accepted I18N. Missing English key explicitly fails. Display-only unknown labels map operation/request text without changing stable business state. Absent interpolation retains marker for existing parameter verification.',
'Messages.kt':'Present message identity/body/state invariants fail on null required body, absent both identities and unknown state; local/server identity fallback corresponds persisted model, not fabricated record. Three states map exact translation keys; retry requires failed own request.',
'Friends.kt':'No-match label requires same submitted query, completed successful search, no busy/error and zero result. Failed or edited query cannot imply empty success.',
'desktop_capabilities.rs':'Generic approved native capability adapters only: reqwest verified HTTPS; keyring NoEntry exact absence; native failures return fixed credential-safe Result errors; Windows show/hide/focus now expect failure explicitly. App-owned appearance tuple validated; I18N defaults only missing/invalid/unavailable language enum under ADR12; unknown tray event does no unrelated action. No auth/protocol/Repo/domain ownership.',
'lib.rs':'Tauri root assembly registers generic SQLx read/atomic commands and approved Windows transport/keyring/presentation adapters. Close hides window and failure panics; startup failure expect. TypeScript retains SQL/Repo/transaction/domain/auth intent.',
'database.rs':'Unchanged approved SQLx native adapter; account filename/physically read-only queries, parameter bindings and typed native result errors. Atomic transaction rollback/commit and write failure handling explicitly Human-excluded. No domain models/protocol.',
'storage_probe.rs':'Private validation executable uses same native atomic/query adapter with hex/null transport. Invalid input returns Err, main exits1; optional NULL serializes sentinel, absent expected count is test protocol. Human-excluded native write behavior unchanged.',
'Schema.kt':'Unchanged SDK SQLite schema and migration constants; required identity/state/seq unique/check constraints retained. Writes/schema excluded.',
'Models.kt':'Equivalent Kotlin immutable local/server/committed/user model records; no runtime catch/fallback or invented contract.',
'MainActivity.kt':'Android Compose host mounts Workspace; optional absent native ActionBar is normal platform presentation.',
'Workspace.kt':'Lifecycle-aware collection and locale injection; passes current VM operations into independent Compose shell.',
'Composer.kt':'Existing draft input/send-clear behavior Human-excluded and unchanged; read-only inspected wiring and 4096 limit.',
}
files=[]
for item in inventory:
 p=item['path']
 if not scope(p):continue
 data=(root/p).read_bytes(); digest=hashlib.sha256(data).hexdigest();assert digest==item['sha256'],p
 name=Path(p).name
 reason=meaning.get(name)
 if reason is None:
  if '/components/' in p:reason='Read complete independent Compose presentation: optional selection/profile/navigation/preview values use truthful current-state labels; callbacks wire Workspace actions. No swallowed operation, business state mutation, extra runtime, or fake required message data.'
  elif '/i18n/' in p:reason='Read complete pure multilingual resource map: presentation data only, no runtime control flow, catches or exception classification; stable key/parameter scheme preserved.'
  elif name=='Cargo.lock':
   lock=tomllib.loads(data.decode()); pkg=next(x for x in lock['package'] if x['name']=='im-client-storage');reason='Parsed entire locked dependency graph. Direct package deps '+', '.join(pkg['dependencies'])+' match approved SQLx/Tauri and ADR9 native families; lock bytes unchanged baseline.'
  elif data.startswith(b'\x89PNG') or name.endswith('.ico'):reason='Native product logo/icon binary resource; byte hash and format inspected; no executable fallback/classifier. Unchanged baseline.'
  elif name.endswith('.jar'):
   with zipfile.ZipFile(root/p) as z: assert z.testzip() is None
   reason='Pinned Gradle wrapper binary archive integrity/entries inspected; build resource unchanged baseline, no candidate runtime dependency change.'
  else:reason='Complete build/config/document/launcher read: approved Gradle/Kotlin/Compose or Tauri toolchain, existing whitelist, pinned wrapper checksum, manifest no backup and SDK HTTPS-only app; build/launcher failures return nonzero. No new sensitive technology or product failure fallback.'
 files.append({'path':p,'sha256':digest,'reviewed_sha':sha,'read_method':'complete source read; metadata/binary structural inspection where stated','responsibility_and_semantic_result':reason,'verdict':'NO_FINDING','baseline_equal':git('show',base+':'+p)==data if p!='clients/mobile/app/src/main/kotlin/im/platform/client/send/RepositoryRead.kt' else False})
tokens=[]
for n in nav:
 if not scope(n['path']):continue
 p=n['path'];ln=n.get('current_line',n.get('line'));col=n.get('current_column',n.get('column')); line=(root/p).read_text('utf-8').splitlines()[ln-1]
 token=n['token']; assert line[col-1:col-1+len(token)]==token,(p,ln,col,token)
 fault='At this exact expression '+line.strip()
 authority='Frozen6.1/6.2/6.3/6.4/7/11, ADR5/6/8/9/12, current error-handling governance.'
 result=meaning.get(Path(p).name, next(x['responsibility_and_semantic_result'] for x in files if x['path']==p))
 if not n['executable']:fault='Non-executable comment or regex/declaration syntax at exact coordinate; no fault-handler behavior.';result='Retain syntax; no runtime recovery claim.'
 if Path(p).name in ('database.rs','storage_probe.rs','Composer.kt'):authority='Human exclusion SQLite write/native adapter/drafts; read-only no modification.'
 if Path(p).name=='Repository.kt':fault='Absent query row initializes contiguous0; NULL/noncanonical negative/fraction/overflow present value is invariant violation.';result='Only authorized contiguous read mapper distinguishes absence from corruption. Current check/long conversion explicitly fails; SQL/other bytes unchanged.';authority='Explicit Human two contiguous READ mapper exception; Frozen6.4/SP-I-001; error-handling no fake0.'
 tokens.append({'composite_identity':n.get('composite_identity',n.get('composite_key')),'path':p,'line':ln,'column':col,'token':token,'executable':n['executable'],'source':line,'source_sha256':hashlib.sha256((root/p).read_bytes()).hexdigest(),'specific_fault':fault,'present_authority':authority,'actual_recovery_or_failure':result,'decision':'FRESH_REGULAR_RETAIN_WITH_PRESENT_GROUND','reviewed_sha':sha,'basis':'Independent fullfile/call-chain assessment above; navigation coordinate only, prior verdict not reused.'})
repo='clients/mobile/app/src/main/kotlin/im/platform/client/storage/Repository.kt'; old=git('show',base+':'+repo).decode(); new=(root/repo).read_text('utf-8')
pat=r'    fun contiguous\(c: String\).*?(?=    fun conversationIds)'
assert re.sub(pat,'CONTIGUOUS_READ',old,flags=re.S)==re.sub(pat,'CONTIGUOUS_READ',new,flags=re.S)
sql='SELECT contiguous_seq FROM conversations WHERE conversation_id=?';assert sql in old and sql in new
protected={'mobile_repository_except_contiguous_bytes_equal':True,'contiguous_sql_equal':True,'rust_database_equal_baseline':git('show',base+':clients/desktop/src-tauri/src/database.rs')==(root/'clients/desktop/src-tauri/src/database.rs').read_bytes(),'composer_equal_baseline':git('show',base+':clients/mobile/app/src/main/kotlin/im/platform/client/ui/components/Composer.kt')==(root/'clients/mobile/app/src/main/kotlin/im/platform/client/ui/components/Composer.kt').read_bytes()}
cap='clients/desktop/src-tauri/src/desktop_capabilities.rs'
source=(root/cap).read_text('utf-8').splitlines(); hit=next((i+1,l) for i,l in enumerate(source) if 'pub fn appearance_load' in l)
assert 'if !p.exists(){return Ok(("cold".into(),16,1.0));}' in hit[1]
assert 'std::fs::read(p).map_err(|_|"Appearance unavailable")?' in hit[1]
native=(root/'clients/desktop/src/application/ui/native.ts').read_text('utf-8')
assert '"appearance_load"' in native and 'nativeFailure(error,["Appearance unavailable","Appearance invalid"])' in native
finding={'id':'F-APPEARANCE-EXISTS-DEFAULT','priority':2,'path':cap,'line':hit[0],'source_sha256':hashlib.sha256((root/cap).read_bytes()).hexdigest(),'candidate':sha,'trigger':'Actual app-owned appearance.json path or parent metadata unavailable, e.g. normal Windows filesystem permission denial. appearance_path obtains app_data_dir Path without performing file-access validation. No invented callback or malformed test return is needed.','actual_producer':'std::path::Path::exists performs filesystem metadata query and converts an IO error to false, documented by Rust standard library. This producer receives the actual app-owned path returned by appearance_path.','consumer_effect':'The false result enters missing-file branch returning Ok(cold,16,1). Registered appearance_load IPC feeds TypeScript appearance.load, which destructures successful tuple; nativeFailure and caller error state are bypassed. Existing persisted preference cannot be loaded, but operation reports normal successful defaults.','authority':'Task all current production error audit; spec/governance/error-handling.md forbids normal defaults concealing failures. Frozen6.1/ADR9 authorize app-owned appearance and actual missing defaults; ADR11 unavailable defaults concern Web, ADR12 unavailable defaults concern language; neither approves Desktop appearance IO errors as absent.','minimal_fix':'Read appearance.json once; default only IO ErrorKind::NotFound; project other read failures to existing Appearance unavailable. Preserve tuple serialization/validation and all SQLite/draft bytes. Add focused missing-file vs actual metadata/read error control without changing trust/device/global ACL.','proof_method':'Source-level actual producer/IPC/TS consumer proof plus official OS-independent Rust API documentation; no Windows ACL mutation or fresh native runtime execution. Reachable when filesystem denies metadata on legitimate app-owned file/parent; runtime incidence not measured.','primary_source':'https://doc.rust-lang.org/std/path/struct.Path.html#method.exists','prior_verdict':'No inherited acceptance; earlier NO_FINDING was preliminary before supplemental non-navigation check.'}
for row in files:
 if row['path']==cap:row['verdict']='FAIL';row['finding_ids']=[finding['id']];row['responsibility_and_semantic_result']+=' Supplemental actual metadata default defect F-APPEARANCE-EXISTS-DEFAULT.'
supplement=[{'id':finding['id'],'path':cap,'line':hit[0],'source':hit[1],'decision':'FAIL','basis':finding}]
for name,obj in [('files.json',files),('tokens.json',tokens),('supplemental-boundaries.json',supplement),('findings.json',[finding]),('protected.json',protected)]: (out/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False),'utf-8')
print(json.dumps({'candidate':sha,'file_count':len(files),'navigation_token_count':len(tokens),'executable_tokens':sum(t['executable'] for t in tokens),'supplemental_findings':1,'protected':protected,'result':'FAIL','finding':finding['id'],'independence':'fresh regular review helper only, ineligible specialized sameSHA'}))
