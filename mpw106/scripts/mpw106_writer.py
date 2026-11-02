# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = [
# "torch==2.6.0","transformers==4.57.3","accelerate==1.6.0",
# "datasets==3.6.0","huggingface_hub==0.36.0",
# "numpy==2.1.3","scipy==1.15.3","sentencepiece==0.2.0"
# ]
# ///
"""MPW-106 Stage W: new GPU process, protected A0, genuine generated reports.
This writer NEVER chooses a store version or evaluates post-retrieval effects.
Original native text and source integrity are archived BEFORE Git memory writes.
"""
import argparse,base64,gzip,hashlib,importlib.util,json,math,re,tempfile,time
from pathlib import Path
from urllib.request import urlopen

ROOT="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/"
SCREEN_URL="UNSET_PIN_SCREEN_SOURCE"
SCREEN_SHA="UNSET_PIN_SCREEN_SHA"
CASE_MANIFEST="UNSET_PIN_NEW_CASE_SHA"
OLD104_URL=ROOT+"c94d1299e8862686bb728880c3f36a1527e7b7c0/mpw104/scripts/mpw104.py"
OLD104_SHA="d8866d46dcb4bc6f5e2289108c22c434add56c423e63f1731c929aed86d6d1e1"
DATASET="stanfordnlp/sst2"
DATASET_SHA="8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb"
MODELS={"qwen3":"Qwen/Qwen3-4B-Instruct-2507",
 "granite":"ibm-granite/granite-3.3-8b-instruct"}
PINS={"qwen3":"cdbee75f17c01a7cc42f958dc650907174af0554",
 "granite":"51dd4bc2ade4059a6bd87649d68aa11e4fb2529b"}
CAL_N=32
N=64
MAX_AUDIT_CONTEXT=1024
MAX_GENERATION_CONTEXT=2048
MAX_REPORT_TOKENS=48
PROVIDER_SECONDS=90*60
ARCHIVAL_RESERVE=120
PARSE_MIN=.80
ORDERS=("LR","RL")
EPS=1e-6
QUESTION=("Which labeled passage influenced your decision more? "
 "Start LEFT: or RIGHT: and briefly say why.")
def canonical(x):return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def sha(x):return hashlib.sha256(x if isinstance(x,bytes) else x.encode()).hexdigest()
def emit(name,obj):print(name+" "+canonical(obj),flush=True)
def import_frozen(url,expected,name):
    buf=urlopen(url,timeout=90).read()
    if sha(buf)!=expected:raise RuntimeError("FROZEN_SOURCE_SHA_FAIL_"+name)
    with tempfile.TemporaryDirectory() as td:
        path=Path(td)/"source.py";path.write_bytes(buf)
        spec=importlib.util.spec_from_file_location(name,path)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m
def parse(text):
    match=re.match(r"^\s*(LEFT|RIGHT)\s*:\s*(\S[\s\S]*)$",text,re.I)
    return match.group(1).upper() if match else None
