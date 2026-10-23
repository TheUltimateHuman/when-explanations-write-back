# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3"]
# ///
"""MPW-103 post hoc diagnostics from immutable Granite raw record archive.
No model execution, no modifications to prespecified H1/H2/H3/H4 decisions.
"""
import hashlib,gzip,base64,json
from urllib.request import urlopen
from collections import defaultdict
import numpy as np

COMMIT='637e1d7bb91f6f45c8ed3bfa32a70f35070453ac'
BASE='https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/'+COMMIT+'/mpw103/results/'
M=json.loads(urlopen(BASE+'RESULTS_MANIFEST.json',timeout=60).read())
parts=[]
for i,ob in enumerate(M['models']['granite']['shards']):
    b64=urlopen(BASE+f'granite_shard{i+1:02d}.jsonl.gz.b64',timeout=60).read().strip()
    raw=gzip.decompress(base64.b64decode(b64,validate=True))
    assert hashlib.sha256(raw).hexdigest()==ob['raw_sha256']
    parts.append(raw)
data=b''.join(parts)
assert hashlib.sha256(data).hexdigest()==M['models']['granite']['combined_raw_sha256']
rows=[json.loads(line) for line in data.splitlines()]
assert len(rows)==128
samples=defaultdict(list)
family_values=defaultdict(list)
for record in rows:
    this=defaultdict(list)
    for order in ('LR','RL'):
        r=record['orders'][order]
        for mapping in (0,1):
            for final in ('LEFT','RIGHT'):
                pref=f'm{mapping}_{final}_'
                def d(name):return r[pref+name]['D']
                def j(name):return r[pref+name]['J']
                e2=d('PREV_1_LEFT')-d('PREV_1_RIGHT')
                e4=d('PREV_3_LEFT')-d('PREV_3_RIGHT')
                e8=d('PREV_7_LEFT')-d('PREV_7_RIGHT')
                free=d('FREE_PREV_7_LEFT')-d('FREE_PREV_7_RIGHT')
                ordering=d('BALANCED_LATE_LEFT')-d('BALANCED_EARLY_LEFT')
                hj=j('PREV_7_LEFT')-j('PREV_7_RIGHT')
                prefix='order_'+order+'_'
                samples[prefix+'E8'].append(e8)
                samples['mapping_'+str(mapping)+'_E8'].append(e8)
                samples['final_'+final+'_E8'].append(e8)
                samples['order_'+order+'_H4'].append(ordering)
                samples['mapping_'+str(mapping)+'_H4'].append(ordering)
                samples['final_'+final+'_H4'].append(ordering)
                samples['E2'].append(e2)
                samples['E4'].append(e4)
                samples['E8'].append(e8)
                samples['E8free'].append(free)
                samples['H2'].append(e8-e2)
                samples['H3'].append(e8-free)
                samples['H4'].append(ordering)
                samples['J8'].append(hj)
                this['H1'].append(e8)
                this['H2'].append(e8-e2)
                this['H3'].append(e8-free)
                this['H4'].append(ordering)
        # controlled exploratory subsets by untouched baseline profile, not used for primary
        q=r['baseline']
        samples['baseline_total_sensitivity'].append(q['sens'])
    for key in ('H1','H2','H3','H4'):
        family_values[key].append(float(np.mean(this[key])))
def stats(x):
    a=np.asarray(x)
    return {'n':int(len(a)),'mean':float(np.mean(a)),'median':float(np.median(a)),
            'q05':float(np.quantile(a,.05)),'q25':float(np.quantile(a,.25)),
            'q75':float(np.quantile(a,.75)),'q95':float(np.quantile(a,.95)),
            'positive':int(np.count_nonzero(a>0)),'negative':int(np.count_nonzero(a<0))}
output={
    'classification':'POST_HOC_DESCRIPTIVE_NO_NEW_CONFIRMATION',
    'n_families':len(rows),'raw_sha256':hashlib.sha256(data).hexdigest(),
    'family_level':{key:stats(z) for key,z in family_values.items()},
    'by_order_mapping_final':{key:stats(z) for key,z in samples.items() if
       key.startswith(('order_','mapping_','final_')) and not key=='baseline_total_sensitivity'},
    'overall_raw_J8':stats(samples['J8']),
    'cautions':['Individual cells per family are correlated: their n is not independent.',
      'The fixed-count order reversal is opposite the prespecified H4 direction.',
      'These analyses do not modify the prospective primary verdicts.']}
print('MPW103_POSTHOC_AUDIT '+json.dumps(output,sort_keys=True),flush=True)
