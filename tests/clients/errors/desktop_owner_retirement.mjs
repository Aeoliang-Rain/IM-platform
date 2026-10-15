import assert from 'node:assert/strict';
const build=new URL(process.argv[2]);
const {Auth,ApiFailure}=await import(new URL('desktop/src/application/ui/auth.js',build));
const {Workspace}=await import(new URL('desktop/src/application/ui/workspace.js',build));
const A='11111111-1111-4111-8111-111111111111',S='22222222-2222-4222-8222-222222222222';
const session={userId:A,sessionId:S,sessionEpoch:1n,accessToken:'controlled'};
const tick=()=>new Promise(r=>setImmediate(r));
function graph(e,seen=new Set(),active=new Set()){assert(!active.has(e));if(seen.has(e))return seen;seen.add(e);active.add(e);if(e instanceof Error){if('cause' in e)graph(e.cause,seen,active);if(e instanceof AggregateError)for(const x of e.errors)graph(x,seen,active);}active.delete(e);return seen;}
let checks=0;
for(const kind of ['normal-cleanup','known','unknown','primitive','close','observer','busy-observer','observer-close']){
 let removes=0,closes=0;const cleanup=new Error('credential bug'),close=new Error('close bug'),observer=new Error('observer bug');
 globalThis.window={__TAURI_INTERNALS__:{invoke:async command=>{if(command==='credential_read')return 'fixture';if(command==='native_https')return [401,{'content-type':'application/json'},[...new TextEncoder().encode('{"error":{"code":"AUTH_SESSION_REVOKED"}}')]];assert.equal(command,'credential_remove');removes++;if(kind!=='normal-cleanup')throw kind==='unknown'?cleanup:kind==='primitive'?0:'Secure credential storage unavailable';}}};
 const owner=new Auth('https://fixture.invalid');owner.session=session;owner.slot=owner.endpoint+'/'+A+'/'+S;let primary;const request=owner.request.bind(owner);owner.request=async(...args)=>{try{return await request(...args)}catch(e){primary=e;throw e}};
 const w=new Workspace();w.auth=owner;w.state.session=session;w.sync={close:async()=>{closes++;if(kind==='close'||kind==='observer-close')throw close;}};let ticks=0;const timer=setInterval(()=>ticks++,1);w.refreshTimer=timer;
 if(kind==='observer'||kind==='observer-close')w.observe(()=>{if(!w.state.session)throw observer;});
 if(kind==='busy-observer')w.observe(()=>{if(!w.state.busy)throw observer;});
 let error;await w.refresh().catch(e=>error=e);
 assert.equal(owner.session,null);assert.equal(w.state.session,null);assert.equal(w.auth,null);assert.equal(w.sync,null);assert.equal(w.refreshTimer,null);assert.equal(closes,1);assert.equal(w.state.busy,false);assert.equal(removes,kind==='normal-cleanup'?2:1);
 const old=ticks;await new Promise(r=>setTimeout(r,10));assert.equal(ticks,old);await w.refresh();assert.equal(closes,1);assert.equal(removes,kind==='normal-cleanup'?2:1);
 if(['normal-cleanup','known'].includes(kind)){assert.equal(error,undefined);assert(w.state.error);}
 else {assert(error);const roots=graph(error);assert(roots.has(primary));if(kind==='unknown')assert(roots.has(cleanup));if(kind==='primitive')assert(roots.has(0));if(kind.includes('close'))assert(roots.has(close));if(kind.includes('observer'))assert(roots.has(observer));}
 checks++;console.log('OWNER '+kind+' PASS');
}
for(const gate of ['operation','generation','owner']){
 let release;const wait=new Promise(r=>release=r);const w=new Workspace();let closed=0;const old={session,...{refresh:async()=>{await wait;old.session=null;throw new ApiFailure('connection_unavailable');}}};w.auth=old;w.state.session=session;const sync={close:async()=>closed++};w.sync=sync;
 const running=w.refresh();await tick();if(gate==='operation')w.operation++;if(gate==='generation')w.generation++;if(gate==='owner')w.auth={session};release();await running;assert.equal(w.state.session,session);assert.equal(w.sync,sync);assert.equal(closed,0);checks++;console.log('OWNER retired '+gate+' PASS');
}
{
 const w=new Workspace();let bound=0;w.auth={session,refresh:async()=>session};w.bind=async(s,op)=>{assert.equal(s,session);assert.equal(op,w.operation);bound++};await w.refresh();assert.equal(bound,1);assert.equal(w.state.busy,false);assert.equal(w.state.session,null);checks++;console.log('OWNER normal refresh reaches existing bind PASS');
}
console.log('OWNER-RETIREMENT-CHECKS='+checks+' PASS; actual compiled Auth/Workspace with literal IPC and controlled existing owner/listener failures');
