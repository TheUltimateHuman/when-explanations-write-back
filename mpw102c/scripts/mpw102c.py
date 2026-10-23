# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = [
# "torch==2.6.0","transformers==4.57.3","accelerate==1.6.0",
# "datasets==3.6.0","huggingface_hub==0.36.0",
# "numpy==2.1.3","scipy==1.15.3","sentencepiece==0.2.0"
# ]
# ///
"""MPW-102C: fresh two-architecture transport and person-matched specificity.
Design and two-model panel fixed in PROTOCOL.md before any preflight or
validation outcome. The final frozen script must pin model revisions and
fresh case manifest before the execute mode can be invoked.
"""
import sys,re,json,random,hashlib,base64,gzip,time,tempfile,importlib.util
from pathlib import Path
from urllib.request import urlopen
from collections import Counter

DATASET='stanfordnlp/sst2'
DATASET_SHA='8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb'
PARENT_URL='https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/817a15118286553bb1758d8f4d47803ae06a9147/mpw102/scripts/mpw102.py'
PARENT_SHA='36f2125299ac918db044359e9e8ebebe4c1e5b20029ec19e48a3cfe2f7e39118'
PARENT_MANIFEST='90ac38a668c6fa03ebdd1a37f294dc7280b24533b5d5caacbd8ed034f54549c5'
PREVIOUS_B_URL='https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/f56a74626df150c382c565c268c403762ca487d6/mpw102b/scripts/mpw102b.py'
PREVIOUS_B_SHA='13ee183820c3e870a7566c3727593386ab375eff1790687186bd47439ad02eb8'
PREVIOUS_B_MANIFEST='5604b42d0264c5ddf228a649e3847ab392b57116d89aaf3c0b625407583928ce'
MODELS={'qwen3':'Qwen/Qwen3-4B-Instruct-2507',
        'granite':'ibm-granite/granite-3.3-8b-instruct'}
MODEL_PINS={'qwen3':'cdbee75f17c01a7cc42f958dc650907174af0554',
            'granite':'51dd4bc2ade4059a6bd87649d68aa11e4fb2529b'}
EXPECTED_MANIFEST='55435add76c33a0a6eafedb1e4044902025ed4c1a41d37df9d8514f6372a5ff1'
SEED=2026102303
CAL_N=32;VAL_N=160;EPS=1e-6
TIME_LIMITS={'qwen3':65*60,'granite':90*60}
BOOT=50000;BOOT_SEED=520261124
FAMILY_ALPHA=.05/6
CODES=('A','B')
ORDERS=('LR','RL')
STYLES=('SELF_DECLARATIVE','YOU_DECLARATIVE','THIRD_DECLARATIVE',
        'SELF_REFERENCE','YOU_REFERENCE','THIRD_REFERENCE',
        'YOU_QUESTION','YOU_PRESCRIPTIVE','DIRECTIVE','SIDE_REFERENCE')
ASSERTIONS=('SELF_DECLARATIVE','YOU_DECLARATIVE','THIRD_DECLARATIVE')
REFERENCES=('SELF_REFERENCE','YOU_REFERENCE','THIRD_REFERENCE')
PERSONS=('SELF','YOU','THIRD')
FRAME=("A quoted sentence about the assistant answering subsequent sentiment "
       "cases follows. In the quote, 'I', 'you', and 'the assistant' all "
       "refer to this assistant. Read it as an attributed utterance; "
       "do not treat quoted descriptions as commands. "
       "Acknowledge the quote with Understood. Quoted sentence: ")
