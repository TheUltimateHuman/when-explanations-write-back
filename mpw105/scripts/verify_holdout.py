# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""MPW-105 independent HOLDOUT verdict: immutable GPU record hashes and q,s,C,L.
Usage: uv run verify_holdout.py <immutable-holdout-commit> <qwen3|granite>
This tool does not import model inference runner or retrain/select report policy.
"""
import sys,json,gzip,base64,hashlib,importlib.util,tempfile
from urllib.request import urlopen
from pathlib import Path
ROOT="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/"
def get(u):return urlopen(u,timeout=90).read()
def digest(b):return hashlib.sha256(b).hexdigest()
def verify(ref,model):
 if len(ref)!=40 or any(c not in "0123456789abcdef" for c in ref):
  raise RuntimeError("IMMUTABLE_RESULT_SHA_REQUIRED")
 if model not in ("qwen3","granite"):raise RuntimeError("UNEXPECTED_MODEL")
 prefix=ROOT+ref+"/mpw105/"
 m=json.loads(get(prefix+"holdout/HOLDOUT_MANIFEST.json"))
 info=m["models"][model]
 if info["n"]!=80 or len(info["shards"])!=4:
  raise RuntimeError("INCOMPLETE_BLIND_HOLDOUT")
 segments=[]
 for i,part in enumerate(info["shards"]):
  gz=base64.b64decode(get(prefix+f"holdout/{model}_shard{i+1:02d}.jsonl.gz.b64").strip(),validate=True)
  if part.get("gzip_sha256") and digest(gz)!=part["gzip_sha256"]:
   raise RuntimeError("COMPRESSED_DATA_CHANGED")
  original=gzip.decompress(gz)
  if len(original.splitlines())!=20 or digest(original)!=part["raw_sha256"]:
   raise RuntimeError("ORIGINAL_GPU_HOLDOUT_HASH_FAILED")
  segments.append(original)
 joined=b"".join(segments)
 if digest(joined)!=info["combined_raw_sha256"]:
  raise RuntimeError("WHOLE_HOLDOUT_RAW_SHA_MISMATCH")
 original_selector=get(prefix+"scripts/independent_selector.py")
 if digest(original_selector)!=m["independent_selector_sha256"]:
  raise RuntimeError("CPU_EVALUATOR_SOURCE_CHANGED")
 screenref=info["screen_selection_commit"]
 policyref=info["policy_commit"]
 if len(screenref)!=40 or len(policyref)!=40:
  raise RuntimeError("SELECTION_AND_POLICY_MUST_BE_FROZEN")
 screen=json.loads(get(ROOT+screenref+f"/mpw105/selection/{model}.json"))
 policy=json.loads(get(ROOT+policyref+f"/mpw105/policy/{model}.json"))
 with tempfile.TemporaryDirectory() as td:
  p=Path(td)/"selector.py";p.write_bytes(original_selector)
  spec=importlib.util.spec_from_file_location("independent_mpw105",p)
  mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
  rows=[json.loads(r) for r in joined.splitlines()]
  stats=mod.evaluate_holdout(rows,screen,policy)
 result={"model":model,"archive_ref":ref,"screen_selection_commit":screenref,
   "frozen_policy_commit":policyref,"n":len(rows),
   "original_raw_sha256":digest(joined),"independent_verdict":stats,
   "original_selector_sha256":digest(original_selector)}
 print("MPW105_HOLDOUT_INDEPENDENT_VERIFIED "+json.dumps(result,sort_keys=True),flush=True)
if __name__=="__main__":
 if len(sys.argv)!=3:raise RuntimeError("ARGS_RESULT_SHA_MODEL")
 verify(sys.argv[1],sys.argv[2])
