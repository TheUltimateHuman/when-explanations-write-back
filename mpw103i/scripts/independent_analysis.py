# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""Independently implemented MPW-103I genuine-iteration scientific analysis.
Does NOT import GPU runner. Audits source provenance and 8 genuinely model-generated
reports rather than treating forced histories as native. N=64 independent families.
"""
import json,hashlib,math,re,argparse
from pathlib import Path
import numpy as np
from scipy.stats import binomtest

ORDERS=("LR","RL")
ARMS=("NATIVE_REPORT","ELICIT_ACK","NEUTRAL_ACK","ARBITRARY_CODE","FORCED_FALSE","DIRECTIVE")
CHECK=(0,1,2,4,8)
N=64
TURNS=8
BOOT=50000
SEED=520261030
ALPHA=.05/6
PARSE_MIN=.8

def get_side(z):
    return "LEFT" if z>0 else "RIGHT" if z<0 else None
def parse(s):
    m=re.match(r"^\s*(LEFT|RIGHT)\s*:\s*\S",s,re.I|re.S)
    return m.group(1).upper() if m else None
def matching(report,audit):
    p=report["parsed_side"]
    return int(p is not None and all(get_side(audit[o]["D"])==p for o in ORDERS))
def signed_mean(v,i):
    a=np.asarray(v,dtype=float)
    if a.shape!=(N,) or not np.isfinite(a).all():raise RuntimeError("INVALID_FAMILY_VECTOR")
    rng=np.random.default_rng(SEED+i)
    draws=[]
    for t in range(0,BOOT,2500):
        ix=rng.integers(0,N,size=(min(2500,BOOT-t),N))
        draws.append(np.mean(a[ix],axis=1))
    bs=np.concatenate(draws)
    pos=int(np.count_nonzero(a>0));neg=int(np.count_nonzero(a<0))
    return {"n":N,"mean":float(a.mean()),
      "ci_familywise":[float(z) for z in np.quantile(bs,[ALPHA/2,1-ALPHA/2])],
      "ci95":[float(z) for z in np.quantile(bs,[.025,.975])],
      "positive":pos,"negative":neg,"zero":N-pos-neg,
      "sign_p":float(binomtest(pos,pos+neg,.5).pvalue) if pos+neg else 1.0}
def check_audit(a):
    if set(a)!=set(ORDERS):raise RuntimeError("MISSING_PHYSICAL_ORDER")
    for data in a.values():
        for k in ("D","J","I_left","I_right","sens"):
            if not math.isfinite(float(data[k])):
                raise RuntimeError("NONFINITE_AUDIT")
def compute(rows):
    if len(rows)!=N or len({r["idx"] for r in rows})!=N:
        raise RuntimeError("DUPLICATE_OR_MISSING_64_FAMILIES")
    tests={k:[] for k in ("H1","H2","H3")}
    by_order={k:{o:[] for o in ORDERS} for k in ("H1","H3")}
    drift={arm:{str(t):[] for t in CHECK} for arm in ARMS}
    matrices={str(t):{"00":0,"01":0,"10":0,"11":0,"parseable":0,
                     "report_side_flips":0} for t in range(TURNS)}
    errors=0
    repeat=[];crossjob=[]
    parseable=0;total=0
    report_flips=0;profile_flips=0;oscillations=0;returned_to_original=0;plateau_depth4to8=0
    for record in rows:
        if len(record.get("case_sha256",""))!=64:raise RuntimeError("MISSING_CASE_HASH")
        if not record.get("original_true_side") in ("LEFT","RIGHT"):
            raise RuntimeError("FROZEN_TRUE_SIDE_MISSING")
        if record["original_false_side"]==record["original_true_side"]:
            raise RuntimeError("FROZEN_FALSE_SIDE_INVALID")
        if set(record.get("arms",{}))!=set(ARMS):
            raise RuntimeError("INCOMPLETE_CONTROL_PANEL")
        src=record["screen_orders"];origin=record["origin"]
        if set(src)!=set(ORDERS) or set(origin)!=set(ORDERS):
            raise RuntimeError("MISSING_SCREEN_OR_BASELINE")
        zero={}
        for order in ORDERS:
            values=origin[order]
            if set(values)!={"baseline","baseline_repeat"}:
                raise RuntimeError("ORIGINAL_REPEAT_MISSING")
            check_audit({order:values["baseline"],"other":values["baseline_repeat"]} if False else
                        {"LR":values["baseline"],"RL":values["baseline_repeat"]})
            screen=src[order]["baseline"]
            b=values["baseline"];r=values["baseline_repeat"]
            old_side=get_side(screen["D"])
            if old_side!=record["original_true_side"]:
                raise RuntimeError("SOURCE_HISTORY_TRUTH_CHANGED")
            repeat.append(abs(b["D"]-r["D"]))
            crossjob.append(abs(b["D"]-screen["D"]))
            if (not b["acc"] or not r["acc"] or get_side(b["D"])!=old_side or
                get_side(r["D"])!=old_side or
                min(b["I_left"],b["I_right"],r["I_left"],r["I_right"])<=0):
                errors+=1
            zero[order]=b
        def distance(version):
            return float(np.mean([abs(version[o]["D"]-zero[o]["D"]) for o in ORDERS]))
        for arm in ARMS:
            a=record["arms"][arm]
            cycles=a["cycles"];snap=a["checkpoints"]
            if len(cycles)!=TURNS or not set(map(str,CHECK)).issubset(snap):
                raise RuntimeError("INCOMPLETE_CYCLES_OR_CHECKPOINTS")
            if snap["0"]!=zero:raise RuntimeError("CHECKPOINT_ZERO_DOES_NOT_EQUAL_PROTECTED_A0")
            for t in CHECK:
                check_audit(snap[str(t)])
                drift[arm][str(t)].append(distance(snap[str(t)]))
            for t,cycle in enumerate(cycles):
                if cycle["t"]!=t:raise RuntimeError("BAD_CYCLE_NUMBER")
                if cycle.get("native_task_answer") not in ("positive","negative"):
                    raise RuntimeError("MISSING_MODEL_GENERATED_TASK_ANSWER")
                if len(cycle.get("pre_state_sha256",""))!=64 or len(cycle.get("post_state_sha256",""))!=64:
                    raise RuntimeError("NO_STATE_HASH")
                if t and cycle["pre_state_sha256"]!=cycles[t-1]["post_state_sha256"]:
                    raise RuntimeError("STATE_CHAIN_BROKEN")
                r=cycle["report"]
                expected={"NATIVE_REPORT":"MODEL_GREEDY_GENERATED",
                          "ELICIT_ACK":"EXPERIMENTER_FORCED_ACKNOWLEDGMENT",
                          "NEUTRAL_ACK":"EXPERIMENTER_FORCED_ACKNOWLEDGMENT",
                          "ARBITRARY_CODE":"MODEL_GREEDY_ARBITRARY_CODE",
                          "FORCED_FALSE":"EXPERIMENTER_FORCED_BASELINE_FALSE",
                          "DIRECTIVE":"EXPERIMENTER_FORCED_ACKNOWLEDGMENT"}[arm]
                if r["source"]!=expected:raise RuntimeError("SIMULATED_NATIVE_EXPLANATION_OR_BAD_CONTROL_PROVENANCE")
                if arm=="NATIVE_REPORT":
                    if not isinstance(r["raw"],str) or r["parsed_side"]!=parse(r["raw"]):
                        raise RuntimeError("NATIVE_TEXT_MISMATCH")
                    if len(r.get("token_ids",[]))!=r.get("n_tokens"):
                        raise RuntimeError("NATIVE_GENERATION_TOKENS_NOT_SAVED")
                elif arm=="FORCED_FALSE" and r["parsed_side"]!=record["original_false_side"]:
                    raise RuntimeError("FORCED_SIDE_MISMATCH")
        native=record["arms"]["NATIVE_REPORT"]
        elic=record["arms"]["ELICIT_ACK"]
        full=native["audits_all"];local=native["local_ack_audits"]
        if set(full)!=set(str(t) for t in range(TURNS+1)) or set(local)!=set(str(t) for t in range(TURNS)):
            raise RuntimeError("INCOMPLETE_VERSION_AND_LOCAL_CONTROL")
        for t in range(TURNS+1):
            check_audit(full[str(t)])
            if native["checkpoints"][str(t)]!=full[str(t)]:
                raise RuntimeError("VERSION_CHECKPOINT_NOT_SAVED")
        for audit in local.values():check_audit(audit)
        d1=distance(native["checkpoints"]["1"])-distance(elic["checkpoints"]["1"])
        d3=(distance(native["checkpoints"]["8"])-distance(native["checkpoints"]["1"]))-(
            distance(elic["checkpoints"]["8"])-distance(elic["checkpoints"]["1"]))
        tests["H1"].append(d1);tests["H3"].append(d3)
        r0=native["cycles"][0]["report"]
        tests["H2"].append(matching(r0,full["1"])-matching(r0,local["0"]))
        for o in ORDERS:
            a0=zero[o]["D"]
            by_order["H1"][o].append(abs(native["checkpoints"]["1"][o]["D"]-a0)-
                                     abs(elic["checkpoints"]["1"][o]["D"]-a0))
            by_order["H3"][o].append(
                abs(native["checkpoints"]["8"][o]["D"]-a0)-
                abs(native["checkpoints"]["1"][o]["D"]-a0)-
                abs(elic["checkpoints"]["8"][o]["D"]-a0)+
                abs(elic["checkpoints"]["1"][o]["D"]-a0))
        previous=None
        for t in range(TURNS):
            rep=native["cycles"][t]["report"]
            total+=1;parseable+=int(rep["parsed_side"] is not None)
            f0=matching(rep,full[str(t)])
            f1=matching(rep,full[str(t+1)])
            matrices[str(t)][f"{f0}{f1}"]+=1
            matrices[str(t)]["parseable"]+=int(rep["parsed_side"] is not None)
            if t and rep["parsed_side"]!=previous:
                matrices[str(t)]["report_side_flips"]+=1;report_flips+=1
            previous=rep["parsed_side"]
        profile=[tuple(get_side(full[str(t)][o]["D"]) for o in ORDERS)
                 for t in range(TURNS+1)]
        ch=sum(x!=y for x,y in zip(profile,profile[1:]))
        profile_flips+=ch
        oscillations+=int(ch>=2)
        returned_to_original+=int(any(z!=profile[0] for z in profile[1:8]) and profile[8]==profile[0])
        plateau_depth4to8+=int(abs(distance(native["checkpoints"]["8"])-
                                   distance(native["checkpoints"]["4"]))<.05)
    confidence={k:signed_mean(v,i+1) for i,(k,v) in enumerate(tests.items())}
    order_effects={k:{order:float(np.mean(v)) for order,v in os.items()}
                   for k,os in by_order.items()}
    valid=errors==0 and max(repeat)<1e-4 and max(crossjob)<1e-4
    parse_rate=parseable/total
    parse_ok=parse_rate>=PARSE_MIN
    verdict={}
    for h,v in confidence.items():
        positive=(v["mean"]>0 and v["ci_familywise"][0]>0 and v["sign_p"]<ALPHA)
        if h in order_effects:
            positive=positive and all(q>0 for q in order_effects[h].values())
        verdict[h]=("INVALID" if not valid else
                    "INSTRUMENT_FAILURE" if not parse_ok else
                    "CONFIRMED" if positive else "NOT_CONFIRMED")
    fidelity={}
    for t,counts in matrices.items():
        q=(counts["10"]+counts["11"])/N
        s=(counts["01"]+counts["11"])/N
        C=counts["01"]/N;L=counts["10"]/N
        if abs(s-(q+C-L))>1e-12:raise RuntimeError("VERSION_IDENTITY_FAILED")
        fidelity[t]={"q":q,"s":s,"C":C,"L":L,
          "transition_table":{k:counts[k] for k in ("00","01","10","11")},
          "parseable":counts["parseable"],"report_side_flips":counts["report_side_flips"]}
    return {"n":N,"valid":bool(valid),"verdicts":verdict,
      "estimates":confidence,"order_effects":order_effects,
      "parse_rate":parse_rate,"instrument_parse_ok":bool(parse_ok),
      "max_baseline_repeat_D":max(repeat),"max_crossjob_screen_D":max(crossjob),
      "invalid_original_cells":errors,
      "arm_drift":{name:{t:float(np.mean(x)) for t,x in table.items()} for name,table in drift.items()},
      "versioned_native_fidelity":fidelity,
      "native_report_side_changes_total":report_flips,
      "native_mechanism_tuple_changes_total":profile_flips,
      "native_families_with_2plus_mechanism_changes":oscillations,
      "native_families_returning_to_original_sign_tuple":returned_to_original,
      "native_families_depth4to8_drift_plateau_delta_lt_005":plateau_depth4to8}
if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("original_records")
    z=a.parse_args()
    raw=Path(z.original_records).read_bytes()
    rows=[json.loads(s) for s in raw.splitlines()]
    out=compute(rows)
    out["raw_sha256"]=hashlib.sha256(raw).hexdigest()
    print("MPW103I_INDEPENDENT "+json.dumps(out,sort_keys=True),flush=True)
