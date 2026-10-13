import {useText,useDisplayText} from "../i18n/context.js";
import React from "react";
import type {View} from "../../application/client.js";
import {connectionText} from "./status.js";
export function Header({page,setPage,v,logout}:{page:"Chat"|"Friends"|"AI"|"Plugin"|"Settings"|"Profile";setPage:(page:"Chat"|"Friends"|"AI"|"Plugin"|"Settings"|"Profile")=>void;v:Pick<View,"session"|"connection"|"authBusy"|"notice">;logout:()=>Promise<void>}){
  const t=useText();const display=useDisplayText();
  return <><header className="top"><span className="eyebrow">{v.session?t("header.online"):t("header.welcome")}</span><div className="top-actions"><span className="connection" role="status">{t("connection."+v.connection)}</span>{!v.session&&page==='Settings'&&<button onClick={()=>setPage('Chat')}>{t("auth.back")}</button>}{v.session&&<button onClick={()=>void logout()} disabled={v.authBusy}>{t("auth.signOut")}</button>}</div></header>{v.notice&&<div className="notice" role="status">{display(v.notice)}</div>}</>;
}
