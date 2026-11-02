# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = []
# ///
"""MPW-106 offline store snapshot builder from original verified GPU writer output.
The four produced JSON snapshots are committed consecutively to the SAME Git file.
No GPU inference, no policy optimization, no use of future retrieval effects.
"""
import argparse,base64,gzip,hashlib,importlib.util,json,tempfile
from pathlib import Path
from urllib.request import urlopen

ROOT="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/"
SCHEMA="MPW106_EXTERNAL_MEMORY_V1"
STORE_ID="mpw106-persistent-report-causal-audit"
NEUTRAL=("In the previous session I classified sentiment. "
         "This note does not describe which passage influenced that answer.")
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def sha(obj):return hashlib.sha256(obj if isinstance(obj,bytes) else obj.encode()).hexdigest()
def fetch(u):return urlopen(u,timeout=90).read()
def emit(label,obj):print(label+" "+canonical(obj),flush=True)
def recover_writer(commit,model):
    path=ROOT+commit+"/mpw106/writer/"
    meta=json.loads(fetch(path+"WRITER_MANIFEST.json"))
    info=meta["models"][model]
    if info["n"]!=64 or len(info["shards"])!=4:
        raise RuntimeError("WRITER_ARCHIVE_NOT_COMPLETE")
    shards=[]
    for i,s in enumerate(info["shards"]):
        compressed=base64.b64decode(fetch(path+f"{model}_shard{i+1:02d}.jsonl.gz.b64").strip(),validate=True)
        raw=gzip.decompress(compressed)
        if sha(raw)!=s["raw_sha256"] or len(raw.splitlines())!=16:
            raise RuntimeError("ORIGINAL_WRITER_SHA_CHANGED")
        shards.append(raw)
    allraw=b"".join(shards)
    if sha(allraw)!=info["combined_raw_sha256"]:
        raise RuntimeError("COMPLETE_WRITER_SHA_CHANGED")
    return [json.loads(l) for l in allraw.splitlines()],info,meta
def build(rows,model,revision,bank,screen_commit):
    result={}
    previous=None
    byid=sorted(rows,key=lambda r:r["idx"])
    if len(byid)!=64 or len({r["idx"] for r in byid})!=64:
        raise RuntimeError("INCOMPLETE_64_REPORTS")
    for step,kind in enumerate(("NEUTRAL","LIVE","CORRECTED","DELETED")):
        entries=[]
        for row in byid:
            n=row["native"]
            if n["source"]!="MODEL_GREEDY_GENERATED" or n["model_revision"]!=revision:
                raise RuntimeError("FALSE_MODEL_AUTHORED_REPORT")
            raw=n["raw"]
            if sha(raw)!=n["raw_sha256"]:raise RuntimeError("ORIGINAL_NATIVE_TEXT_CHANGED")
            truth=row["true_side"]
            origside=n["parsed_side"]
            if truth not in ("LEFT","RIGHT") or origside not in ("LEFT","RIGHT",None):
                raise RuntimeError("SOURCE_SIDE_SCHEMA")
            if kind=="NEUTRAL":
                text=NEUTRAL;status="ACTIVE";source="NEUTRAL_HARNESS_NOTE";prev_text=None
            elif kind=="LIVE":
                text=raw;status="ACTIVE";source="MODEL_GENERATED_RAW";prev_text=NEUTRAL
            elif kind=="CORRECTED":
                text=("Correction by an external auditor: the protected original "
                      "source-reliance test favored "+truth+".")
                status="ACTIVE";source="EXTERNAL_AUDITOR_CORRECTION";prev_text=raw
            else:
                text=None;status="DELETED";source="ACTIVE_TOMBSTONE"
                prev_text=("Correction by an external auditor: the protected original "
                           "source-reliance test favored "+truth+".")
            entries.append({"case_id":"mpw106:sst2:"+str(row["idx"]),
              "case_sha256":row["case_sha256"],
              "reporter_model":model,"reporter_revision":revision,
              "original_report_sha256":n["raw_sha256"],
              "original_report_side":origside,
              "text":text,"text_sha256":sha(text) if text is not None else None,
              "status":status,"source":source,
              "prior_text_sha256":sha(prev_text) if prev_text is not None else None})
        state={"schema":SCHEMA,"store_id":STORE_ID,"model":model,
               "model_revision":revision,"case_manifest_sha256":bank,
               "source_writer_screen_commit":screen_commit,
               "kind":kind,"revision":step,
               "parent_state_sha256":sha(canonical(previous)) if previous else None,
               "entries":entries}
        result[kind]=state
        previous=state
    return result
def main():
    a=argparse.ArgumentParser()
    a.add_argument("writer_archive_commit")
    a.add_argument("model",choices=("qwen3","granite"))
    opts=a.parse_args()
    commit=opts.writer_archive_commit
    if len(commit)!=40 or any(x not in "0123456789abcdef" for x in commit):
        raise RuntimeError("IMMUTABLE_WRITER_GIT_COMMIT_REQUIRED")
    rows,info,meta=recover_writer(commit,opts.model)
    states=build(rows,opts.model,info["model_revision"],
                 meta["case_manifest_sha256"],info["screen_selection_commit"])
    parent=None
    for kind in ("NEUTRAL","LIVE","CORRECTED","DELETED"):
        state=states[kind]
        if state["parent_state_sha256"]!=parent:
            raise RuntimeError("MEMORY_STATE_CHAIN_BROKEN")
        text=canonical(state)
        if kind=="DELETED" and any(e["text"] is not None or e["status"]!="DELETED"
                                   for e in state["entries"]):
            raise RuntimeError("ACTIVE_DELETED_TEXT_RETAINED")
        if kind=="LIVE" and any(e["text_sha256"]!=e["original_report_sha256"] for e in state["entries"]):
            raise RuntimeError("MODEL_NATIVE_TEXT_NOT_STORED_EXACT")
        for i in range(0,len(text),8000):
            emit("MPW106_STORE_STATE_CHUNK",{"kind":kind,"part":i//8000,
                "total":(len(text)+7999)//8000,"sha256":sha(text),
                "data":text[i:i+8000]})
        emit("MPW106_STORE_STATE",{"kind":kind,"revision":state["revision"],
           "sha256":sha(text),"n":len(state["entries"]),"bytes":len(text),
           "parent_state_sha256":parent})
        parent=sha(text)
    emit("MPW106_STORE_BUILD_END",{"status":"FOUR_SNAPSHOTS_CONSTRUCTED",
        "model":opts.model,"writer_archive_commit":commit,
        "writer_original_raw_sha256":info["combined_raw_sha256"],
        "kinds":["NEUTRAL","LIVE","CORRECTED","DELETED"]})
if __name__=="__main__":main()
