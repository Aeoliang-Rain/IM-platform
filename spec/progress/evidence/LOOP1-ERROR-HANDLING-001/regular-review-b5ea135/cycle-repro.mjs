import assert from 'node:assert/strict';
import {SyncHttp} from './compiled/shared/protocol-sdk/src/sync/http.js';
import {SyncFailure,MAX_RESPONSE} from './compiled/shared/protocol-sdk/src/sync/wire.js';
import {Http,ApiFailure} from './compiled/web/src/application/http.js';
import {verifyStreamCleanup} from 'file:///H:/.codex/worktrees/err/IM-platform/tests/clients/errors/stream_cleanup.mjs';
const sid='10000000-0000-4000-8000-000000000001',session={userId:sid,sessionId:sid,sessionEpoch:1n,accessToken:'controlled'},signal=()=>new AbortController().signal;
const sync=(response,s)=>new SyncHttp('https://localhost/',session,async()=>response,()=>sid).user('0',s);
const web=(response,s)=>new Http('https://localhost/',async()=>response).request('/v1/users/me','GET',undefined,undefined,s);
const logout=(response,s)=>new Http('https://localhost/',async()=>response).request('/v1/auth/logout','POST',undefined,undefined,s);
await verifyStreamCleanup(sync,(e,m)=>e instanceof SyncFailure&&e.kind===(m==='protocol-distinct'?'protocol':'transport'),JSON.stringify({syncVersion:'1.0',type:'sync.user.page',requestId:sid,events:[],nextCursor:'0',hasMore:false}));
await verifyStreamCleanup(web,(e,m)=>e instanceof ApiFailure&&e.code===(m==='protocol-distinct'?'INVALID_RESPONSE':'CONNECTION_UNAVAILABLE'),'{}');
await verifyStreamCleanup(logout,(e,m)=>e instanceof ApiFailure&&e.code===(m==='protocol-distinct'?'INVALID_RESPONSE':'CONNECTION_UNAVAILABLE'),'',{logout:true});
for(const [name,invoke,known,mode] of [['Sync size',sync,e=>e instanceof SyncFailure&&e.kind==='protocol','size'],['Web JSON size',web,e=>e instanceof ApiFailure&&e.code==='INVALID_RESPONSE','size'],['Web logout illegal body',logout,e=>e instanceof ApiFailure&&e.code==='INVALID_RESPONSE','logout']]){
 const cleanup=new DOMException('controlled cancel AbortError','AbortError');let cancellations=0;
 const stream=new ReadableStream({start(c){c.enqueue(new Uint8Array(mode==='size'?MAX_RESPONSE+1:1));},cancel(){cancellations++;throw cleanup;}});
 const response=new Response(mode==='logout'?null:stream,{status:mode==='logout'?204:200,headers:{'content-type':'application/json','cache-control':'no-store'}});
 if(mode==='logout')Object.defineProperty(response,'body',{value:stream});
 let caught;try{await invoke(response,signal());assert.fail('expected protocol rejection');}catch(e){caught=e;}
 assert(known(caught));assert(caught.cause instanceof AggregateError);assert.equal(caught.cause.errors[0],caught);assert.equal(caught.cause.errors[1],cleanup);assert.equal(cancellations,1);
 console.log(JSON.stringify({case:name,classification: caught.kind??caught.code,cancelCount:cancellations,selfCycle: caught.cause.errors[0]===caught,causeRoot0IsThrownError:true,source:'current exact source strict compiled; real Response/ReadableStream with controlled known cancellation rejection; logout uses controlled adapter body at real204 status'}));
}
console.log('CONFIRMED all three direct protocol+known cancel paths create cause->errors[0]->same thrown error');

