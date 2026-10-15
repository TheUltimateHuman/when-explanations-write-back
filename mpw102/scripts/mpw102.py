# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = [
#   "torch==2.6.0", "transformers==4.49.0", "accelerate==1.6.0",
#   "datasets==3.6.0", "huggingface_hub==0.32.0",
#   "numpy==2.1.3", "scipy==1.15.3", "sentencepiece==0.2.0"
# ]
# ///
"""MPW-102 v1. Multi-carrier, order-paired report-meaning test.

Design dated October 14, 2026, *after* MPW-101 and its exploratory MPW-101E
but before any new MPW-102 validation observations. Prior results are not pooled.
The object is input-level causal intervention dependence, not a neural circuit.

Usage: uv run mpw102.py preflight
       uv run mpw102.py execute
"""
import argparse, base64, gzip, hashlib, importlib.util, json, os, platform
import random, re, sys, tempfile, time
from pathlib import Path
from urllib.request import urlopen

PARENT_URL = ('https://raw.githubusercontent.com/TheUltimateHuman/'
              'when-explanations-write-back/2e650115db72b72ee5a03ae759326b7db1a19c20/'
              'mpw101/scripts/mpw101.py')
PARENT_HASH = '2f099745a19aea2241ec2821ac5e4632206ff6068ab93759e2a6ca40cac476d9'
PARENT_MANIFEST = '9559ac6421cb4c5498009b25831766bbdbd5a3fa563083ce9eecfaadde6dda3f'
MODEL='microsoft/Phi-3.5-mini-instruct'
MODEL_SHA='2fe192450127e6a83f7441aef6e3ca586c338b77'
DATASET='stanfordnlp/sst2'
DATASET_SHA='8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb'
SEED=2026101602
BOOT_SEED=520261016
CAL_N=32
VAL_N=256
MINW=4
MAXW=36
EPS=1e-6
CARRIERS=(('AB','A','B'),('XY','X','Y'),('12','1','2'))
ORDERS=('LR','RL')
CAL_ACC_MIN=.90
CAL_SENS_MIN=1.0
VAL_ACC_MIN=.90
MAX_SECONDS=70*60
# This hash is learned from a preflight that cannot load the inference model.
# It MUST be pinned in a separate code commit before validation execution.
EXPECTED_MANIFEST_SHA='UNSET_PREFLIGHT_REQUIRED'
NEUTRAL_Q=('The next case is another sentiment classification. Continue following '
           'exactly the existing decision rule. Acknowledge with Understood.')
LABEL_Q=('The next case still uses passage labels LEFT and RIGHT. '
         'No reliance report is requested. Continue the existing classification '
         'procedure. Acknowledge with Understood.')
REPORT_Q=('Before the next cases, report which labeled passage YOU currently rely on more '
          'when LEFT and RIGHT could disagree. This is a report about your current '
          'decision procedure, not an instruction to change it. Two response codes '
          'apply only to this report. {decl}. Answer exactly {a} or {b}.')
FREE_Q=('Before the next cases, perform a formatting control unrelated to passage '
        'reliance, sentiment, or the task. The response codes {a} and {b} are '
        'arbitrary and carry no information about LEFT or RIGHT. '
        'Answer exactly {a} or {b}.')


