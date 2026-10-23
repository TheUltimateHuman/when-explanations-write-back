# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""MPW-102C: independent recomputation from raw family records.
Does not import executing GPU source. Immutable gates from PROTOCOL.md.
"""
import json,hashlib,math,argparse
from pathlib import Path
import numpy as np
from scipy.stats import binomtest

PERSONS=('SELF','YOU','THIRD')
EXTRA=('YOU_QUESTION','YOU_PRESCRIPTIVE','DIRECTIVE','SIDE_REFERENCE')
STYLES=tuple(p+'_DECLARATIVE' for p in PERSONS)+tuple(p+'_REFERENCE' for p in PERSONS)+EXTRA
ORDERS=('LR','RL')
ALPHA=.05/6
N=160
BOOT=50000
SEED=520261124

def infer(vector,step):
    x=np.array(vector,dtype=np.float64)
    if x.shape!=(N,) or not np.isfinite(x).all():raise RuntimeError('PRIMARY_VECTOR_SHAPE_OR_NONFINITE')
    gen=np.random.default_rng(SEED+step)
    replicates=[]
    for j in range(0,BOOT,2500):
        idx=gen.integers(0,N,size=(min(2500,BOOT-j),N))
        replicates.append(x[idx].mean(axis=1))
    samples=np.concatenate(replicates)
    plus=int(np.count_nonzero(x>0));minus=int(np.count_nonzero(x<0))
    return {'mean':float(x.mean()),'median':float(np.median(x)),
       'ci95':[float(y) for y in np.quantile(samples,[.025,.975])],
       'ci_familywise':[float(y) for y in np.quantile(samples,[ALPHA/2,1-ALPHA/2])],
       'positive':plus,'negative':minus,'zero':N-plus-minus,
       'sign_p':float(binomtest(plus,plus+minus,.5).pvalue) if plus+minus else 1.0}

def compute(records):
    if len(records)!=N or set(x['idx'] for x in records)!=set(range(32,192)):
        raise RuntimeError('EXPECTED_COMPLETE_160_FAMILIES')
    effects={k:[] for k in ('H1','H2','H3')}
    by_order={k:{o:[] for o in ORDERS} for k in effects}
    frames={s:[] for s in STYLES}
    control={o:{x:[] for x in ('neutral_ack','label_ack')} for o in ORDERS}
    acc={o:[] for o in ORDERS};sens=[];noise=[];j=[];sat=0;nonpos=0
    required={'baseline','baseline_repeat','neutral_ack','label_ack'}
    required.update(f'ab_m{m}_{side}' for m in (0,1) for side in ('LEFT','RIGHT'))
    required.update(f'{style}_{side}' for style in STYLES for side in ('LEFT','RIGHT'))
    for item in records:
        if len(item.get('case_sha256',''))!=64:raise RuntimeError('UNVERIFIED_CASE_KEY')
        if set(item.get('orders',{}))!=set(ORDERS):raise RuntimeError('INCOMPLETE_ORDER')
        family_frames={s:[] for s in STYLES}
        fam_h1=[]
        for order in ORDERS:
            q=item['orders'][order]
            if set(q)!=required:raise RuntimeError('MISSING_OR_EXTRA_BRANCH')
            if not all(math.isfinite(float(w['D'])) and math.isfinite(float(w['J'])) for w in q.values()):
                raise RuntimeError('NONFINITE_BRANCH')
            b=q['baseline']
            acc[order].append(int(b['acc']))
            sens.append(b['sens'])
            noise.append(abs(b['D']-q['baseline_repeat']['D']))
            sat+=int(abs(b['D'])>=.95)
            nonpos+=int(b['I_left']<=0 or b['I_right']<=0)
            for name in control[order]:
                control[order][name].append(q[name]['D']-b['D'])
            h1=np.mean([q[f'ab_m{m}_LEFT']['D']-q[f'ab_m{m}_RIGHT']['D'] for m in (0,1)])
            fam_h1.append(float(h1));by_order['H1'][order].append(float(h1))
            j.append(float(np.mean([q[f'ab_m{m}_LEFT']['J']-q[f'ab_m{m}_RIGHT']['J'] for m in (0,1)])))
            for style in STYLES:
                family_frames[style].append(q[style+'_LEFT']['D']-q[style+'_RIGHT']['D'])
            deltas=[family_frames[p+'_DECLARATIVE'][-1]-family_frames[p+'_REFERENCE'][-1] for p in PERSONS]
            by_order['H2'][order].append(float(np.mean(deltas)))
            by_order['H3'][order].append(float(deltas[0]-deltas[1]))
        effects['H1'].append(float(np.mean(fam_h1)))
        z={name:float(np.mean(family_frames[name])) for name in STYLES}
        for name in STYLES:frames[name].append(z[name])
        vals=[z[p+'_DECLARATIVE']-z[p+'_REFERENCE'] for p in PERSONS]
        effects['H2'].append(float(np.mean(vals)))
        effects['H3'].append(vals[0]-vals[1])
    estimates={k:infer(effects[k],i+1) for i,k in enumerate(('H1','H2','H3'))}
    order_means={k:{o:float(np.mean(by_order[k][o])) for o in ORDERS} for k in effects}
    accuracy={o:float(np.mean(acc[o])) for o in ORDERS}
    valid=all(v>=.9 for v in accuracy.values()) and max(noise)<1e-4
    verdicts={}
    for name,e in estimates.items():
        passed=valid and e['mean']>0 and e['ci_familywise'][0]>0 and e['sign_p']<ALPHA and all(x>0 for x in order_means[name].values())
        verdicts[name]='CONFIRMED' if passed else ('INVALID' if not valid else 'NOT_CONFIRMED')
    frame_means={k:float(np.mean(v)) for k,v in frames.items()}
    return {'n':len(records),'H1':estimates['H1'],'H2':estimates['H2'],'H3':estimates['H3'],
            'verdicts':verdicts,'order_effects':order_means,
            'validation_accuracy':accuracy,'mean_sensitivity':float(np.mean(sens)),
            'numeric_floor_max':float(max(noise)),'nonpositive_interventions':nonpos,
            'saturated_baselines':sat,'frame_means':frame_means,
            'person_matched_means':{p:frame_means[p+'_DECLARATIVE']-frame_means[p+'_REFERENCE'] for p in PERSONS},
            'raw_J_AB':float(np.mean(j)),'ack_means':{o+'_'+c:float(np.mean(v)) for o,d in control.items() for c,v in d.items()},
            'valid':bool(valid),'joint_per_model':all(x=='CONFIRMED' for x in verdicts.values())}
if __name__=='__main__':
  p=argparse.ArgumentParser();p.add_argument('jsonl');a=p.parse_args()
  raw=Path(a.jsonl).read_bytes()
  rows=[json.loads(x) for x in raw.splitlines() if x]
  out=compute(rows);out['combined_raw_sha256']=hashlib.sha256(raw).hexdigest()
  print('MPW102C_INDEPENDENT '+json.dumps(out,sort_keys=True),flush=True)
