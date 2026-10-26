# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""MPW-103I immutable 64-family, six-arm, 8-cycle original GPU record verifier.
Usage: uv run verify_iteration.py <immutable-40hex-result-commit> <model>
Checks original compressed and decompressed SHA, protected screen selection, and
independently recomputes H1/H2/H3 plus all eight q,s,C,L transitions.
"""
import json,sys,gzip,base64,hashlib,importlib.util,tempfile
from pathlib import Path
from urllib.request import urlopen
ROOT="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/"
def get(url):return urlopen(url,timeout=90).read()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def main(commit,model):
 if len(commit)!=40 or any(c not in "0123456789abcdef" for c in commit):
  raise RuntimeError("IMMUTABLE_RESULTS_SHA_REQUIRED")
 if model not in ("qwen3","granite"):raise RuntimeError("MODEL_NOT_FROZEN")
 path=ROOT+commit+"/mpw103i/"
 mraw=get(path+"results/RESULTS_MANIFEST.json")
 meta=json.loads(mraw)
 info=meta["models"][model]
 if info["n"]!=64 or len(info["shards"])!=4:
  raise RuntimeError("INCOMPLETE_64_FAMILY_RESULTS")
 rowsbytes=[]
 for i,item in enumerate(info["shards"]):
  compressed=base64.b64decode(get(path+f"results/{model}_shard{i+1:02d}.jsonl.gz.b64").strip(),validate=True)
  if item.get("compressed_sha256") and sha(compressed)!=item["compressed_sha256"]:
   raise RuntimeError("ARCHIVED_ORIGINAL_GZIP_CHANGED")
  raw=gzip.decompress(compressed)
  if sha(raw)!=item["raw_sha256"] or len(raw.splitlines())!=16:
   raise RuntimeError("ORIGINAL_GPU_RAW_SHARD_SHA_FAILED")
  rowsbytes.append(raw)
 full=b"".join(rowsbytes)
 if sha(full)!=info["combined_raw_sha256"]:
  raise RuntimeError("COMBINED_64_FAMILY_RAW_SHA_MISMATCH")
 screen_ref=info["screen_selection_commit"]
 frozen_sel=json.loads(get(ROOT+screen_ref+f"/mpw103i/selection/{model}.json"))
 records=[json.loads(line) for line in full.splitlines()]
 frozen_ids={x["idx"]:x for x in frozen_sel["selected"]}
 if len(records)!=64 or {x["idx"] for x in records}!=set(frozen_ids):
  raise RuntimeError("GPU_VALIDATION_SELECTED_DIFFERENT_CASES")
 for r in records:
  s=frozen_ids[r["idx"]]
  if (r["case_sha256"]!=s["case_sha256"] or
      r["original_true_side"]!=s["true_side"] or
      r["screen_orders"]!=s["screen_orders"]):
   raise RuntimeError("FROZEN_SCREEN_VERSION_CHANGED")
 source=get(path+"scripts/independent_analysis.py")
 if sha(source)!=meta["independent_analysis_sha256"]:
  raise RuntimeError("PREREGISTERED_INDEPENDENT_ANALYSIS_CHANGED")
 with tempfile.TemporaryDirectory() as td:
  p=Path(td)/"blind.py";p.write_bytes(source)
  spec=importlib.util.spec_from_file_location("mpw103i_cpu_verifier",p)
  z=importlib.util.module_from_spec(spec);spec.loader.exec_module(z)
  result=z.compute(records)
 return {"model":model,"immutable_result_commit":commit,
    "screen_commit":screen_ref,"n":len(records),
    "original_raw_sha256":sha(full),"independent_result":result}
if __name__=="__main__":
 if len(sys.argv)!=3:raise RuntimeError("ARGS RESULT_COMMIT MODEL")
 print("MPW103I_INDEPENDENT_VERIFIED "+json.dumps(main(*sys.argv[1:]),sort_keys=True),flush=True)