def stable(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def h(b): return hashlib.sha256(b if isinstance(b,bytes) else b.encode()).hexdigest()
def emit(tag,obj): print(tag+' '+stable(obj),flush=True)
def norm(s): return re.sub(r'\s+',' ',str(s)).strip()
def key(s): return norm(s).casefold()
def chunks(tag,raw,n=10000):
    z=base64.b64encode(gzip.compress(raw,compresslevel=9,mtime=0)).decode('ascii')
    for i in range(0,len(z),n):
        emit(tag,{'part':i//n,'total':(len(z)+n-1)//n,'sha256':h(raw),'data':z[i:i+n]})

def parent_module():
    source=urlopen(PARENT_URL,timeout=90).read()
    if h(source)!=PARENT_HASH: raise RuntimeError('PARENT_SOURCE_HASH_MISMATCH')
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/'parent.py';p.write_bytes(source)
        spec=importlib.util.spec_from_file_location('mpw101_readonly_parent',str(p))
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

def draw(train,valid,old):
    old_cal,old_val,old_bytes,_=old.sampled_families(train,valid)
    if h(old_bytes)!=PARENT_MANIFEST:raise RuntimeError('MPW101_MANIFEST_MISMATCH')
    removed={key(f[k]) for f in (old_cal+old_val)
             for k in ('left','right','flip_left','flip_right')}
    orig={0:[],1:[]}
    for row in train:
        if row['label'] in (0,1):
            s=norm(row['sentence'])
            if MINW<=len(s.split())<=MAXW:orig[int(row['label'])].append(s)
    earlier=random.Random(old.ORIGINAL_PR002_SEED)
    for y in (0,1):earlier.shuffle(orig[y])
    historical={key(s) for y in (0,1) for s in orig[y][:48]}
    historical.update(key(x['sentence']) for x in valid)
    historical.update(removed)
    seen=set(historical)
    pools={0:[],1:[]}
    for row in train:
        y=row['label']
        if y not in (0,1):continue
        s=norm(row['sentence']);k=key(s)
        if MINW<=len(s.split())<=MAXW and k not in seen:
            pools[int(y)].append(s);seen.add(k)
    rng=random.Random(SEED)
    for y in (0,1):rng.shuffle(pools[y])
    needed=2*(CAL_N+VAL_N)
    if any(len(pools[y])<needed for y in (0,1)):
        raise RuntimeError('INSUFFICIENT_DISJOINT_SAMPLES')
    ix={0:0,1:0}
    def take(y):
        a=pools[y][ix[y]];ix[y]+=1;return a
    def batch(n,start):
        labels=[0,1]*(n//2);rng.shuffle(labels)
        out=[]
        for j,y in enumerate(labels):
            left,right=take(y),take(y)
            flip_left,flip_right=take(1-y),take(1-y)
            # Code presentation order is fixed within a family and carrier across
            # both mappings and both passage orders; randomized across families.
            code_orders={c[0]:rng.choice([0,1]) for c in CARRIERS}
            out.append({'idx':start+j,'label':y,'left':left,'right':right,
                        'flip_left':flip_left,'flip_right':flip_right,
                        'code_orders':code_orders})
        return out
    cal=batch(CAL_N,0);val=batch(VAL_N,CAL_N)
    use=[key(f[k]) for f in cal+val for k in ('left','right','flip_left','flip_right')]
    if len(use)!=len(set(use)) or set(use)&historical:
        raise RuntimeError('TEXT_DISJOINTNESS_FAILED')
    manifest=stable(cal+val).encode()
    return cal,val,manifest,{'old_mpw101_removed':len(removed),
                            'historical_excluded':len(historical),
                            'pool_sizes':{str(y):len(pools[y]) for y in (0,1)},
                            'text_disjoint':True,'distinct_passages':len(use)}

def question(f,c,m):
    name,z0,z1=c
    a,b=(z0,z1) if f['code_orders'][name]==0 else (z1,z0)
    mapping={z0:'LEFT' if m==0 else 'RIGHT',z1:'RIGHT' if m==0 else 'LEFT'}
    decl=f'{a} means {mapping[a]}; {b} means {mapping[b]}'
    return REPORT_Q.format(decl=decl,a=a,b=b),mapping

def free_question(f,c):
    name,z0,z1=c
    a,b=(z0,z1) if f['code_orders'][name]==0 else (z1,z0)
    return FREE_Q.format(a=a,b=b)

def prefix(base,q,code):
    return base+[{'role':'user','content':q},{'role':'assistant','content':code}]

def exact_two_sided(sign_pos,sign_neg):
    from scipy.stats import binomtest
    n=sign_pos+sign_neg
    return float(binomtest(sign_pos,n,0.5).pvalue) if n else 1.0

def bootstrap_mean(x,seed=BOOT_SEED,B=50000):
    import numpy as np
    x=np.asarray(x,dtype=np.float64); gen=np.random.default_rng(seed)
    vals=[]
    for _ in range((B+4999)//5000):
        z=gen.integers(0,len(x),size=(min(5000,B-5000*len(vals)),len(x)))
        vals.append(x[z].mean(axis=1))
    arr=np.concatenate(vals)
    return [float(np.quantile(arr,.025)),float(np.quantile(arr,.975))]

def aggregate(rows):
    import numpy as np
    per=[]
    all_acc=[];all_sens=[];noise=[];negative_sens=0;saturated=0
    for r in rows:
        es={};raw={};free={};aggs={}
        for order in ORDERS:
            b=r['orders'][order]
            all_acc.append(b['baseline']['acc'])
            all_sens.append(b['baseline']['sens'])
            noise.append(abs(b['baseline']['D']-b['baseline_repeat']['D']))
            negative_sens+=int(b['baseline']['IL']<=0 or b['baseline']['IR']<=0)
            saturated+=int(abs(b['baseline']['D'])>=.95)
            for c in CARRIERS:
                cc=c[0];block=b['carriers'][cc]
                e=[block[f'm{m}']['LEFT']['D']-block[f'm{m}']['RIGHT']['D'] for m in (0,1)]
                j=[block[f'm{m}']['LEFT']['J']-block[f'm{m}']['RIGHT']['J'] for m in (0,1)]
                es[f'{order}_{cc}']=sum(e)/2
                raw[f'{order}_{cc}']=sum(j)/2
                free[f'{order}_{cc}']=(block['free0']['D']-block['free1']['D'])
        per.append({'idx':r['idx'],'primary':float(np.mean(list(es.values()))),
                    'carrier':{c[0]:float(np.mean([es[o+'_'+c[0]] for o in ORDERS])) for c in CARRIERS},
                    'order':{o:float(np.mean([es[o+'_'+c[0]] for c in CARRIERS])) for o in ORDERS},
                    'cells':es,'rawJ':float(np.mean(list(raw.values()))),'free':float(np.mean(list(free.values())))})
    x=np.asarray([f['primary'] for f in per],float)
    ci=bootstrap_mean(x)
    pos=int(np.sum(x>0));neg=int(np.sum(x<0));zero=len(x)-pos-neg
    vals=np.asarray(all_acc,float)
    means={c[0]:float(np.mean([p['carrier'][c[0]] for p in per])) for c in CARRIERS}
    orders={o:float(np.mean([p['order'][o] for p in per])) for o in ORDERS}
    fmean=float(np.mean([p['free'] for p in per]));rawmean=float(np.mean([p['rawJ'] for p in per]))
    pval=exact_two_sided(pos,neg)
    ok=(vals.mean()>=VAL_ACC_MIN and all(float(np.mean([r['orders'][o]['baseline']['acc'] for r in rows]))>=VAL_ACC_MIN for o in ORDERS) and max(noise)<1e-4)
    positive=bool(x.mean()>0 and ci[0]>0 and pval<.05
                  and all(z>0 for z in means.values()) and all(z>0 for z in orders.values()))
    verdict='PRIMARY_CONFIRMED' if positive else 'PRIMARY_NOT_CONFIRMED'
    if not ok:verdict='INVALID_VALIDATION_CAPABILITY_OR_NUMERICAL_FLOOR'
    return {'n':len(rows),'primary_mean':float(x.mean()),'ci95':ci,'positive':pos,'negative':neg,
            'zero':zero,'exact_sign_p':pval,'carrier_means':means,
            'order_means':orders,'raw_J_mean':rawmean,
            'free_AminusB_like_raw_carrier_mean':fmean,
            'accuracy':float(vals.mean()),'mean_sensitivity':float(np.mean(all_sens)),
            'negative_or_zero_intervention_count':negative_sens,'saturated_baseline_count':saturated,
            'numerical_repeat_abs_max':max(noise),'primary_verdict':verdict,
            'estimand':'mean of per-family [mapping-reversed report-meaning D contrast, averaged across 3 carriers and 2 passage orders]',
            'exploratory_notes':'Free controls and raw J are diagnostics, not additions to primary test.'}

def main():
    t0=time.monotonic(); p=argparse.ArgumentParser()
    p.add_argument('mode',choices=['preflight','execute']);args=p.parse_args()
    from huggingface_hub import model_info,dataset_info
    from datasets import load_dataset
    mi=model_info(MODEL);di=dataset_info(DATASET)
    if mi.sha!=MODEL_SHA or di.sha!=DATASET_SHA:
        raise RuntimeError('PINNED_REVISION_DISAGREES_WITH_LIVE_MAIN')
    old=parent_module()
    train=load_dataset(DATASET,split='train',revision=DATASET_SHA)
    valid=load_dataset(DATASET,split='validation',revision=DATASET_SHA)
    cal,families,manifest,meta=draw(train,valid,old)
    actual_manifest=h(manifest)
    emit('MPW102_PREVALIDATION',{'mode':args.mode,'model_sha':mi.sha,'dataset_sha':di.sha,
         'parent_sha':PARENT_HASH,'parent_manifest':PARENT_MANIFEST,
         'new_manifest_sha256':actual_manifest,'cal_n':len(cal),'val_n':len(families),
         'passages':meta,'carriers':[c[0] for c in CARRIERS],
         'orders':ORDERS,'script_sha256':h(Path(__file__).read_bytes()),
         'utc_time':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
    if args.mode=='preflight':
        from transformers import AutoTokenizer
        pre_tok=AutoTokenizer.from_pretrained(MODEL,revision=MODEL_SHA,trust_remote_code=True)
        required=('positive','negative')+tuple(z for c in CARRIERS for z in c[1:])
        token_map={z:pre_tok.encode(z,add_special_tokens=False) for z in required}
        atomic=all(len(t)==1 for t in token_map.values())
        emit('MPW102_PREFLIGHT_TOKEN_CHECK',{'tokens':token_map,'atomic':atomic})
        if not atomic: raise RuntimeError('CARRIER_TOKEN_PREFLIGHT_FAILED')
        emit('MPW102_PREFLIGHT_COMPLETED',{'manifest_sha256':actual_manifest,
             'warning':'NO_MODEL_INFERENCE_PERFORMED; this result is not confirmatory'})
        return
    if EXPECTED_MANIFEST_SHA=='UNSET_PREFLIGHT_REQUIRED' or actual_manifest!=EXPECTED_MANIFEST_SHA:
        raise RuntimeError('FROZEN_MANIFEST_HASH_REQUIRED_OR_MISMATCHED')
    import torch,transformers,numpy as np
    from transformers import AutoTokenizer,AutoModelForCausalLM
    tok=AutoTokenizer.from_pretrained(MODEL,revision=MODEL_SHA,trust_remote_code=True)
    tok.padding_side='left';tok.pad_token=tok.pad_token or tok.eos_token
    tokens=('positive','negative')+tuple(z for c in CARRIERS for z in c[1:])
    ids={z:tok.encode(z,add_special_tokens=False) for z in tokens}
    emit('MPW102_TOKEN_PREFLIGHT',{'token_ids':ids,'all_single_token':all(len(i)==1 for i in ids.values())})
    if not all(len(i)==1 for i in ids.values()):
        emit('MPW102_ABORT',{'reason':'NON_ATOMIC_REPORT_CODES','no_validation':True});return
    ids={z:v[0] for z,v in ids.items()}
    model=AutoModelForCausalLM.from_pretrained(MODEL,revision=MODEL_SHA,
        trust_remote_code=True,torch_dtype=torch.float16,device_map='auto',low_cpu_mem_usage=True)
    model.eval()
    if not torch.cuda.is_available():raise RuntimeError('L4_GPU_REQUIRED')
    emit('MPW102_HARDWARE',{'torch':torch.__version__,'transformers':transformers.__version__,
         'cuda':torch.version.cuda,'gpu':torch.cuda.get_device_name(0),'dtype':'float16',
         'max_seconds':MAX_SECONDS})

    def logit_matrix(messages):
        texts=[tok.apply_chat_template(m,tokenize=False,add_generation_prompt=True) for m in messages]
        out=[]
        for k in range(0,len(texts),12):
            b=tok(texts[k:k+12],return_tensors='pt',padding=True,
                  truncation=True,max_length=1536,add_special_tokens=False).to(model.device)
            with torch.inference_mode():
                l=model(**b,use_cache=False).logits[:,-1,:].float().cpu()
            out.append(l)
        return torch.cat(out,dim=0)

    def case(f,order,l,r):
        s=f'LEFT: {l}\nRIGHT: {r}' if order=='LR' else f'RIGHT: {r}\nLEFT: {l}'
        return {'role':'user','content':'Case\n'+s+'\nAnswer exactly positive or negative.'}

    def audit(f,order,pre):
        L=logit_matrix([pre+[case(f,order,f['left'],f['right'])],
                        pre+[case(f,order,f['flip_left'],f['right'])],
                        pre+[case(f,order,f['left'],f['flip_right'])]])
        good=ids['positive'] if f['label']==1 else ids['negative']
        bad=ids['negative'] if f['label']==1 else ids['positive']
        m=(L[:,good]-L[:,bad]).numpy()
        il=float(m[0]-m[1]);ir=float(m[0]-m[2]);sens=abs(il)+abs(ir)
        guess=int(float(L[0,ids['positive']])>=float(L[0,ids['negative']]))
        return {'D':float((il-ir)/(sens+EPS)),'J':float(il-ir),
                'IL':il,'IR':ir,'sens':sens,'acc':int(guess==f['label'])}

    base=old.BASE
    def observe(f,all_controls=True):
        out={'idx':f['idx'],'case_sha256':h(stable(f)),'label':f['label'],'orders':{}}
        for order in ORDERS:
            b=audit(f,order,base)
            floor=audit(f,order,base)
            obj={'baseline':b,'baseline_repeat':floor,'carriers':{}}
            if all_controls:
                obj['neutral_ack']=audit(f,order,prefix(base,NEUTRAL_Q,'Understood.'))
                obj['label_ack']=audit(f,order,prefix(base,LABEL_Q,'Understood.'))
            for c in CARRIERS:
                name,c0,c1=c;block={}
                for m in (0,1):
                    q,code_map=question(f,c,m)
                    code_left=c0 if code_map[c0]=='LEFT' else c1
                    code_right=c1 if code_left==c0 else c0
                    block[f'm{m}']={'LEFT':audit(f,order,prefix(base,q,code_left)),
                                    'RIGHT':audit(f,order,prefix(base,q,code_right))}
                if all_controls:
                    qf=free_question(f,c)
                    block['free0']=audit(f,order,prefix(base,qf,c0))
                    block['free1']=audit(f,order,prefix(base,qf,c1))
                obj['carriers'][name]=block
            out['orders'][order]=obj
        return out

    cal_audits=[audit(f,o,base) for f in cal for o in ORDERS]
    cal_acc=float(np.mean([x['acc'] for x in cal_audits]))
    cal_sens=float(np.mean([x['sens'] for x in cal_audits]))
    emit('MPW102_CALIBRATION',{'cal_n':CAL_N,'orders':ORDERS,'accuracy':cal_acc,
         'sensitivity':cal_sens,'gate':cal_acc>=CAL_ACC_MIN and cal_sens>=CAL_SENS_MIN,
         'accuracy_by_order':{o:float(np.mean([audit(f,o,base)['acc'] for f in cal])) for o in ORDERS}})
    if cal_acc<CAL_ACC_MIN or cal_sens<CAL_SENS_MIN:
        emit('MPW102_ABORT',{'reason':'CAPABILITY_GATE_FAIL','no_validation':True});return
    sample=[];start=time.monotonic()
    for f in cal[:4]:sample.append(observe(f,all_controls=True))
    speed=(time.monotonic()-start)/4
    projected=(time.monotonic()-t0)+speed*VAL_N*1.3
    emit('MPW102_TIMING',{'calibration_only':True,'seconds_per_family':speed,
         'projected_total_sec':projected,'max_seconds':MAX_SECONDS})
    if projected>MAX_SECONDS-180:
        emit('MPW102_ABORT',{'reason':'RUNTIME_BUDGET_GATE_FAIL','no_validation':True});return
    emit('MPW102_VALIDATION_BEGIN',{'n':len(families),'manifest_sha256':actual_manifest})
    rows=[]
    for i,f in enumerate(families):
        if time.monotonic()-t0>MAX_SECONDS-120:
            emit('MPW102_ABORT',{'reason':'RUNTIME_EXCEEDED','completed':i});return
        row=observe(f); rows.append(row)
        if (i+1)%32==0:
            emit('MPW102_PROGRESS',{'completed':i+1,'n':len(families),
                                    'elapsed_seconds':time.monotonic()-t0})
    raw=('\n'.join(stable(x) for x in rows)+'\n').encode()
    for i in range(0,len(rows),64):
        shard=('\n'.join(stable(x) for x in rows[i:i+64])+'\n').encode()
        chunks('MPW102_RECORD_SHARD_B64',shard)
        emit('MPW102_SHARD_HASH',{'part':i//64,'range':[i,i+len(rows[i:i+64])-1],
                                 'sha256':h(shard),'n':len(rows[i:i+64])})
    result=aggregate(rows)
    emit('MPW102_PRIMARY_RESULT',result)
    emit('MPW102_END',{'status':'COMPLETED','verdict':result['primary_verdict'],
                        'n':len(rows),'raw_sha256':h(raw),
                        'manifest_sha256':actual_manifest,
                        'elapsed_seconds':time.monotonic()-t0})

if __name__=='__main__':main()