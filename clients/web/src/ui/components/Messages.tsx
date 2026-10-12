import {useText} from "../i18n/context.js";
import React from "react";
import type {View} from "../../application/client.js";
import type {MemoryRepository} from "../../application/repository.js";
export function Messages({v,messages,retry}:{v:Pick<View,"user">;messages:ReturnType<MemoryRepository["snapshot"]>;retry:(conversation:string,request:string)=>void}){
  const t=useText();
  return <div className="messages" aria-live="polite">{!messages.length&&<div className="empty"><span>◌</span><h3>{t("chat.webStart")}</h3><p>{t("web.emptyChat1")}<br/>{t("web.emptyChat2")}</p></div>}{messages.map(m=><article key={m.requestId} className={'message '+(m.senderId===v.user?.userId?'own':'')}><p>{m.content.text}</p><div className="message-meta"><span>{m.state==='SENDING'?t("chat.webSending"):m.state==='SENT'?t("chat.webSent"):t("chat.webFailed")}</span>{m.state==='FAILED'&&<button onClick={()=>retry(m.conversationId,m.requestId)}>{t("chat.retry")}</button>}{m.seq!==undefined&&<span>#{m.seq.toString()}</span>}</div></article>)}</div>;
}
