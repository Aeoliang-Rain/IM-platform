import {useText} from "../i18n/context.js";
import React from "react";

export function Composer({text,setText,send}:{text:string;setText:(value:string)=>void;send:(text:string)=>unknown}){
  const t=useText();
  return <form className="composer" onSubmit={e=>{e.preventDefault();if(text.trim()){send(text);setText('');}}}><label className="sr-only" htmlFor="message">{t("chat.message")}</label><textarea id="message" placeholder={t("chat.write")} value={text} maxLength={4096} onChange={e=>setText(e.target.value)} rows={2}/><button className="primary" disabled={!text.trim()}>{t("chat.send")}</button><small>{t("chat.webHelp")}</small></form>;
}
