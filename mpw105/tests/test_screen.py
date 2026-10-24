# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""Compare pre-GPU MPW105 source selection with separately implemented CPU rule.
All records synthetic, no inference and no empirical signal.
"""
import importlib.util,tempfile,urllib.request,json
from pathlib import Path
ROOT="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/"
COMMIT="ab7edb0d8c077e23e336832199262c4f27de8393"
modules={}
with tempfile.TemporaryDirectory() as td:
 for name,path in (("runner","mpw105/scripts/mpw105_screen.py"),
                   ("blind","mpw105/scripts/independent_screen.py")):
  data=urllib.request.urlopen(ROOT+COMMIT+"/"+path,timeout=70).read()
  p=Path(td)/(name+".py");p.write_bytes(data)
  spec=importlib.util.spec_from_file_location(name,p)
  z=importlib.util.module_from_spec(spec);spec.loader.exec_module(z);modules[name]=z
a,b=modules["runner"],modules["blind"]
def score(x):return {"D":float(x),"J":float(x*5),"I_left":5.,"I_right":4.,"sens":9.,"acc":1}
rows=[]
for i in range(64,64+3072):
 label=(i-64)%2
 lr=.4 if label else -.4
 rl=lr if i%5 else -lr
 rows.append({"idx":i,"label":label,"case_sha256":("%064x"%i),
     "orders":{order:{"baseline":score(val),"baseline_repeat":score(val)}
            for order,val in (("LR",lr),("RL",rl))}})
x=a.select_from_screen(rows)
y=b.reanalyze_screen(rows,a.EXPECTED_CANDIDATE_MANIFEST)
assert x==y,("SELECTION_CHANGED",len(x["selected"]),len(y["selected"]))
assert x["selection_complete"] and x["n_train"]==80 and x["n_holdout"]==80
assert x["n_selected"]==160
assert {z["idx"] for z in x["train_selected"]}.isdisjoint({z["idx"] for z in x["holdout_selected"]})
assert sum(z["label"]==0 for z in x["train_selected"])==40
assert sum(z["label"]==1 for z in x["holdout_selected"])==40
rows_bad=rows[:-1]
try:
 b.reanalyze_screen(rows_bad,a.EXPECTED_CANDIDATE_MANIFEST)
 raise AssertionError("MISSING_CASE_ACCEPTED")
except ValueError:
 pass
print("MPW105_SCREEN_SYNTHETIC_VERIFIED "+json.dumps({"screen_n":len(rows),
 "train_n":x["n_train"],"holdout_n":x["n_holdout"],
 "matched_independent":True,"sample_hash":a.EXPECTED_CANDIDATE_MANIFEST,
 "rejection_reasons":x["rejection_reason_counts"]},sort_keys=True),flush=True)
