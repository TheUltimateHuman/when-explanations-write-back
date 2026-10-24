# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""MPW-104B four-shard treatment verification independent of GPU runner.
Usage: uv run verify_treatment.py <immutable_git_commit> <model>
"""
import json,sys,hashlib,gzip,base64,importlib.util,tempfile
from pathlib import Path
from urllib.request import urlopen
ROOT="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/"
def fetch(url):return urlopen(url,timeout=90).read()
def h(data):return hashlib.sha256(data).hexdigest()
def main(ref,model):
 if len(ref)!=40 or any(c not in "0123456789abcdef" for c in ref):
  raise RuntimeError("IMMUTABLE_COMMIT_SHA_REQUIRED")
 if model not in ("qwen3","granite"):raise RuntimeError("UNKNOWN_MODEL")
 prefix=ROOT+ref+"/mpw104b/"
 man=json.loads(fetch(prefix+"results/RESULTS_MANIFEST.json"))
 data=man["models"][model]
 if data["n"]!=80 or len(data["shards"])!=4:
  raise RuntimeError("WRONG_TREATMENT_SHARDS")
 selection_ref=data["screen_selection_commit"]
 selection=json.loads(fetch(ROOT+selection_ref+f"/mpw104b/selection/{model}.json"))
 chunks=[]
 for i,meta in enumerate(data["shards"]):
  blob=fetch(prefix+f"results/{model}_shard{i+1:02d}.jsonl.gz.b64").strip()
  gz=base64.b64decode(blob,validate=True)
  if meta.get("gzip_sha256") and h(gz)!=meta["gzip_sha256"]:
   raise RuntimeError("COMPRESSED_TREATMENT_HASH_MISMATCH")
  raw=gzip.decompress(gz)
  if h(raw)!=meta["raw_sha256"] or len(raw.splitlines())!=20:
   raise RuntimeError("RAW_TREATMENT_SHARD_CHANGED")
  chunks.append(raw)
 all_raw=b"".join(chunks)
 if h(all_raw)!=data["combined_raw_sha256"]:
  raise RuntimeError("COMBINED_TREATMENT_RAW_SHA_MISMATCH")
 source=fetch(prefix+"scripts/independent_analysis.py")
 if h(source)!=man["independent_analysis_sha256"]:
  raise RuntimeError("ORIGINAL_INDEPENDENT_ANALYSIS_CHANGED")
 with tempfile.TemporaryDirectory() as tmp:
  p=Path(tmp)/"analysis.py";p.write_bytes(source)
  spec=importlib.util.spec_from_file_location("blind_treatment",p)
  mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
  family=[json.loads(s) for s in all_raw.splitlines()]
  result=mod.reanalyze_treatment(family,selection)
 output={"archive_ref":ref,"model":model,"screen_selection_commit":selection_ref,
      "n":len(family),"raw_sha256":h(all_raw),"independent_result":result}
 print("MPW104B_TREATMENT_INDEPENDENT_VERIFIED "+json.dumps(output,sort_keys=True),flush=True)
if __name__=="__main__":
 if len(sys.argv)!=3:raise RuntimeError("ARGS_REF_MODEL")
 main(sys.argv[1],sys.argv[2])
