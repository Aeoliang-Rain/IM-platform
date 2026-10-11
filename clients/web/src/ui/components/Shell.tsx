import {Navigation} from "./Navigation.js";
import {Header} from "./Header.js";
import {AuthPanel} from "./AuthPanel.js";
import {ConversationList} from "./ConversationList.js";
import {Messages} from "./Messages.js";
import {Composer} from "./Composer.js";
import {FriendsPanel} from "./FriendsPanel.js";
import {Placeholder} from "./Placeholder.js";
import {SettingsPanel} from "./SettingsPanel.js";
import {ProfilePanel} from "./ProfilePanel.js";
import React,{useState,useEffect,useSyncExternalStore} from 'react';
import {WebClient} from '../../application/client.js';
import {loadAppearance,saveAppearance} from '../appearance.js';
import type {Appearance} from '../appearance.js';
const client=new WebClient(window.location.origin);
export function Shell(){
  const v=useSyncExternalStore(client.subscribe,client.view);const [page,setPage]=useState<"Chat"|"Friends"|"AI"|"Plugin"|"Settings"|"Profile">('Chat'),[prefs,setPrefs]=useState(loadAppearance),[stored,setStored]=useState(true),[username,setUsername]=useState(''),[password,setPassword]=useState(''),[search,setSearch]=useState(''),[searched,setSearched]=useState(false),[text,setText]=useState('');
  useEffect(()=>{document.documentElement.dataset.theme=prefs.theme;document.documentElement.dataset.density=prefs.density;document.documentElement.style.setProperty('--font-size',prefs.fontSize+'px');},[prefs]);
  useEffect(()=>{if(!v.session){setPage('Chat');setText('');setSearch('');setSearched(false);setUsername('');setPassword('');}},[v.session]);
  const loadProfile=client.loadProfile.bind(client),logout=client.logout.bind(client),refresh=client.refresh.bind(client),loadFriends=client.loadFriends.bind(client),reconnect=client.reconnect.bind(client),retry=client.retry.bind(client),send=client.send.bind(client),searchUsers=client.search.bind(client),addFriend=client.addFriend.bind(client),login=client.login.bind(client);
  function appearance(p:Partial<Appearance>){const next={...prefs,...p};setPrefs(next);setStored(saveAppearance(next));}
  function open(c:string){client.open(c);setPage('Chat');}
  const selected=v.friends.find(f=>f.directConversationId===v.selected),messages=client.repository.snapshot(v.selected);
  return <div className="workspace">
    <Navigation page={page} setPage={setPage} v={v} loadProfile={loadProfile}/>
    <div className="main"><Header page={page} setPage={setPage} v={v} logout={logout}/>
    {!v.session&&page!=='Settings'?<AuthPanel v={v} username={username} setUsername={setUsername} password={password} setPassword={setPassword} login={login} refresh={refresh}/>:
    page==='Chat'?<section className="chat-layout"><ConversationList v={v} open={open} setPage={setPage} loadFriends={loadFriends}/><div className="chat-view">{selected?<><div className="chat-heading"><span className="avatar">{selected.user.displayName.slice(0,1)}</span><div><h2>{selected.user.displayName}</h2><p>当前页面的实时消息</p></div><button onClick={()=>reconnect()}>重新连接</button></div>{v.sync&&<p className="sync" role="status">{v.sync}</p>}<Messages v={v} messages={messages} retry={retry}/><Composer text={text} setText={setText} send={send}/></>:<div className="empty chat-empty"><span>◌</span><h2>为有意义的交流留出空间</h2><p>选择左侧会话，开始聊天。</p></div>}</div></section>:
    page==='Friends'?<FriendsPanel v={v} search={search} setSearch={setSearch} searched={searched} setSearched={setSearched} open={open} loadFriends={loadFriends} searchUsers={searchUsers} addFriend={addFriend}/>:
    page==='AI'||page==='Plugin'?<Placeholder page={page} setPage={setPage}/>:
    page==='Settings'?<SettingsPanel prefs={prefs} appearance={appearance} stored={stored}/>:
    <ProfilePanel v={v} loadProfile={loadProfile} refresh={refresh} logout={logout}/>}
    </div></div>;
}

