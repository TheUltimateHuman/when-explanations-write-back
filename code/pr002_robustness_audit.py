#!/usr/bin/env python3
"""Recompute metric-stress and exploratory fidelity-transition analyses from recovered PR-002 Phi CSV."""
import argparse, csv, json, random
from pathlib import Path
from statistics import mean, median
from scipy.stats import binomtest

def ci_boot(x, seed=520260910, B=100000):
    rng=random.Random(seed); n=len(x); vals=sorted(mean(x[rng.randrange(n)] for _ in range(n)) for _ in range(B))
    return [vals[int(.025*B)], vals[int(.975*B)-1]]

def sm(x):
    pos=sum(v>0 for v in x); neg=sum(v<0 for v in x); n=pos+neg
    return {"n":len(x),"mean":mean(x),"median":median(x),"ci95":ci_boot(x),"pos":pos,"neg":neg,"sign_p":binomtest(pos,n,.5).pvalue if n else None}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); ap.add_argument("--out"); a=ap.parse_args()
    rows=[]
    with open(a.csv,newline='') as f:
        for r in csv.DictReader(f):
            for k in list(r):
                if k not in {"order","map1_A","report_side"}: r[k]=float(r[k])
            rows.append(r)
    raw=[]; safe=[]; nonsat=[]; trans={"00":0,"01":0,"10":0,"11":0}
    for r in rows:
        def J(p): return r[p+"_IL"]-r[p+"_IR"]
        raw.append(.5*((J("m1L")-J("m1R"))+(J("m2L")-J("m2R"))))
        semantic=("m1L","m1R","m2L","m2R")
        if all(r[p+"_IL"]>0 and r[p+"_IR"]>0 for p in semantic): safe.append(r["delta_sem"])
        if all(abs(r[p+"_D"])<.95 for p in semantic): nonsat.append(r["delta_sem"])
        sg=1 if r["report_side"]=="LEFT" else -1; post=r["m1L_D"] if sg==1 else r["m1R_D"]
        f0=int(sg*r["base_D"]>0); f1=int(sg*post>0); trans[f"{f0}{f1}"]+=1
    q=(trans['10']+trans['11'])/96; s=(trans['01']+trans['11'])/96; C=trans['01']/96; L=trans['10']/96
    out={"primary":sm([r["delta_sem"] for r in rows]),"all_positive_semantic_branches":sm(safe),"nonsaturated_semantic_branches":sm(nonsat),"raw_margin_contrast":sm(raw),"fidelity_transition":{"counts":trans,"q":q,"s":s,"C":C,"L":L,"identity_error":s-(q+C-L)}}
    text=json.dumps(out,indent=2,sort_keys=True); print(text)
    if a.out: Path(a.out).write_text(text)

if __name__=='__main__': main()
