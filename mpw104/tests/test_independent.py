# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""MPW-104 synthetic positive, negative and baseline eligibility tests.
These are generated fixtures; never scientific observations.
"""
import importlib.util,json,tempfile,urllib.request
from pathlib import Path
base="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/"
files={
 'gpu':'c82c78537a89e71b4c594514cba4297d691d775c/mpw104/scripts/mpw104.py',
 'cpu':'c82c78537a89e71b4c594514cba4297d691d775c/mpw104/scripts/independent_analysis.py'
}
mods={}
with tempfile.TemporaryDirectory() as tmp:
 for name,url in files.items():
  b=urllib.request.urlopen(base+url,timeout=90).read()
  p=Path(tmp)/(name+'.py');p.write_bytes(b)
  spec=importlib.util.spec_from_file_location(name,str(p))
  obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);mods[name]=obj
G,C=mods['gpu'],mods['cpu']
def point(x,sen=12,acc=1):
 return {'D':float(x),'J':float(x*10),'I_left':6.0,'I_right':4.0,'sens':float(sen),'acc':acc}
def fixture(negative=False,low_known=False):
 rows=[]
 for i in range(32,160):
  parts={}
  for order in ("LR","RL"):
   b=point(.5 if not(low_known and i>=50) else .02)
   conditions={"baseline":b,"baseline_repeat":dict(b),"neutral_ack":point(.4)}
   rf=point(.6 if negative else -.6)
   ff=point(-.6 if negative else .3)
   for m in (0,1):
    conditions[f'report_false_m{m}']=rf
    conditions[f'report_true_m{m}']=point(.3)
    conditions[f'free_false_m{m}']=ff
    conditions[f'free_true_m{m}']=point(.3)
   conditions.update({'self_declarative_false':point(-.6),'self_declarative_true':point(.3),
    'self_reference_false':point(.1),'self_reference_true':point(.2),
    'directive_false':point(-.9),'directive_true':point(.5)})
   parts[order]={'true_side':'LEFT','false_side':'RIGHT','conditions':conditions}
  rows.append({'idx':i,'case_sha256':'0'*64,'label':1,'orders':parts})
 return rows
for tag,fixture_opts in [('positive',{}),('negative',{'negative':True}),('low_known',{'low_known':True})]:
 rows=fixture(**fixture_opts)
 a=G.aggregate(rows,'qwen3');b=C.compute(rows)
 for h in ('H1','H2','H3'):
  for key in ('n','mean','median','ci95','ci_familywise','positive','negative','zero','sign_p'):
   if a['estimates'][h][key]!=b['estimates'][h][key]:
    raise RuntimeError('INDEPENDENT_MISMATCH '+tag+' '+h+' '+key)
  if a['verdicts'][h]!=b['verdicts'][h]:
   raise RuntimeError('VERDICT_MISMATCH '+tag+' '+h)
 if tag=='positive' and any(x!='CONFIRMED' for x in a['verdicts'].values()):
  raise RuntimeError('POSITIVE_FIXTURE_NOT_CONFIRMED')
 if tag=='negative' and not (a['verdicts']['H1']=='NOT_CONFIRMED' and a['verdicts']['H2']=='NOT_CONFIRMED'):
  raise RuntimeError('NEGATIVE_FIXTURE_NOT_DETECTED')
 if tag=='low_known' and a['verdicts']['H2']!='INDETERMINATE_CAPABILITY':
  raise RuntimeError('ELIGIBILITY_GATE_NOT_ENFORCED')
 print('MPW104_SYNTHETIC_VERDICT '+json.dumps({'tag':tag,'n':len(rows),'verdicts':a['verdicts']}),flush=True)
print('MPW104_SYNTHETIC_INDEPENDENT_TEST_PASS',flush=True)
