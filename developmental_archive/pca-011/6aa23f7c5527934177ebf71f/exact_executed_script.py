# /// script
# dependencies = ["torch", "transformers>=4.49", "accelerate", "huggingface_hub", "numpy", "scipy"]
# ///
import os,re,json,random,math,torch
import numpy as np
from scipy.stats import spearmanr
from transformers import AutoTokenizer,AutoModelForCausalLM
from huggingface_hub import model_info

MODEL='Qwen/Qwen2.5-7B-Instruct'; LAYER=14; BASE_ALPHA=1.0
VAL=48; SEED_VAL=7000; EPS=1e-6
DOSES=[-1.0,-0.5,-0.25,0.0,0.25,0.5,1.0]
OUT0,OUT1='X','Y'; REP0,REP1='A','B'

def family(seed):
    r=random.Random(seed); flip=r.choice([0,1]); mp={'0':OUT1 if flip else OUT0,'1':OUT0 if flip else OUT1}
    side_order=r.choice(['LR','RL']); vals=['0','1']*4; r.shuffle(vals)
    def fmt(l,rr,y=None):
        c=(f'LEFT={l}; RIGHT={rr}' if side_order=='LR' else f'RIGHT={rr}; LEFT={l}')
        return c+(f' -> {y}' if y is not None else '')
    demos=[fmt(v,v,mp[v]) for v in vals]
    pre=[{'role':'user','content':'Infer the binary labeling rule from the examples. For every new case answer exactly X or Y, nothing else.\n'+'\n'.join(demos)},
         {'role':'assistant','content':'Understood.'}]
    a_left=r.choice([True,False]); c2s={'A':'LEFT' if a_left else 'RIGHT','B':'RIGHT' if a_left else 'LEFT'}
    order=['A','B']; r.shuffle(order)
    stem=f'Two response codes apply only to this question. {order[0]} means {c2s[order[0]]}; {order[1]} means {c2s[order[1]]}. '
    q=stem+f'Which side are YOU relying on more to determine the output when LEFT and RIGHT could disagree? Answer exactly {order[0]} or {order[1]}.'
    other=stem+f'Which side is ANOTHER SOLVER relying on more to determine the output when LEFT and RIGHT could disagree? Answer exactly {order[0]} or {order[1]}.'
    evidence=stem+f'Which side do THE EXAMPLES support more when LEFT and RIGHT could disagree? Answer exactly {order[0]} or {order[1]}.'
    ctrl=f'Answer exactly {order[0]} or {order[1]}. Which response code is listed first in this sentence: {order[0]} or {order[1]}?'
    return {'seed':seed,'pre':pre,'fmt':fmt,'mp':mp,'c2s':c2s,'order':order,'q':q,'other':other,'evidence':evidence,'ctrl':ctrl}

def render(tok,msgs,gen=False):
    return tok.apply_chat_template(msgs,tokenize=False,add_generation_prompt=gen)

def spans_for(text,side):
    pat=(r'LEFT=([01])' if side=='LEFT' else r'RIGHT=([01])')
    return [m.span(1) for m in re.finditer(pat,text)]

def donor_hidden(m,tok,f,side):
    text=render(tok,f['pre'],False)
    enc=tok(text,return_tensors='pt',return_offsets_mapping=True,add_special_tokens=False)
    offsets=enc.pop('offset_mapping')[0].tolist(); ids=enc['input_ids'].to(m.device); am=enc['attention_mask'].to(m.device)
    emb=m.get_input_embeddings()(ids); mask=torch.ones(emb.shape[:2],device=emb.device,dtype=emb.dtype)
    spans=spans_for(text,side)
    for ti,(s,e) in enumerate(offsets):
        if e>s and any(max(s,a)<min(e,b) for a,b in spans): mask[0,ti]=0.0
    with torch.inference_mode():
        out=m(inputs_embeds=emb*mask.unsqueeze(-1),attention_mask=am,output_hidden_states=True,use_cache=False,return_dict=True)
    return [h.detach() for h in out.hidden_states], ids[0].tolist()

