import {WireFailure} from "../../../../shared/protocol-sdk/src/send/wire.js";
import {invoke} from "@tauri-apps/api/core";
// Current native capability provenance, distinct from arbitrary callback values.
// Only exact sanitized Rust command errors are tagged at the literal invoke call.
export class NativeTransportFailure extends Error {constructor(code:string){super(code,{cause:code});}}
export class NativeCapabilityFailure extends Error {constructor(readonly code:string){super(code,{cause:code});}}
function nativeFailure(error:unknown,codes:readonly string[]):never {if(typeof error==="string"&&codes.includes(error))throw new NativeCapabilityFailure(error);throw error;}
export interface Appearance {theme:"cold"|"warm";fontSize:number;density:number}
export const defaults:Appearance={theme:"cold",fontSize:16,density:1};
export const nativeFetch:typeof fetch=async(input,init)=>{
  const request=new Request(input,init);
  if(request.signal.aborted)throw new DOMException("Aborted","AbortError");
  const body=Array.from(new Uint8Array(await request.arrayBuffer()));
  let result:[number,Record<string,string>,number[]];
  try{result=await invoke<[number,Record<string,string>,number[]]>("native_https",{url:request.url,method:request.method,headers:Object.fromEntries(request.headers),body});}
  catch(error){if(error==="HTTPS transport unavailable")throw new NativeTransportFailure(error);if(error==="HTTPS redirects forbidden" || error==="HTTPS response too large")throw new WireFailure();throw error;}
  if(request.signal.aborted)throw new DOMException("Aborted","AbortError");
  const [status,headers,bytes]=result;
  return new Response(status===204?null:new Uint8Array(bytes),{status,headers});
};
export const appearance={
 load:async()=>{let value:[Appearance["theme"],number,number];try{value=await invoke<[Appearance["theme"],number,number]>("appearance_load");}catch(error){nativeFailure(error,["Appearance unavailable","Appearance invalid"]);}const [theme,fontSize,density]=value;return {theme,fontSize,density};},
 save:async(value:Appearance)=>{try{await invoke<void>("appearance_save",{value:[value.theme,value.fontSize,value.density]});}catch(error){nativeFailure(error,["Appearance unavailable"]);}}
};
// No credential is stored in appearance, localStorage or account database.
export const secure={
 read:async(slot:string)=>{try{return await invoke<string|null>("credential_read",{slot});}catch(error){nativeFailure(error,["Secure credential storage unavailable"]);}},
 write:async(slot:string,value:string)=>{try{await invoke<void>("credential_write",{slot,value});}catch(error){nativeFailure(error,["Secure credential storage unavailable"]);}},
 remove:async(slot:string)=>{try{await invoke<void>("credential_remove",{slot});}catch(error){nativeFailure(error,["Secure credential storage unavailable"]);}}
};
export const windowMaximized=async()=>{try{return await invoke<boolean>("window_maximized");}catch(error){nativeFailure(error,["Window unavailable"]);}};
export const windowControl=async(action:"minimize"|"maximize"|"close"|"drag")=>{try{await invoke<void>("window_control",{action});}catch(error){nativeFailure(error,["Window unavailable"]);}};
export const notify=async(title:string,body:string)=>{try{await invoke<void>("native_notify",{title,body});}catch(error){nativeFailure(error,["Notification unavailable"]);}};
import {validLocale,type Locale} from "../../ui/i18n/resources.js";
export const language={
 load:async():Promise<Locale>=>{try{const value=await invoke<unknown>("language_load");return validLocale(value)?value:"en";}catch(error){if(error==="Language unavailable")return "en";throw error;}},
 save:async(value:Locale)=>{if(!validLocale(value))throw new Error("Invalid language");try{await invoke<void>("language_save",{value});}catch(error){nativeFailure(error,["Language unavailable"]);}}
};
export const trayText=async(open:string,hide:string,quit:string,tooltip:string)=>{try{await invoke<void>("tray_text",{open,hide,quit,tooltip});}catch(error){nativeFailure(error,["Tray unavailable"]);}};
