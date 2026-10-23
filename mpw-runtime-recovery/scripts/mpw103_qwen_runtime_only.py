# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = [
# "torch==2.6.0","transformers==4.57.3","accelerate==1.6.0",
# "datasets==3.6.0","huggingface_hub==0.36.0",
# "numpy==2.1.3","scipy==1.15.3","sentencepiece==0.2.0"
# ]
# ///
"""MPW-103 Phase A: prospective sequential, fixed-final report history.
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
PREVIOUS_C_URL='https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/b02449a43edbdc4332d893d69a269f954e3d1e42/mpw102c/scripts/mpw102c.py'
PREVIOUS_C_SHA='a6951dfa98ca00ddf02e50bf09798b09d38ff3845cfaff3583ce3948f0ec8b6a'
PREVIOUS_C_MANIFEST='55435add76c33a0a6eafedb1e4044902025ed4c1a41d37df9d8514f6372a5ff1'
PREVIOUS_B_URL='https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/f56a74626df150c382c565c268c403762ca487d6/mpw102b/scripts/mpw102b.py'
PREVIOUS_B_SHA='13ee183820c3e870a7566c3727593386ab375eff1790687186bd47439ad02eb8'
PREVIOUS_B_MANIFEST='5604b42d0264c5ddf228a649e3847ab392b57116d89aaf3c0b625407583928ce'
MODELS={'qwen3':'Qwen/Qwen3-4B-Instruct-2507',
        'granite':'ibm-granite/granite-3.3-8b-instruct'}
MODEL_PINS={'qwen3':'cdbee75f17c01a7cc42f958dc650907174af0554',
            'granite':'51dd4bc2ade4059a6bd87649d68aa11e4fb2529b'}
EXPECTED_MANIFEST='370a225c22762ba97f4bac87692a9ff6cab032713d467f6a040ebcfd96d4f08b'
SEED=2026102304
CAL_N=32;VAL_N=128;EPS=1e-6
TIME_LIMITS={'qwen3':95*60,'granite':90*60}
BOOT=50000;BOOT_SEED=520261025
FAMILY_ALPHA=.05/8
TOKEN_HARD_CAP=1024
CODES=('A','B')
ORDERS=('LR','RL')
REPORT_QUESTION='Before the next cases, report which labeled passage you currently rely on more. {decl}. Answer exactly A or B.'
FREE_QUESTION='Before the next cases, select a formatting code unrelated to passage reliance. A and B are arbitrary. Answer exactly A or B.'
HISTORY_NAMES=('LAST_ONLY','PREV_1_LEFT','PREV_1_RIGHT','PREV_3_LEFT','PREV_3_RIGHT',
               'PREV_7_LEFT','PREV_7_RIGHT','BALANCED_LATE_LEFT','BALANCED_EARLY_LEFT',
               'FREE_PREV_7_LEFT','FREE_PREV_7_RIGHT')
MAX_HISTORY_TURNS=8

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
    previous=source_module(PREVIOUS_C_URL,PREVIOUS_C_SHA,'mpw102c_frozen_parent')
    cc,vc,bc,_=previous.make_cases(train,valid)
    if sha(bc)!=PREVIOUS_C_MANIFEST:raise RuntimeError('MPW102C_MANIFEST_MISMATCH')
    previous_b=source_module(PREVIOUS_B_URL,PREVIOUS_B_SHA,'mpw102b_frozen_parent')
    cb,vb,bb,_=previous_b.make_cases(train,valid)
    if sha(bb)!=PREVIOUS_B_MANIFEST:raise RuntimeError('MPW102B_MANIFEST_MISMATCH')
    previous_a=source_module(PARENT_URL,PARENT_SHA,'mpw102_frozen_parent')
    previous101=previous_a.parent_module()
    ca,va,ba,_=previous_a.draw(train,valid,previous101)
    if sha(ba)!=PARENT_MANIFEST:raise RuntimeError('MPW102_MANIFEST_MISMATCH')
    c101,v101,b101,_=previous101.sampled_families(train,valid)
    if sha(b101)!=previous_a.PARENT_MANIFEST:raise RuntimeError('MPW101_MANIFEST_MISMATCH')
    old_fams=c101+v101+ca+va+cb+vb+cc+vc
    excluded={key(f[k]) for f in old_fams for k in ('left','right','flip_left','flip_right')}
    excluded.update(key(row['sentence']) for row in valid)
    orig={0:[],1:[]}
    for row in train:
        y=row['label']
        if y in (0,1):
            st=clean(row['sentence'])
            if 4<=len(st.split())<=36:orig[y].append(st)
    first_rng=random.Random(previous101.ORIGINAL_PR002_SEED)
    for y in (0,1):first_rng.shuffle(orig[y])
    excluded.update(key(q) for y in (0,1) for q in orig[y][:48])
    seen=set(excluded);pools={0:[],1:[]}
    for row in train:
        y=row['label']
        if y not in (0,1):continue
        text=clean(row['sentence']);k=key(text)
        if 4<=len(text.split())<=36 and k not in seen:
            pools[y].append(text);seen.add(k)
    rng=random.Random(SEED)
    for y in (0,1):rng.shuffle(pools[y])
    if any(len(pools[y])<2*(CAL_N+VAL_N) for y in (0,1)):raise RuntimeError('NOT_ENOUGH_FRESH_CASES')
    ix={0:0,1:0}
    def take(y):
        v=pools[y][ix[y]];ix[y]+=1;return v
    def batch(n,start):
        labels=[0,1]*(n//2);rng.shuffle(labels);out=[]
        for j,y in enumerate(labels):
            f={'idx':start+j,'label':y,'left':take(y),'right':take(y),
               'flip_left':take(1-y),'flip_right':take(1-y),
               'code_orders':{'AB':rng.choice((0,1))}}
            out.append(f)
        return out
    cal=batch(CAL_N,0);validation=batch(VAL_N,CAL_N)
    texts=[key(f[k]) for f in cal+validation for k in ('left','right','flip_left','flip_right')]
    if len(texts)!=len(set(texts)) or any(k in excluded for k in texts):
        raise RuntimeError('PRIOR_SAMPLE_TEXT_OVERLAP')
    manifest=stable(cal+validation).encode()
    meta={'prior_families':{'101':len(c101+v101),'102':len(ca+va),
                           '102b':len(cb+vb),'102c':len(cc+vc)},
          'historical_excluded':len(excluded),'distinct_passages':len(texts),
          'pools':{str(y):len(pools[y]) for y in (0,1)},'disjoint':True}
    return cal,validation,manifest,meta

def case_text(f,order,a,b):
    passages=f"LEFT: {a}\nRIGHT: {b}" if order=='LR' else f"RIGHT: {b}\nLEFT: {a}"
    return {'role':'user','content':'Case\n'+passages+'\nAnswer exactly positive or negative.'}

def history_sequence(name):
    if name=='LAST_ONLY':return [],False
    for n in (1,3,7):
        for side in ('LEFT','RIGHT'):
            if name==f'PREV_{n}_{side}':return [side]*n,False
    if name=='BALANCED_LATE_LEFT':return ['RIGHT']*3+['LEFT']*4,False
    if name=='BALANCED_EARLY_LEFT':return ['LEFT']*4+['RIGHT']*3,False
    if name=='FREE_PREV_7_LEFT':return ['LEFT']*7,True
    if name=='FREE_PREV_7_RIGHT':return ['RIGHT']*7,True
    raise RuntimeError('UNDECLARED_HISTORY_'+name)

def make_history(f,base,mapping_num,final_side,name):
    order=f['code_orders']['AB'];z0,z1=(('A','B') if order==0 else ('B','A'))
    code_map={'A':'LEFT' if mapping_num==0 else 'RIGHT',
              'B':'RIGHT' if mapping_num==0 else 'LEFT'}
    decl=f'{z0} means {code_map[z0]}; {z1} means {code_map[z1]}'
    question=REPORT_QUESTION.format(decl=decl)
    earlier,free=history_sequence(name)
    if len(earlier)+1>MAX_HISTORY_TURNS:raise RuntimeError('MORE_THAN_8_TURNS')
    def code_for(side):return 'A' if code_map['A']==side else 'B'
    sequence=list(base)
    for side in earlier:
        q=FREE_QUESTION if free else question
        sequence.append({'role':'user','content':q})
        sequence.append({'role':'assistant','content':code_for(side)})
    sequence.append({'role':'user','content':question})
    sequence.append({'role':'assistant','content':code_for(final_side)})
    return sequence

def prefixes(f,old,base):
    out={'baseline':base,'baseline_repeat':base,
         'neutral_ack':old.parent_module().BASE+[{'role':'user','content':old.NEUTRAL_Q},
                                                   {'role':'assistant','content':'Understood.'}],
         'label_ack':old.parent_module().BASE+[{'role':'user','content':old.LABEL_Q},
                                                 {'role':'assistant','content':'Understood.'}]}
    for m in (0,1):
        for final in ('LEFT','RIGHT'):
            for name in HISTORY_NAMES:
                out[f'm{m}_{final}_{name}']=make_history(f,base,m,final,name)
    if len(out)!=48:raise RuntimeError('EXPECTED_48_BRANCHES_NOT_'+str(len(out)))
    return out

def frozen_sequence_preflight(tok,cases,base):
    max_tokens=0;max_case=None
    for f in cases:
        for m in (0,1):
            for final in ('LEFT','RIGHT'):
                for name in ('PREV_7_LEFT','PREV_7_RIGHT','BALANCED_LATE_LEFT',
                             'BALANCED_EARLY_LEFT','FREE_PREV_7_LEFT','FREE_PREV_7_RIGHT'):
                    pref=make_history(f,base,m,final,name)
                    for order in ORDERS:
                        for l,r in ((f['left'],f['right']),(f['flip_left'],f['right']),
                                    (f['left'],f['flip_right'])):
                            prompt=tok.apply_chat_template(pref+[case_text(f,order,l,r)],
                                                          tokenize=False,add_generation_prompt=True)
                            toklen=len(tok.encode(prompt,add_special_tokens=False))
                            if toklen>max_tokens:
                                max_tokens=toklen
                                max_case={'idx':f['idx'],'mapping':m,'final':final,
                                          'history':name,'order':order}
                            if toklen>TOKEN_HARD_CAP:
                                raise RuntimeError('INPUT_CONTEXT_EXCEEDS_1024_NO_TRUNCATION')
    return {'max_tokens':max_tokens,'at':max_case,'cap':TOKEN_HARD_CAP}


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
    from scipy.stats import binomtest
    if len(rows)!=VAL_N or set(r['idx'] for r in rows)!=set(range(CAL_N,CAL_N+VAL_N)):
        raise RuntimeError('INCOMPLETE_VALIDATION_FAMILIES')
    stat_vectors={h:[] for h in ('H1','H2','H3','H4')}
    per_order={h:{o:[] for o in ORDERS} for h in stat_vectors}
    trajectory={name:[] for name in ('E2','E4','E8','E8_FREE','ORDER','J8')}
    agreement={'00':0,'01':0,'10':0,'11':0}
    sat=neg=0;acc={o:[] for o in ORDERS};sensitivity=[];numeric=[]
    neutral={o:[] for o in ORDERS};label={o:[] for o in ORDERS}
    for f in rows:
        local={name:[] for name in ('E2','E4','E8','E8_FREE','ORDER','J8')}
        for order in ORDERS:
            q=f['orders'][order]
            untouched=q['baseline']
            acc[order].append(untouched['acc'])
            sensitivity.append(untouched['sens'])
            numeric.append(abs(untouched['D']-q['baseline_repeat']['D']))
            sat+=int(abs(untouched['D'])>=.95)
            neg+=int(untouched['I_left']<=0 or untouched['I_right']<=0)
            neutral[order].append(q['neutral_ack']['D']-untouched['D'])
            label[order].append(q['label_ack']['D']-untouched['D'])
            for m in (0,1):
                for final in ('LEFT','RIGHT'):
                    prefix=f'm{m}_{final}_'
                    def get(x):return q[prefix+x]
                    for label_x,count in (('E2',1),('E4',3),('E8',7)):
                        value=get(f'PREV_{count}_LEFT')['D']-get(f'PREV_{count}_RIGHT')['D']
                        local[label_x].append(value)
                        if label_x=='E8':
                            j=get('PREV_7_LEFT')['J']-get('PREV_7_RIGHT')['J']
                            local['J8'].append(j)
                    local['E8_FREE'].append(get('FREE_PREV_7_LEFT')['D']-get('FREE_PREV_7_RIGHT')['D'])
                    local['ORDER'].append(get('BALANCED_LATE_LEFT')['D']-get('BALANCED_EARLY_LEFT')['D'])
                    for earlier in ('LEFT','RIGHT'):
                        original=untouched['D'] if final=='LEFT' else -untouched['D']
                        following=get(f'PREV_7_{earlier}')['D']
                        following=following if final=='LEFT' else -following
                        key2=f'{int(original>0)}{int(following>0)}'
                        agreement[key2]+=1
        for name in local:
            trajectory[name].append(float(np.mean(local[name])))
        stat_vectors['H1'].append(trajectory['E8'][-1])
        stat_vectors['H2'].append(trajectory['E8'][-1]-trajectory['E2'][-1])
        stat_vectors['H3'].append(trajectory['E8'][-1]-trajectory['E8_FREE'][-1])
        stat_vectors['H4'].append(trajectory['ORDER'][-1])
        for order in ORDERS:
            q=f['orders'][order]
            for m in (0,1):
                for final in ('LEFT','RIGHT'):
                    prefix=f'm{m}_{final}_'
                    def e(k):return q[prefix+k]['D']
                    e2=e('PREV_1_LEFT')-e('PREV_1_RIGHT')
                    e8=e('PREV_7_LEFT')-e('PREV_7_RIGHT')
                    efree=e('FREE_PREV_7_LEFT')-e('FREE_PREV_7_RIGHT')
                    order_val=e('BALANCED_LATE_LEFT')-e('BALANCED_EARLY_LEFT')
                    per_order['H1'][order].append(e8)
                    per_order['H2'][order].append(e8-e2)
                    per_order['H3'][order].append(e8-efree)
                    per_order['H4'][order].append(order_val)
    estimates={h:stat_vec(v,BOOT_SEED+i) for i,(h,v) in enumerate(stat_vectors.items(),1)}
    order_means={h:{o:float(np.mean(v)) for o,v in orders.items()} for h,orders in per_order.items()}
    accuracy={o:float(np.mean(v)) for o,v in acc.items()}
    valid=(all(v>=.90 for v in accuracy.values()) and max(numeric)<1e-4)
    verdicts={}
    for h,e in estimates.items():
        ok=(valid and e['mean']>0 and e['ci_familywise'][0]>0 and
            e['sign_p']<FAMILY_ALPHA and all(x>0 for x in order_means[h].values()))
        verdicts[h]='CONFIRMED' if ok else ('INVALID' if not valid else 'NOT_CONFIRMED')
    return {'model':which,'n':len(rows),'estimates':estimates,'verdicts':verdicts,
            'orders':order_means,'trajectory':{name:float(np.mean(v)) for name,v in trajectory.items()},
            'validation_accuracy':accuracy,'mean_sensitivity':float(np.mean(sensitivity)),
            'numerical_floor_max':float(max(numeric)),'saturated_baselines':sat,
            'negative_interventions':neg,'neutral_means':{o:float(np.mean(v)) for o,v in neutral.items()},
            'label_means':{o:float(np.mean(v)) for o,v in label.items()},
            'agreement_table_descriptive':agreement,'valid':bool(valid),
            'full_eight_gate_per_model':all(x=='CONFIRMED' for x in verdicts.values())}

def compressed_chunks(tag,raw,maxpart=10000):
    z=base64.b64encode(gzip.compress(raw,compresslevel=9,mtime=0)).decode()
    for n in range(0,len(z),maxpart):
        emit(tag,{'part':n//maxpart,'total':(len(z)+maxpart-1)//maxpart,
                  'sha256':sha(raw),'data':z[n:n+maxpart]})
def main():
    import argparse
    t0=time.monotonic();ap=argparse.ArgumentParser()
    ap.add_argument('mode',choices=('preflight','execute'))
    ap.add_argument('--model',choices=tuple(MODELS),default='qwen3')
    opt=ap.parse_args()
    from huggingface_hub import model_info,dataset_info
    from datasets import load_dataset
    from transformers import AutoTokenizer
    actual_models={name:model_info(repo).sha for name,repo in MODELS.items()}
    if dataset_info(DATASET).sha!=DATASET_SHA:raise RuntimeError('DATASET_REVISION_DIFFERED')
    train=load_dataset(DATASET,split='train',revision=DATASET_SHA)
    valid=load_dataset(DATASET,split='validation',revision=DATASET_SHA)
    cal,val,manifest,meta=make_cases(train,valid)
    manifest_hash=sha(manifest)
    previous=source_module(PARENT_URL,PARENT_SHA,'mpw102_parent_runtime')
    base=previous.parent_module().BASE
    emit('MPW103_PREVALIDATION',{'mode':opt.mode,'model':opt.model,
         'manifest_sha256':manifest_hash,'model_revisions':actual_models,
         'source_sha256':sha(Path(__file__).read_bytes()),
         'historical_102c_manifest_sha256':PREVIOUS_C_MANIFEST,
         'case_meta':meta,'cal_n':len(cal),'validation_n':len(val)})
    if opt.mode=='preflight':
        for name,repo in MODELS.items():
            tok=AutoTokenizer.from_pretrained(repo,revision=actual_models[name],trust_remote_code=True)
            token_ids={z:tok.encode(z,add_special_tokens=False) for z in ('positive','negative','A','B')}
            atomic=all(len(v)==1 for v in token_ids.values())
            emit('MPW103_TOKEN_PREFLIGHT',{'model':name,'token_ids':token_ids,'atomic':atomic})
            if not atomic:raise RuntimeError('NONATOMIC_NEXT_TOKEN_CANDIDATES_'+name)
            leng=frozen_sequence_preflight(tok,cal+val,base)
            emit('MPW103_LONGEST_CONTEXT_PREFLIGHT',{'model':name,**leng})
        emit('MPW103_CPU_PREFLIGHT_END',{'status':'COMPLETED_NO_INFERENCE',
             'manifest_sha256':manifest_hash,'n':len(cal)+len(val)})
        return
    if EXPECTED_MANIFEST=='UNSET_PREFLIGHT_REQUIRED' or manifest_hash!=EXPECTED_MANIFEST:
        raise RuntimeError('FROZEN_MANIFEST_DOES_NOT_MATCH')
    if any(MODEL_PINS[m]!=actual_models[m] for m in MODELS):
        raise RuntimeError('FROZEN_MODEL_REVISION_CHANGED')
    import torch,transformers,numpy as np
    name=opt.model;repo=MODELS[name];max_seconds=TIME_LIMITS[name]
    tok=AutoTokenizer.from_pretrained(repo,revision=MODEL_PINS[name],trust_remote_code=True)
    tok.padding_side='left';tok.pad_token=tok.pad_token or tok.eos_token
    token_ids={z:tok.encode(z,add_special_tokens=False) for z in ('positive','negative','A','B')}
    if any(len(v)!=1 for v in token_ids.values()):
        emit('MPW103_ABORT',{'reason':'TOKEN_PREFLIGHT_FAILED','validation_started':False});return
    ids={z:v[0] for z,v in token_ids.items()}
    if not torch.cuda.is_available():raise RuntimeError('GPU_REQUIRED')
    model=transformers.AutoModelForCausalLM.from_pretrained(repo,revision=MODEL_PINS[name],
        trust_remote_code=True,torch_dtype=torch.float16,device_map='auto',
        low_cpu_mem_usage=True,attn_implementation='sdpa')
    model.eval();batch_size=7 if name=='qwen3' else 8
    emit('MPW103_HARDWARE',{'model':name,'gpu':torch.cuda.get_device_name(0),
         'torch':torch.__version__,'transformers':transformers.__version__,
         'dtype':'fp16','batch_size':batch_size,'max_seconds':max_seconds})
    def logit_margins(messages,label):
        out=[]
        for k in range(0,len(messages),batch_size):
            texts=[tok.apply_chat_template(m,tokenize=False,add_generation_prompt=True)
                   for m in messages[k:k+batch_size]]
            enc=tok(texts,return_tensors='pt',padding=True,truncation=False,
                    add_special_tokens=False)
            if int(enc.attention_mask.sum(dim=1).max())>TOKEN_HARD_CAP:
                raise RuntimeError('INPUT_TOO_LONG_NO_TRUNCATION')
            enc=enc.to(model.device)
            with torch.inference_mode():
                logits=model(**enc,use_cache=False).logits[:,-1,:].float()
                v=logits[:,ids['positive']]-logits[:,ids['negative']]
                out.extend(v.cpu().tolist())
        return [float(v if label==1 else -v) for v in out]
    def audit(f,order,pre):
        samples=[pre+[case_text(f,order,f['left'],f['right'])],
                 pre+[case_text(f,order,f['flip_left'],f['right'])],
                 pre+[case_text(f,order,f['left'],f['flip_right'])]]
        a,b,c=logit_margins(samples,f['label'])
        il=a-b;ir=a-c;sens=abs(il)+abs(ir)
        return {'D':float((il-ir)/(sens+EPS)),'J':float(il-ir),
                'I_left':float(il),'I_right':float(ir),'sens':float(sens),
                'acc':int(a>=0)}
    def observe(f,full):
        d={'idx':f['idx'],'label':f['label'],'case_sha256':sha(stable(f)),'orders':{}}
        for order in ORDERS:
            p=prefixes(f,previous,base) if full else {'baseline':base,'baseline_repeat':base}
            observations={}
            # Collect the whole order in stable key order, independent prefix on every call.
            for keyname,pre in p.items():observations[keyname]=audit(f,order,pre)
            d['orders'][order]=observations
        return d
    calibration=[observe(f,False) for f in cal]
    accuracy={o:float(np.mean([r['orders'][o]['baseline']['acc'] for r in calibration])) for o in ORDERS}
    sensitivity=float(np.mean([r['orders'][o]['baseline']['sens'] for r in calibration for o in ORDERS]))
    eligible=all(v>=.9 for v in accuracy.values()) and sensitivity>=1
    emit('MPW103_CALIBRATION',{'model':name,'n':len(cal),'accuracy_by_order':accuracy,
         'sensitivity':sensitivity,'eligible':eligible})
    if not eligible:
        emit('MPW103_END',{'model':name,'status':'CAPABILITY_GATE_FAIL','no_validation':True});return
    tprobe=time.monotonic()
    for f in cal[:4]:observe(f,True)
    sec=(time.monotonic()-tprobe)/4
    projected=(time.monotonic()-t0)+sec*VAL_N*1.35
    emit('MPW103_TIMING',{'model':name,'seconds_per_family':sec,
         'projection_seconds':projected,'max_seconds':max_seconds})
    if projected>max_seconds-180:
        emit('MPW103_END',{'model':name,'status':'RUNTIME_GATE_FAIL','no_validation':True});return
    emit('MPW103_VALIDATION_START',{'model':name,'n':len(val),'manifest_sha256':manifest_hash})
    rows=[]
    for index,f in enumerate(val):
        if time.monotonic()-t0>max_seconds-120:
            emit('MPW103_END',{'model':name,'status':'RUNTIME_ABORT','n':len(rows)});return
        q=observe(f,True)
        if any(not np.isfinite(a[k]) for order in q['orders'].values()
                 for a in order.values() for k in ('D','J','I_left','I_right','sens')):
            emit('MPW103_END',{'model':name,'status':'INVALID_NONFINITE','n':len(rows)});return
        rows.append(q)
        if (index+1)%16==0:
            emit('MPW103_PROGRESS',{'model':name,'n':len(rows),'total':VAL_N,
                 'elapsed_seconds':time.monotonic()-t0})
    raw=('\n'.join(stable(r) for r in rows)+'\n').encode()
    for first in range(0,VAL_N,32):
        part=('\n'.join(stable(r) for r in rows[first:first+32])+'\n').encode()
        compressed_chunks('MPW103_RECORD_B64',part)
        emit('MPW103_SHARD',{'model':name,'part':first//32,'n':32,
             'range':[first,first+31],'sha256':sha(part)})
    result=aggregate(rows,name)
    emit('MPW103_PRIMARY_RESULT',result)
    emit('MPW103_END',{'model':name,'status':'COMPLETED',
        'manifest_sha256':manifest_hash,'n':len(rows),'raw_sha256':sha(raw),
        'elapsed_seconds':time.monotonic()-t0,'verdicts':result['verdicts']})

if __name__=='__main__':main()
