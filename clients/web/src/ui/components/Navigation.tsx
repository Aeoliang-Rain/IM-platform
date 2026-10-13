import {useText} from "../i18n/context.js";
import React from "react";
import type {View} from "../../application/client.js";
function Logo(){const t=useText();return <img className="logo" src="logo.png" alt={t("brand.logo")}/>;}
export function Navigation({page,setPage,v,loadProfile}:{page:"Chat"|"Friends"|"AI"|"Plugin"|"Settings"|"Profile";setPage:(page:"Chat"|"Friends"|"AI"|"Plugin"|"Settings"|"Profile")=>void;v:Pick<View,"session">;loadProfile:()=>Promise<void>}){
  const t=useText();
  return <aside className="rail"><a className="brand" href="#" onClick={e=>e.preventDefault()}><Logo/><span>IM<span className="brand-plus">+</span><small>PLUGWORLDIM</small></span></a><div className="rail-note">{t("nav.onlineWorkspace")}</div><nav aria-label={t("nav.main")}>{(['Chat','Friends','AI','Plugin'] as const).map((p,i)=><button key={p} className={page===p?'nav selected':'nav'} onClick={()=>setPage(p)} disabled={!v.session}><span aria-hidden="true">{['◌','◫','✧','⊞'][i]}</span>{t("nav."+p.toLowerCase())}<small>{t(["nav.chat","nav.friends","nav.future","nav.extensions"][i])}</small></button>)}</nav><div className="rail-footer"><button className={page==='Settings'?'nav selected':'nav'} onClick={()=>setPage('Settings')}>{t("nav.settings")}</button>{v.session&&<button className={page==='Profile'?'nav selected':'nav'} onClick={()=>{setPage('Profile');void loadProfile();}}>{t("nav.profile")}</button>}<p className="tiny">{t("web.railLine1")}<br/>{t("web.railLine2")}</p></div></aside>;
}
