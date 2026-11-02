# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3"]
# ///
"""Independent MPW-106 writer source and generated-report verification.
Operates only on original GPU JSONL source records and previous screen selection.
No model-runner import, no model inference, no post-retrieval outcome access.
"""
import hashlib,json,math,re
from collections import Counter
N=64
ORDERS=("LR","RL")
def canonical(v):return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def sha(x):return hashlib.sha256(x if isinstance(x,bytes) else x.encode()).hexdigest()
def parsed_side(text):
    m=re.match(r"^\s*(LEFT|RIGHT)\s*:\s*(\S[\s\S]*)$",text,re.I)
    return m.group(1).upper() if m else None
def verify(rows,selection,model_revision):
    selected={x["idx"]:x for x in selection["selected"]}
    if len(rows)!=N or set(x["idx"] for x in rows)!=set(selected):
        raise RuntimeError("FROZEN_WRITER_FAMILY_SET_NOT_COMPLETE")
    parse=0;native_sides=Counter();drift=[];repeat=[]
    for record in rows:
        prev=selected[record["idx"]]
        if any(record[k]!=prev[k] for k in ("idx","label","case_sha256","true_side","false_side","screen_orders")):
            raise RuntimeError("SOURCE_SCREEN_RECORD_NOT_IDENTICAL")
        if set(record["writer_baseline"])!=set(ORDERS) or set(record["writer_repeat"])!=set(ORDERS):
            raise RuntimeError("UNCOMPLETE_ORIGINAL_MECHANISM")
        for order in ORDERS:
            old=prev["screen_orders"][order]["baseline"]
            first=record["writer_baseline"][order]
            rep=record["writer_repeat"][order]
            if any(not math.isfinite(float(v[k])) for v in (old,first,rep)
                   for k in ("D","J","I_left","I_right","sens")):
                raise RuntimeError("NONFINITE_ORIGINAL_CAUSAL_RESPONSE")
            x=abs(first["D"]-old["D"])
            y=abs(first["D"]-rep["D"])
            if x>=1e-4 or y>=1e-4 or first["D"]*old["D"]<=0:
                raise RuntimeError("CAUSAL_SOURCE_VERSION_DRIFT")
            if not first["acc"] or not rep["acc"] or min(first["I_left"],first["I_right"],
                           rep["I_left"],rep["I_right"])<=0:
                raise RuntimeError("SOURCE_ORIGINAL_TASK_AND_CHANNEL_INVALID")
            drift.append(x);repeat.append(y)
        native=record["native"]
        if native["model_revision"]!=model_revision or native["source"]!="MODEL_GREEDY_GENERATED":
            raise RuntimeError("NATIVE_GENERATED_SOURCE_FALSE")
        if native["native_answer"] not in ("positive","negative"):
            raise RuntimeError("NATIVE_ASSISTANT_ANSWER_MISSING")
        raw=native["raw"]
        if not isinstance(raw,str) or len(raw)>2500:
            raise RuntimeError("NATIVE_RAW_TEXT_INVALID")
        if native["raw_sha256"]!=sha(raw) or not isinstance(native["token_ids"],list) or (
             native["n_tokens"]!=len(native["token_ids"]) or native["n_tokens"]>48):
            raise RuntimeError("GENERATED_REPORT_HASH_OR_TOKEN_MISMATCH")
        if native["parsed_side"]!=parsed_side(raw):
            raise RuntimeError("REPORT_PARSE_OUTPUT_NOT_REPRODUCIBLE")
        if len(native["prompt_sha256"])!=64:
            raise RuntimeError("SOURCE_ELICITATION_HASH_MISSING")
        parse+=int(native["parsed_side"] is not None)
        native_sides[str(native["parsed_side"])]+=1
    return {"n":len(rows),"native_parse_rate":parse/N,"n_parseable":parse,
            "native_sides":dict(native_sides),
            "max_screen_to_writer_D":max(drift),
            "max_original_repeat_D":max(repeat),
            "instrument_parse_gate":parse/N>=.8,
            "source_verified":True}
