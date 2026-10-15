import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const base='C:/Users/21441/.codex/visualizations/2026/10/13/01a1341c-f5bd-7a20-8d63-e5a574250f3c/regular-review-a292-recovery2/fixture/clients/desktop/dist/';
const {Repository}=await import(pathToFileURL(base+'shared/protocol-sdk/src/storage/repository.js'));
let rows=[];const repository=new Repository({query:async()=>rows,transaction:async()=>{throw Error('Forbidden write')}});
for(const [value,expected] of [[[],0n],[[['0']],0n],[[['1']],1n],[[['9223372036854775807']],9223372036854775807n]]){rows=value;assert.equal(await repository.contiguous('fixture'),expected);}
for(const value of [null,undefined,'','-1','+1','01','1.0','1e1',' 1','1 ','9223372036854775808',0]){rows=[[value]];await assert.rejects(repository.contiguous('fixture'));}
rows=[[]];await assert.rejects(repository.contiguous('fixture'));
const {SyncHttp}=await import(pathToFileURL(base+'shared/protocol-sdk/src/sync/http.js'));
const {SyncFailure}=await import(pathToFileURL(base+'shared/protocol-sdk/src/sync/wire.js'));
const A='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',S='11111111-1111-4111-8111-111111111111';let count=0;
for(const [read,cancel] of [[new TypeError('read known'),new DOMException('cleanup known')],[new Error('read unknown'),new TypeError('cleanup known')],[new TypeError('read known'),new Error('cleanup unknown')]]){
 count=0;const response={status:200,redirected:false,headers:new Headers({'content-type':'application/json','cache-control':'no-store'}),body:{getReader:()=>({read:async()=>{throw read},cancel:async()=>{count++;throw cancel}})}};
 const http=new SyncHttp('https://example.invalid',{userId:A,sessionId:S,sessionEpoch:1n,accessToken:'fixture'},async()=>response,()=>S);
 try{await http.user('0',new AbortController().signal);assert.fail('did not fail')}catch(error){
  assert.equal(count,1);const aggregate=error instanceof SyncFailure?error.cause:error;assert.ok(aggregate instanceof AggregateError);assert.equal(aggregate.errors[0],read);assert.equal(aggregate.errors[1],cancel);
  assert.ok(!aggregate.errors.includes(error));if(read instanceof TypeError && cancel instanceof DOMException){assert.ok(error instanceof SyncFailure);assert.equal(error.kind,'transport')}else assert.ok(error instanceof AggregateError);
 }
}
console.log('PASS fresh independent controls: contiguous canonical decimal/no-row0/signed64 failure; response known+known projection acyclic; unknown source/cleanup root identity retained; one cancel; no writes');
