# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3","scipy==1.15.3"]
# ///
"""MPW-103I synthetic screening regression, BEFORE any GPU baseline measurement."""
import tempfile,importlib.util,urllib.request,json
from pathlib import Path
ROOT="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/"
COMMIT="ac8a58f54dd4966a4d899ebf2522ca06dd028c5f"
mods={}
with tempfile.TemporaryDirectory() as td:
 for k,path in (("gpu","mpw103i/scripts/mpw103i_screen.py"),
                ("cpu","mpw103i/scripts/independent_screen.py")):
  b=urllib.request.urlopen(ROOT+COMMIT+"/"+path,timeout=60).read()
  p=Path(td)/(k+".py");p.write_bytes(b)
  spec=importlib.util.spec_from_file_location(k,p)
  mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mods[k]=mod
gpu,cpu=mods["gpu"],mods["cpu"]
def point(v):
 return {"D":float(v),"J":float(v*9),"I_left":6.,"I_right":5.,
         "sens":11.,"acc":1}
records=[]
for ix in range(32,2080):
 y=(ix-32)%2
 d=.6 if y else -.6
 o=d if ix%11 else -d
 records.append({"idx":ix,"label":y,"case_sha256":"%064x"%ix,
  "orders":{"LR":{"baseline":point(d),"baseline_repeat":point(d)},
            "RL":{"baseline":point(o),"baseline_repeat":point(o)}}})
got=gpu.select_from_screen(records)
other=cpu.reanalyze_screen(records,gpu.EXPECTED_CANDIDATE_MANIFEST)
assert got==other,("INDEPENDENT_SCREEN_DIFFERED")
assert got["selection_complete"] and got["n_selected"]==64 and got["selected_per_label"]=={"0":32,"1":32}
assert sorted(s["idx"] for s in got["selected"])==[s["idx"] for s in got["selected"]]
try:
 cpu.reanalyze_screen(records[:-1],gpu.EXPECTED_CANDIDATE_MANIFEST)
 raise RuntimeError("INCOMPLETE_SCREEN_WRONGLY_ACCEPTED")
except ValueError:
 pass
print("MPW103I_SCREEN_SYNTHETIC_PASS "+json.dumps(
 {"all_records":len(records),"eligible":got["eligible_per_label"],
 "selected":got["n_selected"],"rejection_causes":got["rejection_reason_counts"]},
 sort_keys=True),flush=True)
