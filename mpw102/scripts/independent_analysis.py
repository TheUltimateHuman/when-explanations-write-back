"""Independent reproduction of MPW-102 from intact raw JSONL.

Recomputes family-level primary estimand directly; NEVER imports model-runner.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from scipy.stats import binomtest
CARRIERS=('AB','XY','KM');ORDERS=('LR','RL')

def compute(records,seed=520261016):
    if len(records)!=256 or len({r['idx'] for r in records})!=256:
        raise ValueError('EXPECTED_256_UNIQUE_FAMILIES')
    p=[];cells={o:{c:[] for c in CARRIERS} for o in ORDERS}
    native_controls={o:{c:[] for c in CARRIERS} for o in ORDERS}
    raw=[];acc={o:[] for o in ORDERS};sens=[];repeat=[];ack={}
    for record in records:
        six=[];sixraw=[]
        for order in ORDERS:
            ob=record['orders'][order]
            pre=ob['baseline'];acc[order].append(int(pre['acc']));sens.append(pre['sens'])
            repeat.append(abs(pre['D']-ob['baseline_repeat']['D']))
            for control in ('neutral_ack','label_ack'):
                ack.setdefault(order+'_'+control,[]).append(ob[control]['D']-pre['D'])
            for carrier in CARRIERS:
                z=ob['carriers'][carrier]
                mapping0=(z['m0']['LEFT']['D']-z['m0']['RIGHT']['D'])
                mapping1=(z['m1']['LEFT']['D']-z['m1']['RIGHT']['D'])
                e=(mapping0+mapping1)/2
                er=((z['m0']['LEFT']['J']-z['m0']['RIGHT']['J'])+(z['m1']['LEFT']['J']-z['m1']['RIGHT']['J']))/2
                cells[order][carrier].append(e);six.append(e);sixraw.append(er)
                native_controls[order][carrier].append(z['free0']['D']-z['free1']['D'])
        p.append(sum(six)/6);raw.append(sum(sixraw)/6)
    p=np.array(p);B=50000;gen=np.random.default_rng(seed);means=[]
    for j in range(0,B,5000):
        ids=gen.integers(0,256,size=(min(5000,B-j),256))
        means.append(p[ids].mean(axis=1))
    lo,hi=np.quantile(np.concatenate(means),[.025,.975]);nplus=int((p>0).sum());nminus=int((p<0).sum());
    cmeans={c:float(np.mean([e for o in ORDERS for e in cells[o][c]])) for c in CARRIERS}
    omeans={o:float(np.mean([e for c in CARRIERS for e in cells[o][c]])) for o in ORDERS}
    passgates={o:float(np.mean(acc[o]))>=.90 for o in ORDERS}
    numerical=max(repeat)
    stat={'n':len(records),'mean':float(p.mean()),'ci95':[float(lo),float(hi)],'positive':nplus,'negative':nminus,
          'exact_sign_p':float(binomtest(nplus,nplus+nminus,.5).pvalue) if nplus+nminus else 1.,
          'carrier_means':cmeans,'order_means':omeans,'accuracy_by_order':{o:float(np.mean(acc[o])) for o in ORDERS},
          'control_mean_by_order_and_carrier':{o:{c:float(np.mean(native_controls[o][c])) for c in CARRIERS} for o in ORDERS},
          'acknowledgment_means':{k:float(np.mean(v)) for k,v in ack.items()},
          'raw_J_mean':float(np.mean(raw)),'mean_sensitivity':float(np.mean(sens)),
          'numerical_floor_max':float(numerical)}
    if not all(passgates.values()) or numerical>=1e-4:stat['verdict']='INVALID'
    elif p.mean()>0 and lo>0 and stat['exact_sign_p']<.05 and all(v>0 for v in cmeans.values()) and all(v>0 for v in omeans.values()):stat['verdict']='PRIMARY_CONFIRMED'
    else:stat['verdict']='PRIMARY_NOT_CONFIRMED'
    return stat

def main():
    p=argparse.ArgumentParser();p.add_argument('jsonl');p.add_argument('--output',required=True)
    opt=p.parse_args();b=Path(opt.jsonl).read_bytes();rows=[json.loads(s) for s in b.splitlines() if s]
    stats=compute(rows);stats['source_sha256']=hashlib.sha256(b).hexdigest()
    Path(opt.output).write_text(json.dumps(stats,indent=2,sort_keys=True)+'\n')
    print(json.dumps(stats,indent=2))
if __name__=='__main__':main()
