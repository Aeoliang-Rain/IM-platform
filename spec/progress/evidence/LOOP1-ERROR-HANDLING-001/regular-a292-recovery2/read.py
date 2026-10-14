from pathlib import Path
import sys,re
R=Path.cwd()
for a in sys.argv[1:]:
 name,_,section=a.partition('#');p=R/name;t=p.read_text('utf-8-sig')
 if section:
  start=t.index('<a id="section-'+section+'"></a>'); end=t.find('<a id="section-',start+1)
  if section.isdigit():
   m=re.search(r'<a id="section-\d+"></a>',t[start+1:]);end=start+1+m.start() if m else len(t)
  t=t[start:end if end!=-1 else len(t)]
 print('\nFILE '+a+'\n'+t)
