import {useText,useDisplayText} from "../i18n/context.js";
import React from "react";
import type {View} from "../../application/client.js";
export function ProfilePanel({v,loadProfile,refresh,logout}:{v:Pick<View,"profileBusy"|"profileError"|"user"|"authBusy">;loadProfile:()=>Promise<void>;refresh:()=>Promise<void>;logout:()=>Promise<void>}){
  const t=useText();const display=useDisplayText();
  return <section className="page"><span className="eyebrow">{t("profile.account")}</span><h1>{t("nav.profile")}</h1><div className="card profile"><button onClick={()=>void loadProfile()} disabled={v.profileBusy}>{t("profile.refresh")}</button>{v.profileBusy?<p role="status">{t("profile.loading")}</p>:v.profileError?<p className="error" role="alert">{display(v.profileError)}</p>:v.user?<><span className="avatar large">{v.user.displayName.slice(0,1)}</span><h2>{v.user.displayName}</h2><p>@{v.user.username}</p></>:<p>{t("profile.empty")}</p>}<hr/><h3>{t("profile.webSession")}</h3><p className="muted">{t("profile.webSecurity")}</p><button onClick={()=>void refresh()} disabled={v.authBusy}>{t("auth.refresh")}</button><button onClick={()=>void logout()} disabled={v.authBusy}>{t("auth.signOut")}</button></div></section>;
}
