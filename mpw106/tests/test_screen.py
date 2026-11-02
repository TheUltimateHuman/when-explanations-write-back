# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""MPW-106 independent blinded screen and negative missing-case fixture.
All source records synthetic; no GPU inference or scientific evidence.
"""
import importlib.util,urllib.request,json,tempfile
from pathlib import Path
ROOT="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/"
REF="f1fd015c7ad3a3cd8e1c48cf4afb6c7fbc2fc532"
modules={}
with tempfile.TemporaryDirectory() as td:
 for name,path in (("source","mpw106/scripts/mpw106_screen.py"),
                   ("blind","mpw106/scripts/independent_screen.py")):
  data=urllib.request.urlopen(ROOT+REF+"/"+path,timeout=90).read()
  p=Path(td)/(name+".py");p.write_bytes(data)
  spec=importlib.util.spec_from_file_location(name,p)
  z=importlib.util.module_from_spec(spec);spec.loader.exec_module(z);modules[name]=z
src,cpu=modules["source"],modules["blind"]
def point(x):return {"D":float(x),"J":float(4*x),"I_left":7.,
   "I_right":4.,"sens":11.,"acc":1}
records=[]
for i in range(32,32+2048):
 label=(i-32)%2
 val=.55 if label else -.55
 reverse=val if i%9 else -val
 records.append({"idx":i,"label":label,"case_sha256":("%064x"%(i+5000)),
   "orders":{"LR":{"baseline":point(val),"baseline_repeat":point(val)},
             "RL":{"baseline":point(reverse),"baseline_repeat":point(reverse)}}})
a=src.select_from_screen(records)
b=cpu.reanalyze_screen(records,src.EXPECTED_CANDIDATE_MANIFEST)
assert a==b
assert a["n_selected"]==64 and a["selected_per_label"]=={"0":32,"1":32}
assert len({r["idx"] for r in a["selected"]})==64
try:
 cpu.reanalyze_screen(records[:-1],src.EXPECTED_CANDIDATE_MANIFEST)
 raise AssertionError("INCOMPLETE_SCREEN_ACCEPTED")
except ValueError:pass
print("MPW106_BLIND_SCREEN_SYNTHETIC_PASS "+json.dumps(
 {"n_screened":len(records),"eligible":a["eligible_per_label"],
  "selected":a["n_selected"],"ignored_treatment_outcomes":True},sort_keys=True),flush=True)
