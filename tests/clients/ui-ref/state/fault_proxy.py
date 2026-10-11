"""Loopback-only fault relay to the actual Go TLS fixture; never fabricates ACKs/messages."""
from pathlib import Path
import base64,hashlib,http.client,http.server,json,mimetypes,socket,ssl,struct,threading,time,os
ROOT=Path(__file__).resolve().parents[4]
PRIVATE=Path(os.environ.get('IM_GUI_PRIVATE_RUNTIME','C:/Users/21441/.codex/visualizations/2026/10/11/01a129aa-d2ed-7350-8f8d-efb0ecc85664/ui-ref-runtime'))
TLS=PRIVATE/'tls-ui-ref'
mimetypes.add_type('application/javascript','.mjs')
CA=ssl.create_default_context(cafile=str(TLS/'ca.pem'))
lock=threading.RLock();events=[];fault=None;held={};attempts={};sessions={};connections={}
def record(kind,**data):
 with lock:events.append({'event':len(events)+1,'kind':kind,**data})
def exact(s,n):
 out=b''
 while len(out)<n:
  b=s.recv(n-len(out))
  if not b:raise EOFError()
  out+=b
 return out
def packet(s):
 head=exact(s,2);n=head[1]&127;extra=b''
 if n==126:extra=exact(s,2);n=struct.unpack('!H',extra)[0]
 elif n==127:extra=exact(s,8);n=struct.unpack('!Q',extra)[0]
 if n>65536:raise RuntimeError('Controlled frame bound exceeded')
 mask=exact(s,4) if head[1]&128 else b'';body=exact(s,n)
 raw=head+extra+mask+body
 if mask:body=bytes(v^mask[i%4] for i,v in enumerate(body))
 return raw,(head[0]&15),body
