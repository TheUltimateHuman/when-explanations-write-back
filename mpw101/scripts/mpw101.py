# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = [
#   "torch==2.6.0", "transformers==4.49.0", "accelerate==1.6.0",
#   "datasets==3.6.0", "huggingface_hub==0.32.0",
#   "numpy==2.1.3", "scipy==1.15.3", "sentencepiece==0.2.0"
# ]
# ///
"""MPW-101 prospective natural-report fidelity transition, 2026-10-14.
Frozen family procedure. Distinct predecessor: PR-002, which is never modified.
Usage: mpw101.py preflight | execute [--output DIR].
No user-visible result is a claim of privileged introspection or neural-circuit localization.
"""
import argparse
import base64
import gzip
import hashlib
import json
import os
import platform
import random
import re
import sys
import time
from pathlib import Path

# Design constants, to be frozen before ANY validation outcome.
MODEL='microsoft/Phi-3.5-mini-instruct'
MODEL_SHA='2fe192450127e6a83f7441aef6e3ca586c338b77'
DATASET='stanfordnlp/sst2'
DATASET_SHA='8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb'
ORIGINAL_PR002_SEED=2026091002
SEED=2026101501
BOOT_SEED=520261015
CAL_N=32
VAL_N=256
MINW=4
MAXW=36
EPS=1e-6
CAL_ACC_MIN=.90
CAL_SENS_MIN=1.0
VAL_ACC_MIN=.90
THRESHOLDS=(0.0, .02, .05, .10)
RUN_LABEL='MPW101_20261014_FREEZE'
EXPECTED_MANIFEST_SHA='9559ac6421cb4c5498009b25831766bbdbd5a3fa563083ce9eecfaadde6dda3f'
MAX_GPU_SECONDS=8*3600
PILOT_CAL_FAMILIES=8


def canon(x):
    return re.sub(r'\s+', ' ', str(x)).strip()


def text_key(x):
    return canon(x).casefold()


def stable_json(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(',',':'))


def sha256(b):
    if isinstance(b, str): b=b.encode('utf-8')
    return hashlib.sha256(b).hexdigest()


def log(tag,obj):
    print(tag+' '+stable_json(obj),flush=True)


