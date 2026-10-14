// Controlled IPC transports actual owned Rust read outcomes; no physical ACL/installed GUI claim.
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {pathToFileURL} from "node:url";
const [build,nativeOutput]=process.argv.slice(2);
const rows=[...readFileSync(nativeOutput,"utf8").matchAll(/^APPEARANCE_RESULT (\S+) (ok|error) (.+)$/gm)].map(([,name,kind,value])=>({name,kind,value:kind==="ok"?JSON.parse(value):value.trim()}));
assert.equal(rows.length,8);assert.equal(rows.filter(r=>r.kind==="error").length,6);
let reply;
globalThis.window={__TAURI_INTERNALS__:{invoke:async(command)=>{
 if(command==="language_load")return "en";
 if(command==="tray_text")return;
 if(command==="appearance_load"){if(reply.kind==="error")throw reply.value;return reply.value;}
 throw new Error("Unexpected literal native command "+command);
}}};
const {appearance,NativeCapabilityFailure}=await import(pathToFileURL(build+"/desktop/src/application/ui/native.js"));
const {Workspace}=await import(pathToFileURL(build+"/desktop/src/application/ui/workspace.js"));
for(reply of rows){
 const workspace=new Workspace();
 if(reply.kind==="ok"){
  const [theme,fontSize,density]=reply.value;
  assert.deepEqual(await appearance.load(),{theme,fontSize,density});await workspace.start();
  assert.equal(workspace.snapshot().error,null);assert.deepEqual(workspace.snapshot().appearance,{theme,fontSize,density});
 }else{
  await assert.rejects(appearance.load(),e=>e instanceof NativeCapabilityFailure&&e.code===reply.value);
  await workspace.start();assert.equal(workspace.snapshot().error,"Appearance could not be loaded");
 }
}
// Unknown callback failures retain identity and reject startup, never normal defaults.
reply={kind:"error",value:new Error("owned unknown callback")};
await assert.rejects(appearance.load(),e=>e===reply.value);
await assert.rejects(new Workspace().start(),e=>e===reply.value);
console.log("PASS: actual Rust owned appearance outcomes -> controlled literal IPC -> fresh compiled appearance.load/Workspace.start; 8 normal/fault rows plus unknown identity. No physical ACL or installed UI acceptance claim.");
