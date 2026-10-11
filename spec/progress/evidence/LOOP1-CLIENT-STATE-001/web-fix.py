from pathlib import Path
p=Path('clients/web/src/application/client.ts');s=p.read_text(encoding='utf-8')
s=s.replace('private reconnectTimer?:','private userCursor="0";private userSyncing=false;private userPoll?:ReturnType<typeof setInterval>;private reconnectTimer?:',1)
s=s.replace('clearTimeout(this.reconnectTimer);clearTimeout(this.refreshTimer);','clearTimeout(this.reconnectTimer);clearTimeout(this.refreshTimer);clearInterval(this.userPoll);this.userPoll=undefined;this.userCursor="0";this.userSyncing=false;',1)
s=s.replace("this.publish({connection:'在线'});for(const c", "this.publish({connection:'在线'});void this.syncFriends();if(!this.userPoll)this.userPoll=setInterval(()=>{if(this.state.connection==='在线')void this.syncFriends();},10000);for(const c",1)
needle='  async sync(c:string){'
method="""  private async syncFriends(){
    const s=this.session,g=this.generation;if(!s||this.userSyncing)return;
    this.userSyncing=true;
    try{const http=new SyncHttp(this.http.origin,s,this.fetcher);
      for(;;){const cursor=this.userCursor,page=await http.user(cursor,this.abort.signal);if(!this.alive(g))return;
        // Consume metadata by re-reading the canonical friend projection; no history pull.
        if(page.events.length){const list=friends(await this.http.request('/v1/friends','GET',undefined,s.accessToken,this.abort.signal));if(!this.alive(g))return;
          if(list.some(f=>f.user.userId===s.userId))throw new Error('Invalid friend');
          this.publish({friends:list,friendsBusy:false,friendsError:''});
        }
        this.userCursor=page.nextCursor;if(!page.hasMore)break;
      }
    }catch(e){this.error(e,g);if(this.alive(g))this.publish({friendsError:'好友同步失败，可重试或重连。'});}
    finally{if(this.alive(g))this.userSyncing=false;}
  }
"""
s=s.replace(needle,method+needle,1);p.write_text(s,encoding='utf-8',newline='\n')
print('Web user metadata polling and canonical friend projection; memory cursor only')

