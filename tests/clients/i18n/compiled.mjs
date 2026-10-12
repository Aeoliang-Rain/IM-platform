// Runs inside the existing Web behavior CI entry against actual compiled implementation.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {join} from 'node:path';
const repository=fileURLToPath(new URL('../../../',import.meta.url));
export async function verifyCompiledI18n(build){
 const module=await import(pathToFileURL(join(build,'web/src/ui/i18n/resources.js')));
 const {resources,translate,validLocale,displayText}=module;
 const keys=Object.keys(resources.en).sort(),placeholders=s=>[...s.matchAll(/\{([A-Za-z]+)\}/g)].map(m=>m[1]).sort();
 for(const locale of module.locales){
  assert.deepEqual(Object.keys(resources[locale]).sort(),keys);
  for(const key of keys)assert.deepEqual(placeholders(resources[locale][key]),placeholders(resources.en[key]));
  // Each platform's pure data must match the actual compiled Web dictionary.
  const desktop=readFileSync(join(repository,`clients/desktop/src/ui/i18n/${locale}.ts`),'utf8');
  assert.deepEqual(JSON.parse(desktop.slice('export default '.length).trim().replace(/;$/,'')),resources[locale]);
  const name=locale==='zh-CN'?'zhCN':locale==='ja-JP'?'jaJP':'en';
  const kotlin=readFileSync(join(repository,`clients/mobile/app/src/main/kotlin/im/platform/client/ui/i18n/${name}.kt`),'utf8');
  const entries=[...kotlin.matchAll(/("(?:[^"\\]|\\.)*") to ("(?:[^"\\]|\\.)*")/g)].map(m=>m.slice(1).map(s=>JSON.parse(s.replace(/\\\$/g,'$'))));
  assert.equal(entries.length,new Set(entries.map(e=>e[0])).size);assert.deepEqual(Object.fromEntries(entries),resources[locale]);
 }
 for(const bad of [null,undefined,'','EN','en-US','zh','ja',' en','en\n','\uFEFFen','ja-jp'])assert.equal(validLocale(bad),false);
 const missing=structuredClone(resources);delete missing['ja-JP']['nav.chat'];assert.equal(translate('ja-JP','nav.chat',{},missing),resources.en['nav.chat']);
 delete missing.en['nav.chat'];assert.throws(()=>translate('ja-JP','nav.chat',{},missing),/Missing English/);
 missing['ja-JP']['nav.chat']='present translation';assert.throws(()=>translate('ja-JP','nav.chat',{},missing),/Missing English/);
 for(const key of ['toString','constructor','__proto__']){assert.throws(()=>translate('ja-JP',key),/Missing English/);assert.equal(displayText('ja-JP',key),resources['ja-JP']['error.operation']);}
 assert.equal(displayText('ja-JP','untrusted server detail'),resources['ja-JP']['error.operation']);
 const previous=globalThis.window;let value=null,writes=0;
 try{
  globalThis.window={localStorage:{getItem:key=>{assert.equal(key,'plugworldim.language.v1');return value},setItem:(key,next)=>{assert.equal(key,'plugworldim.language.v1');value=next;writes++}}};
  const adapter=await import(pathToFileURL(join(build,'web/src/ui/language.js')));
  for(const raw of [null,'','EN','en-US','zh',' en','en\n','\uFEFFen']){value=raw;assert.equal(adapter.loadLanguage(),'en')}
  for(const locale of module.locales){assert.equal(adapter.saveLanguage(locale),true);assert.equal(adapter.loadLanguage(),locale);assert(Buffer.byteLength(value)<=5)}
  const before=writes;assert.equal(adapter.saveLanguage('en-US'),false);assert.equal(writes,before);
  window.localStorage.getItem=()=>{throw Error('unavailable')};assert.equal(adapter.loadLanguage(),'en');window.localStorage.setItem=()=>{throw Error('unavailable')};assert.equal(adapter.saveLanguage('ja-JP'),false);
 }finally{if(previous===undefined)delete globalThis.window;else globalThis.window=previous}
 console.log('PASS compiled i18n resource equivalence/negative controls/Web adapter; native and browser acceptance separate');
}
