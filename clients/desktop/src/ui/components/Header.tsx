import React from "react";
import type {WorkspaceState} from "../../application/ui/workspace.js";
import type {Appearance} from "../../application/ui/native.js";
import type {Friend} from "../../application/ui/auth.js";
export function Header({s,prefs,preferences,run}:{s:Pick<WorkspaceState,"connection"|"offlineAccount"|"page"|"session"|"sync">;prefs:Appearance;preferences:(value:Appearance)=>Promise<void>;run:(promise:Promise<unknown>)=>void}){
return <header className="topbar"><div><small className="eyebrow">YOUR CONNECTED WORKSPACE</small><h1>{(s.session||s.offlineAccount||!["Chat","Friends"].includes(s.page))?s.page:"Welcome to IM+"}</h1></div><div className="top-actions"><span className="sync">{s.sync==="syncing"?"Syncing…":s.sync==="failed"?"Sync needs attention":s.connection==="offline"?"Local history":"Up to date"}</span><button className="quiet" onClick={()=>run(preferences({...prefs,theme:prefs.theme==="cold"?"warm":"cold"}))}>{prefs.theme==="cold"?"Cold AI":"Warm Creative"}</button></div></header>;
}
