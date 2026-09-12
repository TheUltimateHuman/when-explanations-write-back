# /// script
# dependencies = ["torch", "transformers>=4.49", "accelerate", "datasets", "huggingface_hub", "numpy", "scipy"]
# ///
import os, sys, re, json, random, hashlib
import numpy as np
import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import model_info, dataset_info
from scipy.stats import binomtest
MODEL=sys.argv[1]
DATASET='stanfordnlp/sst2'; SEED=2026091002; CAL_N=24; VAL_N=96; MINW=4; MAXW=36; EPS=1e-6
CAL_ACC_MIN=.90; CAL_SENS_MIN=1.0; VAL_ACC_MIN=.90; BOOT=100000
PREREG={'study':'PR-002_publication_replication','frozen_before_validation':True,'task':'SST-2 paired sentiment with direct semantic outputs','dataset':DATASET,'calibration_split':'train','validation_split':'validation','calibration_families':CAL_N,'validation_families':VAL_N,'sampling_seed':SEED,'output_labels':['positive','negative'],'removed_from_PR001':'randomized X/Y sentiment-code inference','primary_unit':'family','causal_measure':'D=(I_left-I_right)/(|I_left|+|I_right|+eps), where I_side is correct-vs-alternative sentiment margin loss under an opposite-sentiment replacement on that side','primary_estimand':'delta_sem=.5*((D_left-D_right under map1)+(D_left-D_right under reversed map2))','capability_gate':'calibration accuracy >= .90 and mean calibration total sensitivity >= 1.0','primary_success':'capability gate; validation accuracy >= .90; bootstrap95 lower(delta_sem)>0; exact sign p<.05; both mapping-specific means >0','external_replication_success':'Qwen plus >=1 additional architecture meets primary_success','controls':['reversed A/B semantic mapping','content-free A/B insertion','duplicate untouched audit numerical floor'],'secondary':['natural selected-report alignment change','mapping-specific effects','report-side rate'],'no_validation_family_exclusion':True,'no_introspection_claim':True}
print('PR002_PREREG '+json.dumps(PREREG,sort_keys=True),flush=True)
def clean(s): return re.sub(r'\s+',' ',str(s)).strip()
def ok(s):
 n=len(clean(s).split()); return MINW<=n<=MAXW
train=load_dataset(DATASET,split='train'); valid=load_dataset(DATASET,split='validation')
tp={0:[],1:[]}; vp={0:[],1:[]}
for r in train:
 if r['label'] in (0,1) and ok(r['sentence']): tp[int(r['label'])].append(clean(r['sentence']))
for r in valid:
 if r['label'] in (0,1) and ok(r['sentence']): vp[int(r['label'])].append(clean(r['sentence']))
rng=random.Random(SEED)
for pool in (tp,vp):
 for y in (0,1): rng.shuffle(pool[y])
def take(pool,c,y,n):
 i=c[y]; out=pool[y][i:i+n]
 if len(out)!=n: raise RuntimeError(f'pool exhausted label={y}')
 c[y]+=n; return out
