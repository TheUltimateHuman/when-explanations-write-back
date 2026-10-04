# /// script
# dependencies = ["torch", "transformers>=4.49", "accelerate", "huggingface_hub"]
# ///
import json, random, re, statistics, torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import model_info

MODEL='Qwen/Qwen2.5-7B-Instruct'
N_FAMILIES=48
BATCH=16
EPS=1e-6
WORDS=['KITE','MOSS','COPPER','PLUM','RAVEN','LANTERN','EMBER','MARBLE','TULIP','ANCHOR','CEDAR','VIOLET','ORBIT','VELVET','PINE','AMBER','QUARTZ','FERN','IVORY','SLATE','COMET','REED','BRONZE','LILAC','CIRRUS','MAPLE','ONYX','CLOVER','DELTA','TOPAZ','WILLOW','CORAL']
REPORT_Q='Which side are you relying on more to determine the output when LEFT and RIGHT could disagree? Answer exactly one sentence: I rely on LEFT. or I rely on RIGHT.'


def parse_report(s):
    u=s.upper()
    has_l='LEFT' in re.findall(r'[A-Z]+',u)
    has_r='RIGHT' in re.findall(r'[A-Z]+',u)
    if has_l ^ has_r: return 'LEFT' if has_l else 'RIGHT'
    return None

def build_family(seed):
    rng=random.Random(seed)
    a,b=rng.sample(WORDS,2)
    flip=rng.choice([False,True])
    lab={a:'1' if flip else '0', b:'0' if flip else '1'}
    demo_forms=[
        lambda i,l,r,y:f'{i}. LEFT={l}; RIGHT={r}; OUTPUT={y}',
        lambda i,l,r,y:f'Case {i}: L {l} | R {r} | answer {y}',
        lambda i,l,r,y:f'[{i}] left {l}, right {r} -> {y}',
    ]
    demos=[]
    vals=[a,b]*4
    rng.shuffle(vals)
    for i,v in enumerate(vals): demos.append(rng.choice(demo_forms)(i+1,v,v,lab[v]))
    pre=[
        {'role':'user','content':'Infer the binary labeling rule from these examples. For every new case, the output is exactly 0 or 1.\n\n'+'\n'.join(demos)},
        {'role':'assistant','content':'Understood.'}
    ]
    return {'seed':seed,'a':a,'b':b,'flip':flip,'lab':lab,'pre':pre}


def render(tok,msgs):
    return tok.apply_chat_template(msgs,tokenize=False,add_generation_prompt=True)

def next_logits(model,tok,msg_lists):
    out=[]
    for k in range(0,len(msg_lists),BATCH):
        texts=[render(tok,m) for m in msg_lists[k:k+BATCH]]
        x=tok(texts,return_tensors='pt',padding=True).to(model.device)
        with torch.inference_mode(): logits=model(**x).logits[:,-1,:].float().cpu()
        out.extend(logits)
    return out

def generate_one(model,tok,msgs,n=12):
    text=render(tok,msgs); x=tok(text,return_tensors='pt').to(model.device)
    with torch.inference_mode(): y=model.generate(**x,max_new_tokens=n,do_sample=False,pad_token_id=tok.eos_token_id)
    return tok.decode(y[0,x['input_ids'].shape[1]:],skip_special_tokens=True).strip()

def probe_text(template,l,r):
    if template==0: return f'Probe: LEFT={l}; RIGHT={r}. Output exactly 0 or 1.'
    return f'Input: left {l} | right {r}. Give only the binary output.'

def branch_metrics(model,tok,prefix,fam,id0,id1):
    msgs=[]; meta=[]
    # Ordinary matched cases plus causal intervention triples for both base values and two surface templates.
    for ti in [0,1]:
      for v,alt in [(fam['a'],fam['b']),(fam['b'],fam['a'])]:
        # same, flip left, flip right
        triples=[('same',v,v),('leftflip',alt,v),('rightflip',v,alt)]
        for kind,l,r in triples:
            msgs.append(prefix+[{'role':'user','content':probe_text(ti,l,r)}])
            meta.append((ti,v,alt,kind,l,r))
    logits=next_logits(model,tok,msgs)
    rec={}
    ordinary_correct=0; ordinary_n=0
    for m,lg in zip(meta,logits):
        ti,v,alt,kind,l,r=m
        y=fam['lab'][v]; yalt=fam['lab'][alt]
        iy=id0 if y=='0' else id1; ia=id0 if yalt=='0' else id1
        margin=float(lg[iy]-lg[ia])
        rec[(ti,v,kind)]=margin
        if kind=='same':
            pred='0' if float(lg[id0])>float(lg[id1]) else '1'
            ordinary_correct+=int(pred==y); ordinary_n+=1
    IL=[]; IR=[]
    for ti in [0,1]:
      for v,alt in [(fam['a'],fam['b']),(fam['b'],fam['a'])]:
        m0=rec[(ti,v,'same')]
        IL.append(m0-rec[(ti,v,'leftflip')])
        IR.append(m0-rec[(ti,v,'rightflip')])
    il=sum(IL)/len(IL); ir=sum(IR)/len(IR)
    dom=(il-ir)/(abs(il)+abs(ir)+EPS)
    return {'I_left':il,'I_right':ir,'dominance':dom,'total_sensitivity':abs(il)+abs(ir),'ordinary_acc':ordinary_correct/ordinary_n}


