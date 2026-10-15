import pathlib,subprocess,json,hashlib,shutil,time
R=pathlib.Path('H:/.codex/worktrees/err/IM-platform');E=pathlib.Path(__file__).parent;D=R/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/fix-android-suppressed';adb='H:/Android/platform-tools/adb.exe';receipt=json.loads((E/'emulator-receipt.json').read_text());assert receipt['serial']=='emulator-5598' and pathlib.Path(receipt['owned_avd']).resolve()==(E/'avd/HttpCleanup20261014.avd').resolve()
reverse=subprocess.check_output([adb,'-s','emulator-5598','reverse','--list'],text=True);assert not reverse.strip(),reverse
subprocess.run([adb,'-s','emulator-5598','emu','kill'],check=True)
for _ in range(60):
 state=subprocess.check_output([adb,'devices','-l'],text=True)
 if 'emulator-5598' not in state:break
 time.sleep(1)
else:raise RuntimeError('Owned emulator remained connected')
owned=pathlib.Path(receipt['owned_avd']).resolve();assert owned.is_relative_to(E.resolve()) and owned.name=='HttpCleanup20261014.avd';shutil.rmtree(owned)
(E/'avds'/'HttpCleanup20261014.ini').unlink(missing_ok=True)
outputs=[]
for name in ['clients/mobile/app/build','clients/mobile/.gradle']:
 src=(R/name).resolve();assert src.is_relative_to(R.resolve()) and str(src)==str((R/name).resolve())
 dest=E/'owned-build-artifacts'/name.replace('/','_');assert not dest.exists();dest.parent.mkdir(exist_ok=True)
 if src.exists():shutil.move(str(src),str(dest));outputs.append(dict(source=str(src),preserved=str(dest)))
result=dict(owned_emulator=receipt,owned_reverse_rules=reverse,remaining_devices=state,deleted_exact_owned_avd=str(owned),preserved_build_outputs=outputs,global_trust_changed=False,private_data_touched=False,main_touched=False)
(D/'runtime-cleanup.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');(E/'runtime-cleanup.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print('Owned5598 closed,reverse empty,exact owned AVD removed; outputs preserved externally; main/private/trust untouched')
