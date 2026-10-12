// Unit evidence: real resource functions and Web adapter, not native runtime acceptance.
import assert from "node:assert/strict";
import {readFileSync,writeFileSync,mkdirSync} from "node:fs";
import {fileURLToPath,pathToFileURL} from "node:url";
import {resolve,join} from "node:path";
import {createRequire} from "node:module";
const root=resolve(fileURLToPath(new URL("../../..",import.meta.url)));
const ts=createRequire(process.env.I18N_TYPESCRIPT_PACKAGE??join(root,"clients/web/package.json"))("typescript");
const run=process.env.I18N_OUTPUT_DIR??join(root,"tests/clients/i18n/.runtime/unit");mkdirSync(run,{recursive:true});
const loaded={};
for(const platform of ["web","desktop"]){
 const output=join(run,platform);mkdirSync(join(output,"i18n"),{recursive:true});
 for(const name of ["en","zh-CN","ja-JP","resources"]){
  const source=readFileSync(join(root,`clients/${platform}/src/ui/i18n/${name}.ts`),"utf8");
  const js=ts.transpileModule(source,{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ES2022}}).outputText.replace(/\.js"/g,'.mjs"');
  writeFileSync(join(output,"i18n",name+".mjs"),js);
 }
 loaded[platform]=await import(pathToFileURL(join(output,"i18n/resources.mjs")));
}
await (await import("./scheduling.mjs")).verifyScheduling(root,run,ts,loaded);
const placeholder=value=>[...value.matchAll(/\{([A-Za-z]+)\}/g)].map(m=>m[1]).sort();
const check=resources=>{
 const keys=Object.keys(resources.en).sort();assert(keys.length>100);
 for(const locale of ["en","zh-CN","ja-JP"]){assert.deepEqual(Object.keys(resources[locale]).sort(),keys);for(const key of keys)assert.deepEqual(placeholder(resources[locale][key]),placeholder(resources.en[key]));}
};
for(const module of Object.values(loaded)){
 check(module.resources);
 for(const value of [null,undefined,"","EN","en-US","zh","ja"," en","en\n","en\uFEFF","ja-jp"])assert.equal(module.validLocale(value),false);
 for(const locale of module.locales)assert.equal(module.validLocale(locale),true);
 assert.equal(module.translate("invalid","nav.chat"),module.resources.en["nav.chat"]);
 const missing=structuredClone(module.resources);delete missing["ja-JP"]["nav.chat"];assert.equal(module.translate("ja-JP","nav.chat",{},missing),module.resources.en["nav.chat"]);
 delete missing.en["nav.chat"];assert.throws(()=>module.translate("ja-JP","nav.chat",{},missing),/Missing English/);
 const mismatch=structuredClone(module.resources);mismatch["ja-JP"]["nav.chat"]="{unexpected}";assert.throws(()=>check(mismatch));
 assert.equal(module.displayText("ja-JP","unknown server detail"),module.resources["ja-JP"]["error.operation"]);
 assert.equal(module.displayText("zh-CN","USERNAME_ALREADY_EXISTS"),module.resources["zh-CN"]["error.usernameExists"]);
}
assert.deepEqual(loaded.web.resources,loaded.desktop.resources);
for(const [locale,name] of [["en","en"],["zh-CN","zhCN"],["ja-JP","jaJP"]]){
 const source=readFileSync(join(root,`clients/mobile/app/src/main/kotlin/im/platform/client/ui/i18n/${name}.kt`),"utf8");
 const entries=[...source.matchAll(/("(?:[^"\\]|\\.)*") to ("(?:[^"\\]|\\.)*")/g)].map(m=>m.slice(1).map(s=>JSON.parse(s.replace(/\\\$/g,"$"))));
 assert.equal(new Set(entries.map(e=>e[0])).size,entries.length);assert.deepEqual(Object.fromEntries(entries),loaded.web.resources[locale]);
}
const output=join(run,"web");
const source=readFileSync(join(root,"clients/web/src/ui/language.ts"),"utf8");
writeFileSync(join(output,"language.mjs"),ts.transpileModule(source,{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ES2022}}).outputText.replace(/\.js"/g,'.mjs"'));
const adapter=await import(pathToFileURL(join(output,"language.mjs")));
let stored=null,writes=[];globalThis.window={localStorage:{getItem:key=>{assert.equal(key,"plugworldim.language.v1");return stored;},setItem:(key,value)=>{assert.equal(key,"plugworldim.language.v1");writes.push(value);stored=value;}}};
for(const raw of [null,"","EN","en-US"," en","en\n","en\uFEFF","ja-jp"]){stored=raw;assert.equal(adapter.loadLanguage(),"en");}
for(const locale of loaded.web.locales){assert.equal(adapter.saveLanguage(locale),true);assert.equal(adapter.loadLanguage(),locale);assert(Buffer.byteLength(stored)<=5);}
const count=writes.length;assert.equal(adapter.saveLanguage("en-US"),false);assert.equal(writes.length,count);
window.localStorage.getItem=()=>{throw new Error("unavailable");};assert.equal(adapter.loadLanguage(),"en");
window.localStorage.setItem=()=>{throw new Error("unavailable");};assert.equal(adapter.saveLanguage("ja-JP"),false);
console.log("PASS resource equivalence/placeholders/fallback negative controls and actual Web adapter unit behavior; native/browser runtime PENDING");
