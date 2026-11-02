"""MPW-106 fixed, fail-closed Git-backed external-memory retrieval contract.
This standard-library code has no model or GPU and cannot select a report.
All snapshots must be archived at immutable Git commits before model reads.
"""
import hashlib,json,math
STORE_SCHEMA="MPW106_EXTERNAL_MEMORY_V1"
STORE_ID="mpw106-persistent-report-causal-audit"
KINDS=("NEUTRAL","LIVE","CORRECTED","DELETED")
def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def sha(x):
    return hashlib.sha256(x if isinstance(x,bytes) else x.encode()).hexdigest()
def case_id(i):
    return "mpw106:sst2:"+str(int(i))
class RetrievalRejected(RuntimeError):pass
def validate_store(state, expected_kind=None, expected_model=None, expected_bank=None):
    if state.get("schema")!=STORE_SCHEMA or state.get("store_id")!=STORE_ID:
        raise RetrievalRejected("WRONG_MEMORY_SCHEMA_OR_STORE")
    kind=state.get("kind")
    if kind not in KINDS or expected_kind is not None and kind!=expected_kind:
        raise RetrievalRejected("WRONG_MEMORY_SNAPSHOT_KIND")
    if expected_model is not None and state.get("model")!=expected_model:
        raise RetrievalRejected("WRONG_MEMORY_REPORTING_MODEL")
    if expected_bank is not None and state.get("case_manifest_sha256")!=expected_bank:
        raise RetrievalRejected("WRONG_MEMORY_SOURCE_BANK")
    entries=state.get("entries",[])
    if not isinstance(entries,list) or len(entries)!=64:
        raise RetrievalRejected("WRONG_MEMORY_FAMILY_COUNT")
    ids=set()
    for rec in entries:
        required={"case_id","case_sha256","reporter_model","reporter_revision",
            "original_report_sha256","original_report_side","text","text_sha256",
            "status","source","prior_text_sha256"}
        if set(rec)!=required:raise RetrievalRejected("MEMORY_RECORD_SCHEMA_MISMATCH")
        cid=rec["case_id"]
        if not isinstance(cid,str) or not cid.startswith("mpw106:sst2:") or cid in ids:
            raise RetrievalRejected("MEMORY_ID_MISSING_OR_DUPLICATED")
        ids.add(cid)
        if len(rec["case_sha256"])!=64 or len(rec["original_report_sha256"])!=64:
            raise RetrievalRejected("MISSING_REPORT_OR_SOURCE_SHA")
        if rec["reporter_model"]!=state["model"] or rec["reporter_revision"]!=state["model_revision"]:
            raise RetrievalRejected("MODEL_REVISION_NOT_ORIGINAL_WRITER")
        if rec["original_report_side"] not in ("LEFT","RIGHT",None):
            raise RetrievalRejected("UNEXPECTED_REPORT_SIDE")
        if rec["status"]=="DELETED":
            if kind!="DELETED" or rec["text"] is not None or rec["text_sha256"] is not None:
                raise RetrievalRejected("TOMBSTONE_LEAKS_REPORT_TEXT")
        elif rec["status"]=="ACTIVE":
            if kind=="DELETED" or not isinstance(rec["text"],str) or not rec["text"].strip():
                raise RetrievalRejected("MISSING_ACTIVE_MEMORY_TEXT")
            if sha(rec["text"])!=rec["text_sha256"]:
                raise RetrievalRejected("CONTENT_HASH_MISMATCH")
        else:
            raise RetrievalRejected("BAD_RECORD_STATUS")
        if kind=="NEUTRAL" and rec["source"]!="NEUTRAL_HARNESS_NOTE":
            raise RetrievalRejected("NEUTRAL_CLAIMED_MODEL_SOURCE")
        if kind=="LIVE" and rec["source"]!="MODEL_GENERATED_RAW":
            raise RetrievalRejected("LIVE_MEMORY_NOT_GENERATED")
        if kind=="CORRECTED" and rec["source"]!="EXTERNAL_AUDITOR_CORRECTION":
            raise RetrievalRejected("CORRECTION_MISATTRIBUTED")
        if kind=="DELETED" and rec["source"]!="ACTIVE_TOMBSTONE":
            raise RetrievalRejected("DELETE_SOURCE_BAD")
    return {"n":len(ids),"kind":kind,"state_sha256":sha(canon(state))}
def lookup(state,index,expected_case_sha,expected_model,expected_bank,expected_kind=None):
    validate_store(state,expected_kind,expected_model,expected_bank)
    key=case_id(index)
    matches=[rec for rec in state["entries"] if rec["case_id"]==key]
    if not matches:return {"status":"NO_RECORD","text":None}
    rec=matches[0]
    if rec["case_sha256"]!=expected_case_sha:
        raise RetrievalRejected("CASE_BINDING_MISMATCH")
    if rec["status"]=="DELETED":
        return {"status":"NO_RECORD","text":None}
    if rec["source"] not in ("MODEL_GENERATED_RAW","NEUTRAL_HARNESS_NOTE",
                             "EXTERNAL_AUDITOR_CORRECTION"):
        raise RetrievalRejected("UNAUTHORIZED_SOURCE_CLASS")
    return {"status":"HIT","text":rec["text"],
            "content_sha256":rec["text_sha256"],"source":rec["source"]}