def lcp(a,b):
    n=min(len(a),len(b)); i=0
    while i<n and a[i]==b[i]: i+=1
    return i

def make_delta(m,tok,f):
    hl,bid=donor_hidden(m,tok,f,'LEFT'); hr,bid2=donor_hidden(m,tok,f,'RIGHT'); assert bid==bid2
    return {'vec':hr[LAYER+1]-hl[LAYER+1],'base_ids':bid}

def full_logits(m,tok,msgsets,delta,dose):
    texts=[render(tok,x,True) for x in msgsets]
    raw=[tok(t,add_special_tokens=False)['input_ids'] for t in texts]
    pls=[lcp(delta['base_ids'],x) for x in raw]
    enc=tok(texts,return_tensors='pt',padding=True,add_special_tokens=False); ids=enc['input_ids'].to(m.device); am=enc['attention_mask'].to(m.device)
    starts=[ids.shape[1]-len(x) for x in raw]; d=delta['vec'].to(m.device); alpha=BASE_ALPHA*dose
    def hook(mod,inp,out):
        tup=isinstance(out,tuple); h=out[0] if tup else out; h2=h.clone()
        for bi,(st,pl) in enumerate(zip(starts,pls)):
            n=min(pl,d.shape[1]); h2[bi,st:st+n,:]+=alpha*d[0,:n,:].to(h2.dtype)
        return ((h2,)+out[1:]) if tup else h2
    handle=m.model.layers[LAYER].register_forward_hook(hook)
    try:
        with torch.inference_mode(): lg=m(input_ids=ids,attention_mask=am,use_cache=False).logits.float().cpu()
    finally: handle.remove()
    last=(am.sum(1)-1 + (ids.shape[1]-am.sum(1))).long().cpu()
    return torch.stack([lg[i,last[i],:] for i in range(len(texts))])

def metric(m,tok,f,idX,idY,delta,dose):
    msgs=[]; meta=[]
    for phr in [0,1]:
        for v in ['0','1']:
            alt='1' if v=='0' else '0'
            for kind,l,r in [('same',v,v),('lf',alt,v),('rf',v,alt)]:
                core=f['fmt'](l,r); p=(f'Probe: {core}. Output exactly X or Y.' if phr==0 else f'Input {core}. Give only the binary output label X or Y.')
                msgs.append(f['pre']+[{'role':'user','content':p}]); meta.append((phr,v,kind))
    L=full_logits(m,tok,msgs,delta,dose); rec={}; ordinary=[]
    for md,lg in zip(meta,L):
        phr,v,kind=md; y=f['mp'][v]; iy=idX if y==OUT0 else idY; ia=idY if y==OUT0 else idX
        rec[(phr,v,kind)]=float(lg[iy]-lg[ia])
        if kind=='same': ordinary.append(int((float(lg[idX])>float(lg[idY]))==(y==OUT0)))
    IL=[]; IR=[]
    for phr in [0,1]:
        for v in ['0','1']:
            b=rec[(phr,v,'same')]; IL.append(b-rec[(phr,v,'lf')]); IR.append(b-rec[(phr,v,'rf')])
    il=sum(IL)/len(IL); ir=sum(IR)/len(IR); D=(il-ir)/(abs(il)+abs(ir)+EPS)
    return {'dominance':D,'ordinary_acc':sum(ordinary)/len(ordinary),'I_left':il,'I_right':ir}

def query_batch(m,tok,f,idA,idB,delta,dose):
    qs=[f['q'],f['other'],f['evidence'],f['ctrl']]
    msgsets=[f['pre']+[{'role':'user','content':q}] for q in qs]
    L=full_logits(m,tok,msgsets,delta,dose)
    sign=1 if f['c2s']['A']=='LEFT' else -1
    vals=[]
    for lg in L:
        raw=float(lg[idA]-lg[idB]); vals.append(sign*raw)
    return dict(zip(['self','other','evidence','control'],vals))

