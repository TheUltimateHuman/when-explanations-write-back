# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""MPW-103 mock-record consistency test: positive and negative gates.
No GPU inference; synthetic records have no empirical research meaning.
"""
import json,urllib.request,importlib.util,tempfile
from pathlib import Path

ROOT='https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/'
SRC={
 'runner':'06b4c7d9ea8a3475fc296ee3e16c96b52f1f5895/mpw103/scripts/mpw103.py',
 'independent':'b04baceff7a3fda66fe66fbcf612df783dfb3558/mpw103/scripts/independent_analysis.py'}
mods={}
with tempfile.TemporaryDirectory() as tmp:
 for name,path in SRC.items():
  raw=urllib.request.urlopen(ROOT+path,timeout=90).read()
  p=Path(tmp)/(name+'.py');p.write_bytes(raw)
  spec=importlib.util.spec_from_file_location(name,str(p))
  mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
  mods[name]=mod
run,ind=mods['runner'],mods['independent']
def measure(d,acc=1):
 return {'D':float(d),'J':float(d*10),'I_left':8.,'I_right':6.,'sens':14.,'acc':acc}
def build(negative=False):
 rows=[]
 for i in range(32,160):
  orders={}
  for order in ('LR','RL'):
   x={k:measure(0) for k in ('baseline','baseline_repeat','neutral_ack','label_ack')}
   for m in (0,1):
    for f in ('LEFT','RIGHT'):
     p=f'm{m}_{f}_'
     vals={'LAST_ONLY':.0,'PREV_1_LEFT':.04,'PREV_1_RIGHT':.0,
       'PREV_3_LEFT':.20,'PREV_3_RIGHT':-.10,
       'PREV_7_LEFT':.50 if not negative else -.10,
       'PREV_7_RIGHT':-.30 if not negative else .40,
       'BALANCED_LATE_LEFT':.25,
       'BALANCED_EARLY_LEFT':-.10,
       'FREE_PREV_7_LEFT':.10,'FREE_PREV_7_RIGHT':0}
     for name,val in vals.items():x[p+name]=measure(val)
   orders[order]=x
  rows.append({'idx':i,'label':1,'case_sha256':'a'*64,'orders':orders})
 return rows
for negative in (False,True):
 rows=build(negative)
 a=run.aggregate(rows,'qwen3');b=ind.compute(rows)
 for h in ('H1','H2','H3','H4'):
  for k in ('mean','median','ci95','ci_familywise','positive','negative','zero','sign_p'):
   if a['estimates'][h][k]!=b['estimates'][h][k]:raise AssertionError((negative,h,k,a['estimates'][h][k],b['estimates'][h][k]))
  if a['verdicts'][h]!=b['verdicts'][h]:raise AssertionError(('verdict',negative,h))
 if not negative and any(x!='CONFIRMED' for x in a['verdicts'].values()):
  raise AssertionError('MISSED_POSITIVE_CONSTRUCTION')
 if negative and a['verdicts']['H1']!='NOT_CONFIRMED':
  raise AssertionError('MISSED_NEGATIVE_CONSTRUCTION')
print('MPW103_SYNTHETIC_TEST_PASS '+json.dumps({'n':128,'conditions_per_order':48,'positive':'ALL_FOUR_CONFIRMED','negative':'H1_NOT_CONFIRMED','not_empirical':True}),flush=True)
