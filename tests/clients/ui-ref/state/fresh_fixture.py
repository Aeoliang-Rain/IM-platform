"""Register only unique disposable STATE accounts through actual canonical Go HTTP."""
from pathlib import Path
import json,ssl,urllib.request,uuid,sys
runtime=Path('C:/Users/21441/.codex/visualizations/2026/10/11/01a129aa-d2ed-7350-8f8d-efb0ecc85664/ui-ref-runtime')
context=ssl.create_default_context(cafile=str(runtime/'tls-ui-ref/ca.pem'))
new_friends='--new-friends-owner' in sys.argv
previous=json.loads((runtime/'fresh-public.json').read_text()) if '--rotate-targets' in sys.argv else None
accounts=[previous['accounts'][0]] if previous else []
for label in (['WebFriend','DesktopFriend','MobileFriend','OfflineFriend'] if previous else ['Fresh','WebFriend','DesktopFriend','MobileFriend','OfflineFriend']):
 username='state_'+label.lower()+'_'+uuid.uuid4().hex[:10]
 body=json.dumps({'username':username,'password':'fixture-password-not-a-real-secret','displayName':'STATE '+label+(' '+username.rsplit('_',1)[1] if previous or new_friends else '')}).encode()
 request=urllib.request.Request('https://localhost:8443/v1/auth/register',data=body,headers={'Content-Type':'application/json'},method='POST')
 with urllib.request.urlopen(request,context=context,timeout=15) as response:
  assert response.status==201
  user=json.load(response)['user'];accounts.append({k:user[k] for k in ['userId','username','displayName']})
result={**(previous or {}),'project':json.loads((Path('C:/Users/21441/.codex/visualizations/2026/10/11/01a129aa-d2ed-7350-8f8d-efb0ecc85664/ui-ref-runtime')/'go-public.json').read_text())['project'],'endpoint':'https://localhost:8443','accounts':accounts,'source':'actual Go register201; unique disposable accounts; no native database reset'}
if previous or new_friends:
    label='friends-fixture-'+uuid.uuid4().hex
    private_target=runtime/(label+'.json');public_target=Path('spec/progress/evidence/LOOP1-CLIENT-UI-REF-001')/(label+'.json')
    result['qualification']=('Independent new controlled Friends owner/four targets isolate accumulated historical fixture load; original fresh-public owner/relationships/DB/evidence unchanged' if new_friends else 'Existing owned fresh account retained; four new targets via actual register201; earlier target friendships/data retained')
else:
    private_target=runtime/'fresh-public.json';public_target=Path('spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/fresh-fixture-public.json')
private_target.write_text(json.dumps(result,indent=2),encoding='utf-8');public_target.write_text(json.dumps(result,indent=2),encoding='utf-8')
print('PASS actual Go HTTP201 disposable accounts; output '+str(private_target))
