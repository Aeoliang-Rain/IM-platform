import assert from 'node:assert/strict';
// Execute actual Response/ReadableStream readers. Dual read faults are controlled
// reader overrides; ordinary native errored streams report the same root twice.
export async function verifyStreamCleanup(invoke,known,body,{logout=false}={}) {
 const response=stream=>{const r=new Response(logout?null:stream,{status:logout?204:200,headers:{'content-type':'application/json','cache-control':'no-store'}});if(logout&&stream)Object.defineProperty(r,'body',{value:stream});return r;};
 const signal=()=>new AbortController().signal;
 let cancellations=0;
 const normal=new ReadableStream({start(c){if(!logout)c.enqueue(new TextEncoder().encode(body));c.close();},cancel(){cancellations++;}});
 const getNormal=normal.getReader.bind(normal);let normalCancel=0;normal.getReader=()=>{const reader=getNormal(),cancel=reader.cancel.bind(reader);reader.cancel=(...args)=>{normalCancel++;return cancel(...args);};return reader;};
 await invoke(response(normal),signal());assert.equal(normalCancel,1); // Completed stream cancel need not invoke underlying cancel.
 if(logout)await invoke(new Response(null,{status:204}),signal());
 const cleanup=new DOMException('controlled cleanup failure','AbortError');
 const original=new Error('controlled internal read failure');
 const decoder=TextDecoder.prototype.decode;
 for(const mode of ['cleanup-only','cleanup-unknown','decoder-distinct','protocol-distinct','read-distinct','read-single','same-known','same-unknown','distinct-known','undefined-distinct','null-distinct','primitive-distinct']) {
  if(logout&&(mode==='decoder-distinct'||mode==='protocol-distinct'))continue; // 204 path never decodes.
  let calls=0;
  const primary=mode==='distinct-known'?new TypeError('controlled network read'):mode==='undefined-distinct'?undefined:mode==='null-distinct'?null:mode==='primitive-distinct'?'controlled primitive':original;
  let stream;
  if(mode.startsWith('same-'))stream=new ReadableStream({start(c){c.error(mode==='same-known'?new TypeError('native stream network failure'):original);}});
  else {
   stream=new ReadableStream({start(c){if(!logout)c.enqueue(new TextEncoder().encode(body));},cancel(){calls++;if(mode==='cleanup-unknown')throw original;if(mode!=='read-single')throw cleanup;}});
   const get=stream.getReader.bind(stream);
   stream.getReader=()=>{const reader=get();if(mode!=='decoder-distinct'&&mode!=='protocol-distinct')reader.read=async()=>{if(mode.startsWith('cleanup-'))return {done:true,value:undefined};throw primary;};return reader;};
  }
  const protocol=new TypeError('controlled invalid UTF8');
  if(mode==='decoder-distinct'||mode==='protocol-distinct')TextDecoder.prototype.decode=function(){throw mode==='protocol-distinct'?protocol:original;};
  try {
   await assert.rejects(invoke(response(stream),signal()),error=>{
    if(mode==='cleanup-only'||mode==='same-known')return known(error,mode)&&!(error instanceof AggregateError);
    if(mode==='cleanup-unknown'||mode==='read-single'||mode==='same-unknown')return error===original;
    const allKnown=mode==='distinct-known'||mode==='protocol-distinct';
    if(allKnown)assert.equal(known(error,mode),true,'two actual known boundary faults retain FAILED classification');
    else {assert(error instanceof AggregateError,'unknown primary must escape known classification');assert.equal(known(error,mode),false);}
    const roots=allKnown?error.cause:error;assert(roots instanceof AggregateError);assert.equal(roots.errors.length,2);
    assert.equal(roots.errors[0],mode==='protocol-distinct'?protocol:mode==='decoder-distinct'?original:primary);assert.equal(roots.errors[1],cleanup);return true;
   });
   if(!mode.startsWith('same-'))assert.equal(calls,1,'cleanup executed exactly once');
  }finally{TextDecoder.prototype.decode=decoder;}
 }
 console.log('PASS stream cleanup normal/single/known same root/unknown same root/distinct dual roots'+(logout?' (actual204 status; controlled adapter-exposed empty stream)':''));
}
