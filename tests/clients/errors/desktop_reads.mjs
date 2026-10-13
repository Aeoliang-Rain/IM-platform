// Literal Tauri invoke boundary controls. No live native/SQLx acceptance claimed.
import assert from "node:assert/strict";
const build=new URL(process.argv[2]??"../../../clients/desktop/dist/",import.meta.url);
const A="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",S="11111111-1111-4111-8111-111111111111",C="cccccccc-cccc-4ccc-8ccc-cccccccccccc";
const known="Storage read open failed",session={userId:A,sessionId:S,sessionEpoch:1n,accessToken:"fixture-only"};
let queryFault=null,hold=null,cursor="0",prefix="0",transactions=0,reads=[];
const row=[S,A,"retained","SENT",S,"1","2026-10-03T00:00:00Z"];
const kind=sql=>sql==="PRAGMA user_version"?"initialize":sql.includes("SELECT cursor")?"cursor":sql.includes("contiguous_seq")?"contiguous":sql.includes("SELECT conversation_id")?"list":"history";
globalThis.window={__TAURI_INTERNALS__:{invoke:async(command,args)=>{
  if(command==="credential_read")return args.slot.endsWith("/current")?`https://localhost/${A}/${S}`:"fixture-refresh";
  if(command==="database_transaction"){transactions++;if(args.statements.some(s=>s[0].startsWith("UPDATE user_cursor SET cursor=?")))cursor="next";return;}
  assert.equal(command,"database_query");const k=kind(args.sql);reads.push(k);
  if(hold && hold.kind===k){const pending=hold;hold=null;await pending.wait;throw pending.error;}
  if(queryFault && queryFault.kind===k){const error=queryFault.error;if(queryFault.once)queryFault=null;throw error;}
  return k==="initialize"?[["2"]]:k==="cursor"?[[cursor]]:k==="contiguous"?[[prefix]]:k==="list"?[[C]]:[row];
}}};
const {Repository}=await import(new URL("shared/protocol-sdk/src/storage/repository.js",build));
const {accountDatabase}=await import(new URL("desktop/src/storage/database.js",build));
const {accountRepository,accountSend}=await import(new URL("desktop/src/application/accountSend.js",build));
const {SendApplication,SendStorageFailure}=await import(new URL("desktop/src/application/send.js",build));
const {SyncApplication}=await import(new URL("desktop/src/application/sync/application.js",build));
const {Workspace}=await import(new URL("desktop/src/application/ui/workspace.js",build));
const repo=()=>accountRepository(A);
function reset(){queryFault=null;hold=null;cursor="0";prefix="0";transactions=0;reads=[];}
function fixture(){const send=new SendApplication(repo(),session);const http={matchesSession:check=>check(session),user:async()=>({syncVersion:"1.0",type:"sync.user.page",events:[],nextCursor:"next",hasMore:false}),conversation:async()=>({messages:[],hasMore:false})};return {send,http,app:new SyncApplication(send,http)};}
for(const target of ["list","history"]){
  reset();const w=new Workspace();await w.updateList(repo(),0);const before=w.state;
  queryFault={kind:target,error:known};await w.updateList(repo(),0);
  assert.equal(w.state.error,"Conversation history unavailable");assert.deepEqual(w.state.conversations,before.conversations);assert.deepEqual(w.state.previews,before.previews);assert.deepEqual(w.state.messages,before.messages);assert.equal(transactions,0);
  queryFault=null;await w.updateList(repo(),0);assert.equal(w.state.previews[C].text,"retained");
}
reset();const offline=new Workspace();offline.offlineRepository=repo();queryFault={kind:"history",error:known};await offline.open(C);assert.equal(offline.state.error,"Sync unavailable; showing local history");assert.equal(transactions,0);
queryFault=null;offline.closeConversation();await offline.open(C);assert.deepEqual(offline.state.messages,[row]);
reset();const restored=new Workspace();queryFault={kind:"list",error:known};await restored.restore("https://localhost");assert.equal(restored.state.error,"Operation unavailable");assert.equal(restored.state.session,null);assert.equal(restored.state.busy,false);assert.equal(transactions,0);assert(reads.includes("initialize"));
for(const error of ["Storage directory unavailable","Storage open failed","Storage close failed",known,"Storage query rejected","Storage result unavailable","Storage result type rejected","Read-only setup failed","Read-only reset failed"]){
  reset();queryFault={kind:"initialize",error};const w=new Workspace();await w.restore("https://localhost");assert.equal(w.state.error,"Operation unavailable");assert.equal(transactions,0);await assert.rejects(accountSend(session),e=>e instanceof SendStorageFailure&&e.cause===error);
}
reset();const bound=new Workspace();queryFault={kind:"list",error:known};await assert.rejects(bound.bind(session,0),e=>e instanceof SendStorageFailure&&e.cause===known);await bound.stop();
reset();const friends=new Workspace();let calls=0;friends.auth={friends:async()=>{calls++;return [{directConversationId:C}];}};queryFault={kind:"cursor",error:known};await friends.refreshFriends(repo(),0);assert.equal(friends.state.error,"Operation unavailable");assert.equal(friends.friendCursor,"");assert.equal(calls,0);queryFault=null;await friends.refreshFriends(repo(),0);assert.equal(calls,1);assert.equal(friends.friendCursor,"0");
for(const target of ["cursor","list","contiguous"]){
  reset();const {app}=fixture();queryFault={kind:target,error:known};const job=app.synchronize();
  await Promise.all([assert.rejects(job,e=>e instanceof SendStorageFailure&&e.cause===known),app.idle()]);
  assert.equal(app.state.status,"failed");assert.equal(app.state.error,"storage");const savedCursor=cursor,savedPrefix=prefix;
  queryFault=null;await app.synchronize();assert.equal(app.state.status,"idle");assert.equal(savedPrefix,"0");if(target==="cursor")assert.equal(savedCursor,"0");await app.close();
}
// Read guards after a successfully committed hasMore page use the same boundary.
for(const target of ["cursor","contiguous"]){
  reset();const {app,http}=fixture();
  if(target==="cursor")http.user=async()=>{queryFault={kind:target,error:known};return {syncVersion:"1.0",type:"sync.user.page",events:[],nextCursor:"next",hasMore:true};};
  else http.conversation=async()=>{queryFault={kind:target,error:known};return {messages:[],hasMore:true};};
  await assert.rejects(app.synchronize(),e=>e instanceof SendStorageFailure&&e.cause===known);await app.idle();assert.equal(app.state.error,"storage");await app.close();
}
const unknowns=[new Error("unrecognized"),new TypeError("unrecognized"),{code:"Storage read open failed"},"unrecognized primitive",42,null];
for(const original of unknowns){
  reset();const w=new Workspace();queryFault={kind:"list",error:original};await assert.rejects(w.updateList(repo(),0),e=>e===original);assert.equal(w.state.error,null);
  const {app}=fixture();queryFault={kind:"cursor",error:original};const job=app.synchronize(),idle=app.idle();await Promise.all([assert.rejects(job,e=>e===original),assert.rejects(idle,e=>e===original)]);assert.equal(app.state.error,null);await assert.rejects(app.close(),e=>e===original);
  for(const operation of ["open","restore","friends","bind","accountSend"]){
    reset();const subject=new Workspace();queryFault={kind:operation==="open"?"history":operation==="friends"?"cursor":operation==="accountSend"?"initialize":"list",error:original};
    subject.offlineRepository=repo();subject.auth={friends:async()=>[]};
    const pending=operation==="open"?subject.open(C):operation==="restore"?subject.restore("https://localhost"):operation==="friends"?subject.refreshFriends(repo(),0):operation==="bind"?subject.bind(session,0):accountSend(session);
    await assert.rejects(pending,e=>e===original);assert.equal(subject.state.error,null);if(operation==="bind")await subject.stop();
  }
}
// Same-code spoof is thrown by consumers, never the actual read boundary.
for(const original of [...unknowns,known]){
  reset();const w=new Workspace();w.observe(()=>{throw original;});await assert.rejects(w.updateList(repo(),0),e=>e===original);assert.equal(w.state.error,null);
  const {app}=fixture();app.observe(s=>{if(s.status==="syncing")throw original;});const job=app.synchronize(),idle=app.idle();await Promise.all([assert.rejects(job,e=>e===original),assert.rejects(idle,e=>e===original)]);assert.equal(app.state.error,null);await assert.rejects(app.close(),e=>e===original);
  const friends=new Workspace();friends.auth={friends:async()=>{throw original;}};await assert.rejects(friends.refreshFriends(repo(),0),e=>e===original);assert.equal(friends.state.error,null);
}
// A retired account may discard only classified known failure; never publish it
// into its replacement and never discard an unknown original.
for(const original of [known,...unknowns]){
  reset();let release;hold={kind:"list",error:original,wait:new Promise(r=>release=r)};const w=new Workspace();const pending=w.updateList(repo(),0);await Promise.resolve();w.generation++;w.state={...w.state,error:"replacement",conversations:[A]};release();
  if(original===known)await pending;else await assert.rejects(pending,e=>e===original);assert.equal(w.state.error,"replacement");assert.deepEqual(w.state.conversations,[A]);
  reset();hold={kind:"cursor",error:original,wait:new Promise(r=>release=r)};const {app}=fixture();const job=app.synchronize();await Promise.resolve();const closing=app.close();release();
  if(original===known)await Promise.all([job,closing]);else await Promise.all([assert.rejects(job,e=>e===original),assert.rejects(closing,e=>e===original)]);assert.equal(app.state.status,"retired");assert.equal(app.state.error,null);assert.equal(transactions,0);
}
console.log("PASS literal native read boundary: list/history/open/restore/bind/friends, Sync initial and continuation reads, known queue recovery, retained state/cursor, unknown identity and same-code observers, retired-account isolation. Controlled invoke only; live SQLx/TLS tested separately.");

