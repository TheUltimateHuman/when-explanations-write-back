# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3", "scipy==1.15.3"]
# ///
"""Independent remote archivist/verifier, no model inference.

Expected usage: uv run verify_from_archive.py COMMIT_SHA
Fetches exactly 4 binary gzip shard files from the frozen GitHub archive;
verifies every member against RESULTS_MANIFEST.json, runs separate
independent_analysis.py, and prints independent verdict and SHA-256.
"""
import gzip,hashlib,importlib.util,json,sys,tempfile
from pathlib import Path
from urllib.request import urlopen

def sha(x):return hashlib.sha256(x).hexdigest()

def fetch(url):return urlopen(url,timeout=90).read()

def main():
 if len(sys.argv)!=2: raise RuntimeError('EXPECTED_GIT_COMMIT_SHA_ARGUMENT')
 commit=sys.argv[1]
 if len(commit)!=40 or any(k not in '0123456789abcdef' for k in commit):
  raise RuntimeError('INVALID_GIT_COMMIT_SHA_ARGUMENT')
 base=f'https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/{commit}/mpw102/'
 manifest=json.loads(fetch(base+'results/RESULTS_MANIFEST.json'))
 if manifest['n']!=256 or len(manifest['shards'])!=4:raise RuntimeError('BAD_RESULTS_MANIFEST')
 raw=[]
 for j,item in enumerate(manifest['shards']):
  b=fetch(base+f'results/shard{j+1:02d}.jsonl.gz')
  if sha(b)!=item['gz_sha256']:raise RuntimeError('COMPRESSED_SHA_MISMATCH')
  text=gzip.decompress(b)
  if sha(text)!=item['raw_sha256']:raise RuntimeError('RAW_SHA_MISMATCH')
  if len(text.splitlines())!=64:raise RuntimeError('INCOMPLETE_SHARD')
  raw.append(text)
 combined=b''.join(raw)
 if sha(combined)!=manifest['combined_raw_sha256']:raise RuntimeError('COMBINED_RAW_SHA_MISMATCH')
 rows=[json.loads(line) for line in combined.splitlines()]
 if len(rows)!=256:raise RuntimeError('BAD_RECORD_COUNT')
 code=fetch(base+'scripts/independent_analysis.py')
 if sha(code)!=manifest['independent_analysis_sha256']:raise RuntimeError('INDEPENDENT_SOURCE_SHA_MISMATCH')
 with tempfile.TemporaryDirectory() as td:
  p=Path(td)/'independent_analysis.py';p.write_bytes(code)
  spec=importlib.util.spec_from_file_location('independent_analysis',str(p))
  mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
  result=mod.compute(rows)
 result['combined_raw_sha256']=sha(combined)
 result['result_manifest_sha256']=sha(fetch(base+'results/RESULTS_MANIFEST.json'))
 result['archive_commit']=commit
 print('MPW102_INDEPENDENT_RECOMPUTATION '+json.dumps(result,sort_keys=True),flush=True)

if __name__=='__main__':main()
