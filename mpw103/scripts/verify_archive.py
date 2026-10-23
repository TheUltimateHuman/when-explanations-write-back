# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""Independent MPW-103 raw archive recovery from an immutable Git commit.
Usage: uv run verify_archive.py <40-hex-Git-commit> <qwen3|granite>
Validates all original raw data SHA-256 anchors and separate analysis source.
"""
import sys,hashlib,base64,gzip,json,tempfile,importlib.util
from pathlib import Path
from urllib.request import urlopen
def sha(b):return hashlib.sha256(b).hexdigest()
def fetch(url):return urlopen(url,timeout=90).read()
def main():
 if len(sys.argv)!=3:raise RuntimeError('EXACT_COMMIT_AND_MODEL_REQUIRED')
 commit,model=sys.argv[1:]
 if len(commit)!=40 or any(c not in '0123456789abcdef' for c in commit):
  raise RuntimeError('BAD_IMMUTABLE_GIT_REF')
 if model not in ('qwen3','granite'):raise RuntimeError('BAD_MODEL_ID')
 root=f'https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/{commit}/mpw103/'
 mraw=fetch(root+'results/RESULTS_MANIFEST.json')
 manifest=json.loads(mraw)
 record=manifest['models'][model]
 if record['n']!=128 or len(record['shards'])!=4:
  raise RuntimeError('INCOMPLETE_RESULT_MANIFEST')
 raw_shards=[]
 for i,desc in enumerate(record['shards']):
  b64=fetch(root+f'results/{model}_shard{i+1:02d}.jsonl.gz.b64').strip()
  compressed=base64.b64decode(b64,validate=True)
  if desc.get('compressed_sha256') and sha(compressed)!=desc['compressed_sha256']:
   raise RuntimeError('COMPRESSED_SHARD_HASH_MISMATCH')
  raw=gzip.decompress(compressed)
  if sha(raw)!=desc['raw_sha256'] or len(raw.splitlines())!=32:
   raise RuntimeError('RAW_SHARD_HASH_OR_CARDINALITY_MISMATCH')
  raw_shards.append(raw)
 all_raw=b''.join(raw_shards)
 if sha(all_raw)!=record['combined_raw_sha256']:raise RuntimeError('COMBINED_RAW_SHA_MISMATCH')
 cases=[json.loads(row) for row in all_raw.splitlines()]
 independent_bytes=fetch(root+'scripts/independent_analysis.py')
 if sha(independent_bytes)!=manifest['independent_analysis_sha256']:
  raise RuntimeError('INDEPENDENT_SOURCE_SHA_MISMATCH')
 with tempfile.TemporaryDirectory() as td:
  f=Path(td)/'analyzer.py';f.write_bytes(independent_bytes)
  spec=importlib.util.spec_from_file_location('mpw103_analysis_independent',f)
  mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
  outcome=mod.compute(cases)
 outcome.update({'model':model,'archive_commit':commit,'raw_sha256':sha(all_raw),
                 'manifest_sha256':sha(mraw)})
 print('MPW103_INDEPENDENT_VERIFICATION '+json.dumps(outcome,sort_keys=True),flush=True)
if __name__=='__main__':main()
