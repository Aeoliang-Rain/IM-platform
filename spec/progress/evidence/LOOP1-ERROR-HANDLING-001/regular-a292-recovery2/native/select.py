import pathlib,json,collections
j=json.loads(pathlib.Path('spec/progress/evidence/LOOP1-ERROR-HANDLING-001/production-inventory.json').read_text())
f=[x for x in j['files'] if x['path'].startswith(('clients/desktop/','clients/mobile/'))]
print('keys',j.keys(),'files',len(f));print('\n'.join(x['path'] for x in f)); print('othercollections',[(k,len(v)) for k,v in j.items() if isinstance(v,list)])
pathlib.Path(__file__).with_name('selected.json').write_text(json.dumps(f,indent=2))
