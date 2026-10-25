# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""Independent MPW-103I untreated-only baseline screening and fixed 64-family selection.

Authored prior to Phase B GPU inference. This module NEVER imports the model
runner. The selection is regenerated from all 2048 baseline-only case records,
with the frozen first 40 per class rule. Treatment tests keep fixed screen truth.
"""
import hashlib,json,math,argparse
from pathlib import Path
import numpy as np
from scipy.stats import binomtest

CAL=32;POOL=2048;PER_LABEL=32;N=64
ORDERS=("LR","RL")
BOOTS=50000;SEED=520261027;ALPHA=.05/6
def stable(x):return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def sha(x):return hashlib.sha256(x if isinstance(x,bytes) else x.encode()).hexdigest()
def reanalyze_screen(rows,candidate_sha):
    if len(rows)!=POOL or {r.get("idx") for r in rows}!=set(range(CAL,CAL+POOL)):
        raise ValueError("INCOMPLETE_SCREEN_CANDIDATE_SET")
    eligible={0:0,1:0};selected={0:[],1:[]};reject={}
    for row in sorted(rows,key=lambda z:z["idx"]):
        y=row["label"]
        if y not in (0,1) or not isinstance(row.get("case_sha256"),str) or len(row["case_sha256"])!=64:
            raise ValueError("MALFORMED_CANDIDATE")
        if set(row.get("orders",{}))!=set(ORDERS):
            raise ValueError("SCREEN_ORDER_MISSING")
        reasons=[]
        signs={}
        for physical in ORDERS:
            audit=row["orders"][physical]
            if set(audit)!={"baseline","baseline_repeat"}:raise ValueError("TREATMENT_PRESENT_IN_SCREEN")
            orig,rep=audit["baseline"],audit["baseline_repeat"]
            for z in (orig,rep):
                if not all(math.isfinite(z[k]) for k in ("D","J","I_left","I_right","sens")):
                    reasons.append("NONFINITE")
            if not orig["acc"] or not rep["acc"]:
                reasons.append("INCORRECT_TASK_"+physical)
            if abs(orig["D"])<.10:reasons.append("LOW_D_"+physical)
            if abs(orig["D"]-rep["D"])>=.0001:reasons.append("NOISY_D_"+physical)
            if not (orig["I_left"]>0 and orig["I_right"]>0 and
                    rep["I_left"]>0 and rep["I_right"]>0):
                reasons.append("NONPOSITIVE_CAUSAL_CHANNEL_"+physical)
            signs[physical]=orig["D"]
        if signs["LR"]*signs["RL"]<=0:
            reasons.append("ORDER_SIGN_INCONSISTENT")
        if reasons:
            for reason in set(reasons):
                reject[reason]=reject.get(reason,0)+1
            continue
        eligible[y]+=1
        if len(selected[y])<PER_LABEL:
            side="LEFT" if signs["LR"]>0 else "RIGHT"
            selected[y].append({"idx":row["idx"],"label":y,
                "case_sha256":row["case_sha256"],
                "true_side":side,
                "false_side":"RIGHT" if side=="LEFT" else "LEFT",
                "screen_orders":row["orders"]})
    records=sorted(selected[0]+selected[1],key=lambda row:row["idx"])
    return {"schema":"MPW103I_SCREEN_SELECTION_V1",
        "source_candidate_sha256":candidate_sha,
        "n_candidates":POOL,"n_selected":len(records),
        "eligible_per_label":{"0":eligible[0],"1":eligible[1]},
        "selected_per_label":{"0":len(selected[0]),"1":len(selected[1])},
        "rejection_reason_counts":dict(sorted(reject.items())),
        "selection_complete":len(selected[0])==PER_LABEL and len(selected[1])==PER_LABEL,
        "selected":records}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("records")
    p.add_argument("candidate_sha")
    z=p.parse_args()
    rows=[json.loads(line) for line in Path(z.records).read_bytes().splitlines()]
    out=reanalyze_screen(rows,z.candidate_sha)
    print("MPW103I_INDEPENDENT_SCREEN "+json.dumps(
        {"selection":out,"selection_sha256":sha(stable(out))},
        sort_keys=True),flush=True)
