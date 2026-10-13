"""Reproducible en/ja JSON artifacts only. No network, publication or runtime installation."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import tempfile

TASK='LOOP1-CLIENT-I18N-001'
ROOT=Path(__file__).resolve().parents[1]
LOCALES=('en','zh-CN','ja-JP')

def unique_object(pairs):
    result={}
    for key,value in pairs:
        if key in result or key in ('__proto__','constructor','prototype'):
            raise ValueError('duplicate or unsafe resource key: '+key)
        result[key]=value
    return result

def parse_json(raw):
    return json.loads(raw,object_pairs_hook=unique_object)

def validate(data):
    if set(data)!=set(LOCALES):raise ValueError('three built-in locales required')
    keys=set(data['en'])
    if not keys:raise ValueError('English base must be complete and nonempty')
    for locale,table in data.items():
        if set(table)!=keys:raise ValueError('resource keys differ: '+locale)
        for key,value in table.items():
            if not isinstance(key,str) or not isinstance(value,str):raise ValueError('resource must contain strings only')
            if key in ('__proto__','constructor','prototype'):raise ValueError('unsafe resource key')
            if sorted(re.findall(r'\{([A-Za-z]+)\}',value))!=sorted(re.findall(r'\{([A-Za-z]+)\}',data['en'][key])):
                raise ValueError('placeholder mismatch: '+locale+'/'+key)

def sources(root):
    all_data={}
    for locale in LOCALES:
        raw=(root/'clients/web/src/ui/i18n'/f'{locale}.ts').read_text(encoding='utf-8')
        if not raw.startswith('export default '):raise ValueError('pure data resource required')
        table=parse_json(raw[len('export default '):].strip().removesuffix(';'))
        other=(root/'clients/desktop/src/ui/i18n'/f'{locale}.ts').read_text(encoding='utf-8')
        if not other.startswith('export default '):raise ValueError('pure Desktop data required')
        if table!=parse_json(other[len('export default '):].strip().removesuffix(';')):raise ValueError('Desktop data mismatch')
        name={'en':'en','zh-CN':'zhCN','ja-JP':'jaJP'}[locale]
        kotlin=(root/'clients/mobile/app/src/main/kotlin/im/platform/client/ui/i18n'/f'{name}.kt').read_text(encoding='utf-8')
        pairs=[]
        for match in re.finditer(r'("(?:[^"\\]|\\.)*") to ("(?:[^"\\]|\\.)*")',kotlin):
            pairs.append(tuple(json.loads(value.replace('\\$','$')) for value in match.groups()))
        if table!=unique_object(pairs):raise ValueError('Android data mismatch')
        all_data[locale]=table
    validate(all_data)
    return all_data

def encode(value):
    return (json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf-8')

def artifacts(data):
    validate(data)
    files={locale+'.json':encode({'artifactVersion':1,'locale':locale,'messages':data[locale]}) for locale in ('en','ja-JP')}
    metadata={'generatedBy':'tools/build_language_packs.py','task':TASK,'publication':'NOT_PUBLISHED','artifacts':[]}
    for name,raw in sorted(files.items()):
        metadata['artifacts'].append({'file':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    files['manifest.json']=encode(metadata)
    return files

def write_owned(directory,files):
    directory=directory.resolve()
    if directory.exists() and any(directory.iterdir()):
        manifest=directory/'manifest.json'
        if not manifest.is_file() or manifest.is_symlink():raise ValueError('existing output is not owned')
        prior=parse_json(manifest.read_bytes())
        if prior.get('generatedBy')!='tools/build_language_packs.py' or prior.get('task')!=TASK:raise ValueError('unknown output owner')
        if any(path.name not in files or path.is_symlink() for path in directory.iterdir()):raise ValueError('unknown output preserved')
    directory.mkdir(parents=True,exist_ok=True)
    for name,raw in files.items():
        path=directory/name
        if path.exists() and path.read_bytes()==raw:continue
        with tempfile.NamedTemporaryFile(dir=directory,prefix='.i18n-owned-',delete=False) as stream:
            temporary=Path(stream.name);stream.write(raw)
        try:temporary.replace(path)
        finally:
            if temporary.exists():temporary.unlink()

def verify(root):
    data=sources(root);first=artifacts(data);second=artifacts(sources(root))
    if first!=second:raise ValueError('nondeterministic artifacts')
    with tempfile.TemporaryDirectory(prefix='i18n-artifacts-') as temporary:
        output=Path(temporary);write_owned(output,first);write_owned(output,second)
        if {path.name:path.read_bytes() for path in output.iterdir()}!=first:raise ValueError('written artifact mismatch')
    for name in ('en.json','ja-JP.json'):
        if parse_json(first[name])['messages']!=data[name.removesuffix('.json')]:raise ValueError('artifact body mismatch')
    return first

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify',action='store_true',help='verify in owned temporary output; no repository writes')
    parser.add_argument('--output',type=Path,default=ROOT/'tests/clients/i18n/.runtime/language-packs')
    args=parser.parse_args();files=verify(ROOT)
    if not args.verify:write_owned(args.output,files)
    print('PASS deterministic en/ja JSON artifact build; NOT_PUBLISHED; download/install deferred')
    return 0

if __name__=='__main__':raise SystemExit(main())
