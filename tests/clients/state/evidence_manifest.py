"""Read-only original evidence indexing; never relabel an original proof or run result."""
from pathlib import Path
import datetime, hashlib, json, shutil, struct, subprocess

E=Path('spec/progress/evidence/LOOP1-CLIENT-STATE-001')
R=Path('H:/IM-platform/.git/worktrees/IM-platform43/state-research/runs/R-STATE-20261010-IMPL')
events=[json.loads(s) for s in (R/'events.jsonl').read_text(encoding='utf-8').splitlines()]
starts={e['data']['command_id']:e for e in events if e['event_type']=='command_started'}
commands=[];(E/'command-originals').mkdir(exist_ok=True)
for event in events:
    if event['event_type']!='command_finished':continue
    data=event['data'];start=starts[data['command_id']];argv=start['data']['argv']
    row={'commandId':data['command_id'],'argv':argv,'cwd':start['data']['cwd'],'startedUTC':start['timestamp'],'finishedUTC':event['timestamp'],'exit':data['exit_code'],'elapsedMs':data['duration_ms'],'result':data['result'],'originals':{}}
    for stream in ('stdout','stderr'):
        src=R/data[stream+'_blob'];raw=src.read_bytes();digest=hashlib.sha256(raw).hexdigest()
        dst=E/'command-originals'/src.name
        if dst.exists():assert dst.read_bytes()==raw,'Never overwrite original output'
        else:dst.write_bytes(raw)
        row['originals'][stream]={'path':str(dst).replace('\\','/'),'storedBlobSHA256':digest,'recordedRawOutputSHA256':data[stream+'_sha256'],'rawByteEqual':digest==data[stream+'_sha256'],'qualification':'Byte-identical Recorder-persisted blob; where rawByteEqual=false, Recorder UTF8decode/redact/JSONcanonicalization changed stored representation and original captured bytes are unavailable. No trace edited.'}
    commands.append(row)
(E/'command-index.json').write_text(json.dumps({'generatedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'recorderRun':'R-STATE-20261010-IMPL','qualification':'Completed recorded commands only. Outer reads/authoring gaps remain explicit; this index is not a complete prospective trace or Task acceptance. Persisted sanitized blobs are byte-identical copies, including failures. Original raw output hashes and stored hashes are distinct where Recorder canonicalized/lossily decoded; unavailable original bytes are never invented.','commands':commands},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

formal=['web-order-fc224acf-80e7-4346-ba93-a21c69a444d1','desktop-dc5abc0e-2d63-4be3-b637-62b778def174','desktop-fresh-648e2d74-bf54-43b4-ace8-a4c6c206f5a1','android-state-738cbf61-090f-44d9-954c-b2947f5c1c5e','android-restart-7cb18750-4e72-4a30-8e82-b541f714e400','android-fresh-8b9f45b9-a99b-4789-9342-450ff733b0ee','friends-15c8a244-cd7e-4cc5-9862-acac2fda6a8c','web-baseline-547514','android-gui-baseline-1791637240890']
entries=[]
for p in sorted((E/'screens').rglob('*.png')):
    raw=p.read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n';w,h=struct.unpack('>II',raw[16:24]);rel=p.relative_to(E/'screens').as_posix()
    category='historical original; not selected formal evidence'
    if any(rel.startswith(f+'/') for f in formal):category='selected local evidence; independent review pending'
    if rel.startswith('desktop-native/') and ('source547514-final3' in rel or 'notification-source547514' in rel):category='selected actual installed Windows18f8 capability evidence'
    if rel.startswith('windows-week2-negative-'):category='trust rollback native negative diagnostic; use only directory with PASS proof.json'
    entry={'path':p.as_posix(),'sha256':hashlib.sha256(raw).hexdigest(),'width':w,'height':h,'state':p.stem,'category':category,'originalUnedited':True}
    metadata=p.with_suffix('.json')
    if metadata.exists():
        try:
            value=json.loads(metadata.read_text(encoding='utf-8-sig'))
            if isinstance(value,dict) and 'theme' in value:entry['appearanceOriginal']=value
        except (ValueError,UnicodeError):pass
    if rel.startswith('friends-15c8'):entry['chainQualification']='Original runner exit1 plus explicitly separate read-only canonical SQL/events continuation PASS; no original result rewritten'
    if category.startswith('selected'):
        entry['productSource']='5648c9d80004ea1db618c7740607f9797b6200a8' if rel.startswith('web-order-') else '547514f6c8c8c0c40e27073b67d17bb3f224b6c5'
        entry['language']='Web Chinese/English current baseline' if rel.startswith('web-') else 'Native English current baseline'
    entries.append(entry)
(E/'screenshot-index.json').write_text(json.dumps({'generatedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'qualification':'Original SHA/kind fields remain untouched. Formal eligibility is an external local implementation claim for independent Architect/Reviewer. Web baseline original manifest retains baseline task label; this Task invokes the same required baseline command. Android appearance comes from original adjacent capture JSON where present. Desktop actual persisted appearance after runs was warm/14/0.8; no per-image runtime appearance claim is fabricated. Web baseline manifest has exact viewport/appearance. Other missing original metadata is explicitly unavailable, not guessed.','entries':entries},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS byte-identical command originals/index',len(commands),'and original PNG index',len(entries),'(local evidence only)')
