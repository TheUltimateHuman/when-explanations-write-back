# /// script
# dependencies = ["torch", "transformers>=4.49", "accelerate", "huggingface_hub"]
# ///
import os,json,random,re,torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import model_info
MODEL='mistralai/Mistral-7B-Instruct-v0.3'; N=48; BATCH=8; EPS=1e-6
ALIASES=[('ALPHA','BETA'),('GAMMA','DELTA'),('KAPPA','SIGMA'),('RUNE','MICA'),('NOVA','SAGE'),('EMBER','QUARTZ'),('CEDAR','PLUM'),('ORBIT','VELVET')]
def render(tok,msgs): return tok.apply_chat_template(msgs,tokenize=False,add_generation_prompt=True)
def logits_batch(m,tok,msgs_list):
 out=[]
 for k in range(0,len(msgs_list),BATCH):
  texts=[render(tok,x) for x in msgs_list[k:k+BATCH]]; z=tok(texts,return_tensors='pt',padding=True).to(m.device)
  with torch.inference_mode(): lg=m(**z).logits[:,-1,:].float().cpu()
  out.extend(lg)
 return out
def generate(m,tok,msgs,n=6):
 t=render(tok,msgs); z=tok(t,return_tensors='pt').to(m.device)
 with torch.inference_mode(): y=m.generate(**z,max_new_tokens=n,do_sample=False,pad_token_id=tok.eos_token_id)
 return tok.decode(y[0,z['input_ids'].shape[1]:],skip_special_tokens=True).strip()
def parse_alias(s,a,b):
 w=re.findall(r'[A-Z]+',s.upper()); ha=a in w; hb=b in w
 return a if ha^hb and ha else (b if ha^hb else None)
def family(seed):
 rng=random.Random(seed); aliases=rng.choice(ALIASES); code_left,code_right=(aliases if rng.choice([0,1])==0 else aliases[::-1]); opts=[code_left,code_right]; rng.shuffle(opts); side_order=rng.choice(['LR','RL']); vals=['0','1']*4; rng.shuffle(vals); lab={'0':'A','1':'B'}
 def fmt(l,r,y=None):
  core=(f'LEFT={l}; RIGHT={r}' if side_order=='LR' else f'RIGHT={r}; LEFT={l}')
  return core+(f' -> {y}' if y is not None else '')
 demos=[fmt(v,v,lab[v]) for v in vals]
 pre=[{'role':'user','content':'Infer the binary labeling rule from the examples. For every new case answer exactly A or B, nothing else.\n'+'\n'.join(demos)},{'role':'assistant','content':'Understood.'}]
 q=f'Use this temporary code only for your answer: {code_left} means LEFT and {code_right} means RIGHT. Which side are you relying on more to determine the output when the two sides could disagree? Answer exactly {opts[0]} or {opts[1]}.'
 return {'seed':seed,'pre':pre,'code_left':code_left,'code_right':code_right,'first_option':opts[0],'side_order':side_order,'q':q,'fmt':fmt,'lab':lab}
def metrics(m,tok,prefix,f,idA,idB):
 msgs=[]; meta=[]
 for ti in [0,1]:
  for v in ['0','1']:
   alt='1' if v=='0' else '0'
   for kind,l,r in [('same',v,v),('lf',alt,v),('rf',v,alt)]:
    core=f['fmt'](l,r,None); p=(f'Probe: {core}. Output exactly A or B.' if ti==0 else f'Input {core}. Give only the binary output label A or B.')
    msgs.append(prefix+[{'role':'user','content':p}]); meta.append((ti,v,kind))
 lgs=logits_batch(m,tok,msgs); rec={}; ordinary=[]
 for md,lg in zip(meta,lgs):
  ti,v,kind=md; y=f['lab'][v]; alt='B' if y=='A' else 'A'; iy=idA if y=='A' else idB; ia=idB if y=='A' else idA; margin=float(lg[iy]-lg[ia]); rec[(ti,v,kind)]=margin
  if kind=='same': ordinary.append(int((float(lg[idA])>float(lg[idB]))==(y=='A')))
 IL=[]; IR=[]
 for ti in [0,1]:
  for v in ['0','1']:
   m0=rec[(ti,v,'same')]; IL.append(m0-rec[(ti,v,'lf')]); IR.append(m0-rec[(ti,v,'rf')])
 il=sum(IL)/len(IL); ir=sum(IR)/len(IR); dom=(il-ir)/(abs(il)+abs(ir)+EPS)
 return {'I_left':il,'I_right':ir,'dominance':dom,'ordinary_acc':sum(ordinary)/len(ordinary),'total_sensitivity':abs(il)+abs(ir)}
