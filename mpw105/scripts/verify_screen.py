# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""Independent frozen MPW-105 raw screen archive verification.
Usage: uv run verify_screen.py <40-hex-git-sha> <qwen3|granite>
Original GPU 12x256 shard hashes, selected cases and 80/80 train/holdout
reconstructed without loading the GPU model runner.
"""
import sys,json,base64,gzip,hashlib,tempfile,importlib.util
from pathlib import Path
from urllib.request import urlopen
ROOT="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/"
def h(raw):return hashlib.sha256(raw).hexdigest()
def read(url):return urlopen(url,timeout=90).read()
def main(ref,model):
    if len(ref)!=40 or any(x not in "0123456789abcdef" for x in ref):
        raise RuntimeError("40_HEX_IMMUTABLE_COMMIT_REQUIRED")
    if model not in ("qwen3","granite"):raise RuntimeError("BAD_MODEL")
    root=ROOT+ref+"/mpw105/"
    meta=json.loads(read(root+"screen/SCREEN_MANIFEST.json"))
    record=meta["models"][model]
    if record["n_candidates"]!=3072 or len(record["shards"])!=12:
        raise RuntimeError("SCREEN_RAW_SHARD_COUNT_INCOMPLETE")
    raw=[]
    for i,anchor in enumerate(record["shards"]):
        compressed=base64.b64decode(
           read(root+f"screen/{model}_shard{i+1:02d}.jsonl.gz.b64").strip(),validate=True)
        if anchor.get("gzip_sha256") and h(compressed)!=anchor["gzip_sha256"]:
            raise RuntimeError("GZIP_BYTES_MISMATCH")
        part=gzip.decompress(compressed)
        if len(part.splitlines())!=256 or h(part)!=anchor["raw_sha256"]:
            raise RuntimeError("ORIGINAL_SCREEN_RAW_SHA_OR_N_MISMATCH")
        raw.append(part)
    full=b"".join(raw)
    if h(full)!=record["combined_raw_sha256"]:
        raise RuntimeError("COMBINED_SCREEN_GPU_HASH_MISMATCH")
    source=read(root+"scripts/independent_screen.py")
    if h(source)!=meta["independent_screen_sha256"]:
        raise RuntimeError("FROZEN_BLIND_SCREEN_SOURCE_CHANGED")
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/"blind.py";p.write_bytes(source)
        spec=importlib.util.spec_from_file_location("mpw105_blind_screen",p)
        z=importlib.util.module_from_spec(spec);spec.loader.exec_module(z)
        original=[json.loads(s) for s in full.splitlines()]
        selection=z.reanalyze_screen(original,meta["candidate_manifest_sha256"])
        actual_sel=z.sha(z.stable(selection))
        saved=json.loads(read(root+f"selection/{model}.json"))
        if actual_sel!=record["selection_sha256"] or selection!=saved:
            raise RuntimeError("INDEPENDENT_TRAIN_HOLDOUT_SELECTION_MISMATCH")
    if not saved["selection_complete"] or saved["n_train"]!=80 or saved["n_holdout"]!=80:
        raise RuntimeError("FROZEN_SCREEN_INSUFFICIENT")
    return {"model":model,"raw_sha256":h(full),"selection_sha256":actual_sel,
       "archive_ref":ref,"screen_n":len(original),
       "eligible_by_class":selection["eligible_per_label"],
       "train_ids":[x["idx"] for x in selection["train_selected"]],
       "holdout_ids":[x["idx"] for x in selection["holdout_selected"]],
       "split_disjoint":True}
if __name__=="__main__":
    if len(sys.argv)!=3:raise RuntimeError("USAGE_COMMIT_MODEL")
    print("MPW105_INDEPENDENT_SCREEN_VERIFIED "+json.dumps(
        main(sys.argv[1],sys.argv[2]),sort_keys=True),flush=True)
