"""Disposable actual PostgreSQL/NATS integration; all existing Go tests, no skips."""
from pathlib import Path
import json,os,secrets,subprocess,tempfile
ROOT=Path('H:/.codex/worktrees/err/IM-platform')
def main():
 docker=os.environ.get("IM_CLIENT_DOCKER","C:/Program Files/Docker/Docker/resources/bin/docker.exe")
 project="im-regular26-tests-"+secrets.token_hex(6);env=os.environ.copy()
 print('Owned project '+project,flush=True)
 cmd=[docker,"compose","-f",str(ROOT/"deploy/compose.yaml"),"-p",project]
 def execute(args,**kwargs):return subprocess.check_output(args,env=env,**kwargs)
 try:
  subprocess.run(cmd+["up","-d","--build","postgres","nats","migrate"],env=env,check=True)
  with tempfile.TemporaryDirectory(prefix="error-live-env-") as tmp:
   private=Path(tmp)/"fixture.env"
   private.write_text("DB_TEST_ENABLE=1\nPGHOST=postgres\nPGPORT=5432\nPGUSER=im\nPGDATABASE=im\nPGPASSWORD=local-development-only\nNATS_URL=nats://nats:4222\n",encoding="utf8")
   subprocess.run([docker,"run","--rm","--label","im.error-task="+project,"--network",project+"_default","--env-file",str(private),"-v",str(ROOT)+":/workspace:ro","-w","/workspace/backend/go","-e","GOPROXY=off","-v","C:/Users/21441/go/pkg/mod/cache/download:/locked-cache:ro","golang:1.25-alpine","sh","-c","mkdir -p /go/pkg/mod/cache/download && cp -R /locked-cache/. /go/pkg/mod/cache/download/ && exec go test -mod=readonly -count=1 -v ./..."],env=env,check=True)
  print("PASS actual disposable PostgreSQL/NATS full Go suite with DB_TEST_ENABLE=1")
 finally:
  ids=execute([docker,"ps","-aq","--filter","label=com.docker.compose.project="+project]).decode().split()
  for ident in ids:assert json.loads(execute([docker,"inspect",ident]))[0]["Config"]["Labels"]["com.docker.compose.project"]==project
  names=execute([docker,"volume","ls","-q","--filter","label=com.docker.compose.project="+project]).decode().split()
  for name in names:assert json.loads(execute([docker,"volume","inspect",name]))[0]["Labels"]["com.docker.compose.project"]==project
  subprocess.run(cmd+["down","--volumes","--remove-orphans"],env=env,check=True)
  assert not execute([docker,"ps","-aq","--filter","label=com.docker.compose.project="+project]).strip()
  assert not execute([docker,"volume","ls","-q","--filter","label=com.docker.compose.project="+project]).strip()
  assert not execute([docker,"network","ls","-q","--filter","label=com.docker.compose.project="+project]).strip()
  subprocess.run([docker,'image','rm',project+'-migrate'],env=env,check=True)
  print("Owned integration containers/volumes removed")
if __name__=="__main__":main()

