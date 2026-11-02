# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""MPW-106 independent original GPU READER archive, four Git memory snapshots
and historical source A0 verification. Does not import writer/reader GPU scripts.
Usage: uv run verify_reader.py <immutable-reader-results-commit> <qwen3|granite>
"""
import sys,json,gzip,base64,hashlib,tempfile,importlib.util
from pathlib import Path
from urllib.request import urlopen
ROOT="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/"
def fetch(u):return urlopen(u,timeout=90).read()
def sha(x):return hashlib.sha256(x).hexdigest()
def verify(ref,model):
    if len(ref)!=40 or any(c not in "0123456789abcdef" for c in ref):
        raise RuntimeError("IMMUTABLE_RESULT_REF_REQUIRED")
    if model not in ("qwen3","granite"):raise RuntimeError("UNKNOWN_MODEL")
    root=ROOT+ref+"/mpw106/"
    meta=json.loads(fetch(root+"reader/READER_MANIFEST.json"))
    entry=meta["models"][model]
    if entry["n"]!=64 or len(entry["shards"])!=4:
        raise RuntimeError("INCOMPLETE_ORIGINAL_GPU_READER_RECORDS")
    shardbytes=[]
    for i,anchor in enumerate(entry["shards"]):
        gz=base64.b64decode(fetch(root+f"reader/{model}_shard{i+1:02d}.jsonl.gz.b64").strip(),validate=True)
        if anchor.get("compressed_sha256") and sha(gz)!=anchor["compressed_sha256"]:
            raise RuntimeError("GPU_READER_COMPRESSED_SHA_MISMATCH")
        raw=gzip.decompress(gz)
        if len(raw.splitlines())!=16 or sha(raw)!=anchor["raw_sha256"]:
            raise RuntimeError("GPU_READER_ORIGINAL_RAW_SHA_MISMATCH")
        shardbytes.append(raw)
    full=b"".join(shardbytes)
    if sha(full)!=entry["combined_raw_sha256"]:
        raise RuntimeError("ORIGINAL_GPU_READER_COMPLETE_SHA_FAILED")
    analysis=fetch(root+"scripts/independent_analysis.py")
    if sha(analysis)!=meta["independent_analysis_sha256"]:
        raise RuntimeError("INDEPENDENT_HYPOTHESIS_ANALYSIS_CHANGED")
    screen=json.loads(fetch(ROOT+entry["screen_selection_commit"]+
                           f"/mpw106/selection/{model}.json"))
    store={}
    previous=None
    for kind,field in (("NEUTRAL","neutral"),("LIVE","live"),
                        ("CORRECTED","corrected"),("DELETED","deleted")):
        raw=fetch(ROOT+entry["store_commits"][field]+"/mpw106/store/state.json")
        obj=json.loads(raw)
        if obj["kind"]!=kind or obj["model"]!=model or obj["case_manifest_sha256"]!=meta["case_manifest_sha256"]:
            raise RuntimeError("WRONG_EXTERNAL_MEMORY_SNAPSHOT")
        nextsha=sha(json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode())
        if obj["parent_state_sha256"]!=previous:
            raise RuntimeError("MEMORY_REVISION_CHAIN_CHANGED")
        previous=nextsha
        store[kind]=obj
    with tempfile.TemporaryDirectory() as td:
        path=Path(td)/"independent.py";path.write_bytes(analysis)
        spec=importlib.util.spec_from_file_location("mpw106_independent_scientific_verifier",path)
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        rows=[json.loads(line) for line in full.splitlines()]
        result=mod.analyze(rows,screen,store,model,meta["case_manifest_sha256"])
    print("MPW106_READER_INDEPENDENT_VERIFIED "+json.dumps({
        "model":model,"n":len(rows),"result_ref":ref,
        "original_gpu_raw_sha256":sha(full),
        "source_screen_commit":entry["screen_selection_commit"],
        "store_commits":entry["store_commits"],
        "independent_result":result},sort_keys=True),flush=True)
if __name__=="__main__":
    if len(sys.argv)!=3:raise RuntimeError("ARGS: ORIGINAL_GIT_COMMIT MODEL")
    verify(sys.argv[1],sys.argv[2])
