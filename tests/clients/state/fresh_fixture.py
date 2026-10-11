"""Register only unique disposable STATE accounts through actual canonical Go HTTP."""
from pathlib import Path
import json,ssl,urllib.request,uuid,sys
runtime=Path('H:/IM-platform/.git/worktrees/IM-platform43/state-runtime')
context=ssl.create_default_context(cafile=str(runtime/'tls-state-week2/ca.pem'))
previous=json.loads((runtime/'fresh-public.json').read_text()) if '--rotate-targets' in sys.argv else None
accounts=[previous['accounts'][0]] if previous else []
for label in (['WebFriend','DesktopFriend','MobileFriend','OfflineFriend'] if previous else ['Fresh','WebFriend','DesktopFriend','MobileFriend','OfflineFriend']):
 username='state_'+label.lower()+'_'+uuid.uuid4().hex[:10]
 body=json.dumps({'username':username,'password':'fixture-password-not-a-real-secret','displayName':'STATE '+label}).encode()
 request=urllib.request.Request('https://localhost:8443/v1/auth/register',data=body,headers={'Content-Type':'application/json'},method='POST')
 with urllib.request.urlopen(request,context=context,timeout=15) as response:
  assert response.status==201
  user=json.load(response)['user'];accounts.append({k:user[k] for k in ['userId','username','displayName']})
result={**(previous or {}),'project':'im-gui-product-20261004-35588','endpoint':'https://localhost:8443','accounts':accounts,'source':'actual Go register201; unique disposable accounts; no native database reset'}
(runtime/'fresh-public.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
Path('spec/progress/evidence/LOOP1-CLIENT-STATE-001/fresh-fixture-public.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('PASS five unique disposable accounts registered via actual Go HTTP201')
