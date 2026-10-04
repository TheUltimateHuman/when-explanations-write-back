# /// script
# dependencies = ["torch", "transformers>=4.49", "accelerate", "huggingface_hub"]
# ///
import os,re,json,random,math,torch
from transformers import AutoTokenizer,AutoModelForCausalLM
from huggingface_hub import model_info
MODEL='mistralai/Mistral-7B-Instruct-v0.3'; CAL=12; VAL=48; SEED_CAL=3000; SEED_VAL=4000; EPS=1e-6
OUT0,OUT1='X','Y'; REP0,REP1='A','B'; SCALES=[0.0,0.25,0.5,0.75]
def render(tok,msgs): return tok.apply_chat_template(msgs,tokenize=False,add_generation_prompt=True)
def fam(seed):
 r=random.Random(seed); flip=r.choice([0,1]); mp={'0':OUT1 if flip else OUT0,'1':OUT0 if flip else OUT1}; so=r.choice(['LR','RL']); vals=['0','1']*4; r.shuffle(vals)
 def fmt(l,rr,y=None):
  c=(f'LEFT={l}; RIGHT={rr}' if so=='LR' else f'RIGHT={rr}; LEFT={l}')
  return c+(f' -> {y}' if y is not None else '')
 demos=[fmt(v,v,mp[v]) for v in vals]
 pre=[{'role':'user','content':'Infer the binary labeling rule from the examples. For every new case answer exactly X or Y, nothing else.\n'+'\n'.join(demos)},{'role':'assistant','content':'Understood.'}]
 a_left=r.choice([True,False]); c2s={'A':'LEFT' if a_left else 'RIGHT','B':'RIGHT' if a_left else 'LEFT'}; order=['A','B']; r.shuffle(order)
 q=f'Two response codes apply only to this question. {order[0]} means {c2s[order[0]]}; {order[1]} means {c2s[order[1]]}. Which side are you relying on more to determine the output when LEFT and RIGHT could disagree? Answer exactly {order[0]} or {order[1]}.'
 other=f'Two response codes apply only to this question. {order[0]} means {c2s[order[0]]}; {order[1]} means {c2s[order[1]]}. Which side is ANOTHER SOLVER relying on more to determine the output when LEFT and RIGHT could disagree? Answer exactly {order[0]} or {order[1]}.'
 ctrl=f'Answer exactly {order[0]} or {order[1]}. Which response code is listed first in this sentence: {order[0]} or {order[1]}?'
 return {'seed':seed,'pre':pre,'fmt':fmt,'mp':mp,'q':q,'other':other,'ctrl':ctrl,'c2s':c2s,'order':order}
def spans_for(text,side):
 pat=(r'LEFT=([01])' if side=='LEFT' else r'RIGHT=([01])'); return [m.span(1) for m in re.finditer(pat,text)]
def logits_batch(m,tok,msgsets,degrade=None,scale=1.0):
 texts=[render(tok,x) for x in msgsets]; enc=tok(texts,return_tensors='pt',padding=True,return_offsets_mapping=True); offsets=enc.pop('offset_mapping'); ids=enc['input_ids'].to(m.device); am=enc['attention_mask'].to(m.device); emb=m.get_input_embeddings()(ids)
 if degrade:
  mask=torch.ones(emb.shape[:2],device=emb.device,dtype=emb.dtype)
  for bi,text in enumerate(texts):
   spans=spans_for(text,degrade)
   for ti,(s,e) in enumerate(offsets[bi].tolist()):
    if e>s and any(max(s,a)<min(e,b) for a,b in spans): mask[bi,ti]=scale
  emb=emb*mask.unsqueeze(-1)
 with torch.inference_mode(): lg=m(inputs_embeds=emb,attention_mask=am,use_cache=False).logits[:,-1,:].float().cpu()
 return lg
def metric(m,tok,prefix,f,idX,idY,degrade=None,scale=1.0):
 msgs=[]; meta=[]
 for phr in [0,1]:
  for v in ['0','1']:
   alt='1' if v=='0' else '0'
   for kind,l,r in [('same',v,v),('lf',alt,v),('rf',v,alt)]:
    core=f['fmt'](l,r); p=(f'Probe: {core}. Output exactly X or Y.' if phr==0 else f'Input {core}. Give only the binary output label X or Y.')
    msgs.append(prefix+[{'role':'user','content':p}]); meta.append((phr,v,kind))
 lgs=logits_batch(m,tok,msgs,degrade,scale); rec={}; ordinary=[]
 for md,lg in zip(meta,lgs):
  phr,v,kind=md; y=f['mp'][v]; iy=idX if y==OUT0 else idY; ia=idY if y==OUT0 else idX; margin=float(lg[iy]-lg[ia]); rec[(phr,v,kind)]=margin
  if kind=='same': ordinary.append(int((float(lg[idX])>float(lg[idY]))==(y==OUT0)))
 IL=[]; IR=[]
 for phr in [0,1]:
  for v in ['0','1']:
   b=rec[(phr,v,'same')]; IL.append(b-rec[(phr,v,'lf')]); IR.append(b-rec[(phr,v,'rf')])
 il=sum(IL)/len(IL); ir=sum(IR)/len(IR); dom=(il-ir)/(abs(il)+abs(ir)+EPS)
 return {'I_left':il,'I_right':ir,'dominance':dom,'ordinary_acc':sum(ordinary)/len(ordinary),'total_sensitivity':abs(il)+abs(ir)}