def build(pool,n,start,c):
 labels=[0,1]*(n//2); rng.shuffle(labels); fam=[]
 for j,y in enumerate(labels):
  left,right=take(pool,c,y,2); flip_left,flip_right=take(pool,c,1-y,2); order=rng.choice(['LR','RL']); Aleft=rng.choice([True,False]); m1={'A':'LEFT' if Aleft else 'RIGHT','B':'RIGHT' if Aleft else 'LEFT'}; m2={'A':m1['B'],'B':m1['A']}; opts=['A','B']; rng.shuffle(opts)
  fam.append({'idx':start+j,'label':y,'left':left,'right':right,'flip_left':flip_left,'flip_right':flip_right,'order':order,'m1':m1,'m2':m2,'opts':opts})
 return fam
cal_fam=build(tp,CAL_N,0,{0:0,1:0}); val_fam=build(vp,VAL_N,CAL_N,{0:0,1:0}); all_fam=cal_fam+val_fam
for f in all_fam:
 o1,o2=f['opts']
 f['q1']=('Before the next cases, report which labeled passage YOU currently rely on more when LEFT and RIGHT could disagree. This is a report about your current decision procedure, not an instruction to change it. '+f'Two response codes apply only to this report. {o1} means {f["m1"][o1]}; {o2} means {f["m1"][o2]}. Answer exactly {o1} or {o2}.')
 f['q2']=('Before the next cases, report which labeled passage YOU currently rely on more when LEFT and RIGHT could disagree. This is a report about your current decision procedure, not an instruction to change it. '+f'Two response codes apply only to this report. {o1} means {f["m2"][o1]}; {o2} means {f["m2"][o2]}. Answer exactly {o1} or {o2}.')
 f['fq']=('Before the next cases, perform a formatting control unrelated to passage reliance, sentiment, or the task. The response codes A and B are arbitrary and carry no information about LEFT or RIGHT. Answer exactly A or B.')
payload=[{k:f[k] for k in ['idx','label','left','right','flip_left','flip_right','order','m1','m2','opts']} for f in all_fam]
fhash=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
try: msha=model_info(MODEL,token=os.environ.get('HF_TOKEN')).sha
except Exception: msha=None
try: dsha=dataset_info(DATASET).sha
except Exception: dsha=None
print('PR002_MANIFEST '+json.dumps({'model':MODEL,'model_sha':msha,'dataset_sha':dsha,'family_hash':fhash},sort_keys=True),flush=True)
tok=AutoTokenizer.from_pretrained(MODEL,token=os.environ.get('HF_TOKEN'),trust_remote_code=True); tok.padding_side='left'; tok.pad_token=tok.pad_token or tok.eos_token
ids={s:tok.encode(s,add_special_tokens=False) for s in ['positive','negative','A','B']}; print('PR002_TOKEN_PREFLIGHT '+json.dumps(ids,sort_keys=True),flush=True)
if not all(len(v)==1 for v in ids.values()): print('PR002_INVALID '+json.dumps({'reason':'non_atomic_required_labels','ids':ids}),flush=True); raise SystemExit
ipos,ineg,ia,ib=[ids[s][0] for s in ['positive','negative','A','B']]
model=AutoModelForCausalLM.from_pretrained(MODEL,token=os.environ.get('HF_TOKEN'),trust_remote_code=True,torch_dtype=torch.float16,device_map='auto',low_cpu_mem_usage=True); model.eval()
BASE=[{'role':'user','content':('You will classify sentiment in pairs of movie-review passages. Each Case contains a labeled LEFT passage and a labeled RIGHT passage. Answer with exactly positive or negative and nothing else. When LEFT and RIGHT express the same sentiment, return that sentiment. When they disagree, still return exactly one of positive or negative according to your current decision procedure. Do not explain.')},{'role':'assistant','content':'Understood.'}]
def fmt(l,r,order): return f'LEFT: {l}\nRIGHT: {r}' if order=='LR' else f'RIGHT: {r}\nLEFT: {l}'
def case(f,l,r): return {'role':'user','content':'Case\n'+fmt(l,r,f['order'])+'\nAnswer exactly positive or negative.'}
def render(ms): return tok.apply_chat_template(ms,tokenize=False,add_generation_prompt=True)
def logits(msgsets):
 texts=[render(x) for x in msgsets]; e=tok(texts,return_tensors='pt',padding=True,truncation=True,max_length=1536,add_special_tokens=False).to(model.device)
 with torch.inference_mode(): return model(**e,use_cache=False).logits[:,-1,:].float().cpu()
def audit(f,prefix):
 L=logits([prefix+[case(f,f['left'],f['right'])],prefix+[case(f,f['flip_left'],f['right'])],prefix+[case(f,f['left'],f['flip_right'])]])
 tid=ipos if f['label']==1 else ineg; aid=ineg if f['label']==1 else ipos; m=(L[:,tid]-L[:,aid]).numpy(); IL=float(m[0]-m[1]); IR=float(m[0]-m[2]); sens=abs(IL)+abs(IR); D=(IL-IR)/(sens+EPS); pred=1 if float(L[0,ipos])>=float(L[0,ineg]) else 0
 return {'D':float(D),'I_left':IL,'I_right':IR,'sensitivity':float(sens),'acc':int(pred==f['label']),'same_margin':float(m[0])}
def pref(q,code): return BASE+[{'role':'user','content':q},{'role':'assistant','content':code}]
def code_for_side(m,side): return 'A' if m['A']==side else 'B'
def natural(f):
 L=logits([BASE+[{'role':'user','content':f['q1']} ]])[0]; raw=float(L[ia]-L[ib]); c='A' if raw>=0 else 'B'; return {'code':c,'side':f['m1'][c],'raw_AminusB':raw,'confidence':abs(raw)}
def sem_branches(f,q,m):
 cl=code_for_side(m,'LEFT'); cr=code_for_side(m,'RIGHT'); return audit(f,pref(q,cl)),audit(f,pref(q,cr))
cal=[audit(f,BASE) for f in cal_fam]; calacc=float(np.mean([x['acc'] for x in cal])); calsens=float(np.mean([x['sensitivity'] for x in cal])); eligible=bool(calacc>=CAL_ACC_MIN and calsens>=CAL_SENS_MIN)
print('PR002_CAL '+json.dumps({'n':CAL_N,'acc':calacc,'mean_sensitivity':calsens,'eligible':eligible},sort_keys=True),flush=True)
if not eligible: print('PR002_INVALID '+json.dumps({'reason':'calibration_gate','acc':calacc,'mean_sensitivity':calsens},sort_keys=True),flush=True); raise SystemExit
rows=[]
for f in val_fam:
 b=audit(f,BASE); br=audit(f,BASE); rep=natural(f); L1,R1=sem_branches(f,f['q1'],f['m1']); L2,R2=sem_branches(f,f['q2'],f['m2']); freeA=audit(f,pref(f['fq'],'A')); freeB=audit(f,pref(f['fq'],'B'))
 e1=L1['D']-R1['D']; e2=L2['D']-R2['D']; ds=.5*(e1+e2); dfree=freeA['D']-freeB['D']; dnoise=br['D']-b['D']; s=1 if rep['side']=='LEFT' else -1; natural_post=L1 if rep['side']=='LEFT' else R1
 row={'idx':f['idx'],'label':f['label'],'order':f['order'],'opts':f['opts'],'m1':f['m1'],'base':b,'base_repeat':br,'report':rep,'m1_left':L1,'m1_right':R1,'m2_left':L2,'m2_right':R2,'free_A':freeA,'free_B':freeB,'effect_map1':e1,'effect_map2':e2,'delta_sem':ds,'delta_free':dfree,'delta_noise':dnoise,'mapping_same_sign':int(e1*e2>0),'pre_align':s*b['D'],'post_align':s*natural_post['D'],'natural_change':s*(natural_post['D']-b['D'])}
 rows.append(row); print('PR002_RECORD '+json.dumps(row,sort_keys=True),flush=True)
 if torch.cuda.is_available(): torch.cuda.empty_cache()
def ci(x):
 x=np.asarray(x,float); rr=np.random.default_rng(520260910); z=x[rr.integers(0,len(x),(BOOT,len(x)))].mean(1); return [float(np.quantile(z,.025)),float(np.quantile(z,.975))]
def sm(x):
 x=np.asarray(x,float); p=int((x>0).sum()); n=int((x<0).sum()); return {'n':len(x),'mean':float(x.mean()),'median':float(np.median(x)),'ci95':ci(x),'pos':p,'neg':n,'sign_p':float(binomtest(p,p+n,.5).pvalue) if p+n else None}
valacc=float(np.mean([r['base']['acc'] for r in rows])); valsens=float(np.mean([r['base']['sensitivity'] for r in rows])); S=sm([r['delta_sem'] for r in rows]); M1=sm([r['effect_map1'] for r in rows]); M2=sm([r['effect_map2'] for r in rows]); F=sm([r['delta_free'] for r in rows]); N=sm([r['delta_noise'] for r in rows]); NC=sm([r['natural_change'] for r in rows]); success=bool(valacc>=VAL_ACC_MIN and S['ci95'][0]>0 and S['sign_p']<.05 and M1['mean']>0 and M2['mean']>0)
out={'model':MODEL,'model_sha':msha,'dataset_sha':dsha,'family_hash':fhash,'cal_acc':calacc,'cal_mean_sensitivity':calsens,'val_acc':valacc,'val_mean_sensitivity':valsens,'primary_delta_sem':S,'map1':M1,'map2':M2,'mapping_same_sign_rate':float(np.mean([r['mapping_same_sign'] for r in rows])),'content_free_AminusB':F,'numerical_noise_floor':N,'natural_alignment_change':NC,'report_left_rate':float(np.mean([r['report']['side']=='LEFT' for r in rows])),'primary_success':success}
print('PR002_SUMMARY '+json.dumps(out,sort_keys=True),flush=True)
