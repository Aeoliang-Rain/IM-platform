import React from "react";
import type {WorkspaceState} from "../../application/ui/workspace.js";
import type {Appearance} from "../../application/ui/native.js";
import type {Friend} from "../../application/ui/auth.js";
export function Navigation({s,page:navigate}:{s:Pick<WorkspaceState,"page"|"profile"|"session">;page:(page:WorkspaceState["page"])=>void}){
return <aside className="rail"><div className="brand" aria-label="IM plus"><img src="logo.png" alt="IM+ logo"/>IM<span>+</span></div><div className="brand-caption">PLUGWORLDIM</div>
      <nav aria-label="Main navigation">{(["Chat","Friends","AI","Plugin"] as const).map((page,i)=><button key={page} className={s.page===page?"nav selected":"nav"} onClick={()=>navigate(page)}><span className="nav-icon" aria-hidden="true">{["◫","♧","✧","⊞"][i]}</span>{page}{page==="AI"&&<small>SOON</small>}</button>)}</nav>
      <div className="rail-bottom"><div className="connection" title={s.session?"Signed in":"Viewing local history"}><span className={"dot "+(s.session?"ready":"offline")}/>{s.session?"Online":"Offline"}</div><button className="nav" onClick={()=>navigate("Settings")}>⚙ Settings</button><div className="identity"><span className="avatar">{s.profile?.displayName[0]??"+"}</span><div><strong>{s.profile?.displayName??"Your workspace"}</strong><small>{s.session?"Personal account":"Sign in to connect"}</small></div></div></div>
    </aside>;
}
