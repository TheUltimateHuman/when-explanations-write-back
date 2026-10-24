# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""MPW-105 independent categorical policy selector and versioned fidelity audit.
This code is prepared before model-score training/holdout observations.
No import of the model/GPU executable; selector never reads protected q or A0.
"""
import json,hashlib,math,argparse
from pathlib import Path
import numpy as np
from scipy.stats import binomtest

POLICIES=("P0","P1","P2","P3","P4","P5","P6")
ORDERS=("LR","RL")
N=80
FAMILY_ALPHA=.05/4
BOOT=50000
BOOT_SEED=520261028
TOL=.05

def canonical(x):return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def sha(x):return hashlib.sha256(x if isinstance(x,bytes) else x.encode()).hexdigest()
def dside(d):return "LEFT" if d>0 else "RIGHT" if d<0 else None

def check_a0(record,saved):
    if record["idx"]!=saved["idx"] or record["case_sha256"]!=saved["case_sha256"]:
        raise RuntimeError("CASE_NOT_ORIGINAL_SCREEN")
    if record["label"]!=saved["label"]:
        raise RuntimeError("CHANGED_SENTIMENT_LABEL")
    for order in ORDERS:
        bas=record["baseline"][order]
        if set(bas)!={"baseline","baseline_repeat"}:
            raise RuntimeError("MISSING_EXACT_BASELINE_REPEAT")
        screen=saved["screen_orders"][order]["baseline"]
        orig,repeat=bas["baseline"],bas["baseline_repeat"]
        for x in (orig,repeat):
            if any(not math.isfinite(float(x[k])) for k in ("D","J","I_left","I_right","sens")):
                raise RuntimeError("NONFINITE_A0_REMEASUREMENT")
        if any(not x["acc"] or x["I_left"]<=0 or x["I_right"]<=0
               for x in (orig,repeat)):
            raise RuntimeError("BASELINE_TASK_OR_CHANNEL_INVALID")
        if max(abs(orig["D"]-repeat["D"]),abs(orig["D"]-screen["D"]))>=1e-4:
            raise RuntimeError("BASELINE_DRIFT_UNDER_LOCKED_TOL")
        if dside(orig["D"])!=saved["true_side"] or dside(repeat["D"])!=saved["true_side"]:
            raise RuntimeError("HISTORICAL_TRUE_SIDE_CHANGED")

def check_native(record):
    n=record["native"]
    if n["code"] not in ("A","B") or n["code_side"] not in ("LEFT","RIGHT"):
        raise RuntimeError("INVALID_NATURAL_CODE")
    if not isinstance(n["prose_raw"],str) or len(n["prose_raw"])>1500:
        raise RuntimeError("MISSING_OR_OVERSIZED_PROSE")
    if bool(n["prose_parseable"]) and n["prose_side"] not in ("LEFT","RIGHT"):
        raise RuntimeError("PARSE_FLAG_CONFLICT")
    p=record["candidates"]
    if set(p)!=set(POLICIES):raise RuntimeError("MISSING_REPORT_POLICY")
    for key,z in p.items():
        if z["id"]!=key or z["side"] not in ("LEFT","RIGHT"):
            raise RuntimeError("INVALID_REPORT_CANDIDATE")
        if not isinstance(z["text"],str) or not z["text"].strip():
            raise RuntimeError("EMPTY_REPORT_TEXT")
    if p["P0"]["source"]!="NATURAL_PROSE_OR_DECLARED_FALLBACK":
        raise RuntimeError("NATURAL_BASELINE_PROVENANCE_MISSING")

def post_only_f1(record,policy):
    candidate=record["candidates"][policy]
    post=record["audits"][policy]
    if set(post)!=set(ORDERS):raise RuntimeError("INCOMPLETE_TWO_ORDER_AUDIT")
    if any(not math.isfinite(float(v[k])) for v in post.values()
           for k in ("D","J","I_left","I_right","sens")):
        raise RuntimeError("NONFINITE_POST_WRITEBACK")
    side=candidate["side"]
    return int(all(dside(post[o]["D"])==side for o in ORDERS))

def score_report(record,policy):
    cand=record["candidates"][policy]
    post=record["audits"][policy]
    if set(post)!=set(ORDERS):raise RuntimeError("INCOMPLETE_TWO_ORDER_AUDIT")
    for v in post.values():
        if any(not math.isfinite(float(v[k])) for k in ("D","J","I_left","I_right","sens")):
            raise RuntimeError("NONFINITE_POST_WRITEBACK")
    side=cand["side"]
    f0=int(side==record["truth_side"]) # screen truth; check_a0 done elsewhere
    f1=int(all(dside(post[o]["D"])==side for o in ORDERS))
    order_f1={o:int(dside(post[o]["D"])==side) for o in ORDERS}
    return f0,f1,order_f1

def select_policy(train_records,selection):
    selected={x["idx"]:x for x in selection["train_selected"]}
    if len(train_records)!=N or {x["idx"] for x in train_records}!=set(selected):
        raise RuntimeError("TRAIN_COHORT_INCOMPLETE")
    score_totals={p:0 for p in POLICIES}
    parseable=0
    for r in train_records:
        saved=selected[r["idx"]]
        check_a0(r,saved);check_native(r)
        if r["truth_side"]!=saved["true_side"]:raise RuntimeError("TRUTH_SIDE_WAS_CHANGED")
        if set(r["audits"])!=set(POLICIES):
            raise RuntimeError("TRAIN_HAS_MISSING_OR_EXTRA_POLICY")
        parseable+=int(r["native"]["prose_parseable"])
        for policy in POLICIES:
            # ONLY F1 is visible in the report selector. No F0, q or screen baseline
            # fidelity contributes to choosing the policy.
            f1=post_only_f1(r,policy)
            score_totals[policy]+=f1
    means={p:score_totals[p]/N for p in POLICIES}
    winner=min(POLICIES,key=lambda p:(-means[p],POLICIES.index(p)))
    return {"schema":"MPW105_POLICY_SELECTION_V1",
       "selector":"ARGMAX_TRAIN_JOINT_POST_WRITEBACK_FIDELITY_ONLY",
       "n_train":N,"policy_order":list(POLICIES),
       "training_scores":means,
       "selected_policy":winner,
       "native_prose_parse_rate":parseable/N,
       "native_prose_parse_count":parseable,
       "candidate_count":len(POLICIES),
       "selection_training_data_sha256":sha(
          ("\n".join(canonical(r) for r in sorted(train_records,key=lambda z:z["idx"]))+"\n").encode()),
       "original_screen_selection_sha256":sha(canonical(selection))}

def decomp(records,policy):
    q=s=C=L=0
    pairs={"00":0,"01":0,"10":0,"11":0}
    for r in records:
        f0,f1,_=score_report(r,policy)
        q+=f0;s+=f1;C+=int(f0==0 and f1==1);L+=int(f0==1 and f1==0)
        pairs[str(f0)+str(f1)]+=1
    out={"n":len(records),"q":q/len(records),"s":s/len(records),
        "C":C/len(records),"L":L/len(records),"transition_table":pairs}
    if abs(out["s"]-(out["q"]+out["C"]-out["L"]))>1e-12:
        raise RuntimeError("VERSION_DECOMPOSITION_IDENTITY_FAILED")
    return out

def bootstrap(vec,seed):
    x=np.asarray(vec,dtype=float)
    if x.shape!=(N,) or not np.isfinite(x).all():
        raise RuntimeError("HOLDOUT_TEST_VECTOR_INCOMPLETE")
    rng=np.random.default_rng(seed);blocks=[]
    for off in range(0,BOOT,2500):
        j=rng.integers(0,N,size=(min(2500,BOOT-off),N))
        blocks.append(x[j].mean(axis=1))
    sample=np.concatenate(blocks)
    plus=int((x>0).sum());minus=int((x<0).sum())
    return {"mean":float(np.mean(x)),
        "ci_familywise":[float(z) for z in np.quantile(sample,[FAMILY_ALPHA/2,1-FAMILY_ALPHA/2])],
        "q_one_sided_upper_9875":float(np.quantile(sample,1-FAMILY_ALPHA)),
        "positive":plus,"negative":minus,"zero":N-plus-minus,
        "sign_p":float(binomtest(plus,plus+minus,.5).pvalue) if plus+minus else 1.0}

def evaluate_holdout(records,selection,policy_manifest):
    holdout={x["idx"]:x for x in selection["holdout_selected"]}
    if len(records)!=N or {r["idx"] for r in records}!=set(holdout):
        raise RuntimeError("HOLDOUT_COHORT_INCOMPLETE")
    winner=policy_manifest["selected_policy"]
    if winner not in POLICIES:raise RuntimeError("POLICY_NOT_FROZEN")
    allowed={"P0",winner}
    delta_s=[];delta_q=[];delta_g=[]
    per_order={o:[] for o in ORDERS}
    parseable=0
    for record in records:
        saved=holdout[record["idx"]]
        check_a0(record,saved);check_native(record)
        if record["truth_side"]!=saved["true_side"]:
            raise RuntimeError("ORIGINAL_TRUE_SIDE_CHANGED")
        if set(record["audits"])!=allowed:
            raise RuntimeError("HOLDOUT_POLICY_SEARCH_LEAKAGE")
        parseable+=int(record["native"]["prose_parseable"])
        q0,s0,o0=score_report(record,"P0")
        qw,sw,ow=score_report(record,winner)
        delta_s.append(sw-s0);delta_q.append(qw-q0)
        delta_g.append((sw-qw)-(s0-q0))
        for o in ORDERS:per_order[o].append(ow[o]-o0[o])
    baseline=decomp(records,"P0")
    selected=decomp(records,winner)
    stat_s=bootstrap(delta_s,BOOT_SEED+1)
    stat_g=bootstrap(delta_g,BOOT_SEED+2)
    stat_q=bootstrap(delta_q,BOOT_SEED+3)
    per={o:float(np.mean(arr)) for o,arr in per_order.items()}
    valid=True # check_a0 and audit coverage fail closed above
    h1=(stat_s["mean"]>0 and stat_s["ci_familywise"][0]>0 and
        stat_s["sign_p"]<FAMILY_ALPHA and all(x>0 for x in per.values()))
    h2=(h1 and stat_g["mean"]>0 and stat_g["ci_familywise"][0]>0 and
        stat_g["sign_p"]<FAMILY_ALPHA and
        stat_q["q_one_sided_upper_9875"]<=TOL)
    return {"n":N,"valid":valid,"policy":winner,
      "primary_verdicts":{"H1":"CONFIRMED" if h1 else "NOT_CONFIRMED",
                          "H2":"CONFIRMED" if h2 else "NOT_CONFIRMED"},
      "post_score_gain":stat_s,"provenance_gap_gain":stat_g,
      "protected_historical_gain":stat_q,
      "per_order_post_score_differences":per,
      "unoptimized_P0":baseline,"optimized_selector":selected,
      "native_prose_parse_rate":parseable/N,
      "q_improvement_upper_tolerance":TOL,
      "delta_s_equals_delta_q_plus_delta_C_minus_delta_L":abs(
            (selected["s"]-baseline["s"])-
            ((selected["q"]-baseline["q"])+
             (selected["C"]-baseline["C"])-
             (selected["L"]-baseline["L"])))<1e-12,
      "interpretation":"POST_WRITEBACK_SCORE_ONLY_SELECTOR; no A0 access during train policy selection"}

if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("mode",choices=("train","holdout"))
    a.add_argument("records");a.add_argument("screen_json")
    a.add_argument("--policy_json");opt=a.parse_args()
    records=[json.loads(x) for x in Path(opt.records).read_bytes().splitlines()]
    selection=json.loads(Path(opt.screen_json).read_text())
    if opt.mode=="train":
        x=select_policy(records,selection)
        print("MPW105_BLIND_POLICY "+canonical(x),flush=True)
    else:
        policy=json.loads(Path(opt.policy_json).read_text())
        x=evaluate_holdout(records,selection,policy)
        print("MPW105_PROVENANCE_EVALUATION "+canonical(x),flush=True)
