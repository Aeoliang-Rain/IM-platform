from pathlib import Path
import subprocess,json,hashlib,sys
out=Path(__file__).parent;root=Path('H:/.codex/worktrees/err/IM-platform')
report='''Fresh regular native Review helper: FAIL

Candidate 26a2941024c561d711d0d572b82f0f0f7a46d984, branch task/LOOP1-ERROR-HANDLING-001, baseline35bd6f5f1091503f95a0282f730ed04233b0b6ea. Fresh helper /root/regular_review_26a2941/native_semantics neither implemented nor fixed this candidate. Regular participant is ineligible for specialized sameSHA audit. Read-only assigned clean committed root H:/.codex/worktrees/err/IM-platform; no source/main/Git/CI/device/trust writes.

F-APPEARANCE-EXISTS-DEFAULT [P2], desktop_capabilities.rs:35. appearance_path returns actual app-owned appearance.json path. Path.exists performs real filesystem metadata and converts errors to false, including permission denial on a parent directory. Therefore an unavailable stored preference enters Ok(default tuple), rather than existing Appearance unavailable result. Registered literal native command feeds appearance.load native.ts:22 and Workspace.start workspace.ts:19, producing normal successful default and omitting appearance load failure. No fake callback/exception object is required for this OS failure. Actual runtime occurrence has not been measured; this is documented standard-library semantics plus current real producer/consumer reachability, not a claimed Windows ACL reproduction.

Rust primary source: https://doc.rust-lang.org/std/path/struct.Path.html#method.exists . Read official API documentation; paraphrased semantics only. Source/API inspection exposed a non-navigation boundary missing from original306 records. Missing-file default is valid; unavailable defaults expressly apply to Web appearance (ADR11) and language (Frozen6.6/ADR12), not permission failure of Desktop appearance. Current task audits all production, so baseline retention is not exemption. Minimal repair: one read, NotFound alone defaults, other failures existing Appearance unavailable. No SQLite/Composer/draft/contract/technology change required.

Four literal compiled TypeScript controls PASS: appearance.load receives default tuple as normal value; Workspace.start then error=null. Sanitized native Appearance unavailable rejects as NativeCapabilityFailure; Workspace.start exposes Appearance could not be loaded. Controlled IPC invoke, not actual Tauri/filesystem reproduction. Reused existing locked compiled fixture; current native.ts/workspace.ts source bytes match fixture, recorded hashes. Prior PASS not inherited.

Coverage:57 full production files including32 Kotlin source files, Rust native adapters/assembly/probe, build/config/resources/launchers/lock metadata;141 navigation records (131 executable,10 syntax-only) independently coordinate/hash matched, with fullfile/callchain grounds; one supplemental finding. files.json/tokens.json/findings.json/supplemental-boundaries.json are current helper assessment. Audit.py deterministic input/coordinate/protection checks PASS; this is evidence integrity, not semantic acceptance. Frozen verifier PASS. Candidate native/mobile tree equal a292 (read-only diff empty); no fresh Android/native full-suite run. Parent owns broader candidate baselines/previous sealed live-evidence validation.

Protected scope: Android Repository all bytes except two-read-authorized contiguous mapper equal35bd6f5; same SELECT unchanged. Rust database adapter and Composer byte-identical baseline. SQLite writes/schema/transactions/drafts excluded, no modifications. No new dependency, import direction or native business responsibility violation identified.

Instrumentation limitations: default python was Python27 and rejected -Xutf8; direct startup reads before Recorder retained as unavailable exact prestart trace. Many source/authority/tool-discovery reads and official web documentation lookups after Recorder were direct commands; not routed through run-command. These gaps are explicitly disclosed; prospective_resume/pre_recorder_trace_complete=false. Recorded audit/frozen/compiled-consumer commands have real exit/duration/blobs. Initial audit NO_FINDING was provisional; subsequent supplemental review found error and final FAIL replaces provisional assessment only. Raw Recorder outputs remain immutable. Structural validity is not complete trace or product/Task/Stage acceptance.

Next: Coordinator adjudicates finding, fresh Fix then NEW regular review and different NEW specialized audit on finalSHA. No push/CI-triggering PR/Taskdone/S2PASS on this FAIL. Hosted required jobs/integration/main sync pending.
'''
(out/'report.md').write_text(report,'utf-8')
args=[sys.executable,'-Xutf8','-B',str(root/'tools/research/recorder.py')]
common=['--research-root',str(out/'research'),'--run-id','R-REGULAR-26A2941-NATIVE']
event={'result':'FAIL','finding':'F-APPEARANCE-EXISTS-DEFAULT','candidate':'26a2941024c561d711d0d572b82f0f0f7a46d984','file_count':57,'navigation_count':141,'direct_inspection_command_gaps':True,'pre_recorder_trace_complete':False,'proof':'Official std API semantics plus current literal producer/consumer and4 compiledTS controlled invoke assertions. No actual Windows ACL reproduction.'}
for sub,extra in [('record-event',['--event-type','review_finished','--data-json',json.dumps(event)]),('finish-run',['--result','FAIL']),('validate-run',[])]:
 p=subprocess.run(args+[sub]+common+extra,cwd=root,capture_output=True)
 (out/(sub+'.stdout')).write_bytes(p.stdout);(out/(sub+'.stderr')).write_bytes(p.stderr);p.check_returncode()
seals=[]
for p in sorted(out.rglob('*')):
 if p.is_file() and p.name not in ('seal.json','seal.sha256'):seals.append({'path':p.relative_to(out).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
seal={'candidate':event['candidate'],'role':'fresh regular review helper','result':'FAIL','findings':[event['finding']],'files':seals}
(out/'seal.json').write_text(json.dumps(seal,indent=2),'utf-8')
(out/'seal.sha256').write_text(hashlib.sha256((out/'seal.json').read_bytes()).hexdigest(),'utf-8')
print(json.dumps({'result':'FAIL','seal_count':len(seals),'seal_sha256':(out/'seal.sha256').read_text(),'external':str(out)}))
