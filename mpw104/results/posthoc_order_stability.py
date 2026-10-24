# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3"]
# ///
"""MPW-104: post hoc boundary audit for order-stable false baselines.
All results explicitly exploratory, not revisions to H1/H2/H3 gates.
"""
import base64,gzip,hashlib,json
from urllib.request import urlopen
import numpy as np

COMMIT="f10e06094607510a98f1d459cb0e4e4626f4e60e"
ROOT=f"https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/{COMMIT}/mpw104/results/"
MAN=json.loads(urlopen(ROOT+"RESULTS_MANIFEST.json",timeout=90).read())

def sha(b):return hashlib.sha256(b).hexdigest()
def load(model):
 info=MAN["models"][model]
 parts=[]
 for j,s in enumerate(info["shards"]):
  b64=urlopen(ROOT+f"{model}_shard{j+1:02d}.jsonl.gz.b64",timeout=90).read().strip()
  raw=gzip.decompress(base64.b64decode(b64,validate=True))
  assert sha(raw)==s["raw_sha256"] and len(raw.splitlines())==32
  parts.append(raw)
 combined=b"".join(parts)
 assert sha(combined)==info["combined_raw_sha256"]
 return [json.loads(x) for x in combined.splitlines()],sha(combined)

def description(rows):
 records=[]
 for f in rows:
  signs={};known={};H1={};H2={};H3={}
  for order in ("LR","RL"):
   q=f["orders"][order];d=q["conditions"];base=d["baseline"];repeat=d["baseline_repeat"]
   signs[order]=1 if base["D"]>=0 else -1
   known[order]=(abs(base["D"])>=.10 and
     abs(base["D"]-repeat["D"])<1e-4 and
     all(p["I_left"]>0 and p["I_right"]>0 for p in (base,repeat)))
   a=1 if q["false_side"]=="LEFT" else -1
   H1[order]=float(np.mean([a*(d[f"report_false_m{m}"]["D"]-d[f"free_false_m{m}"]["D"]) for m in (0,1)]))
   H2[order]=float(np.mean([int(a*d[f"report_false_m{m}"]["D"]>0)-int(a*d[f"free_false_m{m}"]["D"]>0) for m in (0,1)]))
   H3[order]=float(a*(d["self_declarative_false"]["D"]-d["self_reference_false"]["D"]))
  consistent=signs["LR"]==signs["RL"]
  selected=[o for o in ("LR","RL") if known[o]]
  records.append({"idx":f["idx"],"consistent":consistent,
   "known_both":known["LR"] and known["RL"],"known_at_least_one":bool(selected),
   "H1":float(np.mean(list(H1.values()))),
   "H2":float(np.mean([H2[o] for o in selected])) if selected else None,
   "H3":float(np.mean(list(H3.values()))),
   "H2_order":H2})
 output={"families":len(records),
    "order_consistent":sum(x["consistent"] for x in records),
    "order_inconsistent":sum(not x["consistent"] for x in records),
    "known_at_least_one":sum(x["known_at_least_one"] for x in records),
    "known_both_orders":sum(x["known_both"] for x in records)}
 groups={
  "full":records,
  "order_consistent":[x for x in records if x["consistent"]],
  "order_inconsistent":[x for x in records if not x["consistent"]],
  "order_consistent_baseline_known_one":[x for x in records if x["consistent"] and x["known_at_least_one"]],
  "order_consistent_baseline_known_both":[x for x in records if x["consistent"] and x["known_both"]],
  "order_inconsistent_baseline_known_one":[x for x in records if not x["consistent"] and x["known_at_least_one"]]}
 out={}
 rng=np.random.default_rng(520261204)
 for group,tab in groups.items():
  result={"n_families":len(tab)}
  for metric in ("H1","H2","H3"):
   arr=np.array([x[metric] for x in tab if x[metric] is not None],dtype=float)
   if not len(arr):
    result[metric]={"n":0}
    continue
   boots=[]
   for i in range(0,20000,1000):
    indices=rng.integers(0,len(arr),size=(1000,len(arr)))
    boots.append(arr[indices].mean(axis=1))
   bb=np.concatenate(boots)
   result[metric]={"n":len(arr),"mean":float(np.mean(arr)),
      "positive":int(np.count_nonzero(arr>0)),"negative":int(np.count_nonzero(arr<0)),
      "ties":int(np.count_nonzero(arr==0)),
      "exploratory_bootstrap_95":[float(v) for v in np.quantile(bb,[.025,.975])]}
  out[group]=result
 output["groups"]=out
 return output

for model in ("qwen3","granite"):
 rows,digest=load(model)
 print("MPW104_POSTHOC_ORDER_STABILITY "+json.dumps({"model":model,"raw_sha256":digest,
    "status":"EXPLORATORY_AFTER_OUTCOMES_UNADJUSTED",
    "summary":description(rows)},sort_keys=True),flush=True)
