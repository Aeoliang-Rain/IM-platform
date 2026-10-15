import pathlib,json,sys
ss=json.loads(pathlib.Path(__file__).with_name('sites-original.json').read_text())
for s in ss[int(sys.argv[1]):int(sys.argv[2])]:print(s['id'],s['path'].split('/')[-1],s['line'],s['column'],s['source'])
