# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = []
# ///
"""MPW-106 independent Git active-state memory lifecycle audit.
Checks N->L->C->D same-path Git commits, writer report originality,
source-bound retrieval, active deletion, and explicit stale history behavior.
Usage: uv run verify_store.py <writer_ref> <neutral_ref> <live_ref>
    <correction_ref> <deletion_ref> <qwen3|granite> <source_freeze_ref>
"""
import argparse,json,base64,gzip,hashlib,copy,tempfile,importlib.util
from pathlib import Path
from urllib.request import urlopen
ROOT="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/"
def sha(s):return hashlib.sha256(s if isinstance(s,bytes) else s.encode()).hexdigest()
def fetch(u):return urlopen(u,timeout=90).read()
def validate_hex(s):
    if len(s)!=40 or any(c not in "0123456789abcdef" for c in s):
        raise RuntimeError("IMMUTABLE_REF_REQUIRED")
def writer_data(commit,model):
    root=ROOT+commit+"/mpw106/writer/"
    m=json.loads(fetch(root+"WRITER_MANIFEST.json"))
    info=m["models"][model];parts=[]
    for i,shard in enumerate(info["shards"]):
        gz=base64.b64decode(fetch(root+f"{model}_shard{i+1:02d}.jsonl.gz.b64").strip(),validate=True)
        raw=gzip.decompress(gz)
        if sha(raw)!=shard["raw_sha256"]:raise RuntimeError("WRITER_RAW_DATA_SHA_CHANGED")
        parts.append(raw)
    raw=b"".join(parts)
    if sha(raw)!=info["combined_raw_sha256"]:raise RuntimeError("WRITER_SHA_COMBINED_CHANGED")
    return [json.loads(x) for x in raw.splitlines()],info,m
def main(opt):
    refs=[opt.writer,opt.neutral,opt.live,opt.corrected,opt.deleted,opt.source]
    for ref in refs:validate_hex(ref)
    writer,info,meta=writer_data(opt.writer,opt.model)
    code=fetch(ROOT+opt.source+"/mpw106/scripts/memory_contract.py")
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/"contract.py";p.write_bytes(code)
        spec=importlib.util.spec_from_file_location("frozen_memory_contract_mpw106",p)
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        snapshots={}
        previous=None
        for kind,ref in (("NEUTRAL",opt.neutral),("LIVE",opt.live),
                          ("CORRECTED",opt.corrected),("DELETED",opt.deleted)):
            raw=fetch(ROOT+ref+"/mpw106/store/state.json")
            state=json.loads(raw)
            check=mod.validate_store(state,kind,opt.model,meta["case_manifest_sha256"])
            if check["state_sha256"]!=sha(mod.canon(state)):
                raise RuntimeError("STORE_DIGEST_MISMATCH")
            if state["parent_state_sha256"]!=previous:
                raise RuntimeError("DURABLE_ACTIVE_MEMORY_PARENT_CHAIN_BROKEN")
            previous=sha(mod.canon(state))
            snapshots[kind]=(state,ref,previous)
        source={r["idx"]:r for r in writer}
        if len(source)!=64:raise RuntimeError("WRITER_N_INCOMPLETE")
        for kind,(state,ref,sh) in snapshots.items():
            for i,row in source.items():
                z=mod.lookup(state,i,row["case_sha256"],opt.model,meta["case_manifest_sha256"],kind)
                entry=next(e for e in state["entries"] if e["case_id"]==mod.case_id(i))
                if entry["original_report_sha256"]!=row["native"]["raw_sha256"]:
                    raise RuntimeError("ORIGINAL_GENERATED_PROSE_SHA_CHANGED")
                if kind=="LIVE" and (z["status"]!="HIT" or z["text"]!=row["native"]["raw"]):
                    raise RuntimeError("SOURCE_MODEL_PROSE_NOT_STORED_VERBATIM")
                if kind=="DELETED" and (z["status"]!="NO_RECORD" or z["text"] is not None):
                    raise RuntimeError("TOMBSTONE_STILL_RETURNS_REPORT")
                if kind=="CORRECTED" and (z["status"]!="HIT" or
                     row["true_side"] not in z["text"] or
                     entry["source"]!="EXTERNAL_AUDITOR_CORRECTION"):
                    raise RuntimeError("CORRECTION_NOT_SOURCE_AUTHENTICATED")
                if kind=="NEUTRAL" and (z["status"]!="HIT" or
                     "does not describe which passage" not in z["text"]):
                    raise RuntimeError("NEUTRAL_NOT_NEUTRAL")
        probe=writer[0]
        storeL=snapshots["LIVE"][0]
        tested={}
        try:
            mod.lookup(storeL,probe["idx"],"0"*64,opt.model,meta["case_manifest_sha256"],"LIVE")
            raise RuntimeError("CASE_SHA_SPOOF_ACCEPTED")
        except mod.RetrievalRejected:tested["mismatched_case_sha"]="BLOCKED"
        tamper=copy.deepcopy(storeL)
        tamper["entries"][0]["text"]="tampered content"
        try:
            mod.lookup(tamper,probe["idx"],probe["case_sha256"],opt.model,meta["case_manifest_sha256"],"LIVE")
            raise RuntimeError("TAMPER_ACCEPTED")
        except mod.RetrievalRejected:tested["content_tamper"]="BLOCKED"
        try:
            mod.lookup(storeL,probe["idx"],probe["case_sha256"],opt.model,"0"*64,"LIVE")
            raise RuntimeError("WRONG_BANK_ACCEPTED")
        except mod.RetrievalRejected:tested["wrong_bank"]="BLOCKED"
        missing=mod.lookup(storeL,999999,probe["case_sha256"],opt.model,
                           meta["case_manifest_sha256"],"LIVE")
        if missing["status"]!="NO_RECORD":raise RuntimeError("MISSING_ID_NOT_BLOCKED")
        tested["missing_key"]="NO_RECORD"
        prev_stale=mod.lookup(storeL,probe["idx"],probe["case_sha256"],
                               opt.model,meta["case_manifest_sha256"],"LIVE")
        if prev_stale["status"]!="HIT":
            raise RuntimeError("UNEXPECTED_GIT_HISTORY_ERASURE")
        tested["explicit_old_live_revision"]="STILL_HIT_EXPECTED_GIT_HISTORY"
        deleted=mod.lookup(snapshots["DELETED"][0],probe["idx"],probe["case_sha256"],
                            opt.model,meta["case_manifest_sha256"],"DELETED")
        if deleted["status"]!="NO_RECORD":raise RuntimeError("ACTIVE_DELETE_FAILED")
        tested["active_deleted_revision"]="NO_RECORD"
    print("MPW106_STORE_LIFECYCLE_VERIFIED "+json.dumps({
      "model":opt.model,"n":64,
      "writer_ref":opt.writer,"source_freeze":opt.source,
      "neutral_commit":opt.neutral,"live_commit":opt.live,
      "corrected_commit":opt.corrected,"deleted_commit":opt.deleted,
      "snapshot_hashes":{k:v[2] for k,v in snapshots.items()},
      "read_integrity_tests":tested,
      "status":"COMPLETE_FRESH_RETRIEVAL_READY",
      "warning":"Active tombstones do not cryptographically erase previous Git versions"},sort_keys=True),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    for x in ("writer","neutral","live","corrected","deleted"):
        p.add_argument(x)
    p.add_argument("model",choices=("qwen3","granite"))
    p.add_argument("source")
    main(p.parse_args())
