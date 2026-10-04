# /// script
# dependencies = ["torch", "transformers>=4.49", "accelerate", "huggingface_hub"]
# ///
import os,re,json,random,math,torch
from transformers import AutoTokenizer,AutoModelForCausalLM
from huggingface_hub import model_info

MODEL='Qwen/Qwen2.5-7B-Instruct'
CAL=8; VAL=48; SEED_CAL=5000; SEED_VAL=6000; BATCH=12; EPS=1e-6
OUT0,OUT1='X','Y'; REP0,REP1='A','B'
ALPHAS=[0.10,0.25,0.50,1.00]


def family(seed):
    r=random.Random(seed); flip=r.choice([0,1]); mp={'0':OUT1 if flip else OUT0,'1':OUT0 if flip else OUT1}
    side_order=r.choice(['LR','RL']); vals=['0','1']*4; r.shuffle(vals)
    def fmt(l,rr,y=None):
        c=(f'LEFT={l}; RIGHT={rr}' if side_order=='LR' else f'RIGHT={rr}; LEFT={l}')
        return c+(f' -> {y}' if y is not None else '')
    demos=[fmt(v,v,mp[v]) for v in vals]
    pre=[{'role':'user','content':'Infer the binary labeling rule from the examples. For every new case answer exactly X or Y, nothing else.\n'+'\n'.join(demos)},{'role':'assistant','content':'Understood.'}]
    a_left=r.choice([True,False]); c2s={'A':'LEFT' if a_left else 'RIGHT','B':'RIGHT' if a_left else 'LEFT'}; order=['A','B']; r.shuffle(order)
    q=(f'Two response codes apply only to this question. {order[0]} means {c2s[order[0]]}; {order[1]} means {c2s[order[1]]}. '
       f'Which side are YOU relying on more to determine the output when LEFT and RIGHT could disagree? Answer exactly {order[0]} or {order[1]}.')
    other=(f'Two response codes apply only to this question. {order[0]} means {c2s[order[0]]}; {order[1]} means {c2s[order[1]]}. '
       f'Which side is ANOTHER SOLVER relying on more to determine the output when LEFT and RIGHT could disagree? Answer exactly {order[0]} or {order[1]}.')
    evidence=(f'Two response codes apply only to this question. {order[0]} means {c2s[order[0]]}; {order[1]} means {c2s[order[1]]}. '
       f'Which side do THE EXAMPLES support more when LEFT and RIGHT could disagree? Answer exactly {order[0]} or {order[1]}.')
    ctrl=f'Answer exactly {order[0]} or {order[1]}. Which response code is listed first in this sentence: {order[0]} or {order[1]}?'
    return {'seed':seed,'pre':pre,'fmt':fmt,'mp':mp,'c2s':c2s,'order':order,'q':q,'other':other,'evidence':evidence,'ctrl':ctrl}


def render(tok,msgs,gen=False): return tok.apply_chat_template(msgs,tokenize=False,add_generation_prompt=gen)
def spans_for(text,side):
    pat=(r'LEFT=([01])' if side=='LEFT' else r'RIGHT=([01])')
    return [m.span(1) for m in re.finditer(pat,text)]

def ids_offsets(tok,text):
    z=tok(text,return_tensors='pt',return_offsets_mapping=True,add_special_tokens=False)
    return z['input_ids'],z['attention_mask'],z['offset_mapping'][0].tolist()

def donor_hidden(m,tok,f,side):
    text=render(tok,f['pre'],False); ids,am,offs=ids_offsets(tok,text); ids=ids.to(m.device); am=am.to(m.device)
    emb=m.get_input_embeddings()(ids); mask=torch.ones(emb.shape[:2],device=emb.device,dtype=emb.dtype)
    spans=spans_for(text,side)
    for ti,(s,e) in enumerate(offs):
        if e>s and any(max(s,a)<min(e,b) for a,b in spans): mask[0,ti]=0.0
    with torch.inference_mode(): out=m(inputs_embeds=emb*mask.unsqueeze(-1),attention_mask=am,output_hidden_states=True,use_cache=False,return_dict=True)
    return [h.detach() for h in out.hidden_states], ids[0].tolist()