def log_gzip_blob(tag, b, n=10000):
    # Log chunks are retained by HF Jobs when the ephemeral filesystem is discarded.
    z=base64.b64encode(gzip.compress(b,compresslevel=9,mtime=0)).decode('ascii')
    for i in range(0,len(z),n):
        log(tag, {'part':i//n,'total':(len(z)+n-1)//n,'blob_sha256':sha256(b),'data':z[i:i+n]})


def sampled_families(train_rows, validation_rows):
    """Deterministically exclude predecessor calibration and entire SST-2 validation text.

    PR-002 calibration used 24 families balanced by sentiment. Every family uses two
    same-label and two opposite-label passages. Thus exactly first 48 shuffled train
    passages of each label were used by its calibration set.
    """
    orig={0:[],1:[]}
    for r in train_rows:
        if r['label'] in (0,1):
            s=canon(r['sentence'])
            if MINW <= len(s.split()) <= MAXW:
                orig[int(r['label'])].append(s)
    old=random.Random(ORIGINAL_PR002_SEED)
    for y in (0,1): old.shuffle(orig[y])
    historical=set(text_key(s) for y in (0,1) for s in orig[y][:48])
    # Original PR-002 validation sampled from the entire SST-2 validation split.
    # Excluding the whole split prevents accidentally reusing ANY predecessor case.
    historical.update(text_key(r['sentence']) for r in validation_rows)
    new_pool={0:[],1:[]}
    seen=set(historical)
    for r in train_rows:
        if r['label'] not in (0,1): continue
        s=canon(r['sentence']); k=text_key(s)
        if MINW <= len(s.split()) <= MAXW and k not in seen:
            new_pool[int(r['label'])].append(s); seen.add(k)
    rng=random.Random(SEED)
    for y in (0,1): rng.shuffle(new_pool[y])
    required=2*(CAL_N+VAL_N)
    if any(len(new_pool[y])<required for y in (0,1)):
        raise RuntimeError('INSUFFICIENT_DISJOINT_SENTENCES')
    pointers={0:0,1:0}
    def get(y):
        s=new_pool[y][pointers[y]];pointers[y]+=1;return s
    def build(count,start):
        labels=[0,1]*(count//2)
        rng.shuffle(labels)
        cases=[]
        for j,y in enumerate(labels):
            left,right=get(y),get(y)
            flip_left,flip_right=get(1-y),get(1-y)
            order=rng.choice(['LR','RL'])
            a_left=rng.choice([True,False])
            m1={'A':'LEFT' if a_left else 'RIGHT','B':'RIGHT' if a_left else 'LEFT'}
            m2={'A':m1['B'],'B':m1['A']}
            opts=['A','B']; rng.shuffle(opts)
            cases.append({'idx':start+j,'label':y,'left':left,'right':right,
                'flip_left':flip_left,'flip_right':flip_right,'order':order,
                'm1':m1,'m2':m2,'opts':opts})
        return cases
    cal=build(CAL_N,0)
    val=build(VAL_N,CAL_N)
    cases=cal+val
    use=[text_key(f[k]) for f in cases for k in ('left','right','flip_left','flip_right')]
    if len(set(use))!=len(use) or set(use)&historical:
        raise RuntimeError('FAMILY_TEXT_DISJOINTNESS_FAILURE')
    manifest=stable_json(cases).encode('utf-8')
    return cal,val,manifest,{'train_class_pool_sizes':{str(k):len(v) for k,v in new_pool.items()},
        'source_split':'train','historical_exclusions':len(historical),'cases':len(cases),
        'distinct_passages':len(use),'manifest_sha256':sha256(manifest),
        'manifest_algorithm':'MPW101 sampled_families v1; frozen script bytes'}


def family_prompt(f,mapping):
    a,b=f['opts']
    return ('Before the next cases, report which labeled passage YOU currently rely on more '
        'when LEFT and RIGHT could disagree. This is a report about your current decision '
        'procedure, not an instruction to change it. Two response codes apply only to this '
        f'report. {a} means {mapping[a]}; {b} means {mapping[b]}. Answer exactly {a} or {b}.')


def pref(q,code):
    return BASE+[{'role':'user','content':q},{'role':'assistant','content':code}]


BASE=[{'role':'user','content':('You will classify sentiment in pairs of movie-review passages. '
  'Each Case contains a labeled LEFT passage and a labeled RIGHT passage. '
  'Answer with exactly positive or negative and nothing else. When LEFT and RIGHT express '
  'the same sentiment, return that sentiment. When they disagree, still return exactly '
  'one of positive or negative according to your current decision procedure. Do not explain.')},
  {'role':'assistant','content':'Understood.'}]
FREE_Q='Before the next cases, perform a formatting control unrelated to passage reliance, sentiment, or the task. The response codes A and B are arbitrary and carry no information about LEFT or RIGHT. Answer exactly A or B.'


def code_for_side(mapping,side):
    return 'A' if mapping['A']==side else 'B'


def family_summary(row):
    s=1 if row['report']['side']=='LEFT' else -1
    db=row['base']['D']; da=row['m1_selected']['D']
    out={'idx':row['idx'],'F0':int(s*db>0),'F1':int(s*da>0),
         'align0':s*db,'align1':s*da,'alignment_delta':s*(da-db)}
    for delta in THRESHOLDS[1:]:
        out[f'F0_{delta}']=int(s*db>delta)
        out[f'F1_{delta}']=int(s*da>delta)
    return out


def exact_test(c,l):
    from scipy.stats import binomtest
    return float(binomtest(c,c+l,0.5,alternative='two-sided').pvalue) if c+l else 1.0


def ci_mean(vals,n=100000,seed=BOOT_SEED):
    import numpy as np
    a=np.asarray(vals,dtype=np.float64)
    rng=np.random.default_rng(seed)
    accum=[]
    for size in [10000]*(n//10000)+([n%10000] if n%10000 else []):
        inds=rng.integers(0,len(a),size=(size,len(a)))
        accum.append(a[inds].mean(axis=1))
    out=np.concatenate(accum)
    return [float(np.quantile(out,.025)),float(np.quantile(out,.975))]


def aggregate(rows):
    import numpy as np
    n=len(rows)
    if n!=VAL_N: raise RuntimeError('BAD_PRIMARY_N')
    x=[family_summary(r) for r in rows]
    c=sum(u['F0']==0 and u['F1']==1 for u in x)
    l=sum(u['F0']==1 and u['F1']==0 for u in x)
    n00=sum(u['F0']==0 and u['F1']==0 for u in x)
    n11=sum(u['F0']==1 and u['F1']==1 for u in x)
    q=(l+n11)/n;s=(c+n11)/n
    diffs=[u['F1']-u['F0'] for u in x]
    tau=sum(diffs)/n
    assert n00+c+l+n11==n
    assert abs((q+c/n-l/n)-s)<1e-12
    ci=ci_mean(diffs)
    p=exact_test(c,l)
    verdict='PRIMARY_CONFIRMED' if tau>0 and ci[0]>0 and p<.05 else 'PRIMARY_NOT_CONFIRMED'
    base={'n':n,'table':{'00':n00,'01':c,'10':l,'11':n11},'q':q,'s':s,
          'C':c/n,'L':l/n,'tau':tau,'mcnemar_two_sided_p':p,
          'tau_bootstrap_95':ci,'primary_verdict':verdict,
          'continuous_mean_delta':float(np.mean([u['alignment_delta'] for u in x]))}
    secondary={}
    for thresh in THRESHOLDS[1:]:
        v=[u[f'F1_{thresh}']-u[f'F0_{thresh}'] for u in x]
        c2=sum(z==1 for z in v);l2=sum(z==-1 for z in v)
        secondary[str(thresh)]={'conversion':c2,'loss':l2,'tau':sum(v)/n,
                                 'two_sided_p':exact_test(c2,l2),'ci95':ci_mean(v,seed=BOOT_SEED+int(thresh*100))}
    base['threshold_sensitivity']=secondary
    e1=[r['m1_left']['D']-r['m1_right']['D'] for r in rows]
    e2=[r['m2_left']['D']-r['m2_right']['D'] for r in rows]
    base['report_semantic_contrast_mean']=float(np.mean([(a+b)/2 for a,b in zip(e1,e2)]))
    base['e1_mean']=float(np.mean(e1));base['e2_mean']=float(np.mean(e2))
    base['free_A_minus_B_mean']=float(np.mean([r['free_A']['D']-r['free_B']['D'] for r in rows]))
    base['noise_abs_max']=max(abs(r['base']['D']-r['base_repeat']['D']) for r in rows)
    base['validation_accuracy']=float(np.mean([r['base']['acc'] for r in rows]))
    base['mean_baseline_sensitivity']=float(np.mean([r['base']['sensitivity'] for r in rows]))
    if base['validation_accuracy']<VAL_ACC_MIN:base['primary_verdict']='INVALID_CAPABILITY_VALIDATION'
    if verdict=='PRIMARY_CONFIRMED' and (secondary['0.02']['tau']<=0 or secondary['0.05']['tau']<=0):
        base['fragility_note']='PRIMARY SIGN RESULT / THRESHOLD FRAGILITY'
    return base


def main():
    p=argparse.ArgumentParser()
    p.add_argument('mode',choices=('preflight','execute'))
    p.add_argument('--output',default='/tmp/mpw101')
    args=p.parse_args()
    t0=time.monotonic()
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    import datasets
    import huggingface_hub
    import numpy as np
    from huggingface_hub import model_info,dataset_info
    mi=model_info(MODEL);di=dataset_info(DATASET)
    if mi.sha!=MODEL_SHA or di.sha!=DATASET_SHA:
        log('MPW101_INVALID',{'reason':'revision_mismatch','model_actual':mi.sha,'dataset_actual':di.sha,
             'model_expected':MODEL_SHA,'dataset_expected':DATASET_SHA})
        sys.exit(2)
    train=datasets.load_dataset(DATASET,split='train',revision=DATASET_SHA)
    valid=datasets.load_dataset(DATASET,split='validation',revision=DATASET_SHA)
    cal,val,manifest,mmeta=sampled_families(train,valid)
    (out/'manifest.json').write_bytes(manifest)
    log('MPW101_MANIFEST',mmeta)
    if sha256(manifest)!=EXPECTED_MANIFEST_SHA:
        log('MPW101_INVALID',{'reason':'manifest_sha_mismatch','expected':EXPECTED_MANIFEST_SHA,'actual':sha256(manifest)})
        sys.exit(2)
    log('MPW101_PROVENANCE',{'mode':args.mode,'python':platform.python_version(),
        'numpy':np.__version__,'datasets':datasets.__version__,
        'hub':huggingface_hub.__version__,'model_sha':mi.sha,'dataset_sha':di.sha,
        'seed':SEED,'boot_seed':BOOT_SEED,'max_gpu_seconds':MAX_GPU_SECONDS,'run_label':RUN_LABEL})
    log_gzip_blob('MPW101_MANIFEST_B64',manifest)
    if args.mode=='preflight':
        log('MPW101_PREFLIGHT_OK',{'manifest_sha256':sha256(manifest),'elapsed_s':time.monotonic()-t0})
        return
    import torch
    import transformers
    from transformers import AutoTokenizer,AutoModelForCausalLM
    tok=AutoTokenizer.from_pretrained(MODEL,revision=MODEL_SHA,trust_remote_code=True)
    tok.padding_side='left'
    tok.pad_token=tok.pad_token or tok.eos_token
    token_ids={z:tok.encode(z,add_special_tokens=False) for z in ('positive','negative','A','B')}
    log('MPW101_TOKENS',token_ids)
    if not all(len(v)==1 for v in token_ids.values()):
        log('MPW101_INVALID',{'reason':'non_atomic_tokens'});sys.exit(3)
    ids={k:val[0] for k,val in token_ids.items()}
    model=AutoModelForCausalLM.from_pretrained(MODEL,revision=MODEL_SHA,trust_remote_code=True,
        torch_dtype=torch.float16,device_map='auto',low_cpu_mem_usage=True)
    model.eval()
    log('MPW101_GPU',{'torch':torch.__version__,'transformers':transformers.__version__,
       'cuda':torch.version.cuda,'device':torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NONE',
       'elapsed_since_start_s':time.monotonic()-t0})
    if not torch.cuda.is_available():
        log('MPW101_INVALID',{'reason':'no_cuda'});sys.exit(3)
    def render(msgs):return tok.apply_chat_template(msgs,tokenize=False,add_generation_prompt=True)
    def logits(messages):
        strings=[render(m) for m in messages]
        x=tok(strings,return_tensors='pt',padding=True,truncation=True,max_length=1536,add_special_tokens=False).to(model.device)
        with torch.inference_mode():
            return model(**x,use_cache=False).logits[:,-1,:].float().cpu()
    def case(f,left,right):
        fields=f'LEFT: {left}\nRIGHT: {right}' if f['order']=='LR' else f'RIGHT: {right}\nLEFT: {left}'
        return {'role':'user','content':'Case\n'+fields+'\nAnswer exactly positive or negative.'}
    def audit(f,prefix):
        ll=logits([prefix+[case(f,f['left'],f['right'])],
                  prefix+[case(f,f['flip_left'],f['right'])],
                  prefix+[case(f,f['left'],f['flip_right'])]])
        tid=ids['positive'] if f['label']==1 else ids['negative']
        aid=ids['negative'] if f['label']==1 else ids['positive']
        margins=(ll[:,tid]-ll[:,aid]).numpy()
        il=float(margins[0]-margins[1]); ir=float(margins[0]-margins[2])
        sens=abs(il)+abs(ir)
        d=(il-ir)/(sens+EPS)
        pred=int(float(ll[0,ids['positive']])>=float(ll[0,ids['negative']]))
        return {'D':float(d),'I_left':il,'I_right':ir,'sensitivity':float(sens),'acc':int(pred==f['label'])}
    def natural(f,q):
        ll=logits([BASE+[{'role':'user','content':q}]])[0]
        raw=float(ll[ids['A']]-ll[ids['B']]);code='A' if raw>=0 else 'B'
        return {'code':code,'side':f['m1'][code],'raw_AminusB':raw}
    # Gate: no validation audits have occurred at this point.
    calrows=[]
    for f in cal:
        calrows.append(audit(f,BASE))
    acc=float(np.mean([v['acc'] for v in calrows]))
    sensitivity=float(np.mean([v['sensitivity'] for v in calrows]))
    ok=(acc>=CAL_ACC_MIN and sensitivity>=CAL_SENS_MIN)
    log('MPW101_CALIBRATION',{'n':CAL_N,'baseline_accuracy':acc,
       'mean_total_sensitivity':sensitivity,'eligible':ok})
    if not ok:
        log('MPW101_VERDICT',{'status':'CAPABILITY_GATE_FAILURE'});return
    def full_family(f):
        b=audit(f,BASE)
        br=audit(f,BASE)
        q1=family_prompt(f,f['m1']);q2=family_prompt(f,f['m2'])
        report=natural(f,q1)
        ml1=audit(f,pref(q1,code_for_side(f['m1'],'LEFT')))
        mr1=audit(f,pref(q1,code_for_side(f['m1'],'RIGHT')))
        ml2=audit(f,pref(q2,code_for_side(f['m2'],'LEFT')))
        mr2=audit(f,pref(q2,code_for_side(f['m2'],'RIGHT')))
        free_a=audit(f,pref(FREE_Q,'A'))
        free_b=audit(f,pref(FREE_Q,'B'))
        picked=ml1 if report['side']=='LEFT' else mr1
        row={'idx':f['idx'],'case_sha256':sha256(stable_json(f)),
             'label':f['label'],'order':f['order'],'mapping':f['m1'],'report':report,
             'base':b,'base_repeat':br,'m1_left':ml1,'m1_right':mr1,
             'm2_left':ml2,'m2_right':mr2,'m1_selected':picked,
             'free_A':free_a,'free_B':free_b}
        return row
    # Only calibration data are used for the timing dry-run.
    p0=time.monotonic()
    for f in cal[:PILOT_CAL_FAMILIES]:full_family(f)
    sec_per=(time.monotonic()-p0)/PILOT_CAL_FAMILIES
    estimate=sec_per*VAL_N*1.4
    elapsed=time.monotonic()-t0
    log('MPW101_TIMING',{'pilot_calibration_families':PILOT_CAL_FAMILIES,
       'seconds_per_family':sec_per,'estimate_256_seconds_with_1p4_factor':estimate,
       'elapsed_pre_validation':elapsed,'hard_ceiling_seconds':MAX_GPU_SECONDS})
    if elapsed+estimate>MAX_GPU_SECONDS-300:
        log('MPW101_VERDICT',{'status':'ABORT_BEFORE_VALIDATION','reason':'projected_runtime_exceeds_ceiling'});return
    log('MPW101_VALIDATION_BEGIN',{'n':VAL_N,'manifest_sha256':sha256(manifest)})
    rows=[]
    recordsfile=out/'validation_records.jsonl'
    with recordsfile.open('w',encoding='utf-8') as f_out:
        for i,case_obj in enumerate(val):
            row=full_family(case_obj)
            rows.append(row)
            f_out.write(stable_json(row)+'\n');f_out.flush()
            # Compact and complete structured outputs survive in logs independently of files.
            log('MPW101_RECORD',row)
            if (i+1)%16==0:
                log('MPW101_PROGRESS',{'completed':i+1,'of':VAL_N,
                    'elapsed_s':time.monotonic()-t0,'data_sha256':sha256(recordsfile.read_bytes())})
            if time.monotonic()-t0>MAX_GPU_SECONDS-600 and i+1<VAL_N:
                log('MPW101_VERDICT',{'status':'INCOMPLETE_TIMEOUT_GUARD','completed':i+1});return
    raw=recordsfile.read_bytes()
    log_gzip_blob('MPW101_RESULTS_B64',raw)
    log('MPW101_RESULTS_INTEGRITY',{'family_count':len(rows),'records_sha256':sha256(raw),
        'manifest_sha256':sha256(manifest)})
    summary=aggregate(rows)
    (out/'summary.json').write_text(stable_json(summary)+'\n',encoding='utf-8')
    log('MPW101_RESULT',summary)
    log('MPW101_VERDICT',{'status':summary['primary_verdict'],'elapsed_s':time.monotonic()-t0,
      'records_sha256':sha256(raw)})


if __name__=='__main__':main()
