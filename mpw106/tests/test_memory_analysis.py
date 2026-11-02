# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""MPW-106 pre-GPU synthetic positive/null/tamper/delete/wrong-source tests.
Synthetic fixtures are NOT empirical research observations.
"""
import importlib.util,tempfile,urllib.request,copy,json
from pathlib import Path
ROOT="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/"
REF="81b90df478f903e9a50a277950a98ced3f87edd7"
modules={}
with tempfile.TemporaryDirectory() as td:
 for name,path in (("contract","mpw106/scripts/memory_contract.py"),
                   ("builder","mpw106/scripts/build_store.py"),
                   ("analysis","mpw106/scripts/independent_analysis.py")):
  raw=urllib.request.urlopen(ROOT+REF+"/"+path,timeout=90).read()
  p=Path(td)/(name+".py");p.write_bytes(raw)
  spec=importlib.util.spec_from_file_location(name,p)
  z=importlib.util.module_from_spec(spec);spec.loader.exec_module(z)
  modules[name]=z
m,b,a=modules["contract"],modules["builder"],modules["analysis"]
bank="1"*64;rev="c"*40
def audit(D):
 return {"D":float(D),"J":float(10*D),"I_left":6.,"I_right":5.,
         "sens":11.,"acc":1}
def both(D):return {"LR":audit(D),"RL":audit(D)}
writer=[];selected=[]
for i in range(64):
 idx=32+i;side="LEFT" if i%2==0 else "RIGHT"
 original_report=side+": I think this side influenced the answer."
 case=("%064x"%(idx+500))
 native={"source":"MODEL_GREEDY_GENERATED","model_revision":rev,
         "raw":original_report,"raw_sha256":b.sha(original_report),
         "parsed_side":side,"token_ids":[123,456],"n_tokens":2}
 sel={"idx":idx,"label":i%2,"case_sha256":case,
      "true_side":"LEFT","false_side":"RIGHT",
      "screen_orders":{o:{"baseline":audit(.5),"baseline_repeat":audit(.5)}
                       for o in ("LR","RL")}}
 selected.append(sel)
 writer.append({**sel,"native":native})
store=b.build(writer,"qwen3",rev,bank,"a"*40)
for kind,state in store.items():
 check=m.validate_store(state,kind,"qwen3",bank)
 assert check["n"]==64
assert store["DELETED"]["entries"][0]["text"] is None
assert m.lookup(store["DELETED"],32,writer[0]["case_sha256"],"qwen3",bank,"DELETED")["status"]=="NO_RECORD"
assert m.lookup(store["LIVE"],32,writer[0]["case_sha256"],"qwen3",bank,"LIVE")["status"]=="HIT"
for bad_case,kind in (("a"*64,"bad_case"),):
 try:
  m.lookup(store["LIVE"],32,bad_case,"qwen3",bank,"LIVE")
  raise AssertionError(kind+" accepted")
 except m.RetrievalRejected:pass
tampered=copy.deepcopy(store["LIVE"]);tampered["entries"][0]["text"]="wrong content"
try:
 m.lookup(tampered,32,writer[0]["case_sha256"],"qwen3",bank,"LIVE")
 raise AssertionError("tampered payload accepted")
except m.RetrievalRejected:pass
def rows(mode):
 out=[]
 for writerrow in writer:
  ix=writerrow["idx"]
  side=writerrow["native"]["parsed_side"]
  is_false=side=="RIGHT"
  conditions={}
  if mode=="positive":
   changed=-.6 if is_false else .6
   corr=.8
  else:
   changed=.5;corr=.5
  D={"CLEAN":.5,"NEUTRAL":.5,"LIVE":changed,"CORRECTED":corr,
     "DELETED":.5,"MISSING":.5,"EXPLICIT_STALE":changed}
  reads={}
  for arm,value in D.items():
   conditions[arm]=both(value)
   if arm=="CLEAN":
    reads[arm]={"status":"NO_LOOKUP"}
   else:
    origkind="LIVE" if arm=="EXPLICIT_STALE" else arm
    if arm=="MISSING":
     text=None;source=None
    else:
     record=next(x for x in store[origkind]["entries"] if
                 x["case_id"]==m.case_id(ix))
     text=record["text"];source=record["source"]
    visible=a.MEMORY_WRAPPER+text+'"' if text is not None else a.MISSING_WRAPPER
    reads[arm]={"status":"HIT" if text is not None else "NO_RECORD",
      "model_visible_text":visible,"text_sha256":m.sha(text) if text is not None else None,
      "prefix_sha256":"4"*64,"source":source}
  out.append({"idx":ix,"label":writerrow["label"],
    "case_sha256":writerrow["case_sha256"],
    "original_true_side":"LEFT","original_false_side":"RIGHT",
    "original_report_side":side,
    "original_report_sha256":writerrow["native"]["raw_sha256"],
    "original_report_text":writerrow["native"]["raw"],
    "screen_orders":writerrow["screen_orders"],
    "clean_baseline":both(.5),"clean_repeat":both(.5),
    "conditions":conditions,"reads":reads,
    "model_process":"FRESH_HF_GPU_JOB_NO_WRITER_HISTORY"})
 return out
selection={"selected":selected}
for mode in ("positive","null"):
 full=rows(mode)
 result=a.analyze(full,selection,store,"qwen3",bank)
 expected="CONFIRMED" if mode=="positive" else "NOT_CONFIRMED"
 assert all(result["primary"][h]["verdict"]==expected
            for h in ("H1","H2","H3")),(mode,result["primary"])
 for v in result["versioned_fidelity"].values():
  assert abs(v["s"]-v["q"]-v["C"]+v["L"])<1e-12
 print("MPW106_SYNTHETIC_"+mode.upper()+" "+json.dumps(
    {"n":result["n"],"n_false":result["n_originally_unfaithful_parseable_reports"],
     "verdicts":{h:result["primary"][h]["verdict"] for h in ("H1","H2","H3")},
     "q":result["versioned_fidelity"]["LIVE"]["q"],
     "s":result["versioned_fidelity"]["LIVE"]["s"]},sort_keys=True),flush=True)
bad=rows("positive")
bad[0]["reads"]["LIVE"]["text_sha256"]="0"*64
try:
 a.analyze(bad,selection,store,"qwen3",bank)
 raise AssertionError("BAD_SOURCE_ACCEPTED")
except RuntimeError:pass
print("MPW106_SYNTAX_AND_INDEPENDENT_TESTS_PASS",flush=True)
