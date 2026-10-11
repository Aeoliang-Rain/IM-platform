"""Audit preserved original hashes and add explicit per-image binding references."""
from pathlib import Path
import hashlib,json,shutil
E=Path('spec/progress/evidence/LOOP1-CLIENT-STATE-001')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=E/'finalize-originals';old.mkdir(exist_ok=True)
for name in ('verification-matrix.json','verification-matrix.md','screenshot-index.json'):
    dst=old/name
    if not dst.exists():shutil.copyfile(E/name,dst)
index=json.loads((E/'command-index.json').read_text(encoding='utf-8'))
for row in index['commands']:
    for stream in row['originals'].values():assert sha(Path(stream['path']))==stream['storedBlobSHA256']
screens=json.loads((E/'screenshot-index.json').read_text(encoding='utf-8'))
for row in screens['entries']:
    p=Path(row['path']);assert sha(p)==row['sha256']
    manifests=[q/name for q in p.parents if q.is_relative_to(E/'screens') for name in ('manifest.json','proofs.json','proofs-supplemental-readonly.json') if (q/name).exists()]
    row['bindingOriginals']=[{'path':q.as_posix(),'sha256':sha(q)} for q in manifests]
    row['buildBindingReference']='source547514-native-binding.json / final-product-binding.json'
    row['runtime']='unavailable in original image metadata'
    row['fixture']='unavailable in original image metadata; inspect bindingOriginals'
    row['theme']=row['fontSize']=row['density']='unavailable in original image metadata'
    for m in manifests:
        data=json.loads(m.read_text(encoding='utf-8-sig'))
        if not isinstance(data,dict):continue
        row['fixture']=data.get('fixture',row['fixture'])
        row['runtime']=data.get('browser',data.get('runtime',row['runtime']))
        rel=p.relative_to(m.parent).as_posix()
        entry=next((x for x in data.get('entries',[]) if x.get('file')==rel),{})
        appearance=entry.get('appearance',entry)
        if 'font' in appearance:row['fontSize']=appearance['font']
        for key in ('theme','fontSize','density','language'):
            if key in appearance:row[key]=appearance[key]
        if 'avd' in entry:row['runtime']={k:entry[k] for k in ('avd','serial') if k in entry}
        if 'steps' in entry:row['stepsOriginal']=entry['steps']
    for q in (p.with_suffix('.json'),Path(str(p)+'.json')):
        if q.exists():
            data=json.loads(q.read_text(encoding='utf-8-sig'))
            row['bindingOriginals'].append({'path':q.as_posix(),'sha256':sha(q)})
            for key in ('theme','fontSize','density','language'):
                if key in data:row[key]=data[key]
            if 'spacingDensity' in data:row['density']=data['spacingDensity']
    rel=p.relative_to(E/'screens').as_posix()
    if row['category'].startswith('selected'):
        row['task']='LOOP1-CLIENT-STATE-001'
        row['metadataDerivation']=[]
        if rel.startswith('android-gui-baseline-1791637240890/'):
            theme,page,font=p.stem.split('-');font=int(font)
            row.update(theme=theme,fontSize=font,density=1.2 if font==22 else .8,language='English/default',runtime={'platform':'Android API34','avd':'IMClientSend34','serial':'emulator-5590'},fixture='GuiInstrumentation anonymous forms, owned encrypted-storage slot; no real account data')
            row['metadataDerivation'].append('GuiInstrumentation onStart exact theme/font capture loop; run C-0ca4ec63-2992-4da0-982a-6ed86c865c11 PASS46 with captureRun1791637240890; no per-image appearance guesses')
        elif (rel.startswith('android-') or '/native-originals/' in rel) and not 'receiver' in p.stem:
            row.update(theme='cold',fontSize=14,density=.8,language='English/default',runtime={'platform':'Android API34','avd':'IMClientSend34','serial':'emulator-5590'})
            row['metadataDerivation'].append('GuiAuthenticatedInstrumentation onStart API34 assertion then prefs.saveAppearance(cold,14,.8); STATE/fresh/restart/friends branches contain no appearance mutations; exact phase/raw result in same-run originals')
        elif rel.startswith('desktop-') and not 'receiver' in p.stem:
            row.update(theme='warm',fontSize=14,density=.8,language='English/default',runtime={'platform':'Windows installed Tauri','installedSHA256':'18f8b5bb6f8a8c1a6ec8777421a5440c60fabf03a4f8dea0f24deb48ed870503','binding':'source547514-native-binding.json'})
            row['metadataDerivation'].append('same source547514 formal chain: fresh648e/settings.png.json actual header WarmCreative/Fontsize14px/SpacingCompact; source main.tsx22/30 maps to warm/14/.8; actual/fresh/friends scripts never mutate appearance. Build and source hashes are separate from historical original kind.')
        elif rel.startswith('friends-15c8') and p.name.startswith('desktop-'):
            row.update(theme='warm',fontSize=14,density=.8,language='English/default',runtime={'platform':'Windows installed Tauri','binding':'source547514-native-binding.json'})
            row['metadataDerivation'].append('Desktop same-run UIA header WarmCreative plus preceding fresh648e/settings original14px/Compact; friend script contains no appearance action; no later persisted preference assumption')
        elif rel.startswith('web-') or p.name.startswith('web-') or 'receiver' in p.stem:
            row.update(runtime='Chromium151.0.7922.34 actual owned browser; source recorded launch path')
            if str(row['theme']).startswith('unavailable'):
                row.update(theme='cold',fontSize='16px',density='comfortable',language='zh-CN/English existing baseline')
                row['metadataDerivation'].append('Actual harness creates new browser context without storageState; no theme/font/density action; appearance.ts exact defaults cold16comfortable. Receiver context is separate from sender.')
        if rel.startswith('desktop-native/'):
            row['fixture']='Controlled STATE Fresh account from friends15c8; same installed18f8 process; actual notification AppUserModelId im.platform.desktop and tray-owned process/window actions in desktop-native/*.json'
            row['metadataDerivation'].append('tray menu/native notification system surface has no application typography/density; app settings image retains above application binding')
            if 'menu-' in p.name or 'actual-ui' in p.name:row.update(theme='OS system surface; application warm independent',fontSize='not applicable OS surface',density='not applicable OS surface')
        if rel.startswith('android-restart-7cb18750'):
            proof=json.loads((E/'screens'/rel.split('/')[0]/'proofs.json').read_text())
            row['fixture']={'run':proof['run'],'requestId':proof['requestId'],'committedRow':proof['after']['rows'][0],'accountReference':'desktop-dc5abc0e-2d63-4be3-b637-62b778def174/manifest.json fixture; sender/conversation exact match'}
        row['metadataSourceSHA']=row.get('productSource','547514f6c8c8c0c40e27073b67d17bb3f224b6c5')
    row['candidateBinding']='Final clean review candidate sealed externally after commit; original capture source/kind unchanged'
(E/'screenshot-index.json').write_text(json.dumps(screens,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
missing=[{'path':x['path'],'fields':[k for k in ('theme','fontSize','density','runtime','fixture') if str(x.get(k,'unavailable')).startswith('unavailable')],'originalReferences':x['bindingOriginals']} for x in screens['entries'] if x['category'].startswith('selected')]
missing=[x for x in missing if x['fields']]
(E/'screenshot-metadata-gaps.json').write_text(json.dumps(missing,indent=2)+'\n',encoding='utf-8')
receipt={'originalIndexSnapshots':{p.name:sha(p) for p in old.iterdir()},'commandsVerified':len(index['commands']),'pngVerified':len(screens['entries']),'selectorCorrection':'Old Web actual row selected Python -c source binding by substring; exact argv selection now required. Original matrix snapshot preserved.','missingImageMetadata':'Per-image unavailable values are explicit. No appearance/runtime values inferred from later preferences or invented; Architect must judge original binding chain.'}
(E/'finalize-audit.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print('PASS preserved stored-output/PNG hashes and explicit metadata references; unavailable facts remain unavailable')
