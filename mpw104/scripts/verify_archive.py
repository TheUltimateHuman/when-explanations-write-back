# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""Reconstruct and independently recompute MPW-104 raw GPU families.
Usage: uv run verify_archive.py <40hex-immutable-Git-commit> <qwen3|granite>.
Requires RESULTS_MANIFEST.json, 4 untouched GPU gzip+Base64 shards.
"""
import sys,json,base64,gzip,hashlib,tempfile,importlib.util
from pathlib import Path
from urllib.request import urlopen

ROOT="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/"
def get(url):return urlopen(url,timeout=90).read()
def h(raw):return hashlib.sha256(raw).hexdigest()
def verify(commit,model):
    if len(commit)!=40 or any(c not in "0123456789abcdef" for c in commit):
        raise RuntimeError("IMMUTABLE_40_HEX_COMMIT_REQUIRED")
    if model not in ("qwen3","granite"):raise RuntimeError("BAD_MODEL")
    prefix=ROOT+commit+"/mpw104/"
    meta_raw=get(prefix+"results/RESULTS_MANIFEST.json")
    meta=json.loads(meta_raw)
    info=meta["models"][model]
    if info["n"]!=128 or len(info["shards"])!=4:raise RuntimeError("INCOMPLETE_MANIFEST")
    raw_segments=[]
    for i,entry in enumerate(info["shards"]):
        encoded=get(prefix+f"results/{model}_shard{i+1:02d}.jsonl.gz.b64").strip()
        gz=base64.b64decode(encoded,validate=True)
        if entry.get("compressed_sha256") and h(gz)!=entry["compressed_sha256"]:
            raise RuntimeError("COMPRESSED_BYTES_MISMATCH")
        rowbytes=gzip.decompress(gz)
        if len(rowbytes.splitlines())!=32 or h(rowbytes)!=entry["raw_sha256"]:
            raise RuntimeError("ORIGINAL_GPU_SHARD_SHA_MISMATCH")
        raw_segments.append(rowbytes)
    raw=b"".join(raw_segments)
    if h(raw)!=info["combined_raw_sha256"]:raise RuntimeError("ORIGINAL_GPU_COMBINED_SHA_MISMATCH")
    records=[json.loads(s) for s in raw.splitlines()]
    source=get(prefix+"scripts/independent_analysis.py")
    if h(source)!=meta["independent_analysis_sha256"]:
        raise RuntimeError("FROZEN_INDEPENDENT_ANALYZER_SHA_MISMATCH")
    with tempfile.TemporaryDirectory() as td:
        path=Path(td)/"analysis.py";path.write_bytes(source)
        spec=importlib.util.spec_from_file_location("mpw104_independent",path)
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        stats=mod.compute(records)
    return {"model":model,"archive_commit":commit,
            "raw_sha256":h(raw),"manifest_sha256":h(meta_raw),
            "independent_analysis_sha256":h(source),"result":stats}
if __name__=="__main__":
    if len(sys.argv)!=3:raise RuntimeError("ARGS_COMMIT_MODEL_REQUIRED")
    print("MPW104_ARCHIVE_INDEPENDENT_VERIFIED "+
          json.dumps(verify(*sys.argv[1:]),sort_keys=True),flush=True)
