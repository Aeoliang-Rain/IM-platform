"""Read-only supplemental continuation of an otherwise completed actual GUI matrix."""
from pathlib import Path
import datetime,hashlib,json,ssl,subprocess,urllib.request
runtime=Path("H:/IM-platform/.git/worktrees/IM-platform43/state-runtime")
run="friends-15c8a244-cd7e-4cc5-9862-acac2fda6a8c";root=Path("spec/progress/evidence/LOOP1-CLIENT-STATE-001/screens")/run
f=json.loads((runtime/"fresh-public.json").read_text(encoding="utf-8"));owner=f["accounts"][0]["userId"];assert owner=="e57967ea-8fd8-4dd1-ac7e-3ecdea64c8f1"
raw=(root/"instrumentation-original.txt").read_text(encoding="utf-8");assert "INSTRUMENTATION_RESULT: result=PASS" in raw and "assertions=61" in raw
for account in f["accounts"][1:]:
 for name in ["desktop-original-restored-"+account["userId"]+"-visible.png","web-original-account-restored-"+account["userId"]+".png"]:assert (root/name).is_file(),name
 nodes=json.loads((root/("desktop-original-restored-"+account["userId"]+"-visible.png.json")).read_text(encoding="utf-8"))["nodes"];assert any(n["name"]==account["username"] for n in nodes)
for name in ["desktop-other-account-isolated.png","desktop-other-conversations-isolated.png","web-other-account-isolated.png","desktop-offline-recovered-visible.png","web-disconnected-retained.png"]:assert(root/name).is_file(),name
sql="SELECT coalesce(json_agg(json_build_object('userLow',user_low_id,'userHigh',user_high_id,'directConversationId',direct_conversation_id)),'[]'::json) FROM friendships WHERE user_low_id='"+owner+"' OR user_high_id='"+owner+"'"
def db(sql):return json.loads(subprocess.check_output(["C:/Program Files/Docker/Docker/resources/bin/docker.exe","exec",f["project"]+"-postgres-1","psql","-U","im","-d","im","-Atc",sql],text=True,encoding="utf-8",timeout=15))
rows=db(sql);assert len(rows)==4 and len({r["directConversationId"] for r in rows})==4
for account in f["accounts"][1:]:assert len([r for r in rows if account["userId"] in [r["userLow"],r["userHigh"]]])==1
before=json.loads((root/"messages-before.json").read_text(encoding="utf-8"));after=db("SELECT json_build_object('messages',(SELECT count(*) FROM messages),'outbox',(SELECT count(*) FROM outbox_events))");assert before==after
boundary=json.loads((root/"initial-sync-complete-event-boundary.json").read_text(encoding="utf-8"));assert boundary["messages"]==before
context=ssl.create_default_context(cafile=str(runtime/"tls-state-week2/ca.pem"))
with urllib.request.urlopen("https://localhost:8443/__state/events",context=context,timeout=15) as response:events=json.load(response)
assert not any(e["kind"] in ["send","actual_created","actual_ack"] for e in events[boundary["lastEvent"]:])
result={"kind":"supplemental read-only continuation; original full runner exit1 is unchanged","run":run,"fixture":f,"productSource":"547514f6c8c8c0c40e27073b67d17bb3f224b6c5","checkerCommit":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),"actualAfterUTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),"rows":rows,"messagesBefore":before,"messagesAfter":after,"initialEventBoundary":boundary["lastEvent"],"noNewMessageDeliveryEvents":True,"interveningOperations":"Read-only bindings/diagnosis only after GUI matrix completion; no additional Message, Outbox or friendship writes. Global counts and relay event boundary independently verify no new delivery trigger.","mobileActualAssertions":61,"allOriginalPNGsSHA256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob("*.png")},"sync": [e for e in events if e["kind"]=="sync_request" and e.get("userId")==owner],"localResult":"PASS supplemental storage/identity/no-message-trigger checks; independent review still required"}
p=root/"proofs-supplemental-readonly.json";assert not p.exists();p.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print("PASS supplemental same-run four unique relationships/conversations; all original UI recovery/isolation; no new Message/Outbox trigger; original runner exit1 preserved")
