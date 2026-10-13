import assert from 'node:assert/strict';
import {SyncHttp} from './build/shared/protocol-sdk/src/sync/http.js';
import {Http} from './build/web/src/application/http.js';
const unknown=new Error('controlled internal decoder failure');
let cancelCalls=0;
const makeStream=()=>new ReadableStream({start(controller){controller.enqueue(new Uint8Array([0xff]));},cancel(){cancelCalls++;throw new DOMException('controlled cancel failure','AbortError');}});
const fetcher=async()=>new Response(makeStream(),{status:200,headers:{'content-type':'application/json','cache-control':'no-store'}});
const original=TextDecoder.prototype.decode;
TextDecoder.prototype.decode=function(){throw unknown;};
try {
 const session={userId:'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',sessionId:'11111111-1111-4111-8111-111111111111',sessionEpoch:1n,accessToken:'controlled'};
 const sync=new SyncHttp('https://controlled.invalid',session,fetcher);
 const http=new Http('https://controlled.invalid',fetcher);
 for(const [name,action] of [['SyncHttp',()=>sync.user('0',new AbortController().signal)],['WebHttp',()=>http.request('/v1/users/me','GET',undefined,'controlled',new AbortController().signal)]]){
   try{await action();assert.fail('expected rejection');}catch(e){assert.notEqual(e,unknown);console.log(name+': original unknown identity LOST; observed='+e.constructor.name+' '+e.message);}
 }
 assert.equal(cancelCalls,2);
}finally{TextDecoder.prototype.decode=original;}

