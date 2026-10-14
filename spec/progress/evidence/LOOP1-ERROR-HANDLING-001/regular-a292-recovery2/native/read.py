import sys,pathlib,json
for arg in sys.argv[1:]:
 p=pathlib.Path(arg)
 print('\nFILE '+str(p)+'\n'+p.read_text(encoding='utf-8'))
