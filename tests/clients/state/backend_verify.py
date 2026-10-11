"""Full actual Go verification in a newly created, isolated disposable database."""
from pathlib import Path
import json,subprocess,uuid,os
root=Path(__file__).resolve().parents[3];docker='C:/Program Files/Docker/Docker/resources/bin/docker.exe';project='im-gui-product-20261004-35588';database='state_verify_'+uuid.uuid4().hex[:12];container='im-state-test-'+uuid.uuid4().hex[:12]
def call(args,**kw):return subprocess.run([docker,*args],check=True,**kw)
labels=json.loads(subprocess.check_output([docker,'inspect','--format','{{json .Config.Labels}}',project+'-postgres-1'],text=True));assert labels.get('com.docker.compose.project')==project
created=False
try:
 call(['exec',project+'-postgres-1','psql','-U','im','-d','postgres','-v','ON_ERROR_STOP=1','-c','CREATE DATABASE '+database]);created=True
 call(['exec','-i',project+'-postgres-1','psql','-U','im','-d',database,'-v','ON_ERROR_STOP=1'],input=(root/'contracts/database/migrations/0001_initial.up.sql').read_bytes(),stdout=subprocess.DEVNULL)
 print('Isolated actual Go test database '+database+'; fixture im untouched',flush=True)
 args=['run','--rm','--name',container,'--label','im.state.owner=R-STATE-20261010-IMPL','--network',project+'_default','--mount','type=bind,source='+str(root)+',target=/workspace,readonly','-w','/workspace/backend/go','-e','DB_TEST_ENABLE=1','-e','PGHOST=postgres','-e','PGUSER=im','-e','PGPASSWORD=local-development-only','-e','PGDATABASE='+database,'-e','NATS_URL=nats://nats:4222','golang:1.25-alpine','go','test','./...']
 result=subprocess.run([docker,*args],timeout=180)
 if result.returncode:raise SystemExit(result.returncode)
 print('PASS full actual Go suite DB_TEST_ENABLE=1 isolated database',flush=True)
finally:
 if created:call(['exec',project+'-postgres-1','psql','-U','im','-d','postgres','-v','ON_ERROR_STOP=1','-c','DROP DATABASE '+database]);print('Owned isolated database cleanup complete',flush=True)