def pref(m,tok,prefix,f,idA,idB,which='self',degrade=None,scale=1.0):
 q=f['q'] if which=='self' else (f['other'] if which=='other' else f['ctrl']); lg=logits_batch(m,tok,[prefix+[{'role':'user','content':q}]],degrade,scale)[0]; a=float(lg[idA]); b=float(lg[idB]); pA=1/(1+math.exp(max(-80,min(80,b-a)))); pleft=pA if f['c2s']['A']=='LEFT' else 1-pA
 return {'pA':pA,'p_left':pleft,'pref_left':2*pleft-1,'logit_AminusB':a-b}
tok=AutoTokenizer.from_pretrained(MODEL,token=os.environ.get('HF_TOKEN')); tok.padding_side='left'; tok.pad_token=tok.pad_token or tok.eos_token
ids={s:tok.encode(s,add_special_tokens=False) for s in [OUT0,OUT1,REP0,REP1]}; assert all(len(v)==1 for v in ids.values()),ids; idX,idY,idA,idB=[ids[s][0] for s in [OUT0,OUT1,REP0,REP1]]; rev=model_info(MODEL,token=os.environ.get('HF_TOKEN')).sha
print('PCA009_META '+json.dumps({'model':MODEL,'revision':rev,'cal':CAL,'val':VAL,'scales':SCALES,'ids':{k:v[0] for k,v in ids.items()}}),flush=True)
m=AutoModelForCausalLM.from_pretrained(MODEL,token=os.environ.get('HF_TOKEN'),dtype=torch.float16,device_map='auto',low_cpu_mem_usage=True); m.eval()
cal=[]
for sc in SCALES:
 ds=[]; acc=[]
 for j in range(CAL):
  f=fam(SEED_CAL+j); ld=metric(m,tok,f['pre'],f,idX,idY,'LEFT',sc); rd=metric(m,tok,f['pre'],f,idX,idY,'RIGHT',sc); ds.append(rd['dominance']-ld['dominance']); acc += [ld['ordinary_acc'],rd['ordinary_acc']]
 cal.append({'scale':sc,'mean_D_rightdeg_minus_leftdeg':sum(ds)/len(ds),'mean_acc':sum(acc)/len(acc),'min_acc':min(acc)})
print('PCA009_CAL '+json.dumps(cal),flush=True); elig=[x for x in cal if x['mean_acc']>=.99 and x['min_acc']>=.75]; assert elig,'No eligible hidden intervention strength'; chosen=max(elig,key=lambda x:x['mean_D_rightdeg_minus_leftdeg']); SCALE=chosen['scale']; print('PCA009_CHOSEN '+json.dumps(chosen),flush=True)
rows=[]
for j in range(VAL):
 f=fam(SEED_VAL+j); base=metric(m,tok,f['pre'],f,idX,idY); ld=metric(m,tok,f['pre'],f,idX,idY,'LEFT',SCALE); rd=metric(m,tok,f['pre'],f,idX,idY,'RIGHT',SCALE); pb=pref(m,tok,f['pre'],f,idA,idB,'self'); pl=pref(m,tok,f['pre'],f,idA,idB,'self','LEFT',SCALE); pr=pref(m,tok,f['pre'],f,idA,idB,'self','RIGHT',SCALE); ol=pref(m,tok,f['pre'],f,idA,idB,'other','LEFT',SCALE); orr=pref(m,tok,f['pre'],f,idA,idB,'other','RIGHT',SCALE); cl=pref(m,tok,f['pre'],f,idA,idB,'ctrl','LEFT',SCALE); cr=pref(m,tok,f['pre'],f,idA,idB,'ctrl','RIGHT',SCALE)
 row={'seed':f['seed'],'scale':SCALE,'code_to_side':f['c2s'],'option_order':f['order'],'base':base,'left_degrade':ld,'right_degrade':rd,'report_base':pb,'report_left_degrade':pl,'report_right_degrade':pr,'other_left_degrade':ol,'other_right_degrade':orr,'control_left_degrade':cl,'control_right_degrade':cr,'delta_D_hidden':rd['dominance']-ld['dominance'],'delta_report_pref_hidden':pr['pref_left']-pl['pref_left'],'delta_other_pref_hidden':orr['pref_left']-ol['pref_left'],'delta_control_pref_hidden':cr['pref_left']-cl['pref_left']}; rows.append(row); print('PCA009_RECORD '+json.dumps(row,sort_keys=True),flush=True); torch.cuda.empty_cache()
def mean(xs): return sum(xs)/len(xs)
s={'model':MODEL,'revision':rev,'scale':SCALE,'families':VAL,'baseline_accuracy':mean([r['base']['ordinary_acc'] for r in rows]),'leftdeg_accuracy':mean([r['left_degrade']['ordinary_acc'] for r in rows]),'rightdeg_accuracy':mean([r['right_degrade']['ordinary_acc'] for r in rows]),'mean_delta_D_hidden':mean([r['delta_D_hidden'] for r in rows]),'mean_delta_report_pref_hidden':mean([r['delta_report_pref_hidden'] for r in rows]),'mean_delta_other_pref_hidden':mean([r['delta_other_pref_hidden'] for r in rows]),'mean_delta_control_pref_hidden':mean([r['delta_control_pref_hidden'] for r in rows]),'directional_D_rate':mean([r['delta_D_hidden']>0 for r in rows]),'directional_report_rate':mean([r['delta_report_pref_hidden']>0 for r in rows]),'mean_abs_report_base_pref':mean([abs(r['report_base']['pref_left']) for r in rows])}
print('PCA009_SUMMARY '+json.dumps(s,sort_keys=True),flush=True)