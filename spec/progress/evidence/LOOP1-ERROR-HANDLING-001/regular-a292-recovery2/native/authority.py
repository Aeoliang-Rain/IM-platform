import pathlib,sys,re
s=pathlib.Path('spec/architecture/frozen-architecture.md').read_text(encoding='utf-8')
for n in map(int,sys.argv[1:]):
 a=s.index('<a id="section-'+str(n)+'"></a>'); m=re.search(r'<a id="section-\d+"></a>',s[a+1:]); b=a+1+m.start() if m else len(s); print(s[a:b])
