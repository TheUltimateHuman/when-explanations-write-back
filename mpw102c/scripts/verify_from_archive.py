# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""MPW-102C immutable-archive raw recovery and independent recomputation.

Usage: uv run verify_from_archive.py <40-char Git SHA> <qwen3|granite>
The hash-checked independent analyzer is never imported from the model runner.
"""
import sys,hashlib,base64,gzip,json,tempfile,importlib.util
from pathlib import Path
from urllib.request import urlopen
def h(b):return hashlib.sha256(b).hexdigest()
def fetch(url):return urlopen(url,timeout=90).read()
def main():
 if len(sys.argv)!=3:raise RuntimeError('ARGS_REQUIRED_COMMIT_MODEL')
 sha,model=sys.argv[1:]
 if len(sha)!=40 or any(c not in '0123456789abcdef' for c in sha):
  raise RuntimeError('INVALID_IMMUTABLE_COMMIT_SHA')
 if model not in ('qwen3','granite'):raise RuntimeError('UNRECOGNIZED_MODEL')
 root=f'https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/{sha}/mpw102c/'
 manifest_bytes=fetch(root+'results/RESULTS_MANIFEST.json')
 manifest=json.loads(manifest_bytes)
 status=manifest['models'][model]
 if status['n']!=160 or len(status['shards'])!=4:raise RuntimeError('INCOMPLETE_MANIFEST')
 shards=[]
 for i,part in enumerate(status['shards']):
  b64=fetch(root+f'results/{model}_shard{i+1:02d}.jsonl.gz.b64').strip()
  compressed=base64.b64decode(b64,validate=True)
  if part.get('compressed_sha256') and h(compressed)!=part['compressed_sha256']:
   raise RuntimeError('COMPRESSED_CONTENT_HASH_MISMATCH')
  raw=gzip.decompress(compressed)
  if h(raw)!=part['raw_sha256'] or len(raw.splitlines())!=40:
   raise RuntimeError('RAW_SHARD_MISMATCH')
  shards.append(raw)
 combined=b''.join(shards)
 if h(combined)!=status['combined_raw_sha256']:raise RuntimeError('FULL_RAW_SHA_MISMATCH')
 records=[json.loads(line) for line in combined.splitlines()]
 if len(records)!=160:raise RuntimeError('MISSING_FAMILIES')
 analysis=fetch(root+'scripts/independent_analysis.py')
 if h(analysis)!=manifest['independent_analysis_sha256']:
  raise RuntimeError('ANALYZER_SOURCE_SHA_MISMATCH')
 with tempfile.TemporaryDirectory() as td:
  f=Path(td)/'independent.py';f.write_bytes(analysis)
  spec=importlib.util.spec_from_file_location('independent',f)
  mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
  res=mod.compute(records)
 res.update({'model':model,'raw_sha256':h(combined),'archive_commit':sha,
             'manifest_sha256':h(manifest_bytes)})
 print('MPW102C_INDEPENDENT_VERIFICATION '+json.dumps(res,sort_keys=True),flush=True)
if __name__=='__main__':main()
