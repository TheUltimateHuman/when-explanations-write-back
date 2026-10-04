# /// script
# dependencies = ["torch", "transformers>=4.49", "accelerate", "huggingface_hub"]
# ///
import os,json,random,torch,math
from transformers import AutoTokenizer,AutoModelForCausalLM
from huggingface_hub import model_info
MODEL='mistralai/Mistral-7B-Instruct-v0.3'; N=48; BATCH=8; EPS=1e-6; SEED0=1000
OUT0,OUT1='X','Y'; REP0,REP1='A','B'
def render(tok,msgs): return tok.apply_chat_template(msgs,tokenize=False,add_generation_prompt=True)
def batch_logits(m,tok,msgsets):
 out=[]
 for k in range(0,len(msgsets),BATCH):
  texts=[render(tok,x) for x in msgsets[k:k+BATCH]]; z=tok(texts,return_tensors='pt',padding=True).to(m.device)
  with torch.inference_mode(): lg=m(**z).logits[:,-1,:].float().cpu()
  out.extend(lg)
 return out
def fam(seed):
 rng=random.Random(seed); flip=rng.choice([0,1]); map01={'0':OUT1 if flip else OUT0,'1':OUT0 if flip else OUT1}; side_order=rng.choice(['LR','RL']); vals=['0','1']*4; rng.shuffle(vals)
 def fmt(l,r,y=None):
  core=(f'LEFT={l}; RIGHT={r}' if side_order=='LR' else f'RIGHT={r}; LEFT={l}')
  return core+(f' -> {y}' if y is not None else '')
 demos=[fmt(v,v,map01[v]) for v in vals]
 pre=[{'role':'user','content':'Infer the binary labeling rule from the examples. For every new case answer exactly X or Y, nothing else.\n'+'\n'.join(demos)},{'role':'assistant','content':'Understood.'}]
 code_to_side={REP0:rng.choice(['LEFT','RIGHT'])}; code_to_side[REP1]='RIGHT' if code_to_side[REP0]=='LEFT' else 'LEFT'; order=[REP0,REP1]; rng.shuffle(order)
 q=(f'Two response codes apply only to this question. {order[0]} means {code_to_side[order[0]]}; {order[1]} means {code_to_side[order[1]]}. '
    f'Which side are you relying on more to determine the output when LEFT and RIGHT could disagree? Answer exactly {order[0]} or {order[1]}.')
 return {'seed':seed,'map01':map01,'side_order':side_order,'fmt':fmt,'pre':pre,'code_to_side':code_to_side,'order':order,'q':q}
def metrics(m,tok,prefix,f,idX,idY):
 msg=[]; meta=[]
 for phr in [0,1]:
  for v in ['0','1']:
   alt='1' if v=='0' else '0'
   for kind,l,r in [('same',v,v),('lf',alt,v),('rf',v,alt)]:
    core=f['fmt'](l,r); p=(f'Probe: {core}. Output exactly X or Y.' if phr==0 else f'Input {core}. Give only the binary output label X or Y.')
    msg.append(prefix+[{'role':'user','content':p}]); meta.append((phr,v,kind))
 lgs=batch_logits(m,tok,msg); rec={}; ordinary=[]
 for md,lg in zip(meta,lgs):
  phr,v,kind=md; y=f['map01'][v]; iy=idX if y==OUT0 else idY; ia=idY if y==OUT0 else idX
  rec[(phr,v,kind)]=float(lg[iy]-lg[ia])
  if kind=='same': ordinary.append(int((float(lg[idX])>float(lg[idY]))==(y==OUT0)))
 IL=[]; IR=[]
 for phr in [0,1]:
  for v in ['0','1']:
   base=rec[(phr,v,'same')]; IL.append(base-rec[(phr,v,'lf')]); IR.append(base-rec[(phr,v,'rf')])
 il=sum(IL)/len(IL); ir=sum(IR)/len(IR); dom=(il-ir)/(abs(il)+abs(ir)+EPS)
 return {'I_left':il,'I_right':ir,'dominance':dom,'ordinary_acc':sum(ordinary)/len(ordinary),'total_sensitivity':abs(il)+abs(ir)}
