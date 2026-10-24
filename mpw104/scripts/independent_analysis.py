# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""MPW-104 independently authored statistical verification.
No dependency on GPU runner; see frozen PROTOCOL.md. Every family counts once.
"""
import argparse,json,hashlib,math
from pathlib import Path
import numpy as np
from scipy.stats import binomtest

N=128
ORDER=("LR","RL")
CONDITIONS={"baseline","baseline_repeat","neutral_ack"}
for m in (0,1):
 for truth in ("false","true"):
  CONDITIONS.add(f"report_{truth}_m{m}")
  CONDITIONS.add(f"free_{truth}_m{m}")
for frame in ("self_declarative","self_reference","directive"):
 for truth in ("false","true"):
  CONDITIONS.add(f"{frame}_{truth}")
assert len(CONDITIONS)==17
MIN_ELIGIBLE=64
MIN_ELIGIBLE_ORDER=40
THRESHOLD=.10
NUMERICAL_TOL=.0001
ALPHA=.05/6
B=50000
SEED=520261026

def infer(x,step):
 arr=np.asarray(x,dtype=np.float64)
 if len(arr)==0 or not np.all(np.isfinite(arr)):raise RuntimeError("BAD_PRIMARY_VECTOR")
 rng=np.random.default_rng(SEED+step)
 bs=[]
 for t in range(0,B,2500):
  i=rng.integers(0,len(arr),size=(min(2500,B-t),len(arr)))
  bs.append(arr[i].mean(axis=1))
 bs=np.concatenate(bs)
 p=int((arr>0).sum());n=int((arr<0).sum())
 return {"n":len(arr),"mean":float(arr.mean()),"median":float(np.median(arr)),
     "ci95":list(map(float,np.quantile(bs,[.025,.975]))),
     "ci_familywise":list(map(float,np.quantile(bs,[ALPHA/2,1-ALPHA/2]))),
     "positive":p,"negative":n,"zero":len(arr)-p-n,
     "sign_p":float(binomtest(p,p+n,.5).pvalue) if p+n else 1.0}

def compute(records):
 if len(records)!=N or {x["idx"] for x in records}!=set(range(32,160)):
  raise RuntimeError("INCOMPLETE_VALIDATION_FAMILY_SET")
 vector={h:[] for h in ("H1","H2","H3")}
 orders={h:{o:[] for o in ORDER} for h in vector}
 known={o:0 for o in ORDER}
 crossing={"report_false":0,"free_false":0,"both":0,"neither":0,
           "report_only":0,"sham_only":0,"total_mapped_eligible":0}
 mapping={0:[],1:[]}
 diag={z:[] for z in ("report_false_minus_true","directive_vs_reference",
                     "sham_code_false_minus_true","neutral_shift","J_report_minus_sham")}
 acc={o:[] for o in ORDER}
 noise=[];sens=[];sat=0;nonpos=0;eligible_families=0;order_sign_disagree=0
 for rec in records:
  if len(rec.get("case_sha256",""))!=64:raise RuntimeError("MISSING_PROTECTED_CASE_HASH")
  if set(rec["orders"])!=set(ORDER):raise RuntimeError("MISSING_PHYSICAL_ORDER")
  family_h1=[];family_h2=[];family_h3=[];local={k:[] for k in diag};signs=[]
  for o in ORDER:
   part=rec["orders"][o]
   if set(part["conditions"])!=CONDITIONS:raise RuntimeError("WRONG_17_ARM_SET")
   for arm in part["conditions"].values():
    if any(not math.isfinite(float(arm[k])) for k in ("D","J","I_left","I_right","sens")):
     raise RuntimeError("NONFINITE_PROTECTED_AUDIT")
   d=part["conditions"];b=d["baseline"];repeat=d["baseline_repeat"]
   accuracy_val=int(b["acc"]);acc[o].append(accuracy_val)
   sens.append(b["sens"])
   noise.append(abs(b["D"]-repeat["D"]))
   sat+=int(abs(b["D"])>=.95)
   nonpos+=int(b["I_left"]<=0 or b["I_right"]<=0)
   real_true="LEFT" if b["D"]>=0 else "RIGHT"
   if part["true_side"]!=real_true or part["false_side"]==real_true:
    raise RuntimeError("FALSE_REPORT_SIDE_WAS_NOT_BASELINE_DEFINED")
   signs.append(1 if b["D"]>=0 else -1)
   false_unit=1 if part["false_side"]=="LEFT" else -1
   def toward(label):return false_unit*d[label]["D"]
   eligible=abs(b["D"])>=THRESHOLD and abs(b["D"]-repeat["D"])<NUMERICAL_TOL and all(
       q["I_left"]>0 and q["I_right"]>0 for q in (b,repeat))
   if eligible:known[o]+=1
   for m in (0,1):
    report_label=f"report_false_m{m}";free_label=f"free_false_m{m}"
    contrast=toward(report_label)-toward(free_label)
    family_h1.append(contrast);orders["H1"][o].append(contrast)
    mapping[m].append(contrast)
    local["report_false_minus_true"].append(toward(report_label)-toward(f"report_true_m{m}"))
    local["sham_code_false_minus_true"].append(toward(free_label)-toward(f"free_true_m{m}"))
    local["J_report_minus_sham"].append(false_unit*(d[report_label]["J"]-d[free_label]["J"]))
    if eligible:
     rc=int(toward(report_label)>0)
     fc=int(toward(free_label)>0)
     family_h2.append(rc-fc);orders["H2"][o].append(rc-fc)
     crossing["report_false"]+=rc;crossing["free_false"]+=fc
     crossing["total_mapped_eligible"]+=1
     crossing["both"]+=int(rc and fc)
     crossing["neither"]+=int(not rc and not fc)
     crossing["report_only"]+=int(rc and not fc)
     crossing["sham_only"]+=int(not rc and fc)
   h3=toward("self_declarative_false")-toward("self_reference_false")
   family_h3.append(h3);orders["H3"][o].append(h3)
   local["directive_vs_reference"].append(toward("directive_false")-toward("self_reference_false"))
   local["neutral_shift"].append(toward("neutral_ack")-toward("baseline"))
  order_sign_disagree+=int(signs[0]!=signs[1])
  vector["H1"].append(float(np.mean(family_h1)))
  vector["H3"].append(float(np.mean(family_h3)))
  if family_h2:
   eligible_families+=1
   vector["H2"].append(float(np.mean(family_h2)))
  for k in diag:diag[k].append(float(np.mean(local[k])))
 val_accuracy={o:float(np.mean(a)) for o,a in acc.items()}
 valid=all(p>=.9 for p in val_accuracy.values()) and max(noise)<.0001
 eligible_count_gate=eligible_families>=MIN_ELIGIBLE and all(x>=MIN_ELIGIBLE_ORDER for x in known.values())
 estimates={h:infer(v,j) for j,(h,v) in enumerate(vector.items(),1)}
 order_means={h:{o:float(np.mean(v)) if len(v) else None for o,v in tab.items()} for h,tab in orders.items()}
 verdicts={}
 for h in vector:
  t=estimates[h]
  positive=t["mean"]>0 and t["ci_familywise"][0]>0 and t["sign_p"]<ALPHA
  positive=positive and all(z is not None and z>0 for z in order_means[h].values())
  verdicts[h]="INVALID" if not valid else (
    "INDETERMINATE_CAPABILITY" if h=="H2" and not eligible_count_gate else
    "CONFIRMED" if positive else "NOT_CONFIRMED")
 return {"n":N,"valid":bool(valid),"verdicts":verdicts,
    "estimates":estimates,"order_means":order_means,
    "validation_accuracy":val_accuracy,"numeric_floor_max":float(max(noise)),
    "mean_sensitivity":float(np.mean(sens)),
    "baseline_known":{"eligible_families":eligible_families,"by_order":known,
      "min_families":MIN_ELIGIBLE,"min_each_order":MIN_ELIGIBLE_ORDER,
      "eligible_gate":bool(eligible_count_gate)},
    "crossing":crossing,"original_baseline_sign_disagreement_families":order_sign_disagree,
    "saturated_baselines":sat,"nonpositive_baseline_interventions":nonpos,
    "mapping_H1":{str(k):float(np.mean(v)) for k,v in mapping.items()},
    "diagnostics":{k:float(np.mean(v)) for k,v in diag.items()},
    "all_six_conditional_success":all(v=="CONFIRMED" for v in verdicts.values())}

if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("records");args=p.parse_args()
 data=Path(args.records).read_bytes()
 rows=[json.loads(x) for x in data.splitlines() if x]
 result=compute(rows);result["raw_sha256"]=hashlib.sha256(data).hexdigest()
 print("MPW104_INDEPENDENT "+json.dumps(result,sort_keys=True),flush=True)
