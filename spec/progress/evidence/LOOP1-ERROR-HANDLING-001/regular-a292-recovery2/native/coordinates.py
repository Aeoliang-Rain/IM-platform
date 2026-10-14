import pathlib,json,collections
r=json.loads(pathlib.Path(__file__).with_name('retained-grounds.json').read_text())
for x in r:print(x['id'],x['path'].split('/')[-1],x['line'],x['column'],x['operation'],x['token_class'])