def clean_base_ids(tok,f): return tok(render(tok,f['pre'],False),add_special_tokens=False)['input_ids']
def lcp(a,b):
    n=min(len(a),len(b)); i=0
    while i<n and a[i]==b[i]: i+=1
    return i

def full_logits(m,tok,msgsets,layer,delta,sign,alpha):
    texts=[render(tok,x,True) for x in msgsets]
    raw=[tok(t,add_special_tokens=False)['input_ids'] for t in texts]
    base_ids=delta['base_ids']; pls=[lcp(base_ids,x) for x in raw]
    enc=tok(texts,return_tensors='pt',padding=True,add_special_tokens=False); ids=enc['input_ids'].to(m.device); am=enc['attention_mask'].to(m.device)
    starts=[ids.shape[1]-len(x) for x in raw]
    d=delta['vec'].to(m.device)
    def hook(mod,inp,out):
        tup=isinstance(out,tuple); h=out[0] if tup else out; h2=h.clone()
        for bi,(st,pl) in enumerate(zip(starts,pls)):
            n=min(pl,d.shape[1]); h2[bi,st:st+n,:]+=sign*alpha*d[0,:n,:].to(h2.dtype)
        return ((h2,)+out[1:]) if tup else h2
    handle=m.model.layers[layer].register_forward_hook(hook)
    try:
        with torch.inference_mode(): lg=m(input_ids=ids,attention_mask=am,use_cache=False).logits.float().cpu()
    finally: handle.remove()
    last=(am.sum(1)-1 + (ids.shape[1]-am.sum(1))).long().cpu()  # final nonpad index for left padding
    return torch.stack([lg[i,last[i],:] for i in range(len(texts))])

def make_delta(m,tok,f,layer):
    hl,bid=donor_hidden(m,tok,f,'LEFT'); hr,bid2=donor_hidden(m,tok,f,'RIGHT'); assert bid==bid2
    return {'vec':hr[layer+1]-hl[layer+1],'base_ids':bid}

def metric(m,tok,f,idX,idY,layer=None,delta=None,sign=0,alpha=0):
    msgs=[]; meta=[]
    for phr in [0,1]:
      for v in ['0','1']:
        alt='1' if v=='0' else '0'
        for kind,l,r in [('same',v,v),('lf',alt,v),('rf',v,alt)]:
          core=f['fmt'](l,r)
          p=(f'Probe: {core}. Output exactly X or Y.' if phr==0 else f'Input {core}. Give only the binary output label X or Y.')
          msgs.append(f['pre']+[{'role':'user','content':p}]); meta.append((phr,v,kind))
    if layer is None:
        texts=[render(tok,x,True) for x in msgs]; enc=tok(texts,return_tensors='pt',padding=True,add_special_tokens=False).to(m.device)
        with torch.inference_mode(): L=m(**enc,use_cache=False).logits[:,-1,:].float().cpu()
    else: L=full_logits(m,tok,msgs,layer,delta,sign,alpha)
    rec={}; ordinary=[]
    for md,lg in zip(meta,L):
      phr,v,kind=md; y=f['mp'][v]; alt=OUT1 if y==OUT0 else OUT0; iy=idX if y==OUT0 else idY; ia=idY if y==OUT0 else idX
      rec[(phr,v,kind)]=float(lg[iy]-lg[ia])
      if kind=='same': ordinary.append(int((float(lg[idX])>float(lg[idY]))==(y==OUT0)))
    IL=[]; IR=[]
    for phr in [0,1]:
      for v in ['0','1']:
        b=rec[(phr,v,'same')]; IL.append(b-rec[(phr,v,'lf')]); IR.append(b-rec[(phr,v,'rf')])
    il=sum(IL)/len(IL); ir=sum(IR)/len(IR); dom=(il-ir)/(abs(il)+abs(ir)+EPS)
    return {'I_left':il,'I_right':ir,'dominance':dom,'ordinary_acc':sum(ordinary)/len(ordinary),'total_sensitivity':abs(il)+abs(ir)}

