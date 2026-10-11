import React from "react";

export function Composer({text,setText,send}:{text:string;setText:(value:string)=>void;send:(text:string)=>unknown}){
  return <form className="composer" onSubmit={e=>{e.preventDefault();if(text.trim()){send(text);setText('');}}}><label className="sr-only" htmlFor="message">消息</label><textarea id="message" placeholder="写一条消息…" value={text} maxLength={4096} onChange={e=>setText(e.target.value)} rows={2}/><button className="primary" disabled={!text.trim()}>发送 ↑</button><small>仅在线内存态 · 未确认消息可使用相同身份重试</small></form>;
}
