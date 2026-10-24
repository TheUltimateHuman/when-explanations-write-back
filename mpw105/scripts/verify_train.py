# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""MPW-105 independent TRAIN proof: archive SHA, protected screen, F1-only selection.
Usage: uv run verify_train.py <immutable-train-commit> <qwen3|granite>.
Prints immutable policy object; write this exact result to
mpw105/policy/MODEL.json in a NEW Git commit before HOLDOUT GPU dispatch.
"""
import sys,json,gzip,base64,hashlib,importlib.util,tempfile
from urllib.request import urlopen
from pathlib import Path
ROOT="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/"
def get(uri):return urlopen(uri,timeout=90).read()
def h(b):return hashlib.sha256(b).hexdigest()
def load(commit,model):
 if len(commit)!=40 or any(z not in "0123456789abcdef" for z in commit):
  raise RuntimeError("IMMUTABLE_COMMIT_REQUIRED")
 if model not in ("qwen3","granite"):raise RuntimeError("UNKNOWN_MODEL")
 prefix=ROOT+commit+"/mpw105/"
 meta=json.loads(get(prefix+"train/TRAIN_MANIFEST.json"))
 info=meta["models"][model]
 if info["n"]!=80 or len(info["shards"])!=4:raise RuntimeError("MISSING_TRAIN_RECORDS")
 chunks=[]
 for i,anchor in enumerate(info["shards"]):
  gz=base64.b64decode(get(prefix+f"train/{model}_shard{i+1:02d}.jsonl.gz.b64").strip(),validate=True)
  if "gzip_sha256" in anchor and h(gz)!=anchor["gzip_sha256"]:
   raise RuntimeError("COMPRESSED_SHA_MISMATCH")
  raw=gzip.decompress(gz)
  if len(raw.splitlines())!=20 or h(raw)!=anchor["raw_sha256"]:
   raise RuntimeError("ORIGINAL_GPU_TRAIN_RECORDS_CHANGED")
  chunks.append(raw)
 full=b"".join(chunks)
 if h(full)!=info["combined_raw_sha256"]:
  raise RuntimeError("COMPLETE_TRAIN_RAW_SHA_MISMATCH")
 selection_commit=info["screen_selection_commit"]
 if len(selection_commit)!=40:raise RuntimeError("SCREEN_COMMIT_NOT_FROZEN")
 screen=json.loads(get(ROOT+selection_commit+f"/mpw105/selection/{model}.json"))
 source=get(prefix+"scripts/independent_selector.py")
 if h(source)!=meta["independent_selector_sha256"]:
  raise RuntimeError("INDEPENDENT_BLIND_SELECTOR_SHA_CHANGED")
 with tempfile.TemporaryDirectory() as td:
  path=Path(td)/"selector.py";path.write_bytes(source)
  spec=importlib.util.spec_from_file_location("mpw105_cpu_selector",path)
  analyzer=importlib.util.module_from_spec(spec);spec.loader.exec_module(analyzer)
  data=[json.loads(x) for x in full.splitlines()]
  policy=analyzer.select_policy(data,screen)
  if policy["selection_training_data_sha256"]!=h(full):
   raise RuntimeError("BLIND_SELECTOR_TRAIN_SHA_DISAGREEMENT")
  # Don't infer success; report only the selected training policy.
  out={"model":model,"train_archive_commit":commit,"screen_archive_commit":selection_commit,
       "train_raw_sha256":h(full),"policy_sha256":analyzer.sha(analyzer.canonical(policy)),
       "policy":policy}
 print("MPW105_INDEPENDENT_TRAIN_POLICY "+json.dumps(out,sort_keys=True),flush=True)
if __name__=="__main__":
 if len(sys.argv)!=3:raise RuntimeError("ARGS_TRAIN_COMMIT_MODEL")
 load(sys.argv[1],sys.argv[2])
