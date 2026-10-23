# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""Independent MPW-102B archive verifier.

Usage: uv run verify_from_archive.py <immutable_commit> <qwen3|granite>
Downloads only archived rows and an independently written analysis module.
Checks file/combined SHA-256, cardinality, source integrity and recomputes.
"""
import base64,gzip,hashlib,importlib.util,json,sys,tempfile
from pathlib import Path
from urllib.request import urlopen
def sha(b):return hashlib.sha256(b).hexdigest()
def fetch(url):return urlopen(url,timeout=90).read()
def main():
 if len(sys.argv)!=3:raise RuntimeError('ARGS_COMMIT_AND_MODEL_REQUIRED')
 commit,model=sys.argv[1:]
 if len(commit)!=40 or any(c not in '0123456789abcdef' for c in commit):
  raise RuntimeError('INVALID_COMMIT_ID')
 if model not in ('qwen3','granite'):raise RuntimeError('INVALID_MODEL')
 base=f'https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/{commit}/mpw102b/'
 manifest=json.loads(fetch(base+'results/RESULTS_MANIFEST.json'))
 meta=manifest['models'][model]
 if meta['n']!=192 or len(meta['shards'])!=4:raise RuntimeError('INCORRECT_MANIFEST_CARDINALITY')
 raw_parts=[]
 for k,elem in enumerate(meta['shards']):
  b64=fetch(base+f'results/{model}_shard{k+1:02d}.jsonl.gz.b64').strip()
  decoded=base64.b64decode(b64,validate=True)
  if elem.get('compressed_sha256') and sha(decoded)!=elem['compressed_sha256']:
   raise RuntimeError('COMPRESSED_DIGEST_MISMATCH')
  raw=gzip.decompress(decoded)
  if sha(raw)!=elem['raw_sha256']:raise RuntimeError('SHARD_DIGEST_MISMATCH')
  if len(raw.splitlines())!=48:raise RuntimeError('BAD_SHARD_SIZE')
  raw_parts.append(raw)
 combined=b''.join(raw_parts)
 if sha(combined)!=meta['combined_raw_sha256']:raise RuntimeError('COMBINED_HASH_MISMATCH')
 records=[json.loads(x) for x in combined.splitlines()]
 if len(records)!=192:raise RuntimeError('INCOMPLETE_RECORDS')
 src=fetch(base+'scripts/independent_analysis.py')
 if sha(src)!=manifest['independent_analysis_sha256']:
  raise RuntimeError('INDEPENDENT_ANALYSIS_SOURCE_MISMATCH')
 with tempfile.TemporaryDirectory() as tmp:
  path=Path(tmp)/'analysis.py';path.write_bytes(src)
  spec=importlib.util.spec_from_file_location('analysis_module',path)
  module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 result=module.compute(records)
 result['model']=model
 result['archive_commit']=commit
 result['combined_raw_sha256']=sha(combined)
 result['manifest_sha256']=sha(fetch(base+'results/RESULTS_MANIFEST.json'))
 print('MPW102B_INDEPENDENT_VERIFIED '+json.dumps(result,sort_keys=True),flush=True)
if __name__=='__main__':main()
