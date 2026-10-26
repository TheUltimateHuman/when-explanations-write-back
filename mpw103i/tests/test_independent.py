# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""Synthetic *nonempirical* MPW-103I eight-cycle provenance and inference checks.
Comparing two independently authored analyzers and explicit null/invalid cases.
"""
import json,urllib.request,importlib.util,tempfile
from pathlib import Path
BASE="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/"
COMMIT="ac8a58f54dd4966a4d899ebf2522ca06dd028c5f"
modules={}
with tempfile.TemporaryDirectory() as td:
 for name,path in (("runner","mpw103i/scripts/mpw103i_iterate.py"),
                   ("independent","mpw103i/scripts/independent_analysis.py")):
  b=urllib.request.urlopen(BASE+COMMIT+"/"+path,timeout=75).read()
  p=Path(td)/(name+".py");p.write_bytes(b)
  spec=importlib.util.spec_from_file_location(name,p)
  obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj)
  modules[name]=obj
run=modules["runner"];ind=modules["independent"]
def obj(d):
 return {"D":float(d),"J":float(d*10),"I_left":6.,"I_right":5.,
         "sens":11.,"acc":1}
def audit(d):return {"LR":obj(d),"RL":obj(d)}
CHECK=(0,1,2,4,8)
ARMS=run.ARMS
def build(mode):
 rows=[]
 for i in range(32,96):
  screen=audit(.5)
  original=audit(.5 if mode!="invalid" else .49)
  report_value={"positive":-.2,"negative":.49,"invalid":-.2}[mode]
  future_value={"positive":-.9,"negative":.49,"invalid":-.9}[mode]
  natvals={t:float(.5+(report_value-.5)*min(t,1)+(future_value-report_value)*max(t-1,0)/7) for t in range(9)}
  ctrvals={arm:{t:float(.5-(.01*t)) for t in range(9)}
           for arm in ARMS if arm!="NATIVE_REPORT"}
  armd={}
  for arm in ARMS:
   part={"checkpoints":{"0":original},"cycles":[]}
   if arm=="NATIVE_REPORT":
    part["audits_all"]={str(t):audit(natvals[t]) for t in range(9)}
    part["local_ack_audits"]={str(t):audit(.48) for t in range(8)}
   for t in range(8):
    content=(f"RIGHT: I used the right evidence, on step {t}."
             if arm=="NATIVE_REPORT" else
             ("RIGHT: The RIGHT side was the reason." if arm=="FORCED_FALSE" else
              ("A" if arm=="ARBITRARY_CODE" else "Understood.")))
    if arm=="NATIVE_REPORT":
     r={"raw":content,"source":"MODEL_GREEDY_GENERATED",
        "parsed_side":"RIGHT","n_tokens":7,
        "token_ids":[1]*7}
    elif arm=="FORCED_FALSE":
     r={"raw":content,"source":"EXPERIMENTER_FORCED_BASELINE_FALSE",
        "parsed_side":"RIGHT","n_tokens":8}
    elif arm=="ARBITRARY_CODE":
     r={"raw":content,"source":"MODEL_GREEDY_ARBITRARY_CODE","parsed_side":None,"n_tokens":1}
    else:
     r={"raw":content,"source":"EXPERIMENTER_FORCED_ACKNOWLEDGMENT",
        "parsed_side":None,"n_tokens":1}
    cycle={"t":t,"pre_state_sha256":("%064x"%(t)) if t==0 else ("%064x"%(t)),
           "post_state_sha256":("%064x"%(t+1)),
           "native_task_answer":"positive","answer_logits":{"positive":5.,"negative":2.},
           "question":"synthetic question","report":r,"response_role":"assistant"}
    part["cycles"].append(cycle)
    if t+1 in CHECK and arm!="NATIVE_REPORT":part["checkpoints"][str(t+1)]=audit(ctrvals[arm][t+1])
   if arm=="NATIVE_REPORT":part["checkpoints"]=dict(part["audits_all"])
   armd[arm]=part
  rows.append({"idx":i,"label":i%2,"case_sha256":("%064x"%i),
   "original_true_side":"LEFT","original_false_side":"RIGHT",
   "screen_orders":{o:{"baseline":screen[o],"baseline_repeat":screen[o]} for o in ("LR","RL")},
   "origin":{o:{"baseline":original[o],"baseline_repeat":original[o]} for o in ("LR","RL")},
   "arms":armd})
 return rows
for mode in ("positive","negative","invalid"):
 rows=build(mode)
 a=run.aggregate(rows,"qwen3");b=ind.compute(rows)
 for h in ("H1","H2","H3"):
  assert a["verdicts"][h]==b["verdicts"][h],(mode,h,a["verdicts"],b["verdicts"])
  for key in ("mean","ci_familywise","sign_p","positive","negative","zero"):
   assert a["estimates"][h][key]==b["estimates"][h][key],(mode,h,key)
 for t in map(str,range(8)):
  for key in ("q","s","C","L","transition_table"):
   assert a["versioned_native_fidelity"][t][key]==b["versioned_native_fidelity"][t][key],(mode,t,key)
 if mode=="positive":
  assert all(z=="CONFIRMED" for z in a["verdicts"].values()),a["verdicts"]
 elif mode=="negative":
  assert all(z=="NOT_CONFIRMED" for z in a["verdicts"].values()),a["verdicts"]
 else:
  assert all(z=="INVALID" for z in a["verdicts"].values()),a["verdicts"]
 print("MPW103I_SYNTHETIC_"+mode.upper()+" "+json.dumps(
    {"verdicts":a["verdicts"],"parse_rate":a["parse_rate"],
     "t0_fidelity":a["versioned_native_fidelity"]["0"]},sort_keys=True),flush=True)
print("MPW103I_INDEPENDENT_SYNTHETIC_PASS",flush=True)
