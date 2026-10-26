# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""MPW-103I hash-preserving full baseline screen and 64-case selection verification.
Usage: uv run verify_screen.py <immutable-40hex-commit> <qwen3|granite>
No GPU runner import. Rebuilds first-32-per-label from all 2048 untreated records.
"""
import sys,hashlib,gzip,base64,json,tempfile,importlib.util
from pathlib import Path
from urllib.request import urlopen
ROOT="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/"
def fetch(url):return urlopen(url,timeout=90).read()
def sha(b):return hashlib.sha256(b).hexdigest()
def verify(ref,model):
 if len(ref)!=40 or any(c not in "0123456789abcdef" for c in ref):
  raise RuntimeError("IMMUTABLE_SCREEN_COMMIT_REQUIRED")
 if model not in ("qwen3","granite"):raise RuntimeError("UNDECLARED_MODEL")
 base=ROOT+ref+"/mpw103i/"
 manifest_bytes=fetch(base+"screen/SCREEN_MANIFEST.json")
 meta=json.loads(manifest_bytes)
 info=meta["models"][model]
 if info["n_candidates"]!=2048 or len(info["shards"])!=8:
  raise RuntimeError("INCOMPLETE_GPU_SCREEN_RECORD_SET")
 blobs=[]
 for i,item in enumerate(info["shards"]):
  encoded=fetch(base+f"screen/{model}_shard{i+1:02d}.jsonl.gz.b64").strip()
  compressed=base64.b64decode(encoded,validate=True)
  if item.get("gzip_sha256") and sha(compressed)!=item["gzip_sha256"]:
   raise RuntimeError("COMPRESSED_SCREEN_CHANGED")
  part=gzip.decompress(compressed)
  if sha(part)!=item["raw_sha256"] or len(part.splitlines())!=256:
   raise RuntimeError("ORIGINAL_GPU_SCREEN_SHA_OR_SIZE_MISMATCH")
  blobs.append(part)
 full=b"".join(blobs)
 if sha(full)!=info["combined_raw_sha256"]:
  raise RuntimeError("COMPLETE_GPU_SCREEN_HASH_FAILED")
 source=fetch(base+"scripts/independent_screen.py")
 if sha(source)!=meta["independent_screen_sha256"]:
  raise RuntimeError("ORIGINAL_INDEPENDENT_SCREEN_CODE_CHANGED")
 with tempfile.TemporaryDirectory() as td:
  p=Path(td)/"screen.py";p.write_bytes(source)
  spec=importlib.util.spec_from_file_location("blind_mpw103i",p)
  module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  rows=[json.loads(x) for x in full.splitlines()]
  selection=module.reanalyze_screen(rows,meta["candidate_manifest_sha256"])
  selection_hash=module.sha(module.stable(selection))
  original_sel=json.loads(fetch(base+f"selection/{model}.json"))
  if selection!=original_sel or selection_hash!=info["selection_sha256"]:
   raise RuntimeError("INDEPENDENT_SELECTION_DOES_NOT_MATCH_ORIGINAL_GPU")
  if not selection["selection_complete"] or selection["n_selected"]!=64:
   raise RuntimeError("NO_VALID_SELECTION")
  return {"model":model,"n_screened":len(rows),"raw_sha256":sha(full),
     "n_selected":selection["n_selected"],"selected_indices":[x["idx"] for x in selection["selected"]],
     "eligible_per_label":selection["eligible_per_label"],
     "rejection_reason_counts":selection["rejection_reason_counts"],
     "selection_sha256":selection_hash,"immutable_screen_commit":ref}
if __name__=="__main__":
 if len(sys.argv)!=3:raise RuntimeError("ARGS: GIT_COMMIT MODEL")
 print("MPW103I_INDEPENDENT_SCREEN_VERIFIED "+json.dumps(verify(*sys.argv[1:]),sort_keys=True),flush=True)
