import {useText} from "../i18n/context.js";
import React from "react";

export function Placeholder({page,setPage}:{page:"AI"|"Plugin";setPage:(page:"Chat"|"Friends"|"AI"|"Plugin"|"Settings"|"Profile")=>void}){
  const t=useText();
  return <section className="page"><span className="eyebrow">{page==='AI'?t("ai.webEyebrow"):t("plugin.personal")}</span><h1>{t("nav."+page.toLowerCase())}</h1><div className="card placeholder"><div className="placeholder-art" aria-hidden="true">{page==='AI'?'✧':'⊞'}</div><span className="pill">{page==='AI'?t("ai.building"):t("plugin.currentUnavailable")}</span><h2>{page==='AI'?t("ai.webTitle"):t("plugin.webTitle")}</h2><p>{page==='AI'?t("ai.webDescription"):t("plugin.webDescription")}</p><p className="muted">{t("placeholder.continue")}</p><button onClick={()=>setPage('Chat')}>{t("placeholder.back")}</button></div></section>;
}
