# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""Recompute amended MPW outcomes using original independent analyzers."""
import sys,json,gzip,base64,hashlib,importlib.util,tempfile
from pathlib import Path
from urllib.request import urlopen

def get(url):
    return urlopen(url,timeout=90).read()

def digest(content):
    return hashlib.sha256(content).hexdigest()

def main(commit,label):
    assert len(commit)==40 and all(c in '0123456789abcdef' for c in commit)
    assert label in ('mpw102b_granite','mpw103_qwen')
    root='https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/'+commit+'/'
    manifest_bytes=get(root+'mpw-runtime-recovery/results/RESULTS_MANIFEST.json')
    manifest=json.loads(manifest_bytes)
    entry=manifest['runs'][label]
    count=192 if label=='mpw102b_granite' else 128
    n_shard=count//4
    assert entry['n']==count and len(entry['shards'])==4
    assert entry['category']=='POST_RESULT_TIME_GATE_AMENDMENT'
    payload=[]
    for i,anchor in enumerate(entry['shards']):
        uri=root+'mpw-runtime-recovery/results/'+label+'/shard'+str(i+1).zfill(2)+'.jsonl.gz.b64'
        archived=get(uri).strip()
        raw=gzip.decompress(base64.b64decode(archived,validate=True))
        assert len(raw.splitlines())==n_shard
        assert digest(raw)==anchor['raw_sha256']
        payload.append(raw)
    combined=b''.join(payload)
    assert digest(combined)==entry['combined_raw_sha256']
    cases=[json.loads(x) for x in combined.splitlines()]
    analyzer='mpw102b' if label=='mpw102b_granite' else 'mpw103'
    source=get(root+analyzer+'/scripts/independent_analysis.py')
    assert digest(source)==entry['independent_original_analysis_sha256']
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/'independent.py'
        p.write_bytes(source)
        spec=importlib.util.spec_from_file_location('mpw_original_analytic',p)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result=module.compute(cases)
    return {'label':label,'n':len(cases),'raw_sha256':digest(combined),
            'manifest_sha256':digest(manifest_bytes),'original_independent_analysis_sha256':digest(source),
            'amended_job_id':entry['amended_job_id'],
            'classification':'POST_RESULT_TIME_GATE_AMENDMENT',
            'recomputed':result}

if __name__=='__main__':
    assert len(sys.argv)==3
    print('MPW_TIMEGATE_INDEPENDENT_VERIFICATION '+json.dumps(main(sys.argv[1],sys.argv[2]),sort_keys=True),flush=True)
