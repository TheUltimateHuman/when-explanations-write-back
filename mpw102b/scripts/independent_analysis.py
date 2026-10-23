# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""MPW-102B independently implemented family-level analysis; does not import model runner.
All model/hypothesis gates and seeds were frozen in mpw102b/PROTOCOL.md.
"""
import json,argparse,hashlib,math
from pathlib import Path
import numpy as np
from scipy.stats import binomtest

ORDERS=('LR','RL')
EXPL=('SELF_DECLARATIVE','YOU_DECLARATIVE','THIRD_DECLARATIVE')
OTHER=('YOU_QUESTION','YOU_PRESCRIPTIVE','DIRECTIVE','SIDE_REFERENCE')
STYLES=EXPL+OTHER
BOOT=50000;SEED=520261023;ALPHA=.0125

def summary(values,seed):
 a=np.array(values,dtype=float)
 if len(a)!=192 or not np.isfinite(a).all():raise ValueError('INVALID_VECTOR')
 rnd=np.random.default_rng(seed)
 chunks=[]
 for begin in range(0,BOOT,2500):
  ix=rnd.integers(0,len(a),size=(min(2500,BOOT-begin),len(a)))
  chunks.append(np.mean(a[ix],axis=1))
 draws=np.concatenate(chunks)
 p=int(np.count_nonzero(a>0));n=int(np.count_nonzero(a<0))
 return {'mean':float(np.mean(a)),'median':float(np.median(a)),
  'ci95':list(map(float,np.quantile(draws,[.025,.975]))),
  'ci9875':list(map(float,np.quantile(draws,[.00625,.99375]))),
  'positive':p,'negative':n,'zero':len(a)-p-n,
  'sign_p':float(binomtest(p,p+n,0.5).pvalue) if p+n else 1.0}
def compute(records):
 if len(records)!=192 or set(x['idx'] for x in records)!=set(range(32,224)):
  raise ValueError('192_UNIQUE_EXPECTED_INDICES')
 ab=[];sp=[];byorder_ab={o:[] for o in ORDERS};byorder_sp={o:[] for o in ORDERS}
 framing={k:[] for k in STYLES};num=[];acc={o:[] for o in ORDERS}
 controls={o:{k:[] for k in ('neutral_ack','label_ack')} for o in ORDERS}
 raw_j=[];sat=0;neg_int=0
 for record in records:
  if not isinstance(record.get('case_sha256'),str) or len(record['case_sha256'])!=64:raise ValueError('MISSING_CASE_HASH')
  if set(record['orders'])!=set(ORDERS):raise ValueError('INCOMPLETE_DISPLAY_ORDERS')
  per_style={k:[] for k in STYLES};per_ab=[];rj=[]
  for order in ORDERS:
   b=record['orders'][order]
   expected={'baseline','baseline_repeat','neutral_ack','label_ack'}
   expected|={'ab_m'+str(mapping)+'_'+side for mapping in (0,1) for side in ('LEFT','RIGHT')}
   expected|={style+'_'+side for style in STYLES for side in ('LEFT','RIGHT')}
   if set(b)!=expected:raise ValueError('INCOMPLETE_BRANCH_SET')
   base=b['baseline'];acc[order].append(int(base['acc']))
   num.append(abs(base['D']-b['baseline_repeat']['D']))
   sat+=int(abs(base['D'])>=.95);neg_int+=int(base['I_left']<=0 or base['I_right']<=0)
   for c in controls[order]:
    controls[order][c].append(b[c]['D']-base['D'])
   mvalues=[];mj=[]
   for mapping in (0,1):
    l=b['ab_m'+str(mapping)+'_LEFT'];r=b['ab_m'+str(mapping)+'_RIGHT']
    mvalues.append(l['D']-r['D']);mj.append(l['J']-r['J'])
   v=float(np.mean(mvalues));per_ab.append(v);byorder_ab[order].append(v)
   rj.append(float(np.mean(mj)))
   for k in STYLES:per_style[k].append(b[k+'_LEFT']['D']-b[k+'_RIGHT']['D'])
   byorder_sp[order].append(float(np.mean([per_style[k][-1] for k in EXPL])-per_style['SIDE_REFERENCE'][-1]))
  ab.append(float(np.mean(per_ab)));raw_j.append(float(np.mean(rj)))
  for k in STYLES:framing[k].append(float(np.mean(per_style[k])))
  sp.append(float(np.mean([framing[k][-1] for k in EXPL])-framing['SIDE_REFERENCE'][-1]))
 e1=summary(ab,SEED+1);e2=summary(sp,SEED+2)
 order_ab={o:float(np.mean(v)) for o,v in byorder_ab.items()}
 order_sp={o:float(np.mean(v)) for o,v in byorder_sp.items()}
 frame_avg={k:float(np.mean(v)) for k,v in framing.items()}
 accurate={o:float(np.mean(v)) for o,v in acc.items()}
 valid=all(n>=.90 for n in accurate.values()) and max(num)<1e-4
 check=lambda z: z['mean']>0 and z['ci9875'][0]>0 and z['sign_p']<ALPHA
 ok1=bool(valid and check(e1) and all(x>0 for x in order_ab.values()))
 ok2=bool(valid and check(e2) and all(frame_avg[x]>0 for x in EXPL) and all(x>0 for x in order_sp.values()))
 return {'n':192,'valid':bool(valid),'H1_verdict':'CONFIRMED' if ok1 else ('INVALID' if not valid else 'NOT_CONFIRMED'),
  'H2_verdict':'CONFIRMED' if ok2 else ('INVALID' if not valid else 'NOT_CONFIRMED'),
  'AB_transport':e1,'specificity':e2,'order_AB':order_ab,'order_specificity':order_sp,
  'frame_means':frame_avg,'validation_accuracy':accurate,'numeric_floor_max':float(max(num)),
  'negative_interventions':neg_int,'saturated_baselines':sat,
  'raw_J_AB':float(np.mean(raw_j)),
  'ack_means':{o+'_'+k:float(np.mean(controls[o][k])) for o in ORDERS for k in controls[o]}}
if __name__=='__main__':
 parser=argparse.ArgumentParser()
 parser.add_argument('records_jsonl');args=parser.parse_args()
 b=Path(args.records_jsonl).read_bytes()
 rows=[json.loads(x) for x in b.splitlines() if x]
 out=compute(rows);out['combined_raw_sha256']=hashlib.sha256(b).hexdigest()
 print('MPW102B_INDEPENDENT '+json.dumps(out,sort_keys=True),flush=True)