// Current SDK protocol/transport faults remain real FAILED at the Sync consumer.
{
 const {SyncHttp}=await import(new URL('shared/protocol-sdk/src/sync/http.js',build));
 const {SyncFailure}=await import(new URL('shared/protocol-sdk/src/sync/wire.js',build));
 for(const mode of ['same-known','distinct-known','protocol-distinct','direct-validation']) {
  reset();let cancelCount=0;const network=new TypeError('controlled network read'),cleanup=new DOMException('controlled cleanup','AbortError');
  const stream=mode==='same-known'?new ReadableStream({start(controller){controller.error(network);}}):new ReadableStream({start(controller){if(mode==='protocol-distinct')controller.enqueue(new Uint8Array([0xff]));if(mode==='direct-validation')controller.enqueue(new Uint8Array(6*1024*1024+1));},cancel(){throw cleanup;}});
  const get=stream.getReader.bind(stream);stream.getReader=()=>{const reader=get(),cancel=reader.cancel.bind(reader);reader.cancel=(...args)=>{cancelCount++;return cancel(...args)};if(mode==='distinct-known')reader.read=async()=>{throw network};return reader;};
  const send=new SendApplication(repo(),session),http=new SyncHttp('https://localhost/',session,async()=>new Response(stream,{headers:{'content-type':'application/json','cache-control':'no-store'}}),()=>S),app=new SyncApplication(send,http);
  const kind=mode==='protocol-distinct'||mode==='direct-validation'?'protocol':'transport';
  await assert.rejects(app.synchronize(),error=>error instanceof SyncFailure&&error.kind===kind);await app.idle();assert.equal(app.state.status,'failed');assert.equal(app.state.error,kind);assert.equal(cancelCount,1);assert.equal(transactions,0);await app.close();
 }
 console.log('PASS current SDK protocol/transport failures stay FAILED; same/distinct/direct validation cleanup runs once without data/cursor writes');
}
