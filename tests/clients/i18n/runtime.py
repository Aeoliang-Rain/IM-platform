"""Owned staging and actual Android orchestration. No backend ownership transfer."""
from pathlib import Path
import argparse,hashlib,json,os,re,shlex,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[3]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def command(argv,timeout=1200):
    r=subprocess.run(list(map(str,argv)),cwd=ROOT,capture_output=True,timeout=timeout)
    if r.returncode:raise RuntimeError('Command failed; exit='+str(r.returncode)+' (private output withheld)')
    return r.stdout
def git(*args):return command(['git','-C',ROOT,*args]).decode().strip()
def inventory(base):
    result={}
    for p in sorted(base.rglob('*')):
        if p.is_symlink():raise ValueError('Symlink input forbidden')
        if p.is_file():result[p.relative_to(base).as_posix()]=digest(p)
    return result
def source():
    return {name:inventory(ROOT/name) for name in ('clients/web','clients/shared')}
def emit(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def adb(a,*args):return command([a.adb,'-s',a.serial,*args],timeout=600)
def shell(a,*args):return adb(a,'shell',' '.join(shlex.quote(str(x)) for x in args)).decode()
def instrument(a,runner,params,out):
    argv=['am','instrument','-w']
    for k,v in params.items():argv+=['-e',k,v]
    argv+=['im.platform.client.test/im.platform.client.ui.'+runner]
    raw=shell(a,*argv);out.write_text(raw,encoding='utf-8')
    if 'INSTRUMENTATION_CODE: -1' not in raw or not re.search(r'INSTRUMENTATION_RESULT: result=PASS',raw) or re.search(r'INSTRUMENTATION_(?:RESULT|STATUS): (?:failure|shortMsg)=',raw):raise RuntimeError('Actual instrumentation failed; inspect owned raw record')
def installed_hash(a,package):
    raw=shell(a,'pm','path',package).strip().splitlines()
    if len(raw)!=1 or not raw[0].startswith('package:/data/app/'):raise ValueError('Unexpected installed package path')
    return hashlib.sha256(adb(a,'exec-out','cat',raw[0][8:])).hexdigest()
def stage(a,out,report):
    before=source()
    if any(any(part in ('node_modules','dist','build') for part in Path(name).parts) for data in before.values() for name in data):raise ValueError('Source contains generated build output; archive owned outputs first')
    for name in before:shutil.copytree(ROOT/name,out/'stage'/name)
    npm=shutil.which('npm.cmd' if os.name=='nt' else 'npm');node=shutil.which('node')
    if not npm or not node:raise ValueError('Existing npm/Node required')
    env=os.environ.copy();env['WEB_BUILD_DIR']=str(out/'web-build')
    logs=[]
    for label,args in [('npm-ci',[npm,'--prefix',str(out/'stage/clients/web'),'ci','--ignore-scripts','--no-audit','--no-fund']),('build',[npm,'--prefix',str(out/'stage/clients/web'),'run','build'])]:
        r=subprocess.run(args,cwd=ROOT,env=env,capture_output=True,timeout=1200);(out/(label+'.log')).write_bytes(r.stdout+r.stderr);logs.append({'step':label,'exit_code':r.returncode})
        if r.returncode:raise RuntimeError('Locked Web '+label+' failed; inspect owned log')
    if source()!=before:raise ValueError('Source changed during build')
    build=out/'web-build'
    if not (build/'index.html').is_file() or not (build/'web/src/ui/i18n/resources.js').is_file():raise ValueError('Actual compiled Web artifact incomplete')
    report.update(source_inputs=before,build_files=inventory(build),commands=logs,scope='locked actual Web build only; browser/backend acceptance pending',web_build_dir=str(build))
    emit(out/'browser-env.json',{'WEB_BUILD_DIR':str(build),'WEB_CANDIDATE_SHA':a.source_sha,'I18N_CLEAN_CANDIDATE':'0' if a.wip else '1','scope':'Additional fixture TLS/Playwright/output inputs required; real backend must use its actual endpoint separately'})
def android(a,out,report):
    if not re.fullmatch(r'emulator-\d+',a.serial):raise ValueError('Owned emulator serial required')
    if shell(a,'getprop','sys.boot_completed').strip()!='1' or shell(a,'getprop','ro.build.version.sdk').strip()!='34':raise ValueError('Actual boot-completed API34 required')
    public=json.loads(Path(a.fixture_public).read_text(encoding='utf-8'))
    if public['endpoint']!='https://localhost:8443' or not public['status'].startswith('actual owned Go/PG/NATS'):raise ValueError('Live controlled real backend on 8443 required')
    accounts=public['accounts'];avery=next(x for x in accounts if x['displayName']=='GUI Fixture Avery');peer=next(x for x in accounts if x['displayName']=='GUI Fixture Morgan')
    conversation=public['conversationId'];require_uuid=re.compile(r'[a-f0-9-]{36}')
    if not require_uuid.fullmatch(conversation):raise ValueError('Invalid fixture conversation')
    for p in (a.apk,a.test_apk,a.negative_apk):
        if not Path(p).is_file():raise ValueError('Actual APK required')
    report.update(serial=a.serial,backend_project=public['project'],endpoint=public['endpoint'],apks={name:digest(Path(getattr(a,name))) for name in ('apk','test_apk','negative_apk')},scope='actual owned API34 Compose; controlled real Go/PG/NATS; not independent acceptance')
    reverse_added=False
    failure=None
    try:
        reverse=adb(a,'reverse','--list').decode().splitlines()
        if any('tcp:8443' in row.split() for row in reverse):raise ValueError('Existing reverse mapping ownership unknown; use fresh owned mapping')
        adb(a,'reverse','tcp:8443','tcp:8443');reverse_added=True
        for apk in (a.apk,a.negative_apk):
            if 'Success' not in adb(a,'install','-r',apk).decode():raise RuntimeError('APK installation unsuccessful')
        if installed_hash(a,'im.platform.client.test')!=report['apks']['negative_apk']:raise ValueError('Negative installed APK mismatch')
        instrument(a,'UiRefTLSNegative',{},out/'tls-before.txt')
        if 'Success' not in adb(a,'install','-r',a.test_apk).decode():raise RuntimeError('Compose test APK installation unsuccessful')
        if installed_hash(a,'im.platform.client')!=report['apks']['apk'] or installed_hash(a,'im.platform.client.test')!=report['apks']['test_apk']:raise ValueError('Installed APK identity mismatch')
        params={'ownedFixture':'i18n-owned-api34','stateRun':out.name,'sourceSha':a.source_sha,'apkSha256':report['apks']['apk'],'avery':avery['username'],'peerName':peer['displayName'],'expectedConversation':conversation,'historyText':'Welcome to the GUI fixture. This message crossed the actual Go services.','cleanCandidate':'0' if a.wip else '1'}
        if a.ca:
            if a.ca not in ('/sdcard/Android/data/im.platform.client/files/ui-ref-ca.der','/data/data/im.platform.client/files/ui-ref-ca.der'):raise ValueError('Existing approved device CA path required')
            params['uiRefCA']=a.ca
            if not a.ca_sha256 or not re.fullmatch(r'[a-f0-9]{64}',a.ca_sha256):raise ValueError('Explicit owned CA SHA256 required')
            params['caSha256']=a.ca_sha256
        instrument(a,'I18nComposeInstrumentation',params,out/'compose.txt')
        remote='/sdcard/Android/data/im.platform.client/files/i18n/'+out.name
        adb(a,'pull',remote,str(out/'captures'))
        result=json.loads((out/'captures/result.json').read_text(encoding='utf-8'))
        manifest=json.loads((out/'captures/manifest.json').read_text(encoding='utf-8'))
        if result.get('result')!='PASS' or result.get('cleanupComplete') is not True or manifest.get('installed_apk_sha256')!=report['apks']['apk'] or manifest.get('source_sha')!=a.source_sha:raise ValueError('Compose evidence/cleanup binding failed')
        if manifest.get('result')!='PASS' or manifest.get('cleanupComplete') is not True or not manifest.get('captures'):raise ValueError('Actual capture manifest incomplete')
        for capture in manifest['captures']:
            name=capture['file']
            if Path(name).name!=name or not name.endswith('.png') or digest(out/'captures'/name)!=capture['sha256']:raise ValueError('Screenshot hash/name mismatch')
        report['captured_files']=inventory(out/'captures')
        report['compose_checks']='PASS'
    except BaseException as error:failure=error
    finally:
        cleanup=[]
        try:
            if not reverse_added:raise RuntimeError('Runtime not entered; TLS post-check pending')
            if 'Success' not in adb(a,'install','-r',a.negative_apk).decode():raise RuntimeError('Negative APK installation failed')
            if installed_hash(a,'im.platform.client.test')!=report['apks']['negative_apk']:raise ValueError('Post-run negative installed APK mismatch')
            instrument(a,'UiRefTLSNegative',{},out/'tls-after.txt');report['default_tls_before_after']='PASS' if (out/'tls-before.txt').exists() else 'INCOMPLETE'
        except BaseException as error:cleanup.append(type(error).__name__+': '+str(error))
        if reverse_added:
            try:adb(a,'reverse','--remove','tcp:8443')
            except BaseException as error:cleanup.append(type(error).__name__+': '+str(error))
        report['cleanup_errors']=cleanup
        report['cleanup_scope']='Runner preference/trust cleanup verified in result; owned reverse removed. APKs/evidence intentionally retained; parent owns AVD/accounts/backend final teardown.'
        if cleanup and failure is None:failure=RuntimeError('TLS/reverse cleanup failed')
    if failure:raise failure
def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['stage','android']);p.add_argument('--out',required=True);p.add_argument('--source-sha',required=True);p.add_argument('--wip',action='store_true');p.add_argument('--adb');p.add_argument('--serial');p.add_argument('--apk');p.add_argument('--test-apk');p.add_argument('--negative-apk');p.add_argument('--fixture-public');p.add_argument('--ca');p.add_argument('--ca-sha256');a=p.parse_args()
    if not re.fullmatch(r'[a-f0-9]{40}',a.source_sha) or git('rev-parse','HEAD')!=a.source_sha:raise ValueError('Actual HEAD source SHA required')
    dirty=bool(git('status','--porcelain'))
    if dirty and not a.wip:raise ValueError('Dirty candidate requires explicit --wip; never clean acceptance')
    out=Path(a.out).resolve()
    if not Path(a.out).is_absolute() or out==ROOT or ROOT in out.parents or out.exists() or not re.fullmatch(r'[A-Za-z0-9-]{1,80}',out.name):raise ValueError('Fresh external owned output with safe run basename required')
    out.mkdir(parents=True)
    report={'result':'PENDING','source_sha':a.source_sha,'source_is_clean_committed_candidate':not dirty and not a.wip,'mode':a.mode,'started_at_unix':time.time()}
    try:
        if a.mode=='stage':stage(a,out,report)
        else:android(a,out,report)
        if git('rev-parse','HEAD')!=a.source_sha or bool(git('status','--porcelain'))!=dirty:raise ValueError('Source identity changed during harness')
        report['result']='PASS_LOCAL_CHECKS';return 0
    except BaseException as error:report.update(result='FAIL',failure=type(error).__name__+': '+str(error));return 1
    finally:emit(out/'binding.json',report);print(report['result']+'; owned binding.json; no authentication output')
if __name__=='__main__':sys.exit(main())
