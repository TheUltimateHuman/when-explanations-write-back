# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""MPW-104B pre-GPU positive, negative, invalid & screen-selection regression tests."""
import json,importlib.util,tempfile,urllib.request
from pathlib import Path
BASE="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/"
paths={
 "runner":"02c0f00491a2bd40216fc9471755ee201d95f5e3/mpw104b/scripts/mpw104b.py",
 "independent":"02c0f00491a2bd40216fc9471755ee201d95f5e3/mpw104b/scripts/independent_analysis.py"
}
modules={}
with tempfile.TemporaryDirectory() as td:
 for n,u in paths.items():
  raw=urllib.request.urlopen(BASE+u,timeout=60).read()
  p=Path(td)/(n+".py");p.write_bytes(raw)
  spec=importlib.util.spec_from_file_location(n,p)
  z=importlib.util.module_from_spec(spec);spec.loader.exec_module(z)
  modules[n]=z
r=modules["runner"];a=modules["independent"]
def point(D,acc=1):
 return {"D":float(D),"J":float(D*10),"I_left":5.,"I_right":3.,
         "sens":8.,"acc":int(acc)}
screen=[]
for ix in range(64,64+2048):
 y=(ix-64)%2
 lr=point(.4 if y==0 else -.4)
 rl=point(.45 if y==0 else -.35)
 if ix%13==0:
  rl=point(-rl["D"])
 screen.append({"idx":ix,"label":y,"case_sha256":("%064x"%ix),
  "orders":{"LR":{"baseline":lr,"baseline_repeat":dict(lr)},
            "RL":{"baseline":rl,"baseline_repeat":dict(rl)}}})
sel=r.select_from_screen(screen)
blind=a.reanalyze_screen(screen,r.EXPECTED_CANDIDATE_MANIFEST)
assert sel==blind,("SELECTION_DISAGREES",sel["rejection_reason_counts"],blind["rejection_reason_counts"])
assert sel["n_selected"]==80 and sel["selection_complete"]
assert sum(sel["selected_per_label"].values())==80
def synth_data(mode):
 rows=[]
 for entry in sel["selected"]:
  orders={}
  for order in ("LR","RL"):
   b=point(entry["screen_orders"][order]["baseline"]["D"])
   ds={"baseline":b,"baseline_repeat":dict(b),"neutral_ack":point(.01)}
   sign=1 if entry["false_side"]=="LEFT" else -1
   for m in (0,1):
    if mode=="positive":
     report=sign*.5;free=sign*(-.2)
    elif mode=="negative":
     report=sign*(-.2);free=sign*(+.5)
    else:
     report=sign*.5;free=sign*(-.2)
    ds[f"report_false_m{m}"]=point(report)
    ds[f"report_true_m{m}"]=point(-report)
    ds[f"free_false_m{m}"]=point(free)
    ds[f"free_true_m{m}"]=point(-free)
   ds["self_declarative_false"]=point(sign*.35)
   ds["self_declarative_true"]=point(sign*(-.35))
   ds["self_reference_false"]=point(sign*(-.25))
   ds["self_reference_true"]=point(sign*.25)
   ds["directive_false"]=point(sign*.7)
   ds["directive_true"]=point(sign*(-.7))
   if mode=="invalid" and entry["idx"]==sel["selected"][3]["idx"]:
    ds["baseline_repeat"]["D"]=b["D"]+.01
   orders[order]=ds
  rows.append({"idx":entry["idx"],"case_sha256":entry["case_sha256"],
    "label":entry["label"],"true_side":entry["true_side"],
    "false_side":entry["false_side"],"orders":orders})
 return rows
for label in ("positive","negative","invalid"):
 data=synth_data(label)
 x=r.aggregate_treatment(data,sel,"qwen3")
 y=a.reanalyze_treatment(data,sel)
 assert x==y,("ANALYSIS_MISMATCH",label,x["verdicts"],y["verdicts"])
 if label=="positive":
  assert all(v=="CONFIRMED" for v in x["verdicts"].values())
 elif label=="negative":
  assert x["verdicts"]["H1"]=="NOT_CONFIRMED" and x["verdicts"]["H2"]=="NOT_CONFIRMED"
 else:
  assert all(v=="INVALID" for v in x["verdicts"].values())
 print("MPW104B_SYNTHETIC_TEST "+json.dumps({"case":label,"verdicts":x["verdicts"],
    "n":len(data),"selected_per_label":sel["selected_per_label"]}),flush=True)
print("MPW104B_INDEPENDENT_SYNTHETIC_PASS",flush=True)
