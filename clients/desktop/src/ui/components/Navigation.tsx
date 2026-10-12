import {useText} from "../i18n/context.js";
import React from "react";
import type {WorkspaceState} from "../../application/ui/workspace.js";
import type {Appearance} from "../../application/ui/native.js";
import type {Friend} from "../../application/ui/auth.js";
export function Navigation({s,page:navigate}:{s:Pick<WorkspaceState,"page"|"profile"|"session">;page:(page:WorkspaceState["page"])=>void}){
  const t=useText();
return <aside className="rail"><div className="brand" aria-label={t("brand.name")}><img src="logo.png" alt={t("brand.logo")}/>IM<span>+</span></div><div className="brand-caption">PLUGWORLDIM</div>
      <nav aria-label={t("nav.main")}>{(["Chat","Friends","AI","Plugin"] as const).map((page,i)=><button key={page} className={s.page===page?"nav selected":"nav"} onClick={()=>navigate(page)}><span className="nav-icon" aria-hidden="true">{["◫","♧","✧","⊞"][i]}</span>{t("nav."+page.toLowerCase())}{page==="AI"&&<small>{t("nav.soon")}</small>}</button>)}</nav>
      <div className="rail-bottom"><div className="connection" title={s.session?t("nav.signedIn"):t("nav.local")}><span className={"dot "+(s.session?"ready":"offline")}/>{s.session?t("connection.ready"):t("connection.offlineShort")}</div><button className="nav" onClick={()=>navigate("Settings")}>{t("nav.settings")}</button><div className="identity"><span className="avatar">{s.profile?.displayName[0]??"+"}</span><div><strong>{s.profile?.displayName??t("nav.workspace")}</strong><small>{s.session?t("nav.personal"):t("nav.signIn")}</small></div></div></div>
    </aside>;
}
