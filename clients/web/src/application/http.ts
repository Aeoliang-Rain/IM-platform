import {object,uuid,parse,positive} from '../../../shared/protocol-sdk/src/send/wire.js';
export interface User {userId:string;username:string;displayName:string}
export interface Friend {user:User;friendshipId:string;directConversationId:string}
export interface Session {userId:string;sessionId:string;sessionEpoch:bigint;accessToken:string;expires:number}
export class ApiFailure extends Error {constructor(readonly code:string,readonly status:number){super(code);}}
const invalid=():never=>{throw new ApiFailure('INVALID_RESPONSE',0);};
export function user(v:unknown):User {const p=object(v,['userId','username','displayName']);if(typeof p.username!=='string'||!/^[A-Za-z0-9][A-Za-z0-9._-]{2,63}$/.test(p.username)||typeof p.displayName!=='string')return invalid();return {userId:uuid(p.userId),username:p.username,displayName:p.displayName};}
export function friends(v:unknown):Friend[]{const p=object(v,['friends']);if(!Array.isArray(p.friends))return invalid();const ids=new Set<string>();return p.friends.map(v=>{const f=object(v,['user','friendshipId','directConversationId']),u=user(f.user);if(ids.has(u.userId))return invalid();ids.add(u.userId);return {user:u,friendshipId:uuid(f.friendshipId),directConversationId:uuid(f.directConversationId)};});}
export function auth(v:unknown):Session {
  const p=object(v,['session','tokens','replacedExistingSession']),s=object(p.session,['sessionId','userId','clientType','sessionEpoch','status']),t=object(p.tokens,['accessToken','accessTokenExpiresInSeconds','refreshTokenDelivery']);
  if(s.clientType!=='WEB'||s.status!=='ACTIVE'||typeof p.replacedExistingSession!=='boolean'||t.refreshTokenDelivery!=='HTTP_ONLY_SECURE_COOKIE'||typeof t.accessToken!=='string'||!t.accessToken||/[\r\n]/.test(t.accessToken))return invalid();
  const seconds=positive(t.accessTokenExpiresInSeconds);if(seconds>2147483n)return invalid();
  return {userId:uuid(s.userId),sessionId:uuid(s.sessionId),sessionEpoch:positive(s.sessionEpoch),accessToken:t.accessToken,expires:Date.now()+Number(seconds)*1000};
}
export class Http {
  readonly origin:string;
  constructor(origin:string,private fetcher:typeof fetch=(input,init)=>fetch(input,init)){const u=new URL(origin);if(u.protocol!=='https:'||u.username||u.password||u.search||u.hash||u.pathname!=='/')throw new ApiFailure('HTTPS_REQUIRED',0);this.origin=u.origin;}
  async request(path:string,method:string,body:unknown,token:string|undefined,signal:AbortSignal):Promise<unknown>{
    const encoded=body===undefined?undefined:JSON.stringify(body);
    let r:Response;try {r=await this.fetcher(this.origin+path,{method,body:encoded,headers:{'Content-Type':'application/json',...(token?{'Authorization':'Bearer '+token}:{})},credentials:'same-origin',redirect:'error',cache:'no-store',signal});}catch(error){if(error instanceof TypeError || error instanceof DOMException)throw new ApiFailure('CONNECTION_UNAVAILABLE',0);throw error;}
    if(path==='/v1/auth/logout'&&method==='POST'){
      if(r.redirected)return invalid();
      if(r.status===204){
        // Browsers may expose an empty stream for a no-content HTTP response.
        if(r.body){const reader=r.body.getReader();let primary:{error:unknown}|undefined,sourceFailure:{error:unknown}|undefined;try{let part:ReadableStreamReadResult<Uint8Array>;try{part=await reader.read();}catch(error){sourceFailure={error};if(error instanceof TypeError || error instanceof DOMException)throw new ApiFailure("CONNECTION_UNAVAILABLE",0);throw error;}if(!part.done)return invalid();}catch(error){primary={error};throw error;} finally {try{await reader.cancel();}catch(error){
        if(primary){
          if(error===primary.error || (sourceFailure && error===sourceFailure.error))throw primary.error;
          const causes=new AggregateError([sourceFailure?sourceFailure.error:primary.error,error],"Response processing and cleanup failed");
          if(primary.error instanceof ApiFailure && (error instanceof TypeError || error instanceof DOMException)){
            const failure=new ApiFailure(primary.error.code,primary.error.status);
            Object.defineProperty(failure,"cause",{value:causes});throw failure;
          }
          throw causes;
        }
        if(error instanceof TypeError || error instanceof DOMException)throw new ApiFailure("CONNECTION_UNAVAILABLE",0);throw error;}}}
        return undefined;
      }
      if(r.ok)return invalid();
    }
    if(r.redirected||!/^application\/json(?:\s*;|$)/i.test(r.headers.get('content-type')??''))return invalid();
    let raw='';const reader=r.body?.getReader();if(!reader)return invalid();const decoder=new TextDecoder('utf8',{fatal:true});let size=0;
    let primary:{error:unknown}|undefined,sourceFailure:{error:unknown}|undefined;
    try {for(;;){let part:ReadableStreamReadResult<Uint8Array>;try{part=await reader.read();}catch(error){sourceFailure={error};if(error instanceof TypeError || error instanceof DOMException)throw new ApiFailure("CONNECTION_UNAVAILABLE",0);throw error;}if(part.done)break;size+=part.value.byteLength;if(size>6*1024*1024)return invalid();try{raw+=decoder.decode(part.value,{stream:true});}catch(error){sourceFailure={error};if(error instanceof TypeError)return invalid();throw error;}}try{raw+=decoder.decode();}catch(error){sourceFailure={error};if(error instanceof TypeError)return invalid();throw error;}}catch(error){primary={error};throw error;} finally {try{await reader.cancel();}catch(error){
        if(primary){
          if(error===primary.error || (sourceFailure && error===sourceFailure.error))throw primary.error;
          const causes=new AggregateError([sourceFailure?sourceFailure.error:primary.error,error],"Response processing and cleanup failed");
          if(primary.error instanceof ApiFailure && (error instanceof TypeError || error instanceof DOMException)){
            const failure=new ApiFailure(primary.error.code,primary.error.status);
            Object.defineProperty(failure,"cause",{value:causes});throw failure;
          }
          throw causes;
        }
        if(error instanceof TypeError || error instanceof DOMException)throw new ApiFailure("CONNECTION_UNAVAILABLE",0);throw error;}}
    const p=parse(raw,6*1024*1024);
    if(!r.ok){const e=object(p,['requestId','error']);uuid(e.requestId);const detail=e.error as Record<string,unknown>;if(!detail||typeof detail.code!=='string')return invalid();const allowed=['VALIDATION_FAILED','AUTH_REQUIRED','AUTH_TOKEN_INVALID','AUTH_TOKEN_EXPIRED','AUTH_SESSION_REVOKED','AUTH_SESSION_EPOCH_STALE','AUTH_CLIENT_TYPE_MISMATCH','AUTH_REFRESH_REVOKED','AUTH_INVALID_CREDENTIALS','AUTHORIZATION_DENIED','USER_NOT_FOUND','FRIEND_SELF_NOT_ALLOWED','FRIENDSHIP_STATE_CONFLICT','PROTOCOL_VERSION_UNSUPPORTED'];throw new ApiFailure(allowed.includes(detail.code)?detail.code:'REQUEST_FAILED',r.status);}
    return p;
  }
}
