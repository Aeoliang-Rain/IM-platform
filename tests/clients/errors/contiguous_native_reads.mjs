// Actual unchanged SQLx query adapter; fixture-only invalid data/schema.
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
export async function verifyNativeContiguous(build,probe) {
 const {Repository}=await import(new URL('shared/protocol-sdk/src/storage/repository.js',build));
 const root=mkdtempSync(join(tmpdir(),'im-contiguous-read-'));
 const account='10000000-0000-4000-8000-000000000098',conversation='10000000-0000-4000-8000-000000000099';
 const hex=s=>Buffer.from(s,'utf8').toString('hex'),bind=s=>s===null?'~':hex(s);
 function call(input){const result=spawnSync(probe,[root,account],{input,encoding:'utf8'});if(result.error)throw result.error;assert.equal(result.status,0,result.stderr);return result.stdout;}
 const db={async transaction(steps){call(steps.map(([sql,args,n])=>['T',n??'-',hex(sql),...args.map(bind)].join('\t')).join('\n')+'\n');},async query(sql,args){const raw=call(['Q',hex(sql),...args.map(bind)].join('\t')+'\n');return raw?raw.replace(/\r?\n$/,'').split(/\r?\n/).map(line=>line.split('\t').map(value=>value==='~'?null:Buffer.from(value,'hex').toString('utf8'))):[];}};
 try {
  const repo=new Repository(db);await repo.initialize();assert.equal(await repo.contiguous(conversation),0n);
  await db.transaction([['INSERT INTO conversations(conversation_id,contiguous_seq) VALUES(?,?)',[conversation,'0'],1]]);
  for(const value of ['0','7','9007199254740993','9223372036854775807']){await db.transaction([['UPDATE conversations SET contiguous_seq=? WHERE conversation_id=?',[value,conversation],1]]);assert.equal(await repo.contiguous(conversation),BigInt(value));}
  await db.transaction([['UPDATE conversations SET contiguous_seq=? WHERE conversation_id=?',['',conversation],1]]);
  assert.deepEqual(await db.query('SELECT CAST(contiguous_seq AS TEXT),typeof(contiguous_seq) FROM conversations WHERE conversation_id=?',[conversation]),[['','text']]);
  assert.deepEqual(await db.query('SELECT CAST(contiguous_seq AS TEXT) FROM conversations WHERE conversation_id=?',[conversation]),[['']]);
  await assert.rejects(repo.contiguous(conversation),/Invalid contiguous sequence/);
  await db.transaction([['DROP TABLE conversations',[],null],['CREATE TABLE conversations(conversation_id TEXT PRIMARY KEY,contiguous_seq INTEGER)',[],null],['INSERT INTO conversations VALUES(?,NULL)',[conversation],1]]);
  assert.deepEqual(await db.query('SELECT CAST(contiguous_seq AS TEXT) FROM conversations WHERE conversation_id=?',[conversation]),[[null]]);
  await assert.rejects(repo.contiguous(conversation),/Invalid contiguous sequence/);
  await db.transaction([['DELETE FROM conversations',[],null]]);assert.equal(await repo.contiguous(conversation),0n);
  console.log('PASS actual SQLx contiguous: absent0/exact valid prefixes; canonical empty TEXT fails; malformed-schema NULL fails (canonical NOT NULL unchanged)');
 } finally {rmSync(root,{recursive:true,force:true});}
}
