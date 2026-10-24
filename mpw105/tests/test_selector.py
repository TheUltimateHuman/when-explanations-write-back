# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""MPW-105 pre-GPU train optimizer blindness and versioned q,s,C,L tests.
All observations synthetic; not empirical evidence.
"""
import tempfile,urllib.request,importlib.util,json
from pathlib import Path
ROOT="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/"
REF="f83b6ba0962e729aed7be7dab517e769ab6fe0d9"
modules={}
with tempfile.TemporaryDirectory() as td:
 for label,path in (("audit","mpw105/scripts/independent_selector.py"),
                     ("runner","mpw105/scripts/mpw105_optimize.py")):
  raw=urllib.request.urlopen(ROOT+REF+"/"+path,timeout=60).read()
  file=Path(td)/(label+".py");file.write_bytes(raw)
  spec=importlib.util.spec_from_file_location(label,file)
  obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj)
  modules[label]=obj
au,runner=modules["audit"],modules["runner"]
def d(value):return {"D":float(value),"J":float(value*10),"I_left":6.,"I_right":4.,"sens":10.,"acc":1}
def fixture(target,train=True):
  rows=[];selection={"train_selected":[],"holdout_selected":[]}
  for i in range(80):
   idx=64+i if train else 1000+i
   original={"idx":idx,"case_sha256":("%064x"%idx),"true_side":"LEFT","false_side":"RIGHT",
     "label":i%2,"screen_orders":{o:{"baseline":d(.4),"baseline_repeat":d(.4)}
                               for o in ("LR","RL")}}
   selection["train_selected" if train else "holdout_selected"].append(original)
   native={"code":"B","code_side":"RIGHT","prose_raw":"RIGHT: A short reason.",
           "prose_parseable":True,"prose_side":"RIGHT"}
   candidates=runner.candidate_texts(native)
   policies=list(au.POLICIES) if train else ["P0",target]
   audits={}
   for policy in policies:
    if policy=="P0":val=.4
    elif policy==target:val=-.4 if target=="P1" else .4
    else:val=.4
    audits[policy]={order:d(val) for order in ("LR","RL")}
   rows.append({"idx":idx,"case_sha256":original["case_sha256"],"label":original["label"],
      "truth_side":"LEFT","baseline":{o:{"baseline":d(.4),"baseline_repeat":d(.4)}
               for o in ("LR","RL")},
      "native":native,"candidates":candidates,"audits":audits})
  return rows,selection
train,select=fixture("P1",True)
policy=au.select_policy(train,select)
assert policy["selected_policy"]=="P1",policy
assert all("A0" not in z for z in policy["training_scores"]),policy
evalrows,holdsel=fixture("P1",False)
out=au.evaluate_holdout(evalrows,holdsel,policy)
assert out["primary_verdicts"]=={"H1":"CONFIRMED","H2":"CONFIRMED"},out
assert out["optimized_selector"]["q"]==0 and out["optimized_selector"]["s"]==1
assert out["delta_s_equals_delta_q_plus_delta_C_minus_delta_L"]
print("MPW105_FIXTURE_SCORE_INFLATION "+json.dumps({"winner":policy["selected_policy"],
      "delta_s":out["post_score_gain"]["mean"],
      "delta_q":out["protected_historical_gain"]["mean"],
      "delta_gap":out["provenance_gap_gain"]["mean"],
      "verdicts":out["primary_verdicts"]}),flush=True)

# A competitor that improves q and s to the same degree must fail the gaming claim.
train2,select2=fixture("P4",True)
policy2=au.select_policy(train2,select2)
assert policy2["selected_policy"]=="P4"
eval2,sel2=fixture("P4",False)
out2=au.evaluate_holdout(eval2,sel2,policy2)
assert out2["primary_verdicts"]["H1"]=="CONFIRMED"
assert out2["primary_verdicts"]["H2"]=="NOT_CONFIRMED"
assert out2["protected_historical_gain"]["mean"]==1.0
print("MPW105_FIXTURE_TRUE_FIDELITY "+json.dumps(out2["primary_verdicts"]),flush=True)
 
# If the selector learns P0 (baseline), there can be no held-out gain.
tr3,sel3=fixture("P1",True)
for row in tr3:
  for p in au.POLICIES:
   # Every candidate must be post-writeback unfaithful: all scores tie at zero.
   sign=.4 if row["candidates"][p]["side"]=="RIGHT" else -.4
   row["audits"][p]={o:d(sign) for o in ("LR","RL")}
p3=au.select_policy(tr3,sel3)
assert p3["selected_policy"]=="P0"
e3,s3=fixture("P1",False)
for row in e3:row["audits"]={"P0":{o:d(.4) for o in ("LR","RL")}}
o3=au.evaluate_holdout(e3,s3,p3)
assert all(v=="NOT_CONFIRMED" for v in o3["primary_verdicts"].values())
print("MPW105_FIXTURE_NULL "+json.dumps(o3["primary_verdicts"]),flush=True)
print("MPW105_SYNTHETIC_REGRESSIONS_PASS",flush=True)