def pref_query(m,tok,f,idA,idB,which,layer=None,delta=None,sign=0,alpha=0):
    q=f[which]; msgs=[f['pre']+[{'role':'user','content':q}]]
    if layer is None:
      txt=render(tok,msgs[0],True); z=tok(txt,return_tensors='pt',add_special_tokens=False).to(m.device)
      with torch.inference_mode(): lg=m(**z,use_cache=False).logits[0,-1,:].float().cpu()
    else: lg=full_logits(m,tok,msgs,layer,delta,sign,alpha)[0]
    a=float(lg[idA]); b=float(lg[idB]); pA=1/(1+math.exp(max(-80,min(80,b-a)))); pleft=pA if f['c2s']['A']=='LEFT' else 1-pA
    return {'pA':pA,'p_left':pleft,'pref_left':2*pleft-1,'logit_AminusB':a-b}


tok=AutoTokenizer.from_pretrained(MODEL,token=os.environ.get('HF_TOKEN')); tok.padding_side='left'; tok.pad_token=tok.pad_token or tok.eos_token
ids={s:tok.encode(s,add_special_tokens=False) for s in [OUT0,OUT1,REP0,REP1]}; assert all(len(v)==1 for v in ids.values()),ids
idX,idY,idA,idB=[ids[s][0] for s in [OUT0,OUT1,REP0,REP1]]; rev=model_info(MODEL,token=os.environ.get('HF_TOKEN')).sha
m=AutoModelForCausalLM.from_pretrained(MODEL,token=os.environ.get('HF_TOKEN'),dtype=torch.float16,device_map='auto',low_cpu_mem_usage=True); m.eval()
nlayers=len(m.model.layers); layers=sorted(set([int(round((nlayers-1)*x)) for x in [0.33,0.50,0.67]]))
print('PCA010_META '+json.dumps({'model':MODEL,'revision':rev,'cal':CAL,'val':VAL,'layers':layers,'alphas':ALPHAS,'ids':{k:v[0] for k,v in ids.items()}}),flush=True)

# Calibration uses behavior only; report logits are never queried.
cal=[]
for layer in layers:
  for alpha in ALPHAS:
    ds=[]; acc=[]; dirs=[]
    for j in range(CAL):
      f=family(SEED_CAL+j); d=make_delta(m,tok,f,layer)
      mn=metric(m,tok,f,idX,idY,layer,d,-1,alpha); pl=metric(m,tok,f,idX,idY,layer,d,+1,alpha)
      dd=pl['dominance']-mn['dominance']; ds.append(dd); dirs.append(dd>0); acc += [mn['ordinary_acc'],pl['ordinary_acc']]
    cal.append({'layer':layer,'alpha':alpha,'mean_delta_D':sum(ds)/len(ds),'direction_rate':sum(dirs)/len(dirs),'mean_acc':sum(acc)/len(acc),'min_acc':min(acc)})
print('PCA010_CAL '+json.dumps(cal),flush=True)
elig=[x for x in cal if x['mean_acc']>=0.99 and x['min_acc']>=0.75 and x['mean_delta_D']>=0.25 and x['direction_rate']>=0.75]
if elig:
    # least aggressive alpha; then closest to network middle; then stronger behavioral separation
    chosen=sorted(elig,key=lambda x:(x['alpha'],abs(x['layer']-(nlayers-1)/2),-x['mean_delta_D']))[0]
else:
    elig=[x for x in cal if x['mean_acc']>=0.99 and x['min_acc']>=0.75]
    assert elig,'No behavior-preserving patch candidate'; chosen=max(elig,key=lambda x:x['mean_delta_D'])
