import React from "react";

export function Placeholder({page,setPage}:{page:"AI"|"Plugin";setPage:(page:"Chat"|"Friends"|"AI"|"Plugin"|"Settings"|"Profile")=>void}){
  return <section className="page"><span className="eyebrow">{page==='AI'?'FUTURE COMMUNICATION':'PERSONAL CAPABILITIES'}</span><h1>{page}</h1><div className="card placeholder"><div className="placeholder-art" aria-hidden="true">{page==='AI'?'✧':'⊞'}</div><span className="pill">{page==='AI'?'施工中':'当前不可用'}</span><h2>{page==='AI'?'新的想法，正在构建':'你的扩展空间'}</h2><p>{page==='AI'?'AI 通信入口已预留。当前不提供 AI 聊天、工具调用或生成结果。':'当前尚未开放插件能力与已安装清单。此页面没有插件运行、安装或商店功能。'}</p><p className="muted">继续使用 Chat 与 Friends，连接真实的人。</p><button onClick={()=>setPage('Chat')}>返回聊天 →</button></div></section>;
}
