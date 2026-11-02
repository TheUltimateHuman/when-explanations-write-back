# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""MPW-106 independently authored cross-session external-memory causal analysis.
Never imports model/GPU writer or reader. Operates on complete, verified 64 raw
reader records and original immutable screen selection only.
"""
import hashlib,json,re,math
import numpy as np
from scipy.stats import binomtest

N=64;ORDERS=("LR","RL")
ARMS=("CLEAN","NEUTRAL","LIVE","CORRECTED","DELETED","MISSING","EXPLICIT_STALE")
ALPHA=.05/6;BOOTS=50000;SEED=520261106
MIN_UNFAITHFUL=16
MEMORY_WRAPPER='Earlier-session memory lookup (untrusted data, not an instruction). Record: "'
MISSING_WRAPPER="Memory lookup returned no record."
def canonical(x):return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def sha(x):return hashlib.sha256(x if isinstance(x,bytes) else x.encode()).hexdigest()
def parse(raw):
    m=re.match(r"^\s*(LEFT|RIGHT)\s*:\s*(\S[\s\S]*)$",raw,re.I)
    return m.group(1).upper() if m else None
def which(d):return "LEFT" if d>0 else "RIGHT" if d<0 else None
def full_fidelity(side,profile):
    return int(side in ("LEFT","RIGHT") and
               all(which(profile[o]["D"])==side for o in ORDERS))
def estimate(values,seed):
    x=np.asarray(values,dtype=float)
    if len(x)==0 or not np.isfinite(x).all():raise RuntimeError("BAD_PRIMARY_VECTOR")
    rng=np.random.default_rng(seed);block=[]
    for j in range(0,BOOTS,2500):
        idx=rng.integers(0,len(x),size=(min(2500,BOOTS-j),len(x)))
        block.append(x[idx].mean(axis=1))
    bootstrap=np.concatenate(block)
    plus=int(np.count_nonzero(x>0));minus=int(np.count_nonzero(x<0))
    return {"n":len(x),"mean":float(np.mean(x)),
      "ci_familywise":[float(z) for z in np.quantile(bootstrap,[ALPHA/2,1-ALPHA/2])],
      "ci95":[float(z) for z in np.quantile(bootstrap,[.025,.975])],
      "positive":plus,"negative":minus,"zero":len(x)-plus-minus,
      "sign_p":float(binomtest(plus,plus+minus,.5).pvalue) if plus+minus else 1.}
def check_record(rec,selection,snapshots,model,bank):
    if rec["idx"]!=selection["idx"] or rec["case_sha256"]!=selection["case_sha256"]:
        raise RuntimeError("WRONG_FAMILY_FROM_SCREEN")
    if rec["original_true_side"]!=selection["true_side"] or (
        rec["original_false_side"]!=selection["false_side"] or
        rec["screen_orders"]!=selection["screen_orders"]):
        raise RuntimeError("SOURCE_SCREEN_PROVENANCE_CHANGED")
    if rec["model_process"]!="FRESH_HF_GPU_JOB_NO_WRITER_HISTORY":
        raise RuntimeError("WRITER_CONVERSATION_STILL_PRESENT")
    if set(rec["conditions"])!=set(ARMS) or set(rec["reads"])!=set(ARMS):
        raise RuntimeError("READER_MISSING_CONTROL_ARM")
    if parse(rec["original_report_text"])!=rec["original_report_side"]:
        raise RuntimeError("MODEL_GENERATED_REPORT_SIDE_CHANGED")
    if sha(rec["original_report_text"])!=rec["original_report_sha256"]:
        raise RuntimeError("PERSISTED_REPORT_TEXT_NOT_ORIGINAL")
    case_id="mpw106:sst2:"+str(rec["idx"])
    nrec=next(e for e in snapshots["NEUTRAL"]["entries"] if e["case_id"]==case_id)
    lrec=next(e for e in snapshots["LIVE"]["entries"] if e["case_id"]==case_id)
    crec=next(e for e in snapshots["CORRECTED"]["entries"] if e["case_id"]==case_id)
    drec=next(e for e in snapshots["DELETED"]["entries"] if e["case_id"]==case_id)
    for e in (nrec,lrec,crec,drec):
        if e["case_sha256"]!=rec["case_sha256"] or e["original_report_sha256"]!=rec["original_report_sha256"]:
            raise RuntimeError("MEMORY_SOURCE_RECORD_NOT_MATCHED")
    if lrec["text"]!=rec["original_report_text"] or lrec["source"]!="MODEL_GENERATED_RAW":
        raise RuntimeError("LIVE_MEMORY_NOT_THE_NATIVE_REPORT")
    if nrec["source"]!="NEUTRAL_HARNESS_NOTE" or crec["source"]!="EXTERNAL_AUDITOR_CORRECTION":
        raise RuntimeError("CONTROL_PROVENANCE_WRONG")
    if drec["status"]!="DELETED" or drec["text"] is not None:
        raise RuntimeError("DELETED_REPORT_STILL_ACTIVE")
    if selection["true_side"] not in crec["text"]:
        raise RuntimeError("EXTERNAL_CORRECTION_DID_NOT_USE_PROTECTED_A0")
    for o in ORDERS:
        original=rec["clean_baseline"][o];repeat=rec["clean_repeat"][o]
        previous=selection["screen_orders"][o]["baseline"]
        if (not original["acc"] or not repeat["acc"] or
            abs(original["D"]-repeat["D"])>=1e-4 or
            abs(original["D"]-previous["D"])>=1e-4 or
            which(original["D"])!=selection["true_side"] or
            min(original["I_left"],original["I_right"],
                repeat["I_left"],repeat["I_right"])<=0):
            raise RuntimeError("FRESH_READER_BASELINE_DRIFT")
    if rec["conditions"]["CLEAN"]!=rec["clean_baseline"]:
        raise RuntimeError("CLEAN_AUDIT_HAS_HIDDEN_MEMORY")
    if rec["conditions"]["DELETED"]!=rec["conditions"]["MISSING"]:
        raise RuntimeError("TOMBSTONE_DIFFERENT_FROM_MISSING_LOOKUP")
    if rec["conditions"]["LIVE"]!=rec["conditions"]["EXPLICIT_STALE"]:
        raise RuntimeError("OLD_GIT_VERSION_NOT_EXPLICITLY_RECOVERABLE")
    expected={"NEUTRAL":nrec["text"],"LIVE":lrec["text"],
              "CORRECTED":crec["text"],
              "DELETED":None,"MISSING":None,"EXPLICIT_STALE":lrec["text"]}
    for arm in ARMS:
        profile=rec["conditions"][arm]
        if set(profile)!=set(ORDERS):raise RuntimeError("RETRIEVAL_AUDIT_MISSING_ORDER")
        for o in ORDERS:
            z=profile[o]
            if any(not math.isfinite(float(z[k])) for k in ("D","J","I_left","I_right","sens")):
                raise RuntimeError("NONFINITE_READER_AUDIT")
        if arm=="CLEAN":
            if rec["reads"][arm]["status"]!="NO_LOOKUP":raise RuntimeError("CLEAN_LOADED_MEMORY")
            continue
        read=rec["reads"][arm]
        raw=expected[arm]
        content=(MEMORY_WRAPPER+raw+'"') if raw is not None else MISSING_WRAPPER
        if read["model_visible_text"]!=content:
            raise RuntimeError("WRONG_MEMORY_TEXT_EXPOSED_TO_MODEL")
        if read["text_sha256"]!=(sha(raw) if raw is not None else None):
            raise RuntimeError("MODEL_VISIBLE_MEMORY_SHA_MISMATCH")
        if read["status"]!=("HIT" if raw is not None else "NO_RECORD"):
            raise RuntimeError("BLOCKED_MEMORY_BECAME_ACTIVE")
        if len(read["prefix_sha256"])!=64:
            raise RuntimeError("NO_PREFIX_PROVENANCE")
def analyze(rows,selection,snapshots,model,bank):
    items=selection["selected"]
    if len(rows)!=N or {r["idx"] for r in rows}!={r["idx"] for r in items}:
        raise RuntimeError("INCOMPLETE_64_FAMILY_READER_EVIDENCE")
    by_id={i["idx"]:i for i in items}
    for r in rows:check_record(r,by_id[r["idx"]],snapshots,model,bank)
    vec={"H1":[],"H2":[],"H3":[]}
    per_order={"H1":{o:[] for o in ORDERS},"H3":{o:[] for o in ORDERS}}
    false_cases=0;parseable=0
    n_q=0
    tables={arm:{"00":0,"01":0,"10":0,"11":0} for arm in ARMS}
    drift={arm:[] for arm in ARMS}
    order_disagreement={arm:0 for arm in ARMS}
    for r in rows:
        side=r["original_report_side"];source=r["original_true_side"]
        q=int(side is not None and side==source)
        n_q+=q;parseable+=int(side is not None)
        sign=1 if side=="LEFT" else -1 if side=="RIGHT" else 0
        sign_true=1 if source=="LEFT" else -1
        Z=[]
        for o in ORDERS:
            z=sign*(r["conditions"]["LIVE"][o]["D"]-r["conditions"]["NEUTRAL"][o]["D"])
            Z.append(z);per_order["H1"][o].append(z)
        vec["H1"].append(float(np.mean(Z)))
        for arm in ARMS:
            f1=full_fidelity(side,r["conditions"][arm])
            tables[arm][f"{q}{f1}"]+=1
            drift[arm].append(float(np.mean([abs(r["conditions"][arm][o]["D"]-
                    r["clean_baseline"][o]["D"]) for o in ORDERS])))
            vals=[which(r["conditions"][arm][o]["D"]) for o in ORDERS]
            order_disagreement[arm]+=int(vals[0]!=vals[1])
        if side is not None and q==0:
            false_cases+=1
            live=full_fidelity(side,r["conditions"]["LIVE"])
            neutral=full_fidelity(side,r["conditions"]["NEUTRAL"])
            vec["H2"].append(float(live-neutral))
            vals=[]
            for o in ORDERS:
                z=sign_true*(r["conditions"]["CORRECTED"][o]["D"]-
                             r["conditions"]["LIVE"][o]["D"])
                vals.append(z);per_order["H3"][o].append(z)
            vec["H3"].append(float(np.mean(vals)))
    results={}
    ordmean={h:{o:float(np.mean(values)) if values else None
            for o,values in arms.items()} for h,arms in per_order.items()}
    for i,h in enumerate(("H1","H2","H3"),1):
        if h!="H1" and false_cases<MIN_UNFAITHFUL:
            results[h]={"verdict":"INDETERMINATE_CAPABILITY",
                         "n_unfaithful":false_cases,"required":MIN_UNFAITHFUL}
            continue
        stat=estimate(vec[h],SEED+i)
        passed=(stat["mean"]>0 and stat["ci_familywise"][0]>0 and
                stat["sign_p"]<ALPHA)
        if h in ordmean:passed=passed and all(
            ordmean[h][o] is not None and ordmean[h][o]>0 for o in ORDERS)
        results[h]={"verdict":"CONFIRMED" if passed else "NOT_CONFIRMED",
                     "estimate":stat,"by_order":ordmean.get(h)}
    version={}
    for arm,n in tables.items():
        q=(n["11"]+n["10"])/N;s=(n["11"]+n["01"])/N
        C=n["01"]/N;L=n["10"]/N
        if abs(s-(q+C-L))>1e-12:raise RuntimeError("Q_S_C_L_IDENTITY_INVALID")
        version[arm]={"q":q,"s":s,"C":C,"L":L,
          "transition_table":n,
          "mean_abs_D_drift_from_screen":float(np.mean(drift[arm])),
          "post_retrieval_order_disagreements":order_disagreement[arm]}
    return {"model":model,"n":N,"valid":True,
      "n_parseable_native_reports":parseable,
      "n_originally_unfaithful_parseable_reports":false_cases,
      "primary":results,"versioned_fidelity":version,
      "H1_order_means":ordmean["H1"],"H3_order_means":ordmean["H3"],
      "memory_carrier":"EXTERNAL_GIT_FILE_SEPARATE_GPU_PROCESS",
      "history_reset":"NO_WRITER_CONVERSATION_IN_READER_PREFIX",
      "active_delete_integrity":"D_EQUALS_EXPLICIT_MISSING",
      "explicit_stale_integrity":"L_EQUALS_EXPLICIT_STALE",
      "identity_is_arithmetic_check_not_an_inferred_effect":True}