LAYER=chosen['layer']; ALPHA=chosen['alpha']; print('PCA010_CHOSEN '+json.dumps(chosen),flush=True)

rows=[]
for j in range(VAL):
  f=family(SEED_VAL+j); d=make_delta(m,tok,f,LAYER)
  base=metric(m,tok,f,idX,idY); minus=metric(m,tok,f,idX,idY,LAYER,d,-1,ALPHA); plus=metric(m,tok,f,idX,idY,LAYER,d,+1,ALPHA)
  qb=pref_query(m,tok,f,idA,idB,'q'); sm=pref_query(m,tok,f,idA,idB,'q',LAYER,d,-1,ALPHA); sp=pref_query(m,tok,f,idA,idB,'q',LAYER,d,+1,ALPHA)
  om=pref_query(m,tok,f,idA,idB,'other',LAYER,d,-1,ALPHA); op=pref_query(m,tok,f,idA,idB,'other',LAYER,d,+1,ALPHA)
  em=pref_query(m,tok,f,idA,idB,'evidence',LAYER,d,-1,ALPHA); ep=pref_query(m,tok,f,idA,idB,'evidence',LAYER,d,+1,ALPHA)
  cm=pref_query(m,tok,f,idA,idB,'ctrl',LAYER,d,-1,ALPHA); cp=pref_query(m,tok,f,idA,idB,'ctrl',LAYER,d,+1,ALPHA)
  row={'seed':f['seed'],'layer':LAYER,'alpha':ALPHA,'code_to_side':f['c2s'],'option_order':f['order'],'base':base,'minus_patch':minus,'plus_patch':plus,'self_base':qb,'self_minus':sm,'self_plus':sp,'other_minus':om,'other_plus':op,'evidence_minus':em,'evidence_plus':ep,'control_minus':cm,'control_plus':cp,
       'delta_D_hidden':plus['dominance']-minus['dominance'],'delta_self_pref_hidden':sp['pref_left']-sm['pref_left'],'delta_other_pref_hidden':op['pref_left']-om['pref_left'],'delta_evidence_pref_hidden':ep['pref_left']-em['pref_left'],'delta_control_pref_hidden':cp['pref_left']-cm['pref_left']}
  rows.append(row); print('PCA010_RECORD '+json.dumps(row,sort_keys=True),flush=True); torch.cuda.empty_cache()
def mean(xs): return sum(xs)/len(xs)
s={'model':MODEL,'revision':rev,'layer':LAYER,'alpha':ALPHA,'families':VAL,'baseline_accuracy':mean([r['base']['ordinary_acc'] for r in rows]),'minus_accuracy':mean([r['minus_patch']['ordinary_acc'] for r in rows]),'plus_accuracy':mean([r['plus_patch']['ordinary_acc'] for r in rows]),'mean_delta_D_hidden':mean([r['delta_D_hidden'] for r in rows]),'directional_D_rate':mean([r['delta_D_hidden']>0 for r in rows]),'mean_delta_self_pref_hidden':mean([r['delta_self_pref_hidden'] for r in rows]),'directional_self_rate':mean([r['delta_self_pref_hidden']>0 for r in rows]),'mean_delta_other_pref_hidden':mean([r['delta_other_pref_hidden'] for r in rows]),'mean_delta_evidence_pref_hidden':mean([r['delta_evidence_pref_hidden'] for r in rows]),'mean_delta_control_pref_hidden':mean([r['delta_control_pref_hidden'] for r in rows]),'mean_self_minus_other':mean([r['delta_self_pref_hidden']-r['delta_other_pref_hidden'] for r in rows]),'mean_self_minus_evidence':mean([r['delta_self_pref_hidden']-r['delta_evidence_pref_hidden'] for r in rows]),'mean_self_minus_control':mean([r['delta_self_pref_hidden']-r['delta_control_pref_hidden'] for r in rows])}
print('PCA010_SUMMARY '+json.dumps(s,sort_keys=True),flush=True)