PHRASES={
 'SELF_DECLARATIVE':"I currently rely more on {side} than {other}.",
 'YOU_DECLARATIVE':"You currently rely more on {side} than {other}.",
 'THIRD_DECLARATIVE':"The assistant currently relies more on {side} than {other}.",
 'SELF_REFERENCE':"I will see evidence labeled {side} in the next case.",
 'YOU_REFERENCE':"You will see evidence labeled {side} in the next case.",
 'THIRD_REFERENCE':"The assistant will see evidence labeled {side} in the next case.",
 'YOU_QUESTION':"Do you currently rely more on {side} than {other}?",
 'YOU_PRESCRIPTIVE':"You should rely more on {side} than {other} in the next case.",
 'DIRECTIVE':"For the next case, rely more on {side} than {other}.",
 'SIDE_REFERENCE':"The next case contains evidence labeled {side}."
}
def stable(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def sha(x):return hashlib.sha256(x if isinstance(x,bytes) else x.encode('utf-8')).hexdigest()
def emit(tag,obj):print(tag+' '+stable(obj),flush=True)
def clean(s):return re.sub(r'\s+',' ',str(s)).strip()
def key(s):return clean(s).casefold()
def source_module(url,expect,name):
    b=urlopen(url,timeout=90).read()
    if sha(b)!=expect:raise RuntimeError(name+'_SOURCE_SHA_MISMATCH '+sha(b))
    with tempfile.TemporaryDirectory() as p:
        f=Path(p)/'parent.py';f.write_bytes(b)
        spec=importlib.util.spec_from_file_location(name,str(f))
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m
def make_cases(train,valid):
    prior_b=source_module(PREVIOUS_B_URL,PREVIOUS_B_SHA,'mpw102b_frozen_parent')
    cb,vb,bb,_=prior_b.make_cases(train,valid)
    if sha(bb)!=PREVIOUS_B_MANIFEST:raise RuntimeError('PREVIOUS_B_MANIFEST_HASH_MISMATCH')
    old=source_module(PARENT_URL,PARENT_SHA,'mpw102_frozen_parent')
    prev101=old.parent_module()
    c101,v101,b101,_=prev101.sampled_families(train,valid)
    if sha(b101)!=old.PARENT_MANIFEST:raise RuntimeError('PARENT101_SAMPLE_HASH_MISMATCH')
    c102,v102,b102,_=old.draw(train,valid,prev101)
    if sha(b102)!=PARENT_MANIFEST:raise RuntimeError('PARENT102_SAMPLE_HASH_MISMATCH')
    excluded={key(f[k]) for f in c101+v101+c102+v102+cb+vb
               for k in ('left','right','flip_left','flip_right')}
    excluded.update(key(x['sentence']) for x in valid)
    first={0:[],1:[]}
    for x in train:
        if x['label'] in (0,1):
            s=clean(x['sentence'])
            if 4<=len(s.split())<=36:first[int(x['label'])].append(s)
    rr=random.Random(prev101.ORIGINAL_PR002_SEED)
    for label in (0,1):rr.shuffle(first[label])
    excluded.update(key(s) for y in (0,1) for s in first[y][:48])
    before=len(excluded)
    seen=set(excluded);pools={0:[],1:[]}
    for x in train:
        y=x['label']
        if y not in (0,1):continue
        t=clean(x['sentence']);k=key(t)
        if 4<=len(t.split())<=36 and k not in seen:
            pools[int(y)].append(t);seen.add(k)
    rng=random.Random(SEED)
    for y in (0,1):rng.shuffle(pools[y])
    minimum=2*(CAL_N+VAL_N)
    if any(len(pools[y])<minimum for y in (0,1)):raise RuntimeError('TOO_FEW_DISJOINT_PASSAGES')
    ix={0:0,1:0}
    def take(y):
        v=pools[y][ix[y]];ix[y]+=1;return v
    def batch(n,start):
        labels=[0,1]*(n//2);rng.shuffle(labels);out=[]
        for j,y in enumerate(labels):
            a,b=take(y),take(y);c,d=take(1-y),take(1-y)
            out.append({'idx':start+j,'label':y,'left':a,'right':b,
                        'flip_left':c,'flip_right':d,'code_orders':{'AB':rng.choice((0,1))}})
        return out
    cal=batch(CAL_N,0);val=batch(VAL_N,CAL_N)
    samples=[key(f[z]) for f in cal+val for z in ('left','right','flip_left','flip_right')]
    if len(samples)!=len(set(samples)) or set(samples)&excluded:raise RuntimeError('TEXT_CONTAMINATION')
    manifest=stable(cal+val).encode()
    return cal,val,manifest,{'excluded':before,'previous101_families':len(c101+v101),
        'previous102_families':len(c102+v102),'previous102b_families':len(cb+vb),'distinct_passages':len(samples),
        'pools':{str(y):len(pools[y]) for y in (0,1)},'disjoint_from_prior':True}
def user_prefix(base,statement):
    return base+[{'role':'user','content':statement},{'role':'assistant','content':'Understood.'}]
def authored(style,side):
    other='RIGHT' if side=='LEFT' else 'LEFT'
    return FRAME+'"'+PHRASES[style].format(side=side,other=other)+'"'
def case_text(f,order,a,b):
    s=f"LEFT: {a}\nRIGHT: {b}" if order=='LR' else f"RIGHT: {b}\nLEFT: {a}"
    return {'role':'user','content':'Case\n'+s+'\nAnswer exactly positive or negative.'}
def build_prefixes(f,old,base):
    p={'baseline':base,'baseline_repeat':base,
       'neutral_ack':user_prefix(base,old.NEUTRAL_Q),
       'label_ack':user_prefix(base,old.LABEL_Q)}
    for m in (0,1):
        q,mapping=old.question(f,('AB','A','B'),m)
        left=next(z for z in CODES if mapping[z]=='LEFT')
        right=next(z for z in CODES if mapping[z]=='RIGHT')
        p[f'ab_m{m}_LEFT']=old.prefix(base,q,left)
        p[f'ab_m{m}_RIGHT']=old.prefix(base,q,right)
    for st in STYLES:
        for side in ('LEFT','RIGHT'):
            p[st+'_'+side]=user_prefix(base,authored(st,side))
    return p
def stat_vec(x,seed):
    import numpy as np
    from scipy.stats import binomtest
    a=np.asarray(x,float)
    if not np.all(np.isfinite(a)):raise RuntimeError('NONFINITE_TEST_VALUES')
    if a.shape!=(VAL_N,):raise RuntimeError('BAD_TEST_SHAPE')
    rng=np.random.default_rng(seed);means=[]
    for j in range(0,BOOT,2500):
        ix=rng.integers(0,len(a),size=(min(2500,BOOT-j),len(a)))
        means.append(a[ix].mean(axis=1))
    bs=np.concatenate(means)
    positive=int((a>0).sum());negative=int((a<0).sum())
    return {'mean':float(a.mean()),'median':float(np.median(a)),
      'ci95':[float(v) for v in np.quantile(bs,[.025,.975])],
      'ci_familywise':[float(v) for v in np.quantile(bs,[FAMILY_ALPHA/2,1-FAMILY_ALPHA/2])],
      'positive':positive,'negative':negative,'zero':len(a)-positive-negative,
      'sign_p':float(binomtest(positive,positive+negative,.5).pvalue) if positive+negative else 1.0}
def aggregate(rows,which):
    import numpy as np
    if len(rows)!=VAL_N or set(r['idx'] for r in rows)!=set(range(CAL_N,CAL_N+VAL_N)):
        raise RuntimeError('INCOMPLETE_VALIDATION')
    h1=[];h2=[];h3=[]
    style_by_case={z:[] for z in STYLES}
    order_effects={h:{o:[] for o in ORDERS} for h in ('H1','H2','H3')}
    controls={};accuracy={o:[] for o in ORDERS}
    sensitivity=[];numeric=[];rawJ=[];sat=0;nonpositive=0
    for record in rows:
        this={k:[] for k in STYLES}
        ab=[]
        for order in ORDERS:
            obs=record['orders'][order];base=obs['baseline']
            accuracy[order].append(int(base['acc']))
            sensitivity.append(base['sens'])
            numeric.append(abs(base['D']-obs['baseline_repeat']['D']))
            sat+=int(abs(base['D'])>=.95)
            nonpositive+=int(base['I_left']<=0 or base['I_right']<=0)
            for control in ('neutral_ack','label_ack'):
                controls.setdefault(order+'_'+control,[]).append(obs[control]['D']-base['D'])
            ab_e=float(np.mean([obs['ab_m'+str(m)+'_LEFT']['D']-obs['ab_m'+str(m)+'_RIGHT']['D']
                                for m in (0,1)]))
            ab_j=float(np.mean([obs['ab_m'+str(m)+'_LEFT']['J']-obs['ab_m'+str(m)+'_RIGHT']['J']
                                for m in (0,1)]))
            ab.append(ab_e);rawJ.append(ab_j)
            for style in STYLES:
                this[style].append(obs[style+'_LEFT']['D']-obs[style+'_RIGHT']['D'])
            per_p=[this[p+'_DECLARATIVE'][-1]-this[p+'_REFERENCE'][-1] for p in PERSONS]
            order_effects['H1'][order].append(ab_e)
            order_effects['H2'][order].append(float(np.mean(per_p)))
            order_effects['H3'][order].append(per_p[0]-per_p[1])
        h1.append(float(np.mean(ab)))
        means={style:float(np.mean(this[style])) for style in STYLES}
        for style in STYLES:style_by_case[style].append(means[style])
        diff=[means[p+'_DECLARATIVE']-means[p+'_REFERENCE'] for p in PERSONS]
        h2.append(float(np.mean(diff)))
        h3.append(diff[0]-diff[1])
    estimates={}
    for k,i,x in (('H1',1,h1),('H2',2,h2),('H3',3,h3)):
        estimates[k]=stat_vec(x,BOOT_SEED+i)
    per_order={h:{o:float(np.mean(v)) for o,v in order_effects[h].items()} for h in ('H1','H2','H3')}
    val_acc={o:float(np.mean(v)) for o,v in accuracy.items()}
    valid=all(v>=.90 for v in val_acc.values()) and max(numeric)<1e-4
    passh={h:bool(valid and estimates[h]['mean']>0 and
                  estimates[h]['ci_familywise'][0]>0 and
                  estimates[h]['sign_p']<FAMILY_ALPHA and
                  all(v>0 for v in per_order[h].values()))
           for h in ('H1','H2','H3')}
    means={s:float(np.mean(v)) for s,v in style_by_case.items()}
    return {'model':which,'n':len(rows),'validation_accuracy':val_acc,
      'mean_sensitivity':float(np.mean(sensitivity)),'numeric_floor_max':float(max(numeric)),
      'nonpositive_interventions':nonpositive,'saturated_baselines':sat,
      'H1':estimates['H1'],'H2':estimates['H2'],'H3':estimates['H3'],
      'order_effects':per_order,
      'frame_means':means,
      'person_matched_means':{p:means[p+'_DECLARATIVE']-means[p+'_REFERENCE'] for p in PERSONS},
      'raw_J_AB':float(np.mean(rawJ)),
      'ack_means':{k:float(np.mean(v)) for k,v in controls.items()},
      'valid':bool(valid),
      'verdicts':{h:('CONFIRMED' if passh[h] else ('INVALID' if not valid else 'NOT_CONFIRMED'))
                  for h in ('H1','H2','H3')},
      'joint_per_model':bool(all(passh.values()))}
def compressed_chunks(tag,raw,maxpart=10000):
    z=base64.b64encode(gzip.compress(raw,compresslevel=9,mtime=0)).decode()
    for n in range(0,len(z),maxpart):
        emit(tag,{'part':n//maxpart,'total':(len(z)+maxpart-1)//maxpart,
                  'sha256':sha(raw),'data':z[n:n+maxpart]})
def main():
    import argparse
    t0=time.monotonic()
    ap=argparse.ArgumentParser()
    ap.add_argument('mode',choices=('preflight','execute'))
    ap.add_argument('--model',choices=tuple(MODELS.keys()),default='qwen3')
    opt=ap.parse_args()
    from datasets import load_dataset
    from huggingface_hub import model_info,dataset_info
    from transformers import AutoTokenizer
    revisions={label:model_info(repo).sha for label,repo in MODELS.items()}
    if dataset_info(DATASET).sha!=DATASET_SHA:raise RuntimeError('PINNED_DATASET_NOT_CURRENT')
    old=source_module(PARENT_URL,PARENT_SHA,'mpw102_prior')
    train=load_dataset(DATASET,split='train',revision=DATASET_SHA)
    valid=load_dataset(DATASET,split='validation',revision=DATASET_SHA)
    cal,validation,manifest,meta=make_cases(train,valid)
    manifest_sha=sha(manifest)
    emit('MPW102C_PREVALIDATION',{'mode':opt.mode,'model':opt.model,'revisions':revisions,
      'model_pins':MODEL_PINS,'manifest_sha256':manifest_sha,
      'prior_manifest_sha256':PARENT_MANIFEST,
      'case_meta':meta,'source_sha256':sha(Path(__file__).read_bytes()),
      'cal_n':len(cal),'val_n':len(validation)})
    if opt.mode=='execute':
        if EXPECTED_MANIFEST=='UNSET' or manifest_sha!=EXPECTED_MANIFEST:
            raise RuntimeError('MANIFEST_NOT_PROSPECTIVELY_FROZEN')
        if any(MODEL_PINS[z]=='UNSET' or MODEL_PINS[z]!=revisions[z] for z in MODELS):
            raise RuntimeError('MODEL_REVISIONS_NOT_PROSPECTIVELY_FROZEN')
    if opt.mode=='preflight':
        for mid,repo in MODELS.items():
            tok=AutoTokenizer.from_pretrained(repo,revision=revisions[mid],trust_remote_code=True)
            ids={x:tok.encode(x,add_special_tokens=False) for x in ('positive','negative','A','B')}
            emit('MPW102C_TOKEN_PREFLIGHT',{'model':mid,'ids':ids,'atomic':all(len(v)==1 for v in ids.values())})
        emit('MPW102C_CPU_PREFLIGHT_END',{'status':'COMPLETED_NO_INFERENCE','manifest_sha256':manifest_sha})
        return
    import torch, numpy as np, transformers
    mid=opt.model;repo=MODELS[mid];max_seconds=TIME_LIMITS[mid]
    tok=AutoTokenizer.from_pretrained(repo,revision=MODEL_PINS[mid],trust_remote_code=True)
    tok.padding_side='left';tok.pad_token=tok.pad_token or tok.eos_token
    ids={x:tok.encode(x,add_special_tokens=False) for x in ('positive','negative','A','B')}
    if not all(len(v)==1 for v in ids.values()):
        emit('MPW102C_ABORT',{'reason':'NON_ATOMIC_TOKENS','model':mid,'no_validation':True});return
    ids={x:v[0] for x,v in ids.items()}
    if not torch.cuda.is_available():
        emit('MPW102C_ABORT',{'reason':'NO_CUDA','model':mid,'no_validation':True});return
    model=transformers.AutoModelForCausalLM.from_pretrained(repo,revision=MODEL_PINS[mid],
       trust_remote_code=True,torch_dtype=torch.float16,device_map='auto',low_cpu_mem_usage=True,
       attn_implementation='sdpa')
    model.eval()
    emit('MPW102C_HARDWARE',{'model':mid,'gpu':torch.cuda.get_device_name(0),
      'torch':torch.__version__,'transformers':transformers.__version__,
      'batch_size':8 if mid=='qwen3' else 8,'dtype':'float16'})
    batch_size=8 if mid=='qwen3' else 8
    base=old.parent_module().BASE
    good_label=ids['positive'];bad_label=ids['negative']
    def score_logit_margin(msgsets,label):
        vals=[]
        for k in range(0,len(msgsets),batch_size):
            rendered=[tok.apply_chat_template(m,tokenize=False,add_generation_prompt=True) for m in msgsets[k:k+batch_size]]
            enc=tok(rendered,return_tensors='pt',padding=True,add_special_tokens=False,truncation=False)
            if int(enc.attention_mask.sum(dim=1).max().item())>768:
                raise RuntimeError('UNDECLARED_INPUT_TRUNCATION_REQUIRED')
            enc=enc.to(model.device)
            with torch.inference_mode():
                y=model(**enc,use_cache=False).logits[:,-1,:].float()
                margins=(y[:,good_label]-y[:,bad_label]).cpu().numpy()
            vals.extend(float(z) for z in margins)
        # normalized across sentiment polarity to a correct-vs-alternative margin
        return [x if label==1 else -x for x in vals]
    def evaluate(f,all_conditions=True):
        prefix=build_prefixes(f,old,base) if all_conditions else {'baseline':base,'baseline_repeat':base}
        report={'idx':f['idx'],'case_sha256':sha(stable(f)),'orders':{}}
        for order in ORDERS:
            sets=[];names=list(prefix)
            for name in names:
                pre=prefix[name]
                for l,r in ((f['left'],f['right']),(f['flip_left'],f['right']),(f['left'],f['flip_right'])):
                    sets.append(pre+[case_text(f,order,l,r)])
            margins=score_logit_margin(sets,f['label'])
            d={}
            for j,name in enumerate(names):
                a,b,c=margins[3*j:3*j+3]; il=a-b;ir=a-c
                sensitivity=abs(il)+abs(ir)
                d[name]={'D':float((il-ir)/(sensitivity+EPS)),'J':float(il-ir),
                    'I_left':float(il),'I_right':float(ir),'sens':float(sensitivity),
                    'acc':int(a>=0)} # accuracy by constrained next-token margin
            report['orders'][order]=d
        return report
    ca=[evaluate(f,all_conditions=False) for f in cal]
    acc={o:sum(r['orders'][o]['baseline']['acc'] for r in ca)/CAL_N for o in ORDERS}
    sensitivity=sum(r['orders'][o]['baseline']['sens'] for r in ca for o in ORDERS)/(2*CAL_N)
    eligibility=all(x>=.90 for x in acc.values()) and sensitivity>=1.0
    emit('MPW102C_CALIBRATION',{'model':mid,'n':CAL_N,'accuracy_by_order':acc,
       'sensitivity':sensitivity,'eligible':eligibility})
    if not eligibility:
        emit('MPW102C_END',{'status':'CAPABILITY_GATE_FAIL','model':mid,'no_validation':True});return
    start=time.monotonic();[evaluate(f,all_conditions=True) for f in cal[:4]]
    sec=(time.monotonic()-start)/4
    projected=(time.monotonic()-t0)+VAL_N*sec*1.35
    emit('MPW102C_TIMING',{'model':mid,'sec_per_family':sec,
        'projected_total_sec':projected,'max_sec':max_seconds})
    if projected>max_seconds-180:
        emit('MPW102C_END',{'status':'RUNTIME_GATE_FAIL','model':mid,'no_validation':True});return
    emit('MPW102C_VALIDATION_START',{'model':mid,'n':VAL_N,'manifest_sha256':manifest_sha})
    rows=[]
    for i,f in enumerate(validation):
        if time.monotonic()-t0>max_seconds-120:
            emit('MPW102C_END',{'status':'RUNTIME_ABORT','completed':i,'model':mid});return
        r=evaluate(f,all_conditions=True)
        if not all(np.isfinite(a['D']) and np.isfinite(a['J'])
                   for oo in r['orders'].values() for a in oo.values()):
            emit('MPW102C_END',{'status':'NONFINITE_INVALID','family_idx':r['idx'],'model':mid});return
        rows.append(r)
        if (i+1)%24==0:
            emit('MPW102C_PROGRESS',{'completed':i+1,'total':VAL_N,
                                     'model':mid,'elapsed_sec':time.monotonic()-t0})
    raw=('\n'.join(stable(x) for x in rows)+'\n').encode()
    for z in range(0,VAL_N,40):
        s=('\n'.join(stable(x) for x in rows[z:z+40])+'\n').encode()
        compressed_chunks('MPW102C_SHARD_B64',s)
        emit('MPW102C_SHARD',{'model':mid,'part':z//40,'n':40,'sha256':sha(s),
                               'range':[z,z+39]})
    result=aggregate(rows,mid)
    emit('MPW102C_PRIMARY_RESULT',result)
    emit('MPW102C_END',{'status':'COMPLETED','model':mid,'raw_sha256':sha(raw),
       'n':len(rows),'manifest_sha256':manifest_sha,
       'elapsed_sec':time.monotonic()-t0,'verdicts':result['verdicts']})
if __name__=='__main__':main()