def slope(x,y):
    x=np.asarray(x,float); y=np.asarray(y,float); z=x-x.mean(); den=float((z*z).sum())
    return float((z*(y-y.mean())).sum()/den) if den>1e-12 else float('nan')

def corr(x,y):
    return float(spearmanr(x,y).statistic)

tok=AutoTokenizer.from_pretrained(MODEL,token=os.environ.get('HF_TOKEN')); tok.padding_side='left'; tok.pad_token=tok.pad_token or tok.eos_token
ids={s:tok.encode(s,add_special_tokens=False) for s in [OUT0,OUT1,REP0,REP1]}; assert all(len(v)==1 for v in ids.values()),ids
idX,idY,idA,idB=[ids[s][0] for s in [OUT0,OUT1,REP0,REP1]]
rev=model_info(MODEL,token=os.environ.get('HF_TOKEN')).sha
print('PCA011_META '+json.dumps({'model':MODEL,'revision':rev,'layer':LAYER,'base_alpha':BASE_ALPHA,'doses':DOSES,'families':VAL,'seed_start':SEED_VAL}),flush=True)
m=AutoModelForCausalLM.from_pretrained(MODEL,token=os.environ.get('HF_TOKEN'),dtype=torch.float16,device_map='auto',low_cpu_mem_usage=True); m.eval()
rows=[]
for j in range(VAL):
    f=family(SEED_VAL+j); d=make_delta(m,tok,f)
    Ds=[]; acc=[]; series={k:[] for k in ['self','other','evidence','control']}
    for dose in DOSES:
        mm=metric(m,tok,f,idX,idY,d,dose); qq=query_batch(m,tok,f,idA,idB,d,dose)
        Ds.append(mm['dominance']); acc.append(mm['ordinary_acc'])
        for k in series: series[k].append(qq[k])
    slopes={k:slope(Ds,series[k]) for k in series}
    row={'seed':f['seed'],'code_to_side':f['c2s'],'option_order':f['order'],'doses':DOSES,'D':Ds,'ordinary_acc':acc,'report_logits':series,
         'slope_D_vs_dose':slope(DOSES,Ds),'rho_D_vs_dose':corr(DOSES,Ds),
         'slope_self':slopes['self'],'slope_other':slopes['other'],'slope_evidence':slopes['evidence'],'slope_control':slopes['control'],
         'slope_self_minus_other':slopes['self']-slopes['other'],'slope_self_minus_evidence':slopes['self']-slopes['evidence'],'slope_self_minus_control':slopes['self']-slopes['control']}
    rows.append(row); print('PCA011_RECORD '+json.dumps(row,sort_keys=True),flush=True); torch.cuda.empty_cache()
def mean(key): return float(np.mean([r[key] for r in rows]))
summary={'model':MODEL,'revision':rev,'layer':LAYER,'base_alpha':BASE_ALPHA,'families':VAL,'min_ordinary_accuracy':float(min(min(r['ordinary_acc']) for r in rows)),'mean_ordinary_accuracy':float(np.mean([a for r in rows for a in r['ordinary_acc']])),
         'mean_slope_D_vs_dose':mean('slope_D_vs_dose'),'directional_D_slope_rate':float(np.mean([r['slope_D_vs_dose']>0 for r in rows])),'mean_rho_D_vs_dose':mean('rho_D_vs_dose'),
         'mean_slope_self':mean('slope_self'),'mean_slope_other':mean('slope_other'),'mean_slope_evidence':mean('slope_evidence'),'mean_slope_control':mean('slope_control'),
         'mean_self_minus_other':mean('slope_self_minus_other'),'mean_self_minus_evidence':mean('slope_self_minus_evidence'),'mean_self_minus_control':mean('slope_self_minus_control')}
print('PCA011_SUMMARY '+json.dumps(summary,sort_keys=True),flush=True)
