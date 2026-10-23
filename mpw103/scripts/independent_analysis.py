# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""Independent MPW-103 Phase A family-level verifier (no model runner imported).
Blind to hypotheses' GPU outcome values; all gates established in PROTOCOL.md.
"""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from scipy.stats import binomtest

N=128
ORDERS=('LR','RL')
HISTORY_NAMES=('LAST_ONLY','PREV_1_LEFT','PREV_1_RIGHT','PREV_3_LEFT','PREV_3_RIGHT',
 'PREV_7_LEFT','PREV_7_RIGHT','BALANCED_LATE_LEFT','BALANCED_EARLY_LEFT',
 'FREE_PREV_7_LEFT','FREE_PREV_7_RIGHT')
BOOT=50000
BOOT_SEED=520261025
ALPHA=0.05/8

def independent_stat(a,index):
    a=np.asarray(a,dtype=np.float64)
    if a.shape!=(N,) or not np.isfinite(a).all():raise ValueError('INVALID_FAMILY_PRIMARY_VECTOR')
    rng=np.random.default_rng(BOOT_SEED+index)
    samples=[]
    for begin in range(0,BOOT,2500):
        indices=rng.integers(0,N,size=(min(2500,BOOT-begin),N))
        samples.append(a[indices].mean(axis=1))
    bs=np.concatenate(samples)
    pos=int(np.count_nonzero(a>0));neg=int(np.count_nonzero(a<0))
    return {'mean':float(np.mean(a)),'median':float(np.median(a)),
     'ci95':[float(z) for z in np.quantile(bs,[.025,.975])],
     'ci_familywise':[float(z) for z in np.quantile(bs,[ALPHA/2,1-ALPHA/2])],
     'positive':pos,'negative':neg,'zero':N-pos-neg,
     'sign_p':float(binomtest(pos,pos+neg,.5).pvalue) if pos+neg else 1.}

def compute(records):
    if len(records)!=N or {r['idx'] for r in records}!=set(range(32,160)):
        raise ValueError('INCOMPLETE_OR_DUPLICATED_128_VALIDATION_FAMILIES')
    vectors={k:[] for k in ('H1','H2','H3','H4')}
    order_vec={k:{o:[] for o in ORDERS} for k in vectors}
    run_trajectory={k:[] for k in ('E2','E4','E8','E8_FREE','ORDER','J8')}
    accuracy={o:[] for o in ORDERS}
    neutral={o:[] for o in ORDERS};label={o:[] for o in ORDERS}
    sensitivity=[];repeat=[];saturation=0;negativeI=0
    transitions={'00':0,'01':0,'10':0,'11':0}
    required={'baseline','baseline_repeat','neutral_ack','label_ack'}
    required.update(f'm{mapping}_{side}_{history}' for mapping in (0,1)
                    for side in ('LEFT','RIGHT') for history in HISTORY_NAMES)
    if len(required)!=48:raise AssertionError('EXPECTED_48_BRANCHES')
    for record in records:
        if not isinstance(record.get('case_sha256'),str) or len(record['case_sha256'])!=64:
            raise ValueError('MISSING_CASE_SHA')
        orders=record.get('orders',{})
        if set(orders)!=set(ORDERS):raise ValueError('MISSING_PHYSICAL_ORDER')
        local={name:[] for name in run_trajectory}
        for order in ORDERS:
            obs=orders[order]
            if set(obs)!=required:raise ValueError('MISSING_HISTORY_AUDIT_BRANCH')
            for branch in obs.values():
                if any(not math.isfinite(float(branch[k])) for k in ('D','J','I_left','I_right','sens')):
                    raise ValueError('NONFINITE_CAUSAL_BRANCH')
            ref=obs['baseline']
            accuracy[order].append(int(ref['acc']))
            sensitivity.append(float(ref['sens']))
            repeat.append(abs(float(ref['D'])-float(obs['baseline_repeat']['D'])))
            saturation+=int(abs(ref['D'])>=.95)
            negativeI+=int(ref['I_left']<=0 or ref['I_right']<=0)
            neutral[order].append(obs['neutral_ack']['D']-ref['D'])
            label[order].append(obs['label_ack']['D']-ref['D'])
            for mapping in (0,1):
                for final_side in ('LEFT','RIGHT'):
                    p=f'm{mapping}_{final_side}_'
                    def val(history):return obs[p+history]['D']
                    for label_k,k in [('E2',1),('E4',3),('E8',7)]:
                        local[label_k].append(val(f'PREV_{k}_LEFT')-val(f'PREV_{k}_RIGHT'))
                    local['E8_FREE'].append(val('FREE_PREV_7_LEFT')-val('FREE_PREV_7_RIGHT'))
                    local['ORDER'].append(val('BALANCED_LATE_LEFT')-val('BALANCED_EARLY_LEFT'))
                    local['J8'].append(obs[p+'PREV_7_LEFT']['J']-obs[p+'PREV_7_RIGHT']['J'])
                    family_e2=val('PREV_1_LEFT')-val('PREV_1_RIGHT')
                    family_e8=val('PREV_7_LEFT')-val('PREV_7_RIGHT')
                    family_free=val('FREE_PREV_7_LEFT')-val('FREE_PREV_7_RIGHT')
                    measures={'H1':family_e8,'H2':family_e8-family_e2,
                              'H3':family_e8-family_free,
                              'H4':val('BALANCED_LATE_LEFT')-val('BALANCED_EARLY_LEFT')}
                    for h,v in measures.items():order_vec[h][order].append(float(v))
                    for prior_side in ('LEFT','RIGHT'):
                        base_alignment=ref['D'] if final_side=='LEFT' else -ref['D']
                        after=val('PREV_7_'+prior_side)
                        after_alignment=after if final_side=='LEFT' else -after
                        transitions[f'{int(base_alignment>0)}{int(after_alignment>0)}']+=1
        for key in local:run_trajectory[key].append(float(np.mean(local[key])))
        vectors['H1'].append(run_trajectory['E8'][-1])
        vectors['H2'].append(run_trajectory['E8'][-1]-run_trajectory['E2'][-1])
        vectors['H3'].append(run_trajectory['E8'][-1]-run_trajectory['E8_FREE'][-1])
        vectors['H4'].append(run_trajectory['ORDER'][-1])
    stats={name:independent_stat(vals,index) for index,(name,vals) in enumerate(vectors.items(),1)}
    order_means={name:{order:float(np.mean(vals)) for order,vals in v.items()}
                 for name,v in order_vec.items()}
    acc={o:float(np.mean(v)) for o,v in accuracy.items()}
    valid=(all(z>=.9 for z in acc.values()) and max(repeat)<1e-4)
    verdicts={}
    for name,st in stats.items():
        passgate=(valid and st['mean']>0 and st['ci_familywise'][0]>0 and
                  st['sign_p']<ALPHA and all(value>0 for value in order_means[name].values()))
        verdicts[name]='CONFIRMED' if passgate else ('INVALID' if not valid else 'NOT_CONFIRMED')
    return {'n':N,'estimates':stats,'verdicts':verdicts,'orders':order_means,
      'trajectory':{k:float(np.mean(v)) for k,v in run_trajectory.items()},
      'validation_accuracy':acc,'mean_sensitivity':float(np.mean(sensitivity)),
      'numerical_floor_max':float(max(repeat)),'saturated_baselines':saturation,
      'negative_interventions':negativeI,'neutral_means':{o:float(np.mean(v)) for o,v in neutral.items()},
      'label_means':{o:float(np.mean(v)) for o,v in label.items()},
      'agreement_table_descriptive':transitions,'valid':bool(valid),
      'full_eight_gate_per_model':all(v=='CONFIRMED' for v in verdicts.values())}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('records');a=p.parse_args()
 b=Path(a.records).read_bytes()
 rows=[json.loads(z) for z in b.splitlines() if z]
 result=compute(rows);result['raw_sha256']=hashlib.sha256(b).hexdigest()
 print('MPW103_INDEPENDENT_COMPUTATION '+json.dumps(result,sort_keys=True),flush=True)
