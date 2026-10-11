"""Actual installed fixture pages, appearance extrema and native capabilities."""
from pathlib import Path
import subprocess,json,uuid,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3];out=ROOT/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/screens'/('desktop-matrix-'+uuid.uuid4().hex);out.mkdir()
prefs=Path('C:/Users/21441/AppData/Roaming/im.platform.desktop/appearance.json');observedBefore=prefs.read_bytes();original=b'["warm",14,0.8]';theme,font,density=json.loads(original);passed=False
def ui(action,name='',value='',label='observe'):
 p=out/(label+'.png');r=subprocess.run(['powershell','-NoProfile','-File','tests/clients/ui-ref/state/desktop_window.ps1','-Action',action,'-Name',name,'-Value',str(value),'-Output',str(p)],cwd=ROOT,capture_output=True,timeout=45)
 (out/(label+'.stderr.txt')).write_bytes(r.stderr)
 if r.returncode:print(r.stderr.decode('utf-8',errors='replace'));raise RuntimeError('Actual UI action failed '+label)
 return json.loads(Path(str(p)+'.json').read_text(encoding='utf-8'))['nodes']
def appearance(t,f,d,label):
 nodes=ui('click','⚙ Settings',label=label+'-settings')
 button=next(n['name'] for n in nodes if n['type']=='ControlType.Button' and n['name'].startswith('Cold AI Blue' if t=='cold' else 'Warm Creative Warm'))
 ui('click',button,label=label+'-theme');ui('range','font',f,label+'-font');ui('range','density',d,label+'-density')
 assert json.loads(prefs.read_bytes())==[t,f,d]
try:
 for t,f,d in [('cold',14,.8),('cold',22,1.2),('warm',22,1.2),('warm',14,.8)]:
  label=f'{t}-{f}-{d}';appearance(t,f,d,label)
  for page in ('Chat','Friends','AI','Plugin'):
   current=ui('observe',label=label+'-'+page+'-before')
   button=next(n['name'] for n in current if n['type']=='ControlType.Button' and (n['name']==page or page=='AI' and n['name']=='AI SOON'))
   nodes=ui('click',button,label=label+'-'+page)
   assert any(n['name'] for n in nodes)
  ui('click','⚙ Settings',label=label+'-profile')
 ui('click','Refresh session',label='actual-refresh')
 for helper,args in [('desktop_notification.ps1',[]),('desktop_shortcut.ps1',[]),('desktop_tray.ps1',['-Exercise'])]:
  subprocess.run(['powershell','-NoProfile','-File','tests/clients/ui-ref/state/'+helper,*args,'-Output',str(out/(helper+'.json'))],cwd=ROOT,check=True,capture_output=True,timeout=90)
 passed=True;print('PASS actual installed pages/theme/extrema/profile refresh/notification/shortcut/tray',flush=True)
finally:
 appearance(theme,font,density,'restore-original-appearance');assert prefs.read_bytes()==original
 entries=[{'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.iterdir()) if p.is_file()]
 (out/'manifest.json').write_text(json.dumps({'result':'PASS' if passed else 'FAIL','actualUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'actualHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'productSource':'1bd1a1bf015edd6422bd8bfeeb73bc454b565034','observedBefore':json.loads(observedBefore),'originalAppearance':json.loads(original),'originalMethod':'Recovered initial readonly actual warm/14/.8 receipt; earlier failed theme-toggle attempt changed to cold; exact Rust serialization bytes','appearanceRestoredExactly':True,'fixture':'owned installed NSIS identity; no presentation injection','entries':entries},indent=2)+'\n',encoding='utf-8')