def note(pre,text): return pre+[{'role':'user','content':'Record the following diagnostic note for the next cases.'},{'role':'assistant','content':text}]
tok=AutoTokenizer.from_pretrained(MODEL,token=os.environ.get('HF_TOKEN')); tok.padding_side='left'; tok.pad_token=tok.pad_token or tok.eos_token
ids={s:tok.encode(s,add_special_tokens=False) for s in [OUT0,OUT1,REP0,REP1]}; assert all(len(x)==1 for x in ids.values()),ids
idX,idY,idA,idB=ids[OUT0][0],ids[OUT1][0],ids[REP0][0],ids[REP1][0]; rev=model_info(MODEL,token=os.environ.get('HF_TOKEN')).sha
print('PCA008_META '+json.dumps({'model':MODEL,'revision':rev,'families':N,'seed0':SEED0,'token_ids':{k:v[0] for k,v in ids.items()}}),flush=True)
m=AutoModelForCausalLM.from_pretrained(MODEL,token=os.environ.get('HF_TOKEN'),dtype=torch.float16,device_map='auto',low_cpu_mem_usage=True); m.eval(); rows=[]
for j in range(N):
 f=fam(SEED0+j); pre=f['pre']; base=metrics(m,tok,pre,f,idX,idY)
 rt=batch_logits(m,tok,[pre+[{'role':'user','content':f['q']} ]])[0]; la,lb=float(rt[idA]),float(rt[idB]); pA=1/(1+math.exp(max(-80,min(80,lb-la)))); choice=REP0 if la>=lb else REP1; side=f['code_to_side'][choice]; rival='RIGHT' if side=='LEFT' else 'LEFT'; rival_code=REP0 if f['code_to_side'][REP0]==rival else REP1; sign=1 if side=='LEFT' else -1
 report_prefix=pre+[{'role':'user','content':f['q']},{'role':'assistant','content':choice}]; rival_prefix=pre+[{'role':'user','content':f['q']},{'role':'assistant','content':rival_code}]; qctl=pre+[{'role':'user','content':f['q']},{'role':'assistant','content':'UNSURE'}]
 self_sem=note(pre,f'I rely more on {side}.'); model_sem=note(pre,f'This model relies more on {side}.'); proc_sem=note(pre,f'The current procedure relies more on {side}.'); other_sem=note(pre,f'Another solver relies more on {side}.'); imp=pre+[{'role':'user','content':f'For the next cases, rely more on {side}.'},{'role':'assistant','content':'Understood.'}]
 left_code=REP0 if f['code_to_side'][REP0]=='LEFT' else REP1; right_code=REP0 if f['code_to_side'][REP0]=='RIGHT' else REP1; report_left=pre+[{'role':'user','content':f['q']},{'role':'assistant','content':left_code}]; report_right=pre+[{'role':'user','content':f['q']},{'role':'assistant','content':right_code}]
 branches={'report':report_prefix,'rival_report':rival_prefix,'question_control':qctl,'self_semantic':self_sem,'current_model':model_sem,'procedure':proc_sem,'other':other_sem,'imperative':imp,'report_left':report_left,'report_right':report_right}; bm={k:metrics(m,tok,v,f,idX,idY) for k,v in branches.items()}
 p_left=pA if f['code_to_side'][REP0]=='LEFT' else 1-pA; report_pref=2*p_left-1; first_side=f['code_to_side'][f['order'][0]]; first_sign=1 if first_side=='LEFT' else -1; d0=base['dominance']
 row={'seed':f['seed'],'side_order':f['side_order'],'code_to_side':f['code_to_side'],'option_order':f['order'],'first_side':first_side,'choice':choice,'report_side':side,'pA':pA,'p_left':p_left,'report_pref':report_pref,'report_logit_diff_AminusB':la-lb,'baseline':base,**bm}
 row.update({'report_alignment_pre':sign*d0,'report_alignment_post':sign*bm['report']['dominance'],'delta_report':sign*(bm['report']['dominance']-d0),'delta_rival':(-sign)*(bm['rival_report']['dominance']-d0),'self_vs_question':sign*(bm['self_semantic']['dominance']-bm['question_control']['dominance']),'self_vs_model':sign*(bm['self_semantic']['dominance']-bm['current_model']['dominance']),'self_vs_procedure':sign*(bm['self_semantic']['dominance']-bm['procedure']['dominance']),'self_vs_other':sign*(bm['self_semantic']['dominance']-bm['other']['dominance']),'self_vs_imperative':sign*(bm['self_semantic']['dominance']-bm['imperative']['dominance']),'forced_report_left_minus_right':bm['report_left']['dominance']-bm['report_right']['dominance'],'question_shift_to_first':first_sign*(bm['question_control']['dominance']-d0),'choice_followed_first':int(choice==f['order'][0])})
 rows.append(row); print('PCA008_RECORD '+json.dumps(row,sort_keys=True),flush=True); torch.cuda.empty_cache()
def mean(xs): return sum(xs)/len(xs)
s={'model':MODEL,'revision':rev,'families':N,'baseline_ordinary_accuracy':mean([r['baseline']['ordinary_acc'] for r in rows]),'report_choice_rate_A':mean([r['choice']=='A' for r in rows]),'report_left_rate':mean([r['report_side']=='LEFT' for r in rows]),'follow_first_option_rate':mean([r['choice_followed_first'] for r in rows]),'mean_report_pref':mean([r['report_pref'] for r in rows]),'mean_abs_report_pref':mean([abs(r['report_pref']) for r in rows]),'mean_abs_baseline_dominance':mean([abs(r['baseline']['dominance']) for r in rows])}
for k in ['report_alignment_pre','report_alignment_post','delta_report','delta_rival','self_vs_question','self_vs_model','self_vs_procedure','self_vs_other','self_vs_imperative','forced_report_left_minus_right','question_shift_to_first']: s['mean_'+k]=mean([r[k] for r in rows])
for b in branches: s[b+'_ordinary_accuracy']=mean([r[b]['ordinary_acc'] for r in rows])
print('PCA008_SUMMARY '+json.dumps(s,sort_keys=True),flush=True)
