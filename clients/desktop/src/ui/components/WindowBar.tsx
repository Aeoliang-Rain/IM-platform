import React from "react";
import type {WorkspaceState} from "../../application/ui/workspace.js";
import type {Appearance} from "../../application/ui/native.js";
import type {Friend} from "../../application/ui/auth.js";
export function WindowBar({maximized,windowControl,run}:{maximized:boolean;windowControl:(action:"drag"|"maximize"|"minimize"|"close")=>Promise<void>;run:(promise:Promise<unknown>)=>void}){
return <div className="window-bar"><div className="window-drag" onPointerDown={e=>{if(e.button===0)run(windowControl("drag"));}} onDoubleClick={()=>run(windowControl("maximize"))}><img src="logo.png" alt=""/><span>IM+ · PlugWorldIM</span></div><div className="window-actions"><button title="Minimize" aria-label="Minimize" onClick={()=>run(windowControl("minimize"))}>−</button><button title={maximized?"Restore":"Maximize"} aria-label={maximized?"Restore":"Maximize"} onClick={()=>run(windowControl("maximize"))}><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">{maximized?<><path d="M8 5V4a1 1 0 0 1 1-1h11a1 1 0 0 1 1 1v11a1 1 0 0 1-1 1h-1"/><rect x="4" y="7" width="13" height="13" rx="1"/></>:<rect x="5" y="5" width="14" height="14" rx="1"/>}</svg></button><button className="window-close" aria-label="Close" onClick={()=>run(windowControl("close"))}>×</button></div></div>;
}
