import {useText} from "../i18n/context.js";
import React from "react";
import type {WorkspaceState} from "../../application/ui/workspace.js";
import type {Appearance} from "../../application/ui/native.js";
import type {Friend} from "../../application/ui/auth.js";
export function Header({s,prefs,preferences,run}:{s:Pick<WorkspaceState,"connection"|"offlineAccount"|"page"|"session"|"sync">;prefs:Appearance;preferences:(value:Appearance)=>Promise<void>;run:(promise:Promise<unknown>)=>void}){
  const t=useText();
return <header className="topbar"><div><small className="eyebrow">{t("header.connected")}</small><h1>{(s.session||s.offlineAccount||!["Chat","Friends"].includes(s.page))?t("nav."+s.page.toLowerCase()):t("header.title")}</h1></div><div className="top-actions"><span className="sync">{s.sync==="syncing"?t("sync.syncing"):s.sync==="failed"?t("sync.attention"):s.connection==="offline"?t("sync.local"):t("sync.current")}</span><button className="quiet" onClick={()=>run(preferences({...prefs,theme:prefs.theme==="cold"?"warm":"cold"}))}>{prefs.theme==="cold"?t("settings.cold"):t("settings.warm")}</button></div></header>;
}
