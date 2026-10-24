# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""MPW-104B immutable screen archive integrity + blind selection verification.
Usage: uv run verify_screen.py <immutable_git_commit> <qwen3|granite>
"""
import sys,json,gzip,base64,hashlib,importlib.util,tempfile
from pathlib import Path
from urllib.request import urlopen
ROOT="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/"
def fetch(url):return urlopen(url,timeout=90).read()
def sha(b):return hashlib.sha256(b).hexdigest()
def main(commit,model):
 if len(commit)!=40 or any(c not in '0123456789abcdef' for c in commit):
  raise RuntimeError("INVALID_IMMUTABLE_COMMIT_SHA")
 if model not in ("qwen3","granite"):raise RuntimeError("INVALID_MODEL_NAME")
 url=ROOT+commit+"/mpw104b/"
 manifest=json.loads(fetch(url+"screen/SCREEN_MANIFEST.json"))
 entry=manifest["models"][model]
 if entry["n_candidates"]!=2048 or len(entry["shards"])!=8:
  raise RuntimeError("INCOMPLETE_SCREEN_RECORDS")
 chunks=[]
 for j,anchor in enumerate(entry["shards"]):
  gz=base64.b64decode(fetch(url+f"screen/{model}_shard{j+1:02d}.jsonl.gz.b64").strip(),validate=True)
  if "gzip_sha256" in anchor and sha(gz)!=anchor["gzip_sha256"]:
   raise RuntimeError("COMPRESSED_SCREEN_HASH_MISMATCH")
  raw=gzip.decompress(gz)
  if sha(raw)!=anchor["raw_sha256"] or len(raw.splitlines())!=256:
   raise RuntimeError("SCREEN_ORIGINAL_GPU_SHARD_MISMATCH")
  chunks.append(raw)
 combined=b"".join(chunks)
 if sha(combined)!=entry["combined_raw_sha256"]:
  raise RuntimeError("COMPLETE_SCREEN_SHA_MISMATCH")
 records=[json.loads(z) for z in combined.splitlines()]
 source=fetch(url+"scripts/independent_analysis.py")
 if sha(source)!=manifest["independent_analysis_sha256"]:
  raise RuntimeError("SCREEN_ANALYSIS_SHA_MISMATCH")
 with tempfile.TemporaryDirectory() as td:
  f=Path(td)/"blind_analysis.py";f.write_bytes(source)
  spec=importlib.util.spec_from_file_location("screen_analysis",f)
  m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  selected=m.reanalyze_screen(records,manifest["candidate_manifest_sha256"])
  expected_sha=m.sha(m.stable(selected))
  if expected_sha!=entry["original_screen_selected_sha256"]:
   raise RuntimeError("INDEPENDENT_SELECTION_HASH_MISMATCH")
  saved_bytes=fetch(url+f"selection/{model}.json").strip()
  saved=json.loads(saved_bytes)
  if selected!=saved:
   raise RuntimeError("SELECTED_RECORDS_DIFFER_FROM_FROZEN_SCREEN")
  if saved["selection_complete"]!=True or saved["n_selected"]!=80:
   raise RuntimeError("SCREEN_COULD_NOT_PRODUCE_TARGET")
  result={"model":model,"screen_raw_sha256":sha(combined),
   "selection_sha256":expected_sha,"screen_n":len(records),
   "selected_n":selected["n_selected"],
   "selected_indices":[q["idx"] for q in selected["selected"]],
   "eligible_per_label":selected["eligible_per_label"],
   "selected_per_label":selected["selected_per_label"],
   "rejection_reason_counts":selected["rejection_reason_counts"],
   "archive_commit":commit}
 print("MPW104B_SCREEN_INDEPENDENT_VERIFIED "+json.dumps(result,sort_keys=True),flush=True)
if __name__=="__main__":
 if len(sys.argv)!=3:raise RuntimeError("ARGS_COMMIT_MODEL_REQUIRED")
 main(sys.argv[1],sys.argv[2])
