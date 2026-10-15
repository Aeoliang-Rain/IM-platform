import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const build=process.argv[2];let mode='success';
globalThis.window={__TAURI_INTERNALS__:{invoke:async(command)=>{
 if(command==='language_load')return 'en';
 if(command==='tray_text')return undefined;
 if(command==='appearance_load'){if(mode==='error')throw 'Appearance unavailable';return ['cold',16,1];}
 throw new Error('Unexpected literal native command '+command);
}}};
const {appearance,NativeCapabilityFailure}=await import(pathToFileURL(build+'/desktop/src/application/ui/native.js'));
const {Workspace}=await import(pathToFileURL(build+'/desktop/src/application/ui/workspace.js'));
assert.deepEqual(await appearance.load(),{theme:'cold',fontSize:16,density:1});
const good=new Workspace();await good.start();assert.equal(good.snapshot().error,null);
mode='error';await assert.rejects(appearance.load(),e=>e instanceof NativeCapabilityFailure&&e.code==='Appearance unavailable');
const failed=new Workspace();await failed.start();assert.equal(failed.snapshot().error,'Appearance could not be loaded');
console.log(JSON.stringify({result:'PASS',assertions:4,meaning:'Literal compiled appearance.load/Workspace.start: Rust-success-default bypasses existing error state, sanitized error reaches observable failure. Controlled invoke, not real Tauri or filesystem runtime.'}));
