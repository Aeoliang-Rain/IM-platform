import React from "react";
import type {WorkspaceState} from "../../application/ui/workspace.js";
import type {Appearance} from "../../application/ui/native.js";
import type {Friend} from "../../application/ui/auth.js";
export function Messages({s,retry,run}:{s:Pick<WorkspaceState,"messages"|"offlineAccount"|"selected"|"session">;retry:(id:string)=>Promise<void>;run:(promise:Promise<unknown>)=>void}){
return <div className="messages" role="log" aria-live="polite">{!s.selected?<div className="empty"><span>✧</span><h3>Good conversations have a place</h3><p>Choose a conversation to begin.</p></div>:s.messages.length===0?<div className="empty"><h3>A fresh start</h3><p>No messages yet. Say hello.</p></div>:s.messages.map((m,i)=><div key={m[0]??m[4]??i} className={m[1]===(s.session?.userId??s.offlineAccount)?"message own":"message"}><div className="bubble">{m[2]}</div><small>{m[6]?new Date(m[6]).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"}):"Now"} · {m[3]==="SENT"?"Sent":m[3]==="SENDING"?"Sending…":"Failed"}{m[3]==="FAILED"&&m[1]===(s.session?.userId??s.offlineAccount)&&m[0]&&<button disabled={!s.session} onClick={()=>run(retry(m[0]!))}>Retry</button>}</small></div>)}</div>;
}
