import fs from 'node:fs/promises';import crypto from 'node:crypto';import {execFileSync} from 'node:child_process';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
export async function actualBinding(){
 const receipt=JSON.parse(await fs.readFile(process.env.IM_UIREF_ANDROID_BINDING??'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/android-install-binding-324a2d0.json','utf8'));
 const adb='H:/Android/platform-tools/adb.exe';const artifacts={};
 for(const [packageName,artifact] of [['im.platform.client',receipt.production],['im.platform.client.test',receipt.afterTest]]){
  if(sha(await fs.readFile(artifact.archive))!==artifact.sha256)throw Error('Actual archived APK hash mismatch');
  const devicePath=execFileSync(adb,['-s','emulator-5590','shell','pm','path',packageName],{encoding:'utf8'}).trim().replace(/^package:/,'');
  const bytes=execFileSync(adb,['-s','emulator-5590','exec-out','cat',devicePath],{maxBuffer:64*1024*1024});
  if(sha(bytes)!==artifact.sha256)throw Error('Actual installed APK hash mismatch');
  artifacts[packageName]={archive:artifact.archive,sha256:artifact.sha256,devicePath};
 }
 return {actualUTC:new Date().toISOString(),actualHEAD:execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),actualStatus:execFileSync('git',['status','--porcelain'],{encoding:'utf8'}),productionSource:receipt.productSource,testSource:receipt.HEAD,runner:receipt.runner,artifacts};
}
