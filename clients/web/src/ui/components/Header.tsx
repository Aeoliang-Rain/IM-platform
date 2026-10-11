import React from "react";
import type {View} from "../../application/client.js";
import {connectionText} from "./status.js";
export function Header({page,setPage,v,logout}:{page:"Chat"|"Friends"|"AI"|"Plugin"|"Settings"|"Profile";setPage:(page:"Chat"|"Friends"|"AI"|"Plugin"|"Settings"|"Profile")=>void;v:Pick<View,"session"|"connection"|"authBusy"|"notice">;logout:()=>Promise<void>}){
  return <><header className="top"><span className="eyebrow">{v.session?'YOUR ONLINE SPACE':'WELCOME TO YOUR WORKSPACE'}</span><div className="top-actions"><span className="connection" role="status">{connectionText[v.connection]}</span>{!v.session&&page==='Settings'&&<button onClick={()=>setPage('Chat')}>返回登录</button>}{v.session&&<button onClick={()=>void logout()} disabled={v.authBusy}>退出登录</button>}</div></header>{v.notice&&<div className="notice" role="status">{v.notice}</div>}</>;
}
