# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = []
# ///
"""MPW-106 synthetic writer-provenance regression; no model inference."""
import urllib.request,importlib.util,tempfile,copy,json
from pathlib import Path
URL="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/"
REF="f1fd015c7ad3a3cd8e1c48cf4afb6c7fbc2fc532"
b=urllib.request.urlopen(URL+REF+"/mpw106/scripts/independent_writer.py",timeout=60).read()
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp)/"writer.py";p.write_bytes(b)
 spec=importlib.util.spec_from_file_location("mpw106_writer_independent",p)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def point(d):return {"D":float(d),"J":float(5*d),"I_left":7.,"I_right":4.,
 "sens":11.,"acc":1}
rows=[];selected=[]
for i in range(64):
 idx=32+i;case_sha="%064x"%(idx+500)
 ref={"idx":idx,"label":i%2,"case_sha256":case_sha,
   "true_side":"LEFT","false_side":"RIGHT",
   "screen_orders":{o:{"baseline":point(.5),"baseline_repeat":point(.5)}
                    for o in ("LR","RL")}}
 selected.append(ref)
 text="LEFT: I used the left sentence."
 native={"raw":text,"raw_sha256":m.sha(text),"parsed_side":"LEFT",
   "token_ids":[1,2,3],"n_tokens":3,
   "native_answer":"positive","source":"MODEL_GREEDY_GENERATED",
   "model_revision":"r"*40,"prompt_sha256":"2"*64}
 rows.append({**ref,"writer_baseline":{o:point(.5) for o in ("LR","RL")},
  "writer_repeat":{o:point(.5) for o in ("LR","RL")},
  "native":native})
res=m.verify(rows,{"selected":selected},"r"*40)
assert res["source_verified"] and res["n_parseable"]==64
for mode in ("wrong_case","wrong_report","wrong_version"):
 invalid=copy.deepcopy(rows)
 if mode=="wrong_case":invalid[0]["case_sha256"]="0"*64
 if mode=="wrong_report":invalid[0]["native"]["raw"]="RIGHT: altered"
 if mode=="wrong_version":invalid[0]["writer_baseline"]["LR"]["D"]=.51
 try:
  m.verify(invalid,{"selected":selected},"r"*40)
  raise AssertionError("FAILED_TO_REJECT_"+mode)
 except RuntimeError:pass
print("MPW106_WRITER_SYNTHETIC_PASS "+json.dumps(
 {"n":res["n"],"parse_rate":res["native_parse_rate"],
 "max_baseline_error":res["max_screen_to_writer_D"],
 "negative_fixtures_rejected":3}),flush=True)