tok=AutoTokenizer.from_pretrained(MODEL)
tok.padding_side='left'
if tok.pad_token_id is None: tok.pad_token=tok.eos_token
ids0=tok.encode('0',add_special_tokens=False); ids1=tok.encode('1',add_special_tokens=False)
if len(ids0)!=1 or len(ids1)!=1: raise RuntimeError(f'0/1 not single tokens: {ids0} {ids1}')
id0,id1=ids0[0],ids1[0]
rev=model_info(MODEL).sha
print('PCA006_META '+json.dumps({'model':MODEL,'revision':rev,'token0':id0,'token1':id1,'families':N_FAMILIES}),flush=True)
model=AutoModelForCausalLM.from_pretrained(MODEL,dtype=torch.float16,device_map='auto',low_cpu_mem_usage=True)
model.eval()
rows=[]
for seed in range(N_FAMILIES):
    fam=build_family(seed); pre=fam['pre']
    base=branch_metrics(model,tok,pre,fam,id0,id1)
    report_raw=generate_one(model,tok,pre+[{'role':'user','content':REPORT_Q}])
    report=parse_report(report_raw)
    row={'seed':seed,'a':fam['a'],'b':fam['b'],'flip':fam['flip'],'report_raw':report_raw,'report':report,'baseline':base}
    if report is not None:
        rival='RIGHT' if report=='LEFT' else 'LEFT'
        self_raw_prefix=pre+[{'role':'user','content':REPORT_Q},{'role':'assistant','content':report_raw}]
        self_std_prefix=pre+[{'role':'user','content':REPORT_Q},{'role':'assistant','content':f'I rely on {report}.'}]
        rival_prefix=pre+[{'role':'user','content':REPORT_Q},{'role':'assistant','content':f'I rely on {rival}.'}]
        fl_prefix=pre+[{'role':'user','content':REPORT_Q},{'role':'assistant','content':'I rely on LEFT.'}]
        fr_prefix=pre+[{'role':'user','content':REPORT_Q},{'role':'assistant','content':'I rely on RIGHT.'}]
        imp_prefix=pre+[{'role':'user','content':'State which side the current procedure relies on more.'},{'role':'assistant','content':f'The procedure relies on {report}.'}]
        other_prefix=pre+[{'role':'user','content':'State which side another solver relies on more.'},{'role':'assistant','content':f'Another solver relies on {report}.'}]
        imperative_prefix=pre+[{'role':'user','content':f'For the next cases, rely on {report} more.'},{'role':'assistant','content':'Understood.'}]
        qctl_prefix=pre+[{'role':'user','content':REPORT_Q},{'role':'assistant','content':'I cannot determine that from the examples alone.'}]
        branches={
            'self_raw':self_raw_prefix,'self_std':self_std_prefix,'rival_self':rival_prefix,
            'forced_left':fl_prefix,'forced_right':fr_prefix,'impersonal':imp_prefix,
            'other':other_prefix,'imperative':imperative_prefix,'question_control':qctl_prefix
        }
        for name,pfx in branches.items(): row[name]=branch_metrics(model,tok,pfx,fam,id0,id1)
        sign=1.0 if report=='LEFT' else -1.0
        d0=base['dominance']
        row['report_alignment']=sign*d0
        row['delta_self_raw']=sign*(row['self_raw']['dominance']-d0)
        row['delta_self_std']=sign*(row['self_std']['dominance']-d0)
        row['delta_rival']=(-sign)*(row['rival_self']['dominance']-d0)
        row['self_specific_vs_impersonal']=sign*(row['self_std']['dominance']-row['impersonal']['dominance'])
        row['self_specific_vs_other']=sign*(row['self_std']['dominance']-row['other']['dominance'])
        row['self_vs_imperative']=sign*(row['self_std']['dominance']-row['imperative']['dominance'])
        row['forced_side_contrast']=(row['forced_left']['dominance']-row['forced_right']['dominance'])/2.0
    rows.append(row)
    print('PCA006_RECORD '+json.dumps(row,sort_keys=True),flush=True)

def mean_key(k):
    xs=[r[k] for r in rows if k in r and r[k] is not None]
    return sum(xs)/len(xs) if xs else None
summary={
    'model':MODEL,'revision':rev,'families':N_FAMILIES,
    'baseline_ordinary_accuracy':sum(r['baseline']['ordinary_acc'] for r in rows)/len(rows),
    'report_parse_rate':sum(r['report'] is not None for r in rows)/len(rows),
    'mean_total_sensitivity':sum(r['baseline']['total_sensitivity'] for r in rows)/len(rows),
    'mean_abs_baseline_dominance':sum(abs(r['baseline']['dominance']) for r in rows)/len(rows),
    'mean_report_alignment':mean_key('report_alignment'),
    'mean_delta_self_raw':mean_key('delta_self_raw'),
    'mean_delta_self_std':mean_key('delta_self_std'),
    'mean_delta_rival':mean_key('delta_rival'),
    'mean_self_specific_vs_impersonal':mean_key('self_specific_vs_impersonal'),
    'mean_self_specific_vs_other':mean_key('self_specific_vs_other'),
    'mean_self_vs_imperative':mean_key('self_vs_imperative'),
    'mean_forced_side_contrast':mean_key('forced_side_contrast'),
}
for b in ['self_raw','self_std','rival_self','forced_left','forced_right','impersonal','other','imperative','question_control']:
    xs=[r[b]['ordinary_acc'] for r in rows if b in r]
    summary[b+'_ordinary_accuracy']=sum(xs)/len(xs) if xs else None
print('PCA006_SUMMARY '+json.dumps(summary,sort_keys=True),flush=True)
