# /// script
# dependencies = ["torch", "transformers>=4.49", "accelerate", "huggingface_hub", "numpy"]
# ///
import os, json, random, torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import model_info
MODEL='mistralai/Mistral-7B-Instruct-v0.3'; CAL=12; VAL=48; CAL_SEED=9000; VAL_SEED=10000; EPS=1e-6
TASKS=['DIRECT','XOR','MOD3']; OUTS={'DIRECT':['X','Y'],'XOR':['X','Y'],'MOD3':['X','Y','Z']}
def family(task,seed):
 r=random.Random(sum(map(ord,task))*1000003+seed*7919); outs=OUTS[task][:]; perm=outs[:]; r.shuffle(perm); k=2 if task!='MOD3' else 3; om={i:perm[i] for i in range(k)}; al=r.choice([1,0]); c2s={'A':'LEFT' if al else 'RIGHT','B':'RIGHT' if al else 'LEFT'}; order=['A','B']; r.shuffle(order); so=r.choice(['LR','RL'])
 def fmt(zl,zr,m=None,label=None):
  p=[]; p += ([] if m is None else [f'MODE={m}']); p += ([f'LEFT={zl}',f'RIGHT={zr}'] if so=='LR' else [f'RIGHT={zr}',f'LEFT={zl}']); s='; '.join(p); return s+(f' -> {label}' if label else '')
 if task=='DIRECT': intro='Use the shared LEFT/RIGHT bit as the hidden result. Infer from the examples which output label corresponds to result 0 and result 1. For every new case answer exactly X or Y, nothing else.'; combos=[(z,None) for z in range(2)]*4; r.shuffle(combos); demos=[fmt(z,z,None,om[z]) for z,_ in combos]
 elif task=='XOR': intro='When LEFT and RIGHT agree on bit z, compute hidden result z XOR MODE. Infer from the examples which output label corresponds to result 0 and result 1. For every new case answer exactly X or Y, nothing else.'; combos=[(z,m) for z in range(2) for m in range(2)]*2; r.shuffle(combos); demos=[fmt(z,z,m,om[z^m]) for z,m in combos]
 else: intro='When LEFT and RIGHT agree on value z, compute hidden result (z + MODE) mod 3. Infer from the examples which output label corresponds to results 0, 1, and 2. For every new case answer exactly X, Y, or Z, nothing else.'; combos=[(z,m) for z in range(3) for m in range(3)]; r.shuffle(combos); demos=[fmt(z,z,m,om[(z+m)%3]) for z,m in combos]
 pre=[{'role':'user','content':intro+'\n'+'\n'.join(demos)},{'role':'assistant','content':'Understood.'}]; q=f'Two response codes apply only to this question. {order[0]} means {c2s[order[0]]}; {order[1]} means {c2s[order[1]]}. Which side are YOU relying on more to determine the output when LEFT and RIGHT could disagree? Answer exactly {order[0]} or {order[1]}.'
 return {'task':task,'seed':seed,'k':k,'outmap':om,'pre':pre,'fmt':fmt,'c2s':c2s,'order':order,'q':q}
def truth(t,z,m): return z if t=='DIRECT' else (z^m if t=='XOR' else (z+m)%3)
def render(tok,msgs): return tok.apply_chat_template(msgs,tokenize=False,add_generation_prompt=True)
def blogs(model,tok,msgsets):
 texts=[render(tok,m) for m in msgsets]; enc=tok(texts,return_tensors='pt',padding=True,add_special_tokens=False).to(model.device)
 with torch.inference_mode(): lg=model(**enc,use_cache=False).logits[:,-1,:].float().cpu()
 return lg
def metric(model,tok,f,prefix,oid):
 t=f['task']; k=f['k']; modes=[None] if t=='DIRECT' else list(range(k if t=='MOD3' else 2)); msgs=[]; meta=[]
 for phr in [0,1]:
  for z in range(k):
   for m in modes:
    alt=(z+1)%k
    for kind,zl,zr in [('same',z,z),('lf',alt,z),('rf',z,alt)]:
     core=f['fmt'](zl,zr,m); ask=(f'Probe: {core}. Output only the required label.' if phr==0 else f'Input {core}. Give exactly one output label.'); msgs.append(prefix+[{'role':'user','content':ask}]); meta.append((z,m,kind))
 L=blogs(model,tok,msgs); rec={}; acc=[]; labs=OUTS[t]; labids=[oid[x] for x in labs]
 for md,lg in zip(meta,L):
  z,m,kind=md; y=f['outmap'][truth(t,z,m)]; iy=oid[y]; alts=[oid[o] for o in labs if o!=y]; margin=float(lg[iy]-torch.max(lg[alts])); rec.setdefault((z,m,kind),[]).append(margin)
  if kind=='same': acc.append(int(labs[int(torch.argmax(lg[labids]))]==y))
 IL=[]; IR=[]
 for z in range(k):
  for m in modes:
   b=np.mean(rec[(z,m,'same')]); IL.append(b-np.mean(rec[(z,m,'lf')])); IR.append(b-np.mean(rec[(z,m,'rf')]))
 il=float(np.mean(IL)); ir=float(np.mean(IR)); return {'I_left':il,'I_right':ir,'dominance':(il-ir)/(abs(il)+abs(ir)+EPS),'ordinary_acc':float(np.mean(acc)),'total_sensitivity':abs(il)+abs(ir)}
