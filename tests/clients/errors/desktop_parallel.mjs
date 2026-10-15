import assert from 'node:assert/strict';
const build=new URL(process.argv[2]??'../../../clients/desktop/dist/',import.meta.url);
const {Auth,ApiFailure}=await import(new URL('desktop/src/application/ui/auth.js',build));
const {Workspace}=await import(new URL('desktop/src/application/ui/workspace.js',build));
const {NativeCapabilityFailure}=await import(new URL('desktop/src/application/ui/native.js',build));
const {SendStorageFailure}=await import(new URL('desktop/src/application/send.js',build));
const {accountRepository}=await import(new URL('desktop/src/application/accountSend.js',build));
const tick=()=>new Promise(resolve=>setImmediate(resolve));
const A='11111111-1111-4111-8111-111111111111',B='33333333-3333-4333-8333-333333333333',S='22222222-2222-4222-8222-222222222222',C='44444444-4444-4444-8444-444444444444';
const session={userId:A,sessionId:S,sessionEpoch:1n,accessToken:'public-controlled-fixture'};
const unhandled=[];const handler=e=>unhandled.push(e);process.on('unhandledRejection',handler);let checks=0;
function roots(value){const seen=new Set(),active=new Set();function walk(e){assert(!active.has(e),'cyclic root graph');active.add(e);if(!seen.has(e)){seen.add(e);if(e instanceof Error){if(e.cause!==undefined)walk(e.cause);if(e instanceof AggregateError)e.errors.forEach(walk);}}active.delete(e);}walk(value);return seen;}
function pending(){let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b});return {promise,resolve,reject};}
function owner(){const a=new Auth('https://fixture.invalid');a.session=session;a.slot=a.endpoint+'/'+A+'/'+S;return a;}
async function logoutCase(name,remote,cleanup,first,consumer=false,same=false){
 const r=pending(),c=pending();const calls=[];globalThis.window={__TAURI_INTERNALS__:{invoke:async(command,args)=>{calls.push([command,args]);if(command==='native_https')return r.promise;if(command==='credential_remove'){await c.promise;return;}throw Error('unexpected '+command);}}};
 const auth=owner(),w=new Workspace();if(consumer){w.auth=auth;w.state.session=session;}
 let settled=false,error;const operation=(consumer?w.logout():auth.logout()).then(()=>{settled=true},e=>{settled=true;error=e});await tick();
 const reply=()=>{if(remote instanceof Error)r.reject(remote);else r.resolve(remote==='known'?[503,{'content-type':'application/json'},[...new TextEncoder().encode('{"error":{"code":"REQUEST_FAILED"}}')]]:[204,{},[]]);};
 const remove=()=>cleanup?c.reject(cleanup):c.resolve();
 if(first==='remote'){reply();await tick();assert(!settled,name+' must await cleanup');remove();}else{remove();await tick();assert(!settled,name+' must await remote');reply();}
 await operation;await tick();const knownCleanup=cleanup==='Secure credential storage unavailable';const unknowns=[remote,cleanup].filter(v=>v instanceof Error);const count=(remote?1:0)+(cleanup?1:0);
 if(consumer){assert.equal(w.state.busy,false);assert.equal(w.state.session,null);assert.equal(w.auth,null);if(unknowns.length)assert(error);else assert.equal(error,undefined);}
 else if(count){assert(error);}else assert.equal(error,undefined);
 if(error){const graph=roots(error);unknowns.forEach(v=>assert(graph.has(v),name+' preserves identity'));if((count===1&&unknowns.length===1)||same)assert.equal(error,unknowns[0]);if(count===2&&!same)assert(error instanceof AggregateError);if(remote==='known'&&cleanup&& !consumer)assert([...graph].some(e=>e instanceof ApiFailure));if(knownCleanup&&!consumer)assert([...graph].some(e=>e instanceof NativeCapabilityFailure));}
 assert(calls.some(([command])=>command==='native_https'));assert(calls.some(([command])=>command==='credential_remove'));checks++;console.log(name+' PASS');
}
async function listCase(name,left,right,first,retired=false){
 const l=pending(),r=pending();const calls=[];globalThis.window={__TAURI_INTERNALS__:{invoke:async(command,args)=>{assert.equal(command,'database_query');assert.equal(args.accountId,A);calls.push(args);if(args.sql.startsWith('SELECT conversation_id'))return [[B],[C]];assert(args.sql.startsWith('SELECT request_id'));return args.binds[0]===B?l.promise:r.promise;}}};
 const w=new Workspace();w.state.selected=B;let observed;const failure=w.failure.bind(w);w.failure=(error,...args)=>{observed=error;return failure(error,...args);};let settled=false,error;const operation=w.updateList(accountRepository(A),0).then(()=>{settled=true},e=>{settled=true;error=e});await tick();
 const row=id=>[[id,A,'controlled text','SENT',S,'1','2026-10-03T00:00:00Z']];const release=(deferred,fault,id)=>fault?deferred.reject(fault):deferred.resolve(row(id));
 if(first==='left'){release(l,left,B);await tick();assert(!settled,name+' must await right');}else{release(r,right,C);await tick();assert(!settled,name+' must await left');}
 if(retired)w.generation++;
 if(first==='left')release(r,right,C);else release(l,left,B);await operation;await tick();
 const unknowns=[left,right].filter(v=>v instanceof Error);
 if(unknowns.length){assert(error,name+' unknown must reject');const graph=roots(error);unknowns.forEach(v=>assert(graph.has(v)));if(unknowns.length===1&&!(left&&right))assert.equal(error,unknowns[0]);if(left&&right&&left!==right)assert(error instanceof AggregateError);assert.equal(w.state.error,null);}
 else {assert.equal(error,undefined);if(left||right){assert.equal(w.state.error,retired?null:'Conversation history unavailable');assert.deepEqual(w.state.conversations,[]);if(left&&right){assert(observed instanceof AggregateError);assert.equal(observed.errors.length,2);assert(observed.errors.every(root=>root instanceof SendStorageFailure));roots(observed);}}else if(!retired){assert.equal(w.state.messages.length,1);assert.deepEqual(new Set(w.state.conversations),new Set([B,C]));}}
 assert.equal(calls.length,3);checks++;console.log(name+' PASS');
}
async function refreshCase(name,cleanup,fail=false,consumer=false){
 let primary,removes=0;globalThis.window={__TAURI_INTERNALS__:{invoke:async(command)=>{if(command==='credential_read')return 'public-owned-refresh-fixture';if(command==='native_https')return [401,{'content-type':'application/json'},[...new TextEncoder().encode('{"error":{"code":"AUTH_SESSION_REVOKED"}}')]];assert.equal(command,'credential_remove');removes++;if(fail)throw cleanup==='same-primary'?primary:cleanup;}}};
 const auth=owner(),request=auth.request.bind(auth);auth.request=async(...args)=>{try{return await request(...args);}catch(error){primary=error;throw error;}};
 const w=new Workspace();w.auth=auth;w.state.session=session;let closed=0;w.sync={close:async()=>{closed++;}};let error,failed=false;
 await (consumer?w.refresh():auth.refresh()).catch(root=>{failed=true;error=root;});await tick();if(consumer){assert.equal(w.state.session,null);assert.equal(w.auth,null);assert.equal(w.sync,null);assert.equal(closed,1);const before=removes;await w.refresh();assert.equal(removes,before);}assert(primary instanceof ApiFailure);assert.equal(primary.kind,'session_expired');
 if(consumer&&cleanup==='Secure credential storage unavailable'){assert.equal(failed,false);assert.equal(w.state.error,'Operation unavailable');assert.equal(w.state.busy,false);assert.equal(removes,1,'known cleanup aggregate must not trigger extra credential retry');}
 else {assert(failed);const graph=roots(error);assert(graph.has(primary));if(fail&&cleanup!=='same-primary'){assert(error instanceof AggregateError);assert(graph.has(cleanup));}else assert.equal(error,primary);assert.equal(removes,fail?1:2);if(consumer)assert.equal(w.state.busy,false);}
 checks++;console.log(name+' PASS');
}
async function primitiveSibling(value){
 const c=pending();globalThis.window={__TAURI_INTERNALS__:{invoke:async(command)=>{if(command==='native_https')return [503,{'content-type':'application/json'},[...new TextEncoder().encode('{"error":{"code":"REQUEST_FAILED"}}')]];assert.equal(command,'credential_remove');return c.promise;}}};
 let error,failed=false;const operation=owner().logout().catch(e=>{failed=true;error=e;});await tick();assert(!failed);c.reject(value);await operation;assert(failed);assert(error instanceof AggregateError);assert(roots(error).has(value));
 const slow=pending();globalThis.window={__TAURI_INTERNALS__:{invoke:async(command,args)=>{assert.equal(command,'database_query');assert.equal(args.accountId,A);if(args.sql.startsWith('SELECT conversation_id'))return [[B],[C]];if(args.binds[0]===B)throw 'Storage query rejected';return slow.promise;}}};
 const w=new Workspace();failed=false;const list=w.updateList(accountRepository(A),0).catch(e=>{failed=true;error=e;});await tick();assert(!failed);slow.reject(value);await list;assert(failed);assert(error instanceof AggregateError);assert(roots(error).has(value));assert.equal(w.state.error,null);
 checks+=2;console.log('falsy primitive sibling '+String(value)+' logout/list preserve roots PASS');
}
try{
 await logoutCase('logout known-first late unknown', 'known',new Error('remove bug'),'remote');
 await logoutCase('logout unknown-first late known',new Error('remote bug'),'Secure credential storage unavailable','remote');
 await logoutCase('logout cleanup known-first late unknown',new Error('remote bug'),'Secure credential storage unavailable','cleanup');
 await logoutCase('logout cleanup unknown-first late known','known',new Error('remove bug'),'cleanup');
 await logoutCase('logout dual-known roots','known','Secure credential storage unavailable','remote');
 await logoutCase('logout remote known-only','known',null,'remote');
 await logoutCase('logout cleanup known-only',null,'Secure credential storage unavailable','cleanup');
 await logoutCase('logout unknown-only identity',null,new Error('remove bug'),'remote');
 const same=new Error('shared exact root');await logoutCase('logout same identity',same,same,'remote',false,true);
 await logoutCase('logout normal',null,null,'remote');
 await logoutCase('Workspace logout mixed rejects/busy reset','known',new Error('remove bug'),'remote',true);
 await logoutCase('Workspace logout dual-known honest error','known','Secure credential storage unavailable','cleanup',true);
 await logoutCase('Workspace logout normal',null,null,'remote',true);
 await listCase('list known-first late unknown','Storage query rejected',new Error('read bug'),'left');
 await listCase('list unknown-first late known',new Error('read bug'),'Storage query rejected','left');
 await listCase('list reverse known-first late unknown',new Error('read bug'),'Storage query rejected','right');
 await listCase('list dual-known history error','Storage query rejected','Storage read open failed','left');
 await listCase('list known-only history error','Storage query rejected',null,'left');
 await listCase('list unknown-only identity',null,new Error('read bug'),'left');
 await listCase('list normal rows/order',null,null,'left');
 await listCase('retired list known failure no stale state','Storage query rejected',null,'left',true);
 await listCase('retired list mixed unknown still rejects','Storage query rejected',new Error('read bug'),'left',true);
 await refreshCase('refresh successful cleanup original primary',null);
 await refreshCase('refresh unknown cleanup preserves known primary',new Error('cleanup bug'),true);
 await refreshCase('refresh known cleanup distinct roots','Secure credential storage unavailable',true);
 await refreshCase('refresh same primary identity','same-primary',true);
 await refreshCase('Workspace refresh mixed roots rejects/busy reset',new Error('cleanup bug'),true,true);
 await refreshCase('Workspace refresh dual-known no new cleanup retry','Secure credential storage unavailable',true,true);
 for(const value of [0,null,undefined]){await refreshCase('refresh falsy cleanup '+String(value),value,true);await primitiveSibling(value);}
 assert.equal(unhandled.length,0);console.log('DESKTOP-PARALLEL-CHECKS='+checks+' PASS; actual compiled consumers/literal IPC; no live SQLite or private credential operations');
}finally{process.removeListener('unhandledRejection',handler);}
