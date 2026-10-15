import assert from 'node:assert/strict';
const build=new URL(process.argv[2]);
const {Auth}=await import(new URL('desktop/src/application/ui/auth.js',build));
const {Workspace}=await import(new URL('desktop/src/application/ui/workspace.js',build));
const {SendApplication}=await import(new URL('desktop/src/application/send.js',build));
const {SyncApplication}=await import(new URL('desktop/src/application/sync/application.js',build));
const {SyncHttp}=await import(new URL('shared/protocol-sdk/src/sync/http.js',build));
const session={userId:'11111111-1111-4111-8111-111111111111',sessionId:'22222222-2222-4222-8222-222222222222',sessionEpoch:1n,accessToken:'public-controlled-fixture'};
const tick=()=>new Promise(resolve=>setImmediate(resolve));
const deferred=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};};
const unhandled=[];const onUnhandled=root=>unhandled.push(root);process.on('unhandledRejection',onUnhandled);
function roots(root,seen=new Set(),active=new Set()){
  assert(!active.has(root),'failure graph must be acyclic');if(seen.has(root))return seen;
  seen.add(root);active.add(root);if(root instanceof Error){if('cause' in root)roots(root.cause,seen,active);if(root instanceof AggregateError)for(const child of root.errors)roots(child,seen,active);}active.delete(root);return seen;
}
function fixture(options={}){
  const auth=new Auth('https://fixture.invalid');auth.session=session;auth.slot=auth.endpoint+'/'+session.userId+'/'+session.sessionId;
  const saved=new Map([[auth.slot,'public-controlled-refresh'],[auth.endpoint+'/current',auth.slot]]),calls=[];
  globalThis.window={__TAURI_INTERNALS__:{invoke:async(command,args)=>{
    calls.push(command);
    if(command==='native_https'){assert(args.url.endsWith('/v1/auth/logout'));return options.remote.promise;}
    assert.equal(command,'credential_remove');if('cleanup' in options)throw options.cleanup;saved.delete(args.slot);
  }}};
  const w=new Workspace();w.auth=auth;w.state.session=session;
  let closes=0;const socket={onopen:null,onmessage:null,onclose:null,onerror:null,send(){throw Error('No send expected');},close(){closes++;if('close' in options)throw options.close;}};
  const send=new SendApplication({},session);send.socket=socket;
  const sync=new SyncApplication(send,new SyncHttp(auth.endpoint,session));w.sync=sync;
  let timerTicks=0;w.refreshTimer=setInterval(()=>timerTicks++,1);
  let nullPublications=0;
  w.observe(()=>{if(w.state.session!==null){if(options.initialObserver&&w.state.busy)throw options.initialObserver;return;}nullPublications++;if(nullPublications===1&&'observer' in options)throw options.observer;if(nullPublications>1&&'finalObserver' in options)throw options.finalObserver;if(nullPublications>2&&'errorObserver' in options)throw options.errorObserver;});
  return {w,auth,sync,saved,calls,get closes(){return closes;},get timerTicks(){return timerTicks;}};
}
async function retired(f){
  assert.equal(f.w.auth,null);assert.equal(f.w.sync,null);assert.equal(f.w.state.session,null);assert.equal(f.w.refreshTimer,null);assert.equal(f.w.state.busy,false);assert.equal(f.auth.session,null);assert.equal(f.sync.state.status,'retired');assert.equal(f.closes,1);
  const ticks=f.timerTicks;await new Promise(resolve=>setTimeout(resolve,6));assert.equal(f.timerTicks,ticks);
  const removes=f.calls.filter(command=>command==='credential_remove').length;await f.w.refresh();assert.equal(f.closes,1);assert.equal(f.calls.filter(command=>command==='credential_remove').length,removes,'no credential cleanup retry');
}
let checks=0;
const observer=new Error('actual publication observer'),cleanup=new Error('literal credential IPC bug'),close=new Error('actual socket close bug'),finalObserver=new Error('busy publication observer'),initialObserver=new Error('initial busy observer');
for(const [name,options,expected] of [
  ['normal',{},[]],
  ['observer',{observer},[observer]],
  ['cleanup-known',{cleanup:'Secure credential storage unavailable'},[]],
  ['cleanup-unknown',{cleanup},[cleanup]],
  ['observer-and-cleanup',{observer,cleanup},[observer,cleanup]],
  ['observer-and-close',{observer,close},[observer,close]],
  ['observer-and-final',{observer,finalObserver},[observer,finalObserver]],
  ...[0,null,undefined,false,''].map(value=>['cleanup-'+String(value),{cleanup:value},[value]])
]){
  const f=fixture(options);let rejected=false,error;await f.w.expire().catch(root=>{rejected=true;error=root;});
  await retired(f);assert.equal(f.calls.filter(command=>command==='credential_remove').length,'cleanup' in options?1:2);
  if(!('cleanup' in options))assert.equal(f.saved.size,0,'expiry removes both saved pointers after retirement failure');
  if(expected.length){assert(rejected,name);const graph=roots(error);for(const root of expected)assert(graph.has(root),name+' exact root');if(expected.length===1)assert.equal(error,expected[0]);}
  else{assert.equal(rejected,false);assert(f.w.state.error);}
  checks++;console.log('EXPIRY '+name+' PASS');
}
for(const [name,options,remoteFault,expected] of [
  ['normal',{},false,[]],
  ['observer',{observer},false,[observer]],
  ['late-unknown',{observer},true,[observer]],
  ['observer-close-late',{observer,close},true,[observer,close]],
  ['cleanup-and-late',{cleanup},true,[cleanup]],
  ['initial-observer',{initialObserver},false,[initialObserver]],
  ['observer-and-final',{observer,finalObserver},true,[observer,finalObserver]],
  ['known-with-final-observer',{cleanup:'Secure credential storage unavailable',finalObserver},false,[finalObserver]],
  ['known-with-error-observer',{cleanup:'Secure credential storage unavailable',errorObserver:finalObserver},false,[finalObserver]],
  ...[0,null,undefined,false,''].map(value=>['late-'+String(value),{observer,remoteRoot:value},true,[observer]])
]){
  const remote=deferred(),f=fixture({...options,remote});const remoteRoot='remoteRoot' in options?options.remoteRoot:new Error('late actual native HTTPS rejection '+name);
  let settled=false,rejected=false,error;const operation=f.w.logout().then(()=>{settled=true;},root=>{settled=true;rejected=true;error=root;});
  await tick();assert.equal(f.w.state.session,null);assert.equal(f.sync.state.status,'retired');assert.equal(settled,false,'logout must await already-started remote after stop failure');
  if(remoteFault)remote.reject(remoteRoot);else remote.resolve([204,{},[]]);
  await operation;await tick();await tick();await retired(f);
  const wanted=[...expected,...(remoteFault?[remoteRoot]:[])];
  if(wanted.length){assert(rejected,name);const graph=roots(error);for(const root of wanted)assert(graph.has(root),name+' exact root');if(wanted.length===1&&!('cleanup' in options))assert.equal(error,wanted[0]);if('cleanup' in options&&options.cleanup==='Secure credential storage unavailable')assert([...graph].some(root=>root instanceof Error&&root.message==='Secure credential storage unavailable'),'preserve known cleanup root when observer also fails');}
  else assert.equal(rejected,false);
  assert.equal(f.calls.filter(command=>command==='native_https').length,1);assert.equal(f.calls.filter(command=>command==='credential_remove').length,'cleanup' in options?1:2);assert.deepEqual(unhandled,[],'all started operation roots belong to caller result');
  checks++;console.log('LOGOUT '+name+' PASS');
}
{
  const remote=deferred(),f=fixture({remote});const operation=f.w.logout();await tick();f.w.operation++;const newer={...session,sessionId:'33333333-3333-4333-8333-333333333333'};f.w.auth={session:newer};f.w.state={...f.w.state,session:newer,busy:true,error:'new owner'};remote.resolve([204,{},[]]);await operation;assert.equal(f.w.auth.session,newer);assert.equal(f.w.state.session,newer);assert.equal(f.w.state.busy,true);assert.equal(f.w.state.error,'new owner');checks++;console.log('LOGOUT newer operation publication guard PASS');
}
{
  const same=new Error('shared retirement and remote root'),remote=deferred(),f=fixture({observer:same,remote});let error;const operation=f.w.logout().catch(root=>error=root);await tick();remote.reject(same);await operation;await retired(f);assert.equal(error,same);checks++;console.log('LOGOUT same-root identity PASS');
}
for(const [name,options,wanted] of [
  ['retirement-observer',{observer},[observer]],
  ['retirement-and-final',{observer,finalObserver},[observer,finalObserver]],
  ['falsy-retirement',{observer:0},[0]]
]){
  const f=fixture(options);let rejected=false,error;await f.w.login(f.auth.endpoint,'fixture','fixture').catch(root=>{rejected=true;error=root;});
  assert(rejected);const graph=roots(error);for(const root of wanted)assert(graph.has(root));if(wanted.length===1)assert.equal(error,wanted[0]);
  assert.equal(f.w.state.busy,false);assert.equal(f.w.state.session,null);assert.equal(f.w.auth,f.auth,'failed stop retains original Auth owner before clear/new login');assert.equal(f.auth.session,session);assert.equal(f.w.sync,null);assert.equal(f.sync.state.status,'retired');assert.equal(f.closes,1);assert.equal(f.w.refreshTimer,null);assert.deepEqual(f.calls,[],'no clear or new Auth operation started after retirement failure');
  checks++;console.log('LOGIN '+name+' PASS');
}
for(const [name,options,wanted] of [
  ['retirement-observer',{observer},[observer]],
  ['retirement-and-final',{observer,finalObserver},[observer,finalObserver]],
  ['falsy-retirement',{observer:undefined},[undefined]]
]){
  const f=fixture(options);let rejected=false,error;await f.w.restore(f.auth.endpoint).catch(root=>{rejected=true;error=root;});assert(rejected);const graph=roots(error);for(const root of wanted)assert(graph.has(root));if(wanted.length===1)assert.equal(error,wanted[0]);assert.equal(f.w.state.busy,false);assert.equal(f.w.state.session,null);assert.equal(f.w.auth,f.auth);assert.equal(f.closes,1);assert.equal(f.sync.state.status,'retired');assert.deepEqual(f.calls,[]);checks++;console.log('RESTORE '+name+' PASS');
}
{
  let primary;globalThis.window={__TAURI_INTERNALS__:{invoke:async command=>{if(command==='credential_read')return 'public-fixture';assert.equal(command,'native_https');return [503,{'content-type':'application/json'},[...new TextEncoder().encode('{"error":{"code":"REQUEST_FAILED"}}')]];}}};
  const auth=new Auth('https://fixture.invalid');auth.session=session;auth.slot='public-fixture';const request=auth.request.bind(auth);auth.request=async(...args)=>{try{return await request(...args)}catch(error){primary=error;throw error;}};
  const w=new Workspace();w.auth=auth;w.state.session=session;const observer=new Error('actual known failure observer');w.observe(()=>{if(w.state.error)throw observer});let error;await w.refresh().catch(root=>error=root);assert(primary);const graph=roots(error);assert(graph.has(primary));assert(graph.has(observer));assert.equal(w.state.busy,false);assert.equal(w.auth,auth);assert.equal(w.state.session,session);checks++;console.log('REFRESH actual503 and error-publication observer roots PASS');
}
{
  const w=new Workspace();const auth=new Auth('https://fixture.invalid');auth.session=session;w.auth=auth;w.state.session=session;const first=new Error('initial busy observer'),last=new Error('final busy observer');w.observe(()=>{throw w.state.busy?first:last});let error;await w.refresh().catch(root=>error=root);const graph=roots(error);assert(graph.has(first));assert(graph.has(last));assert.equal(w.state.busy,false);assert.equal(w.auth,auth);assert.equal(auth.session,session);checks++;console.log('REFRESH initial and final busy observer roots PASS');
}
for(const method of ['register','search','add']){
  let primary;const request=Auth.prototype.request;Auth.prototype.request=async function(...args){try{return await request.apply(this,args)}catch(error){primary=error;throw error;}};
  globalThis.window={__TAURI_INTERNALS__:{invoke:async command=>{assert.equal(command,'native_https');return [503,{'content-type':'application/json'},[...new TextEncoder().encode('{"error":{"code":"REQUEST_FAILED"}}')]];}}};
  const w=new Workspace(),auth=new Auth('https://fixture.invalid');auth.session=session;w.auth=auth;w.state.session=session;let publications=0;const first=new Error('actual failure observer A'),final=new Error('actual busy observer B');w.observe(()=>{if(w.state.error)throw ++publications===1?first:final});let error;
  try{const operation=method==='register'?w.register('fixture-user','fixture-only-input','fixture-only-input'):method==='search'?w.search('fixture'):w.add(session.userId);await operation.catch(root=>error=root);}finally{Auth.prototype.request=request;}
  assert(primary);const graph=roots(error);assert(graph.has(primary));assert(graph.has(first));assert(graph.has(final));assert.equal(publications,2);assert.equal(w.state.busy,false);assert.equal(w.auth,auth);assert.equal(w.state.session,session);checks++;console.log(method.toUpperCase()+' actual503 primary and failure/final observer roots PASS');
}
assert.deepEqual(unhandled,[]);process.off('unhandledRejection',onUnhandled);
console.log('RETIREMENT-CONSUMER-CHECKS='+checks+' PASS; actual compiled Auth/Workspace/Send/Sync; only literal IPC/socket/observer producers controlled; no SQLite WRITE/draft/native credential acceptance');