class Handler(http.server.BaseHTTPRequestHandler):
 protocol_version='HTTP/1.1'
 def log_message(self,*a):pass
 def answer(self,status,body,headers=()):
  self.send_response(status)
  for k,v in headers:
   if k.lower() not in ('content-length','transfer-encoding','connection'):self.send_header(k,v)
  self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
 def do_POST(self):self.handle_request()
 def do_PUT(self):self.handle_request()
 def do_GET(self):self.handle_request()
 def handle_request(self):
  global fault
  if self.path=='/v1/ws':return self.websocket()
  body=self.rfile.read(int(self.headers.get('Content-Length','0')))
  if self.path=='/__state/control':
   data=json.loads(body)
   with lock:fault={'mode':data['mode'],'text':data['text'],'userId':data.get('userId'),'clientType':data.get('clientType')}
   record('arm',**fault);return self.answer(200,b'{}',[('Content-Type','application/json')])
  if self.path=='/__state/stop':
   self.answer(200,b'{}');threading.Thread(target=self.server.shutdown,daemon=True).start();return
  if self.path=='/__state/disconnect':
   data=json.loads(body)
   with lock:targets=[pair for token,pair in connections.items() if sessions.get(token)==(data['userId'],data['clientType'])]
   if not targets:return self.answer(409,b'{}')
   record('controlled_disconnect',userId=data['userId'],clientType=data['clientType'],connections=len(targets))
   for pair in targets:
    for sock in pair:
     try:sock.shutdown(socket.SHUT_RDWR)
     except OSError:pass
   return self.answer(200,b'{}')
  if self.path=='/__state/events':
   with lock:data=json.dumps(events).encode()
   return self.answer(200,data,[('Content-Type','application/json')])
  if self.path in ('/v1/sync/user','/v1/sync/conversation'):
   supplied=json.loads(body);sync_token=self.headers.get('Authorization','').removeprefix('Bearer ')
   with lock:identity=sessions.get(sync_token)
   record('sync_request',path=self.path,cursor=supplied.get('cursor'),afterSeq=supplied.get('afterSeq'),conversationId=supplied.get('conversationId'),userId=identity[0] if identity else None,clientType=identity[1] if identity else None)
  if self.path=='/v1/sync/conversation':
   token=self.headers.get('Authorization','').removeprefix('Bearer ')
   with lock:block=any(h['token']==token and h['conversationId']==json.loads(body)['conversationId'] for h in held.values()) or bool(fault and fault['mode']=='B' and sessions.get(token)==(fault['userId'],fault['clientType']))
   if block:
    record('held_sender_sync',conversationId=json.loads(body)['conversationId'])
    return self.answer(503,b'{}',[('Content-Type','application/json')])
  if not self.path.startswith('/v1/') and self.path!='/__infra/health':
   path=PRIVATE/'web-build'/self.path.lstrip('/').split('?',1)[0]
   if self.path=='/':path=PRIVATE/'web-build/index.html'
   if not path.resolve().is_relative_to((PRIVATE/'web-build').resolve()) or not path.is_file():return self.answer(404,b'')
   return self.answer(200,path.read_bytes(),[('Content-Type',mimetypes.guess_type(path)[0] or 'application/octet-stream')])
  upstream=http.client.HTTPSConnection('localhost',18443,context=CA,timeout=20)
  try:
   headers={k:v for k,v in self.headers.items() if k.lower() not in ('host','connection','content-length')}
   upstream.request(self.command,self.path,body or None,headers);response=upstream.getresponse();content=response.read()
   if self.path in ('/v1/auth/login','/v1/auth/refresh/native','/v1/auth/logout'):
    code=None
    if response.status>=400:
     try:code=json.loads(content).get('error',{}).get('code')
     except (ValueError,AttributeError):pass
    record('actual_auth_response',path=self.path,status=response.status,errorCode=code)
   if self.path=='/v1/sync/conversation':
    token=self.headers.get('Authorization','').removeprefix('Bearer ')
    with lock:block=any(h['token']==token for h in held.values())
    if block:record('held_inflight_sender_sync');return self.answer(503,b'{}',[('Content-Type','application/json')])
   self.answer(response.status,content,response.getheaders())
  finally:upstream.close()
 def websocket(self):
  remote=CA.wrap_socket(socket.create_connection(('localhost',18443),timeout=10),server_hostname='localhost');remote.settimeout(None)
  remote.sendall(('GET /v1/ws HTTP/1.1\r\nHost: '+self.headers['Host']+'\r\n'+''.join(k+': '+v+'\r\n' for k,v in self.headers.items() if k.lower()!='host')+'\r\n').encode())
  head=b''
  while not head.endswith(b'\r\n\r\n'):head+=exact(remote,1)
  if not head.startswith(b'HTTP/1.1 101 '):raise RuntimeError('Actual upstream upgrade refused')
  self.connection.sendall(head);self.close_connection=True;token=[None]
  def pump(source,dest,direction):
   global fault
   try:
    while True:
     raw,opcode,payload=packet(source)
     f=json.loads(payload) if opcode==1 else None
     drop=False
     with lock:
      if f and direction=='up' and f['type']=='auth.bind':token[0]=f['payload']['accessToken']
      if f and direction=='down' and f['type']=='auth.ack' and f['payload'].get('status')=='bound':
       sessions[token[0]]=(f['payload']['userId'],f['payload']['clientType']);connections[token[0]]=(self.connection,remote)
      if f and direction=='up' and f['type']=='message.send':
       r=f['requestId'];attempts[r]=attempts.get(r,0)+1
       record('send',requestId=r,conversationId=f['payload']['conversationId'],content=f['payload']['content'],attempt=attempts[r])
       if r in held:
        held.pop(r);record('retry_release',requestId=r)
       elif fault and f['payload']['content'].get('text')==fault['text']:
        mode=fault['mode'];fault=None
        if mode=='A':drop=True;record('not_forwarded',requestId=r)
        elif mode=='B':held[r]={'token':token[0],'conversationId':f['payload']['conversationId']};record('hold_confirmation',requestId=r)
      if f and direction=='down' and f['type']=='message.ack':
       r=f['requestId'];record('actual_ack',requestId=r,payload=f['payload'],held=r in held)
       drop=r in held
      if f and direction=='down' and f['type']=='message.created':
       record('actual_created',requestId=f['requestId'],payload=f['payload'])
       drop=f['requestId'] in held and held[f['requestId']]['token']==token[0]
     if not drop:dest.sendall(raw)
   except (OSError,EOFError):pass
   finally:
    try:dest.shutdown(socket.SHUT_RDWR)
    except OSError:pass
  worker=threading.Thread(target=pump,args=(remote,self.connection,'down'),daemon=True);worker.start()
  pump(self.connection,remote,'up')
  with lock:
   if connections.get(token[0])==(self.connection,remote):connections.pop(token[0],None)
  remote.close()
server=http.server.ThreadingHTTPServer(('127.0.0.1',8443),Handler)
context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.load_cert_chain(str(TLS/'server.pem'),str(TLS/'server.key'));server.socket=context.wrap_socket(server.socket,server_side=True)
print('READY actual-Go fault relay https://localhost:8443; no fabricated confirmation',flush=True)
try:server.serve_forever()
finally:server.server_close();(PRIVATE/('fault-events-'+str(time.time_ns())+'.json')).write_text(json.dumps(events,indent=2)+'\n')
