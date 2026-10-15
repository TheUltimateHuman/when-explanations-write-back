#!/usr/bin/env python3
"""Independent MPW-101 result recomputation. No inference-model imports.
Requires numpy/scipy. Use only on the prospectively frozen 256 original family rows.
"""
import argparse
import json
from pathlib import Path
from scipy.stats import binomtest
import numpy as np

N=256
BOOT=100000
SEED=520261015

def assess(rows):
    if len(rows)!=N or len({r['idx'] for r in rows})!=N or {r['idx'] for r in rows}!=set(range(32,288)):
        raise ValueError('Incomplete or duplicated frozen validation family collection')
    d=[]; f0=[]; f1=[]; al=[]; tables={}
    for r in sorted(rows,key=lambda x:x['idx']):
        sign=1 if r['report']['side']=='LEFT' else -1
        x=sign*r['base']['D'];y=sign*r['m1_selected']['D']
        al.append(y-x)
        f0.append(int(x>0));f1.append(int(y>0));d.append((x,y))
    def table(q,p):
        a=sum((not i) and (not j) for i,j in zip(q,p))
        b=sum((not i) and j for i,j in zip(q,p))
        c=sum(i and (not j) for i,j in zip(q,p))
        e=sum(i and j for i,j in zip(q,p))
        return [a,b,c,e]
    t=table(f0,f1)
    def bootstrap(z,seed):
        rr=np.random.default_rng(seed)
        obs=[]
        for n in range(0,BOOT,10000):
            ids=rr.integers(0,len(z),size=(min(10000,BOOT-n),len(z)))
            obs.extend(np.mean(z[ids],axis=1))
        return [float(np.quantile(obs,.025)),float(np.quantile(obs,.975))]
    delta=np.asarray(f1,float)-np.asarray(f0,float)
    lo,hi=bootstrap(delta,SEED)
    p=float(binomtest(t[1],t[1]+t[2],.5).pvalue) if t[1]+t[2] else 1.
    res={'n':N,'table':dict(zip(('00','01','10','11'),t)),
         'q':float(np.mean(f0)),'s':float(np.mean(f1)),
         'C':t[1]/N,'L':t[2]/N,'tau':float(np.mean(delta)),
         'mcnemar_two_sided_p':p,'tau_bootstrap_95':[lo,hi],
         'continuous_mean_delta':float(np.mean(al))}
    assert abs(res['s']-(res['q']+res['C']-res['L']))<1e-12
    res['primary_verdict']='PRIMARY_CONFIRMED' if res['tau']>0 and p<.05 and lo>0 else 'PRIMARY_NOT_CONFIRMED'
    res['validation_accuracy']=float(np.mean([r['base']['acc'] for r in rows]))
    if res['validation_accuracy']<.90:res['primary_verdict']='INVALID_CAPABILITY_VALIDATION'
    res['sensitivity']={}
    for th in (.02,.05,.10):
        z=np.asarray([int(b>th)-int(a>th) for a,b in d],float)
        b,c=int(sum(z>0)),int(sum(z<0))
        res['sensitivity'][str(th)]={'conversion':b,'loss':c,'tau':float(np.mean(z)),
          'p':float(binomtest(b,b+c,.5).pvalue) if b+c else 1.,
          'ci95':bootstrap(z,SEED+int(th*100))}
    res['mean_report_meaning_effect']=float(np.mean([.5*(r['m1_left']['D']-r['m1_right']['D']+r['m2_left']['D']-r['m2_right']['D']) for r in rows]))
    res['free_carrier_effect']=float(np.mean([r['free_A']['D']-r['free_B']['D'] for r in rows]))
    res['max_abs_noise_floor']=max(abs(r['base']['D']-r['base_repeat']['D']) for r in rows)
    return res

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('rows_jsonl')
    parser.add_argument('--output',default='')
    a=parser.parse_args()
    rows=[json.loads(t) for t in Path(a.rows_jsonl).read_text().splitlines() if t.strip()]
    result=assess(rows)
    print(json.dumps(result,sort_keys=True,indent=2))
    if a.output:Path(a.output).write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
if __name__=='__main__':main()
