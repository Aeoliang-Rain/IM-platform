"""Locked, isolated resource/Web-adapter unit evidence; native evidence is separate."""
from pathlib import Path
import os, shutil, subprocess, sys, tempfile
root=Path(__file__).resolve().parents[3]
subprocess.run([sys.executable,"-Xutf8","-B","-m","unittest","discover","-s","tests/clients/i18n","-p","test_language_packs.py"],cwd=root,check=True)
npm=shutil.which("npm.cmd" if os.name=="nt" else "npm")
node=shutil.which("node")
if not npm or not node: raise RuntimeError("Actual npm/Node tools required")
with tempfile.TemporaryDirectory(prefix="i18n-unit-") as directory:
 stage=Path(directory).resolve()
 for name in ("package.json","package-lock.json"):
  shutil.copyfile(root/"clients/web"/name,stage/name)
 subprocess.run([npm,"--prefix",str(stage),"ci","--ignore-scripts","--no-audit","--no-fund"],cwd=root,check=True)
 env=os.environ.copy()
 env.update(I18N_TYPESCRIPT_PACKAGE=str(stage/"package.json"),I18N_OUTPUT_DIR=str(stage/"output"))
 result=subprocess.run([node,str(root/"tests/clients/i18n/verify.mjs")],cwd=root,env=env)
 sys.exit(result.returncode)
