import pathlib,json,collections
j=json.loads(pathlib.Path('spec/progress/evidence/LOOP1-ERROR-HANDLING-001/production-inventory.json').read_text());s=[x for x in j['retained_sites'] if x['path'].startswith(('clients/desktop/','clients/mobile/'))]
print(len(s));print(json.dumps(s[:6],indent=2));print(collections.Counter(x['path'] for x in s))
pathlib.Path(__file__).with_name('sites-original.json').write_text(json.dumps(s,indent=2))
