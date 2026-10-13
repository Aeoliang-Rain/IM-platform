// Actual unchanged SQLx query adapter via private storage_probe; controlled path
// fault only. This is not installed Tauri GUI/OS permission or Go E2E acceptance.
import assert from "node:assert/strict";
import {spawnSync} from "node:child_process";
import {mkdtempSync,writeFileSync,rmSync} from "node:fs";
import {tmpdir} from "node:os";
import {join,resolve} from "node:path";
const build=new URL(process.argv[2]??"../../../clients/desktop/dist/",import.meta.url),probe=resolve(process.argv[3]);
const root=mkdtempSync(join(tmpdir(),"im-error-read-")),blocked=join(root,"controlled-unavailable-directory");writeFileSync(blocked,"owned fault");
const A="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",S="11111111-1111-4111-8111-111111111111",C="cccccccc-cccc-4ccc-8ccc-cccccccccccc";
const session={userId:A,sessionId:S,sessionEpoch:1n,accessToken:"fixture-only"},hex=s=>Buffer.from(s,"utf8").toString("hex"),bind=s=>s===null?"~":hex(s);
let fault="",observed=[];
const kind=sql=>sql==="PRAGMA user_version"?"initialize":sql.includes("SELECT cursor")?"cursor":sql.includes("contiguous_seq")?"contiguous":sql.includes("SELECT conversation_id")?"list":"history";
function call(input,path){const r=spawnSync(probe,[path,A],{input,encoding:"utf8",maxBuffer:10*1024*1024});if(r.error)throw r.error;if(r.status){const error=r.stderr.trim();observed.push(error);throw error;}return r.stdout;}
globalThis.window={__TAURI_INTERNALS__:{invoke:async(command,args)=>{
  if(command==="credential_read")return args.slot.endsWith("/current")?`https://localhost/${A}/${S}`:"fixture-refresh";
  if(command==="database_transaction"){call(args.statements.length?args.statements.map(([sql,binds,changes])=>["T",changes??"-",hex(sql),...binds.map(bind)].join("\t")).join("\n")+"\n":"",root);return;}
  assert.equal(command,"database_query");const raw=call(["Q",hex(args.sql),...args.binds.map(bind)].join("\t")+"\n",kind(args.sql)===fault?blocked:root).trimEnd();return raw?raw.split(/\r?\n/).map(l=>l.split("\t").map(v=>v==="~"?null:Buffer.from(v,"hex").toString("utf8"))):[];
}}};
const {accountRepository}=await import(new URL("desktop/src/application/accountSend.js",build));
const {SendApplication,SendStorageFailure}=await import(new URL("desktop/src/application/send.js",build));
const {SyncApplication}=await import(new URL("desktop/src/application/sync/application.js",build));
const {Workspace}=await import(new URL("desktop/src/application/ui/workspace.js",build));
try{
  const repo=accountRepository(A);await repo.initialize();await repo.localSend({conversationId:C,requestId:S,senderId:A,content:{kind:"TEXT",text:"retained"}});await repo.markFailed(C,S);const before=await repo.messages(C),savedCursor=await repo.cursor(),savedPrefix=await repo.contiguous(C);
  for(const target of ["cursor","list","contiguous"]){
    fault=target;const send=new SendApplication(repo,session),http={matchesSession:check=>check(session),user:async()=>({syncVersion:"1.0",type:"sync.user.page",events:[],nextCursor:savedCursor,hasMore:false}),conversation:async()=>({messages:[],hasMore:false})},app=new SyncApplication(send,http);
    await assert.rejects(app.synchronize(),e=>e instanceof SendStorageFailure&&e.cause==="Storage directory unavailable");await app.idle();assert.equal(app.state.status,"failed");assert.equal(app.state.error,"storage");fault="";await app.synchronize();assert.equal(app.state.status,"idle");await app.close();
    assert.deepEqual(await repo.messages(C),before);assert.equal(await repo.cursor(),savedCursor);assert.equal(await repo.contiguous(C),savedPrefix);
  }
  const w=new Workspace();await w.updateList(repo,0);const previews=w.state.previews;
  for(const target of ["list","history"]){fault=target;await w.updateList(repo,0);assert.equal(w.state.error,"Conversation history unavailable");assert.deepEqual(w.state.previews,previews);}
  w.auth={friends:async()=>{throw new Error("must not request friends after failed native cursor read");}};fault="cursor";await w.refreshFriends(repo,0);assert.equal(w.state.error,"Operation unavailable");assert.equal(w.friendCursor,"");
  const offline=new Workspace();offline.offlineRepository=repo;fault="history";await offline.open(C);assert.equal(offline.state.error,"Sync unavailable; showing local history");fault="";offline.closeConversation();await offline.open(C);assert.deepEqual(offline.state.messages,before);
  fault="initialize";const restored=new Workspace();await restored.restore("https://localhost");assert.equal(restored.state.error,"Operation unavailable");assert.equal(restored.state.busy,false);
  fault="list";const bound=new Workspace();await assert.rejects(bound.bind(session,0),e=>e instanceof SendStorageFailure&&e.cause==="Storage directory unavailable");await bound.stop();
  fault="";assert.deepEqual(await repo.messages(C),before);assert.equal(await repo.cursor(),savedCursor);assert.equal(await repo.contiguous(C),savedPrefix);assert(observed.length>=9);assert(observed.every(e=>e==="Storage directory unavailable"));
  console.log("PASS actual SQLx read-path failure -> query provenance -> Sync failed/recovery and Workspace list/history/friends/offline/initialize errors; original durable data and cursor preserved. Private probe, no installed GUI/Go acceptance claim.");
}finally{rmSync(root,{recursive:true,force:true});}
