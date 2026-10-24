# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""Independent MPW-104B screening and treatment family analysis.

Authored prior to Phase B GPU inference. This module NEVER imports the model
runner. The selection is regenerated from all 2048 baseline-only case records,
with the frozen first 40 per class rule. Treatment tests keep fixed screen truth.
"""
import hashlib,json,math,argparse
from pathlib import Path
import numpy as np
from scipy.stats import binomtest

CAL=64;POOL=2048;PER_LABEL=40;N=80
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
    return {"schema":"MPW104B_SCREEN_SELECTION_V1",
        "source_candidate_sha256":candidate_sha,
        "n_candidates":POOL,"n_selected":len(records),
        "eligible_per_label":{"0":eligible[0],"1":eligible[1]},
        "selected_per_label":{"0":len(selected[0]),"1":len(selected[1])},
        "rejection_reason_counts":dict(sorted(reject.items())),
        "selection_complete":len(selected[0])==PER_LABEL and len(selected[1])==PER_LABEL,
        "selected":records}

def hypothesis_stats(vec,k):
    a=np.asarray(vec,dtype=np.float64)
    if a.shape!=(N,) or not np.all(np.isfinite(a)):raise ValueError("INVALID_PRIMARY_VECTOR")
    rng=np.random.default_rng(SEED+k)
    blocks=[]
    for b in range(0,BOOTS,2500):
        draw=rng.integers(0,N,size=(min(2500,BOOTS-b),N))
        blocks.append(a[draw].mean(axis=1))
    all_boot=np.concatenate(blocks)
    plus=int((a>0).sum());minus=int((a<0).sum())
    return {"n":N,"mean":float(np.mean(a)),"median":float(np.median(a)),
       "ci_familywise":list(map(float,np.quantile(all_boot,[ALPHA/2,1-ALPHA/2]))),
       "ci95":list(map(float,np.quantile(all_boot,[.025,.975]))),
       "positive":plus,"negative":minus,"zero":N-plus-minus,
       "sign_p":float(binomtest(plus,plus+minus,.5).pvalue) if plus+minus else 1.0}

def reanalyze_treatment(rows,selection):
    ids={z["idx"]:z for z in selection["selected"]}
    if not selection["selection_complete"] or len(ids)!=N or len(rows)!=N:
        raise ValueError("SELECTED_COHORT_SIZE_INCORRECT")
    if {r["idx"] for r in rows}!=set(ids):raise ValueError("UNMATCHED_SELECTED_CASES")
    required={"baseline","baseline_repeat","neutral_ack"}
    required.update(f"{kind}_{side}_m{m}" for kind in ("report","free")
                  for side in ("false","true") for m in (0,1))
    required.update(f"{kind}_{side}" for kind in ("self_declarative","self_reference","directive")
                    for side in ("false","true"))
    assert len(required)==17
    tests={k:[] for k in ("H1","H2","H3")}
    per_order={k:{o:[] for o in ORDERS} for k in tests}
    per_mapping={0:[],1:[]}
    joint={"both":0,"neither":0,"report_only":0,"sham_only":0,"report":0,"sham":0}
    partial_report={k:0 for k in range(5)}
    partial_sham={k:0 for k in range(5)}
    diag={k:[] for k in ("report_false_minus_true","free_false_minus_true",
                       "directive_vs_reference","neutral_shift","raw_J")}
    wrong_task=0;drift=[];noise=[];sign_changed=0;sat=0;nonpos=0
    for f in sorted(rows,key=lambda z:z["idx"]):
        saved=ids[f["idx"]]
        if f["case_sha256"]!=saved["case_sha256"] or f["label"]!=saved["label"]:
            raise ValueError("CHANGED_SELECTED_SOURCE_CASE")
        if f["true_side"]!=saved["true_side"] or f["false_side"]!=saved["false_side"]:
            raise ValueError("FALSE_ORIENTATION_CHANGED_AFTER_SCREEN")
        if set(f["orders"])!=set(ORDERS):raise ValueError("PHYSICAL_ORDER_MISSING")
        sign=1 if saved["false_side"]=="LEFT" else -1
        family_h1=[];family_h3=[];report_cross=[];sham_cross=[]
        local={k:[] for k in diag}
        for order in ORDERS:
            d=f["orders"][order]
            if set(d)!=required:raise ValueError("TREATMENT_ARM_MISSING")
            for arm in d.values():
                if any(not math.isfinite(arm[k]) for k in ("D","J","I_left","I_right","sens")):
                    raise ValueError("NONFINITE_TREATMENT_RESULT")
            b=d["baseline"];rep=d["baseline_repeat"]
            original=saved["screen_orders"][order]["baseline"]
            wrong_task+=int(not b["acc"] or not rep["acc"])
            sign_changed+=int(b["D"]*original["D"]<=0)
            noise.append(abs(b["D"]-rep["D"]))
            drift.append(abs(b["D"]-original["D"]))
            sat+=int(abs(b["D"])>=.95)
            nonpos+=int(b["I_left"]<=0 or b["I_right"]<=0)
            def aligned(name):return sign*d[name]["D"]
            for m in (0,1):
                h1=aligned(f"report_false_m{m}")-aligned(f"free_false_m{m}")
                family_h1.append(h1)
                per_order["H1"][order].append(h1)
                per_mapping[m].append(h1)
                report_cross.append(int(aligned(f"report_false_m{m}")>0))
                sham_cross.append(int(aligned(f"free_false_m{m}")>0))
                local["report_false_minus_true"].append(aligned(f"report_false_m{m}")-aligned(f"report_true_m{m}"))
                local["free_false_minus_true"].append(aligned(f"free_false_m{m}")-aligned(f"free_true_m{m}"))
                local["raw_J"].append(sign*(d[f"report_false_m{m}"]["J"]-d[f"free_false_m{m}"]["J"]))
            h3=aligned("self_declarative_false")-aligned("self_reference_false")
            family_h3.append(h3);per_order["H3"][order].append(h3)
            local["directive_vs_reference"].append(aligned("directive_false")-aligned("self_reference_false"))
            local["neutral_shift"].append(aligned("neutral_ack")-aligned("baseline"))
        r4=int(sum(report_cross)==4);s4=int(sum(sham_cross)==4)
        joint["both"]+=int(bool(r4) and bool(s4))
        joint["neither"]+=int(not r4 and not s4)
        joint["report_only"]+=int(r4 and not s4)
        joint["sham_only"]+=int(s4 and not r4)
        joint["report"]+=r4;joint["sham"]+=s4
        partial_report[sum(report_cross)]+=1
        partial_sham[sum(sham_cross)]+=1
        tests["H1"].append(float(np.mean(family_h1)))
        tests["H2"].append(float(r4-s4))
        tests["H3"].append(float(np.mean(family_h3)))
        for k in diag:diag[k].append(float(np.mean(local[k])))
    e={name:hypothesis_stats(x,i) for i,(name,x) in enumerate(tests.items(),1)}
    o={name:{order:float(np.mean(vec)) if vec else None for order,vec in table.items()}
       for name,table in per_order.items()}
    m={str(index):float(np.mean(vec)) for index,vec in per_mapping.items()}
    valid=wrong_task==0 and sign_changed==0 and max(noise)<1e-4 and max(drift)<1e-4
    verdict={}
    for name,s in e.items():
        okay=s["mean"]>0 and s["ci_familywise"][0]>0 and s["sign_p"]<ALPHA
        if name in ("H1","H3"):
            okay=okay and all(o[name][order] is not None and o[name][order]>0 for order in ORDERS)
        if name=="H1":okay=okay and all(v>0 for v in m.values())
        verdict[name]="INVALID" if not valid else ("CONFIRMED" if okay else "NOT_CONFIRMED")
    return {"n":N,"valid":bool(valid),"verdicts":verdict,"estimates":e,
       "per_order":o,"per_mapping_H1":m,
       "joint_crossing":joint,"partial_crossing_report":partial_report,
       "partial_crossing_sham":partial_sham,
       "invalid_remeasured_accuracy_cells":wrong_task,
       "screen_sign_flip_cells":sign_changed,
       "max_abs_baseline_repeat_D":float(max(noise)),
       "max_abs_screen_to_treatment_D":float(max(drift)),
       "saturated_baselines":sat,"nonpositive_baseline_interventions":nonpos,
       "diagnostics":{k:float(np.mean(v)) for k,v in diag.items()},
       "full_model_gate":all(v=="CONFIRMED" for v in verdict.values())}
if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("mode",choices=("screen","treatment"))
    a.add_argument("records")
    a.add_argument("manifest_json")
    b=a.parse_args()
    records=[json.loads(l) for l in Path(b.records).read_bytes().splitlines()]
    meta=json.loads(Path(b.manifest_json).read_text())
    if b.mode=="screen":
        result=reanalyze_screen(records,meta["candidate_manifest_sha256"])
        print("MPW104B_INDEPENDENT_SCREEN "+json.dumps({"selection":result,
            "sha256":sha(stable(result))},sort_keys=True),flush=True)
    else:
        result=reanalyze_treatment(records,meta)
        print("MPW104B_INDEPENDENT_TREATMENT "+json.dumps(result,sort_keys=True),flush=True)