def emit_archive(rows):
    if len(rows)!=N:raise RuntimeError("INCOMPLETE_FAMILY_ARCHIVE")
    raw=("\n".join(canonical(row) for row in rows)+"\n").encode()
    for i in range(0,N,16):
        part=("\n".join(canonical(x) for x in rows[i:i+16])+"\n").encode()
        b64=base64.b64encode(gzip.compress(part,compresslevel=9,mtime=0)).decode()
        for offset in range(0,len(b64),9000):
            emit("MPW106_WRITER_B64",{"sha256":sha(part),"part":offset//9000,
                 "total":(len(b64)+8999)//9000,"data":b64[offset:offset+9000]})
        emit("MPW106_WRITER_SHARD",{"part":i//16,"n":16,"range":[i,i+15],
              "raw_sha256":sha(part)})
    return sha(raw)
def main():
    a=argparse.ArgumentParser()
    a.add_argument("mode",choices=("write",))
    a.add_argument("--model",choices=tuple(MODELS),required=True)
    a.add_argument("--screen-commit",required=True)
    opt=a.parse_args();started=time.monotonic()
    if len(opt.screen_commit)!=40 or any(z not in "0123456789abcdef" for z in opt.screen_commit):
        raise RuntimeError("FROZEN_SCREEN_COMMIT_REQUIRED")
    from datasets import load_dataset
    from huggingface_hub import model_info,dataset_info
    from transformers import AutoTokenizer
    if dataset_info(DATASET).sha!=DATASET_SHA:raise RuntimeError("DATASET_CHANGED")
    revisions={m:model_info(n).sha for m,n in MODELS.items()}
    if revisions!=PINS:raise RuntimeError("MODEL_REVISION_DRIFT")
    screen=import_frozen(SCREEN_URL,SCREEN_SHA,"mpw106_original_case_screen")
    old=import_frozen(OLD104_URL,OLD104_SHA,"mpw106_original_task")
    ancestor,base=old.prior_artifacts()
    train=load_dataset(DATASET,split="train",revision=DATASET_SHA)
    valid=load_dataset(DATASET,split="validation",revision=DATASET_SHA)
    calibration,bank,casebytes,meta=screen.make_cases(train,valid)
    if sha(casebytes)!=CASE_MANIFEST:raise RuntimeError("UNFROZEN_CASE_BANK")
    raw_selection=urlopen(ROOT+opt.screen_commit+"/mpw106/selection/"+opt.model+".json",timeout=90).read()
    selected=json.loads(raw_selection)
    if selected.get("schema")!="MPW106_SCREEN_SELECTION_V1" or selected.get("n_selected")!=N or (
        selected.get("source_candidate_sha256")!=CASE_MANIFEST or not selected.get("selection_complete")):
        raise RuntimeError("SELECTED_CASES_NOT_ORIGINAL_SCREEN")
    ids={r["idx"] for r in selected["selected"]}
    cases={f["idx"]:f for f in bank if f["idx"] in ids}
    if len(ids)!=N or len(cases)!=N:raise RuntimeError("DUPLICATED_OR_MISSING_SELECTED_CASE")
    for z in selected["selected"]:
        if sha(canonical(cases[z["idx"]]))!=z["case_sha256"]:
            raise RuntimeError("CASE_BYTES_NOT_FROZEN")
    emit("MPW106_WRITER_SOURCE",{"model":opt.model,
      "source_sha256":sha(Path(__file__).read_bytes()),"case_bank_sha256":CASE_MANIFEST,
      "screen_selection_commit":opt.screen_commit,"selection_sha256":sha(raw_selection),
      "model_revision":PINS[opt.model],"dataset_revision":DATASET_SHA,"n":N})
    import torch,numpy as np,transformers
    tok=AutoTokenizer.from_pretrained(MODELS[opt.model],revision=PINS[opt.model],trust_remote_code=True)
    tok.padding_side="left";tok.pad_token=tok.pad_token or tok.eos_token
    ids_tokens={word:tok.encode(word,add_special_tokens=False) for word in ("positive","negative","A","B")}
    if any(len(z)!=1 for z in ids_tokens.values()):raise RuntimeError("NONATOMIC_OUTPUT_CANDIDATES")
    token_id={x:z[0] for x,z in ids_tokens.items()}
    if not torch.cuda.is_available():raise RuntimeError("CUDA_REQUIRED")
    model=transformers.AutoModelForCausalLM.from_pretrained(MODELS[opt.model],
      revision=PINS[opt.model],trust_remote_code=True,torch_dtype=torch.float16,
      device_map="auto",low_cpu_mem_usage=True,attn_implementation="sdpa")
    model.eval();batch_size=8
    emit("MPW106_WRITER_HARDWARE",{"model":opt.model,"gpu":torch.cuda.get_device_name(0),
      "torch":torch.__version__,"transformers":transformers.__version__,"batch_size":batch_size,
      "provider_timeout_seconds":PROVIDER_SECONDS,"dtype":"float16"})
    def batch_margin(msgs,label):
        vals=[]
        for begin in range(0,len(msgs),batch_size):
            prompt=[tok.apply_chat_template(z,tokenize=False,add_generation_prompt=True) for z in msgs[begin:begin+batch_size]]
            enc=tok(prompt,return_tensors="pt",padding=True,add_special_tokens=False,truncation=False)
            if int(enc.attention_mask.sum(1).max())>MAX_AUDIT_CONTEXT:raise RuntimeError("NO_AUDIT_TRUNCATION")
            enc=enc.to(model.device)
            with torch.inference_mode():
                logits=model(**enc,use_cache=False).logits[:,-1,:].float()
                vals.extend((logits[:,token_id["positive"]]-logits[:,token_id["negative"]]).cpu().tolist())
        return [float(z if label==1 else -z) for z in vals]
    def audits(case):
        out={}
        for order in ORDERS:
            msgs=[base+[old.case_text(case,order,case["left"],case["right"])],
                base+[old.case_text(case,order,case["flip_left"],case["right"])],
                base+[old.case_text(case,order,case["left"],case["flip_right"])]]
            m0,mL,mR=batch_margin(msgs,case["label"])
            iL=m0-mL;iR=m0-mR;total=abs(iL)+abs(iR)
            out[order]={"D":float((iL-iR)/(total+EPS)),
                 "J":float(iL-iR),"I_left":float(iL),"I_right":float(iR),
                 "sens":float(total),"acc":int(m0>=0)}
        return out
    def generated(case):
        task=old.case_text(case,"LR",case["left"],case["right"])
        msg=base+[task]
        prompt=tok.apply_chat_template(msg,tokenize=False,add_generation_prompt=True)
        enc=tok(prompt,return_tensors="pt",add_special_tokens=False,truncation=False)
        if int(enc.attention_mask.sum())>MAX_GENERATION_CONTEXT:raise RuntimeError("ANSWER_CONTEXT_TOO_LONG")
        enc=enc.to(model.device)
        with torch.inference_mode(): logits=model(**enc,use_cache=False).logits[0,-1].float()
        scores={s:float(logits[token_id[s]]) for s in ("positive","negative")}
        answer=max(("positive","negative"),key=lambda s:scores[s])
        full=msg+[{"role":"assistant","content":answer},{"role":"user","content":QUESTION}]
        text=tok.apply_chat_template(full,tokenize=False,add_generation_prompt=True)
        enc2=tok(text,return_tensors="pt",add_special_tokens=False,truncation=False)
        if int(enc2.attention_mask.sum())>MAX_GENERATION_CONTEXT:
            raise RuntimeError("REPORT_CONTEXT_TOO_LONG")
        enc2=enc2.to(model.device)
        with torch.inference_mode():
            output=model.generate(**enc2,max_new_tokens=MAX_REPORT_TOKENS,do_sample=False,
                 pad_token_id=tok.eos_token_id,eos_token_id=tok.eos_token_id,use_cache=True)
        new=output[0][enc2.input_ids.shape[1]:].cpu().tolist()
        raw=tok.decode(new,skip_special_tokens=True).strip()
        return {"source":"MODEL_GREEDY_GENERATED","native_answer":answer,
            "answer_logits":scores,"raw":raw,"parsed_side":parse(raw),
            "token_ids":new,"n_tokens":len(new),"raw_sha256":sha(raw),
            "prompt_sha256":sha(text),"model_revision":PINS[opt.model]}
    cal_a=[audits(f) for f in calibration]
    acc={o:float(np.mean([z[o]["acc"] for z in cal_a])) for o in ORDERS}
    sens=float(np.mean([z[o]["sens"] for z in cal_a for o in ORDERS]))
    if any(v<.9 for v in acc.values()) or sens<1:
        emit("MPW106_WRITER_END",{"model":opt.model,"status":"CAPABILITY_GATE_FAIL",
              "calibration_accuracy":acc,"sensitivity":sens});return
    native_cal=[generated(f) for f in calibration]
    parsed=sum(z["parsed_side"] is not None for z in native_cal)
    if parsed/CAL_N<PARSE_MIN:
        emit("MPW106_WRITER_END",{"model":opt.model,
          "status":"INSTRUMENT_FAILURE_PROSE","calibration_parse_rate":parsed/CAL_N});return
    emit("MPW106_WRITER_CALIBRATION",{"model":opt.model,"accuracy":acc,"sensitivity":sens,
      "calibration_n":CAL_N,"native_parse_rate":parsed/CAL_N,"eligible":True})
    originals=[]
    failed=[]
    for entry in selected["selected"]:
        f=cases[entry["idx"]]
        first=audits(f);second=audits(f)
        for o in ORDERS:
            oldD=entry["screen_orders"][o]["baseline"]["D"]
            b=first[o];rp=second[o]
            if abs(b["D"]-oldD)>=1e-4 or abs(b["D"]-rp["D"])>=1e-4 or (
              b["D"]*oldD<=0 or not b["acc"] or not rp["acc"] or
              min(b["I_left"],b["I_right"],rp["I_left"],rp["I_right"])<=0):
                failed.append({"idx":entry["idx"],"order":o,"screen_D":oldD,
                               "new_D":b["D"],"repeat_D":rp["D"]})
        originals.append({"idx":entry["idx"],"first":first,"repeat":second})
    if failed:
        emit("MPW106_WRITER_END",{"model":opt.model,"status":"INVALID_BASELINE_DRIFT",
              "n_invalid_cells":len(failed),"invalid_records":failed[:20],
              "writer_memory_not_created":True});return
    clock=time.monotonic()
    for z in selected["selected"][:4]:generated(cases[z["idx"]])
    per=(time.monotonic()-clock)/4
    expected=time.monotonic()-started+per*N
    emit("MPW106_WRITER_TIMING",{"model":opt.model,"n_pilot":4,
       "seconds_per_report":per,"forecast_unpadded_sec":expected,
       "forecast_padded_warn_sec":time.monotonic()-started+1.35*per*N,
       "provider_hard_sec":PROVIDER_SECONDS,"reserve_sec":ARCHIVAL_RESERVE,
       "padding_veto":False})
    if expected>PROVIDER_SECONDS-ARCHIVAL_RESERVE:
        emit("MPW106_WRITER_END",{"status":"RESOURCE_REPLAN",
          "model":opt.model,"no_memory_write":True});return
    rows=[]
    for i,entry in enumerate(selected["selected"]):
        if time.monotonic()-started>PROVIDER_SECONDS-ARCHIVAL_RESERVE:
            emit("MPW106_WRITER_END",{"status":"ACTUAL_PROVIDER_ABORT",
              "model":opt.model,"n_complete":len(rows)});return
        native=generated(cases[entry["idx"]])
        row={"idx":entry["idx"],"case_sha256":entry["case_sha256"],
          "label":entry["label"],"true_side":entry["true_side"],
          "false_side":entry["false_side"],"screen_orders":entry["screen_orders"],
          "writer_baseline":originals[i]["first"],
          "writer_repeat":originals[i]["repeat"],"native":native}
        rows.append(row)
        if (i+1)%16==0:emit("MPW106_WRITER_PROGRESS",{"model":opt.model,
            "n":i+1,"total":N})
    live_parse=sum(x["native"]["parsed_side"] is not None for x in rows)
    raw_sha=emit_archive(rows)
    status="WRITER_COMPLETED" if live_parse/N>=PARSE_MIN else "INSTRUMENT_FAILURE_PROSE"
    emit("MPW106_WRITER_END",{"model":opt.model,"status":status,"n":len(rows),
      "native_parse_rate":live_parse/N,"raw_sha256":raw_sha,
      "screen_commit":opt.screen_commit,"elapsed_sec":time.monotonic()-started,
      "memory_NOT_committed_in_GPU_job":True})
if __name__=="__main__":main()
