# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3"]
# ///
"""MPW-103I exploratory AFTER-OUTCOME content and dynamics hostile audit.
Not preregistered; cannot update H1/H2/H3. Uses unchanged immutable GPU raw records.
"""
import hashlib,gzip,base64,json,collections,statistics
from urllib.request import urlopen
import numpy as np

REF="923b024055403fb031e673c4de373878bb81f6f5"
ROOT=f"https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/{REF}/mpw103i/results/"
META=json.loads(urlopen(ROOT+"RESULTS_MANIFEST.json",timeout=90).read())
INFO=META["models"]["qwen3"]
def sha(b):return hashlib.sha256(b).hexdigest()
chunks=[]
for i,anchor in enumerate(INFO["shards"]):
    data=urlopen(ROOT+f"qwen3_shard{i+1:02d}.jsonl.gz.b64",timeout=90).read().strip()
    raw=gzip.decompress(base64.b64decode(data,validate=True))
    assert sha(raw)==anchor["raw_sha256"] and len(raw.splitlines())==16
    chunks.append(raw)
full=b"".join(chunks)
assert sha(full)==INFO["combined_raw_sha256"]
rows=[json.loads(x) for x in full.splitlines()]
assert len(rows)==64

by_step=[]
native_side_counts=collections.Counter()
constant_side=constant_raw=change_raw=0
raw_identical_edges=0
report_side_change_edges=0
native_token_counts=[]
mechanism_signs=[]
mechanism_changed_after8=0
mechanism_first_changed=0
natural_first_vs_ack=[]
delta_ack=[]
for row in rows:
    n=row["arms"]["NATIVE_REPORT"]
    reports=[x["report"] for x in n["cycles"]]
    raw=[x["raw"] for x in reports]
    sides=[x["parsed_side"] for x in reports]
    native_token_counts.extend(x["n_tokens"] for x in reports)
    native_side_counts.update(str(x) for x in sides)
    constant_side+=int(len(set(sides))==1)
    constant_raw+=int(len(set(raw))==1)
    change_raw+=int(len(set(raw))>1)
    raw_identical_edges+=sum(raw[i]==raw[i-1] for i in range(1,8))
    report_side_change_edges+=sum(sides[i]!=sides[i-1] for i in range(1,8))
    orig={o:row["origin"][o]["baseline"]["D"] for o in ("LR","RL")}
    signs=[tuple("L" if n["audits_all"][str(t)][o]["D"]>0 else "R" if n["audits_all"][str(t)][o]["D"]<0 else "Z"
                 for o in ("LR","RL")) for t in range(9)]
    mechanism_signs.append(signs)
    mechanism_changed_after8+=int(signs[8]!=signs[0])
    mechanism_first_changed+=int(signs[1]!=signs[0])
    # Local first fork signed-fidelity of native report vs same-history elicitation+ACK
    r0=sides[0]
    def faithful(profile):
        return bool(r0 is not None and all(("LEFT" if profile[o]["D"]>0 else "RIGHT" if profile[o]["D"]<0 else None)==r0 for o in ("LR","RL")))
    f_n=faithful(n["audits_all"]["1"])
    f_ack=faithful(n["local_ack_audits"]["0"])
    natural_first_vs_ack.append((int(f_n),int(f_ack)))
    for t in range(8):
        by_step.append({"step":t,"side":sides[t],"text":raw[t],"n_tokens":reports[t]["n_tokens"]})
for t in range(8):
    row=[x for x in by_step if x["step"]==t]
    distinct=len({x["text"] for x in row})
    tok=[x["n_tokens"] for x in row]
    print("MPW103I_POSTHOC_STEP "+json.dumps({"step":t,"n_reports":len(row),
     "parsed":sum(z["side"] in ("LEFT","RIGHT") for z in row),
     "side_left":sum(z["side"]=="LEFT" for z in row),
     "side_right":sum(z["side"]=="RIGHT" for z in row),
     "distinct_raw_texts":distinct,"avg_output_tokens":float(np.mean(tok))},sort_keys=True),flush=True)

pairs=collections.Counter(natural_first_vs_ack)
result={
 "category":"POST_HOC_DESCRIPTIVE_NOT_NEW_PRIMARY",
 "screened_source_sha256":INFO["combined_raw_sha256"],
 "n_families":len(rows),
 "generated_reports":sum(len(r["arms"]["NATIVE_REPORT"]["cycles"]) for r in rows),
 "constant_side_families":constant_side,
 "constant_raw_text_families":constant_raw,
 "families_with_some_raw_text_change":change_raw,
 "identical_neighboring_raw_texts":raw_identical_edges,
 "neighboring_report_pairs":64*7,
 "report_side_changes_total":report_side_change_edges,
 "total_nonparsed":native_side_counts.get("None",0),
 "report_side_counts":dict(native_side_counts),
 "generated_text_token_stats":{"min":int(min(native_token_counts)),
   "median":float(statistics.median(native_token_counts)),
   "mean":float(np.mean(native_token_counts)),
   "max":int(max(native_token_counts))},
 "profile_sign_changed_between0and1":mechanism_first_changed,
 "profile_sign_changed_between0and8":mechanism_changed_after8,
 "local_first_native_vs_ack_joint_fidelity":{
   "both_true":pairs[(1,1)],"native_only":pairs[(1,0)],
   "ack_only":pairs[(0,1)],"both_false":pairs[(0,0)]
 },
 "limitation":"Report side persistence can arise from language-prior, prompt pattern, earlier repeated response, or a stabilized source; no mechanistic localization."
}
print("MPW103I_POSTHOC_CONTENT_AUDIT "+json.dumps(result,sort_keys=True),flush=True)