def report(model,tok,f,idA,idB):
 lg=blogs(model,tok,[f['pre']+[{'role':'user','content':f['q']} ]])[0]; a=float(lg[idA]); b=float(lg[idB]); raw=a-b; code='A' if raw>=0 else 'B'; side=f['c2s'][code]; orient=1 if f['c2s']['A']=='LEFT' else -1; return {'code':code,'side':side,'logit_AminusB':raw,'pref_left_logit':orient*raw,'confidence':abs(raw)}
tok=AutoTokenizer.from_pretrained(MODEL); tok.padding_side='left'; tok.pad_token=tok.pad_token or tok.eos_token; ids={s:tok.encode(s,add_special_tokens=False) for s in ['X','Y','Z','A','B']}; assert all(len(ids[s])==1 for s in ['X','Y','A','B']),ids; mod3ok=len(ids['Z'])==1; oid={s:ids[s][0] for s in ['X','Y']}; oid.update({'Z':ids['Z'][0]} if mod3ok else {}); idA,idB=ids['A'][0],ids['B'][0]; rev=model_info(MODEL).sha; print('PCA012_META '+json.dumps({'model':MODEL,'revision':rev,'tasks':TASKS,'mod3_token_ok':mod3ok,'ids':ids}),flush=True)
model=AutoModelForCausalLM.from_pretrained(MODEL,dtype=torch.float16,device_map='auto',low_cpu_mem_usage=True); model.eval(); elig={}; cal={}
for ti,t in enumerate(TASKS):
 if t=='MOD3' and not mod3ok: cal[t]={'eligible':False,'reason':'Z_not_single_token'}; elig[t]=False; continue
 aa=[]; ss=[]
 for j in range(CAL):
  f=family(t,CAL_SEED+ti*1000+j); mm=metric(model,tok,f,f['pre'],oid); aa.append(mm['ordinary_acc']); ss.append(mm['total_sensitivity'])
 cal[t]={'mean_acc':float(np.mean(aa)),'min_acc':float(np.min(aa)),'mean_sensitivity':float(np.mean(ss)),'eligible':float(np.mean(aa))>=.98}; elig[t]=cal[t]['eligible']
print('PCA012_CAL '+json.dumps(cal,sort_keys=True),flush=True); rows=[]
for ti,t in enumerate(TASKS):
 if not elig.get(t): continue
 for j in range(VAL):
  f=family(t,VAL_SEED+ti*1000+j); base=metric(model,tok,f,f['pre'],oid); rep=report(model,tok,f,idA,idB); code=rep['code']; side=rep['side']; sgn=1 if side=='LEFT' else -1; q=f['q']; qpre=f['pre']+[{'role':'user','content':q},{'role':'assistant','content':'UNSURE'}]; spre=f['pre']+[{'role':'user','content':q},{'role':'assistant','content':code}]; cL='A' if f['c2s']['A']=='LEFT' else 'B'; cR='A' if f['c2s']['A']=='RIGHT' else 'B'; lpre=f['pre']+[{'role':'user','content':q},{'role':'assistant','content':cL}]; rpre=f['pre']+[{'role':'user','content':q},{'role':'assistant','content':cR}]; qc=metric(model,tok,f,qpre,oid); post=metric(model,tok,f,spre,oid); fl=metric(model,tok,f,lpre,oid); fr=metric(model,tok,f,rpre,oid); row={'task':t,'seed':f['seed'],'code_to_side':f['c2s'],'option_order':f['order'],'report':rep,'base':base,'question_control':qc,'post_report':post,'forced_left':fl,'forced_right':fr,'pre_alignment':sgn*base['dominance'],'post_alignment':sgn*post['dominance'],'delta_total':sgn*(post['dominance']-base['dominance']),'delta_question':sgn*(qc['dominance']-base['dominance']),'delta_answer':sgn*(post['dominance']-qc['dominance']),'forced_contrast':fl['dominance']-fr['dominance']}; rows.append(row); print('PCA012_RECORD '+json.dumps(row,sort_keys=True),flush=True); torch.cuda.empty_cache()
def mean(t,k): return float(np.mean([r[k] for r in rows if r['task']==t]))
sumry={'model':MODEL,'revision':rev,'calibration':cal,'eligible_tasks':[t for t in TASKS if elig.get(t)],'rows':len(rows)}
for t in sumry['eligible_tasks']:
 rr=[r for r in rows if r['task']==t]; sumry[t]={'n':len(rr),'baseline_accuracy':float(np.mean([r['base']['ordinary_acc'] for r in rr])),'post_accuracy':float(np.mean([r['post_report']['ordinary_acc'] for r in rr])),'report_left_rate':float(np.mean([r['report']['side']=='LEFT' for r in rr])),'mean_pre_alignment':mean(t,'pre_alignment'),'mean_post_alignment':mean(t,'post_alignment'),'mean_delta_total':mean(t,'delta_total'),'mean_delta_question':mean(t,'delta_question'),'mean_delta_answer':mean(t,'delta_answer'),'mean_forced_contrast':mean(t,'forced_contrast')}
print('PCA012_SUMMARY '+json.dumps(sumry,sort_keys=True),flush=True)