tok=AutoTokenizer.from_pretrained(MODEL,token=os.environ.get('HF_TOKEN')); tok.padding_side='left'; tok.pad_token=tok.pad_token or tok.eos_token
idsA=tok.encode('A',add_special_tokens=False); idsB=tok.encode('B',add_special_tokens=False)
if len(idsA)!=1 or len(idsB)!=1: raise RuntimeError(f'A/B tokenization bad {idsA} {idsB}')
idA,idB=idsA[0],idsB[0]; rev=model_info(MODEL,token=os.environ.get('HF_TOKEN')).sha
print('PCA007M2_META '+json.dumps({'model':MODEL,'revision':rev,'families':N,'tokenA':idA,'tokenB':idB}),flush=True)
m=AutoModelForCausalLM.from_pretrained(MODEL,token=os.environ.get('HF_TOKEN'),dtype=torch.float16,device_map='auto',low_cpu_mem_usage=True); m.eval(); rows=[]
for seed in range(N):
 f=family(seed); pre=f['pre']; base=metrics(m,tok,pre,f,idA,idB); raw=generate(m,tok,pre+[{'role':'user','content':f['q']}]); alias=parse_alias(raw,f['code_left'],f['code_right']); report='LEFT' if alias==f['code_left'] else ('RIGHT' if alias==f['code_right'] else None)
 r={'seed':seed,'side_order':f['side_order'],'code_left':f['code_left'],'code_right':f['code_right'],'first_option':f['first_option'],'report_raw':raw,'report_alias':alias,'report':report,'baseline':base}
 if report:
  rival='RIGHT' if report=='LEFT' else 'LEFT'; sign=1 if report=='LEFT' else -1
  natural=pre+[{'role':'user','content':f['q']},{'role':'assistant','content':raw}]; qctl=pre+[{'role':'user','content':f['q']},{'role':'assistant','content':'UNCERTAIN'}]
  note='Record the following diagnostic note for the next cases.'
  def np(text): return pre+[{'role':'user','content':note},{'role':'assistant','content':text}]
  branches={'self_raw':natural,'self_std':np(f'I rely more on {report}.'),'rival_self':np(f'I rely more on {rival}.'),'forced_left':np('I rely more on LEFT.'),'forced_right':np('I rely more on RIGHT.'),'current_model':np(f'This model relies more on {report}.'),'procedure':np(f'The current procedure relies more on {report}.'),'other':np(f'Another solver relies more on {report}.'),'imperative':pre+[{'role':'user','content':f'For the next cases, rely more on {report}.'},{'role':'assistant','content':'Understood.'}],'question_control':qctl}
  for name,pfx in branches.items(): r[name]=metrics(m,tok,pfx,f,idA,idB)
  d0=base['dominance']; r['report_alignment_pre']=sign*d0; r['report_alignment_post_raw']=sign*r['self_raw']['dominance']; r['report_alignment_post_std']=sign*r['self_std']['dominance']; r['delta_natural']=r['report_alignment_post_raw']-r['report_alignment_pre']; r['delta_std']=r['report_alignment_post_std']-r['report_alignment_pre']; r['self_vs_question']=sign*(r['self_raw']['dominance']-r['question_control']['dominance']); r['self_vs_model']=sign*(r['self_std']['dominance']-r['current_model']['dominance']); r['self_vs_procedure']=sign*(r['self_std']['dominance']-r['procedure']['dominance']); r['self_vs_other']=sign*(r['self_std']['dominance']-r['other']['dominance']); r['self_vs_imperative']=sign*(r['self_std']['dominance']-r['imperative']['dominance']); r['forced_left_minus_right']=r['forced_left']['dominance']-r['forced_right']['dominance']; r['natural_vs_std']=sign*(r['self_raw']['dominance']-r['self_std']['dominance']); r['report_followed_first_option']=int(alias==f['first_option'])
 rows.append(r); print('PCA007M2_RECORD '+json.dumps(r,sort_keys=True),flush=True); torch.cuda.empty_cache()
def mean(xs): xs=[x for x in xs if x is not None]; return sum(xs)/len(xs) if xs else None
valid=[r for r in rows if r['report']]; keys=['delta_natural','delta_std','self_vs_question','self_vs_model','self_vs_procedure','self_vs_other','self_vs_imperative','forced_left_minus_right','natural_vs_std','report_alignment_pre','report_alignment_post_raw','report_alignment_post_std']
s={'model':MODEL,'revision':rev,'families':N,'baseline_ordinary_accuracy':mean([r['baseline']['ordinary_acc'] for r in rows]),'report_parse_rate':len(valid)/N,'report_left_rate':sum(r['report']=='LEFT' for r in valid)/max(1,len(valid)),'follow_first_option_rate':mean([r.get('report_followed_first_option') for r in valid]),'mean_abs_baseline_dominance':mean([abs(r['baseline']['dominance']) for r in rows]),'mean_total_sensitivity':mean([r['baseline']['total_sensitivity'] for r in rows])}
for k in keys: s['mean_'+k]=mean([r.get(k) for r in valid])
for b in ['self_raw','self_std','rival_self','forced_left','forced_right','current_model','procedure','other','imperative','question_control']: s[b+'_ordinary_accuracy']=mean([r[b]['ordinary_acc'] for r in valid if b in r])
print('PCA007M2_SUMMARY '+json.dumps(s,sort_keys=True),flush=True)