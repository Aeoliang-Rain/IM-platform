import React from "react";
import type {View} from "../../application/client.js";
import type {MemoryRepository} from "../../application/repository.js";
export function Messages({v,messages,retry}:{v:Pick<View,"user">;messages:ReturnType<MemoryRepository["snapshot"]>;retry:(conversation:string,request:string)=>void}){
  return <div className="messages" aria-live="polite">{!messages.length&&<div className="empty"><span>◌</span><h3>从此刻开始</h3><p>这里只展示本页实时消息，不补聊天历史。<br/>发一句问候，开启新的交流。</p></div>}{messages.map(m=><article key={m.requestId} className={'message '+(m.senderId===v.user?.userId?'own':'')}><p>{m.content.text}</p><div className="message-meta"><span>{m.state==='SENDING'?'SENDING · 发送中':m.state==='SENT'?'SENT · 已确认':'FAILED · 未确认'}</span>{m.state==='FAILED'&&<button onClick={()=>retry(m.conversationId,m.requestId)}>重试</button>}{m.seq!==undefined&&<span>#{m.seq.toString()}</span>}</div></article>)}</div>;
}
