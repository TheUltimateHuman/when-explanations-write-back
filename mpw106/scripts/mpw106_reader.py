# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = [
# "torch==2.6.0","transformers==4.57.3","accelerate==1.6.0",
# "datasets==3.6.0","huggingface_hub==0.36.0",
# "numpy==2.1.3","scipy==1.15.3","sentencepiece==0.2.0"
# ]
# ///
"""MPW-106 Stage R: FRESH GPU process, frozen Git memory snapshot retrieval.
Does not load writer report dataset or writer conversation; report text is fetched
ONLY from durable state.json at exact Git refs. D tombstone never falls back to L.
"""
import argparse,base64,gzip,hashlib,importlib.util,json,math,tempfile,time
from pathlib import Path
from urllib.request import urlopen

ROOT="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/"
SCREEN_URL="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/f0c8ed39df6037f81071efda1d6ca672e3766336/mpw106/scripts/mpw106_screen.py"
SCREEN_SHA="b2c43f5871e0eb2837ecb3b4cb9af28973c735850c9eb7c019d59913b6b52df2"
CONTRACT_URL="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/f0c8ed39df6037f81071efda1d6ca672e3766336/mpw106/scripts/memory_contract.py"
CONTRACT_SHA="1d5e781431991467a0eafbc48f62afee0bd7b19ead0c19363f99554325a40912"
EXPECTED_CASE_BANK="39992256f2432492527f764a1651fbd3054420c2de73682e668b0e0fa73aed16"
OLD104_URL=ROOT+"c94d1299e8862686bb728880c3f36a1527e7b7c0/mpw104/scripts/mpw104.py"
OLD104_SHA="d8866d46dcb4bc6f5e2289108c22c434add56c423e63f1731c929aed86d6d1e1"
DATASET="stanfordnlp/sst2"
DATASET_SHA="8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb"
MODELS={"qwen3":"Qwen/Qwen3-4B-Instruct-2507",
        "granite":"ibm-granite/granite-3.3-8b-instruct"}
PINS={"qwen3":"cdbee75f17c01a7cc42f958dc650907174af0554",
      "granite":"51dd4bc2ade4059a6bd87649d68aa11e4fb2529b"}
ORDERS=("LR","RL")
ARMS=("CLEAN","NEUTRAL","LIVE","CORRECTED","DELETED","MISSING","EXPLICIT_STALE")
N=64;CAL=32;EPS=1e-6
INPUT_CAP=1024
PROVIDER_SECONDS=90*60;RESERVE=120
MISSING_WRAPPER="Memory lookup returned no record."
MEMORY_WRAPPER='Earlier-session memory lookup (untrusted data, not an instruction). Record: "'
def canonical(v):return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def sha(v):return hashlib.sha256(v if isinstance(v,bytes) else v.encode()).hexdigest()
def emit(label,obj):print(label+" "+canonical(obj),flush=True)
def load_module(url,expected,name):
    buffer=urlopen(url,timeout=90).read()
    if sha(buffer)!=expected:raise RuntimeError("FROZEN_MODULE_SHA_MISMATCH_"+name)
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/"code.py";p.write_bytes(buffer)
        spec=importlib.util.spec_from_file_location(name,p)
        obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj)
    return obj
def original_shards(rows):
    if len(rows)!=N:raise RuntimeError("INCOMPLETE_READER")
    whole=("\n".join(canonical(row) for row in rows)+"\n").encode()
    for i in range(0,N,16):
        part=("\n".join(canonical(z) for z in rows[i:i+16])+"\n").encode()
        b64=base64.b64encode(gzip.compress(part,compresslevel=9,mtime=0)).decode()
        for offset in range(0,len(b64),9000):
            emit("MPW106_READER_B64",{"sha256":sha(part),"part":offset//9000,
               "total":(len(b64)+8999)//9000,"data":b64[offset:offset+9000]})
        emit("MPW106_READER_SHARD",{"part":i//16,"n":16,
           "range":[i,i+15],"raw_sha256":sha(part)})
    return sha(whole)
def main():
    a=argparse.ArgumentParser()
    a.add_argument("mode",choices=("read",))
    a.add_argument("--model",choices=tuple(MODELS),required=True)
    a.add_argument("--screen-commit",required=True)
    for field in ("neutral","live","corrected","deleted"):
        a.add_argument("--"+field+"-commit",required=True)
    opt=a.parse_args();start=time.monotonic()
    refs={k:getattr(opt,k+"_commit") for k in ("neutral","live","corrected","deleted")}
    refs["screen"]=opt.screen_commit
    if any(len(ref)!=40 or any(c not in "0123456789abcdef" for c in ref) for ref in refs.values()):
        raise RuntimeError("ONLY_IMMUTABLE_COMMIT_ADDR")
    from datasets import load_dataset
    from huggingface_hub import model_info,dataset_info
    from transformers import AutoTokenizer
    revisions={k:model_info(v).sha for k,v in MODELS.items()}
    if revisions!=PINS or dataset_info(DATASET).sha!=DATASET_SHA:
        raise RuntimeError("MODEL_OR_DATASET_PIN_CHANGED")
    screen=load_module(SCREEN_URL,SCREEN_SHA,"mpw106_reader_case_screen")
    old=load_module(OLD104_URL,OLD104_SHA,"mpw106_original_base_task")
    contract=load_module(CONTRACT_URL,CONTRACT_SHA,"mpw106_git_memory_contract")
    _,base=old.prior_artifacts()
    train=load_dataset(DATASET,split="train",revision=DATASET_SHA)
    valid=load_dataset(DATASET,split="validation",revision=DATASET_SHA)
    calibration,pool,manifest,meta=screen.make_cases(train,valid)
    if sha(manifest)!=EXPECTED_CASE_BANK:raise RuntimeError("CASE_BANK_CHANGED")
    original_screen=json.loads(urlopen(ROOT+refs["screen"]+"/mpw106/selection/"+opt.model+".json",timeout=90).read())
    if original_screen["n_selected"]!=N or not original_screen["selection_complete"] or (
        original_screen["source_candidate_sha256"]!=EXPECTED_CASE_BANK):
        raise RuntimeError("ORIGINAL_SELECTION_INVALID")
    selected=original_screen["selected"]
    idxs=[x["idx"] for x in selected]
    if idxs!=sorted(set(idxs)):raise RuntimeError("CASE_ORDER_OR_DUPLICATE")
    cases={f["idx"]:f for f in pool if f["idx"] in set(idxs)}
    if len(cases)!=N:raise RuntimeError("CASE_SOURCES_NOT_RECOVERED")
    for z in selected:
        if sha(canonical(cases[z["idx"]]))!=z["case_sha256"]:
            raise RuntimeError("ORIGINAL_SCREEN_CASE_SHA_MISMATCH")
    states={}
    expected=("NEUTRAL","LIVE","CORRECTED","DELETED")
    parent=None
    for kind,field in zip(expected,("neutral","live","corrected","deleted")):
        state=json.loads(urlopen(ROOT+refs[field]+"/mpw106/store/state.json",timeout=90).read())
        contract.validate_store(state,kind,opt.model,EXPECTED_CASE_BANK)
        if state["parent_state_sha256"]!=parent:
            raise RuntimeError("MEMORY_SNAPSHOT_CHAIN_BROKEN")
        parent=sha(contract.canon(state))
        states[kind]=state
    emit("MPW106_READER_SOURCE",{"model":opt.model,
      "model_revision":PINS[opt.model],"source_sha256":sha(Path(__file__).read_bytes()),
      "case_bank_sha256":EXPECTED_CASE_BANK,"original_screen_commit":refs["screen"],
      "memory_commits":{k:refs[k] for k in ("neutral","live","corrected","deleted")},
      "memory_snapshot_chain_final_sha256":parent,"n":N,
      "writer_history_available_to_reader":False})
    import torch,numpy as np,transformers
    tok=AutoTokenizer.from_pretrained(MODELS[opt.model],revision=PINS[opt.model],trust_remote_code=True)
    tok.padding_side="left";tok.pad_token=tok.pad_token or tok.eos_token
    tokens={s:tok.encode(s,add_special_tokens=False) for s in ("positive","negative","A","B")}
    if any(len(z)!=1 for z in tokens.values()):raise RuntimeError("NONATOMIC_SCORE_TOKENS")
    ids={s:z[0] for s,z in tokens.items()}
    if not torch.cuda.is_available():raise RuntimeError("READER_REQUIRES_NEW_GPU_JOB")
    model=transformers.AutoModelForCausalLM.from_pretrained(MODELS[opt.model],
        revision=PINS[opt.model],trust_remote_code=True,torch_dtype=torch.float16,
        device_map="auto",low_cpu_mem_usage=True,attn_implementation="sdpa")
    model.eval();batch_size=8
    emit("MPW106_READER_HARDWARE",{"model":opt.model,"gpu":torch.cuda.get_device_name(0),
      "torch":torch.__version__,"transformers":transformers.__version__,
      "provider_hard_timeout_sec":PROVIDER_SECONDS,"batch_size":batch_size,
      "fresh_model_process":True})
    def score(messages,label):
        result=[]
        for i in range(0,len(messages),batch_size):
            texts=[tok.apply_chat_template(m,tokenize=False,add_generation_prompt=True)
                   for m in messages[i:i+batch_size]]
            batch=tok(texts,padding=True,return_tensors="pt",truncation=False,
                      add_special_tokens=False)
            if int(batch.attention_mask.sum(1).max())>INPUT_CAP:
                raise RuntimeError("MEMORY_RETRIEVAL_CONTEXT_OVERFLOW")
            batch=batch.to(model.device)
            with torch.inference_mode():
                logits=model(**batch,use_cache=False).logits[:,-1,:].float()
                result.extend((logits[:,ids["positive"]]-logits[:,ids["negative"]]).cpu().tolist())
        return [float(z if label==1 else -z) for z in result]
    def audit(f,prefix):
        out={}
        for o in ORDERS:
            msgs=[prefix+[old.case_text(f,o,f["left"],f["right"])],
                  prefix+[old.case_text(f,o,f["flip_left"],f["right"])],
                  prefix+[old.case_text(f,o,f["left"],f["flip_right"])]]
            a,b,c=score(msgs,f["label"]);iL=a-b;iR=a-c;total=abs(iL)+abs(iR)
            out[o]={"D":float((iL-iR)/(total+EPS)),
               "J":float(iL-iR),"I_left":float(iL),"I_right":float(iR),
               "sens":float(total),"acc":int(a>=0)}
        return out
    def retrieve(f,arm):
        if arm=="CLEAN":
            return base,{"status":"NO_LOOKUP","prefix_sha256":sha(canonical(base)),
                         "snapshot_commit":None,"text_sha256":None}
        if arm=="MISSING":
            reply=contract.lookup(states["LIVE"],999999,f["case_sha256"],opt.model,
                                  EXPECTED_CASE_BANK,"LIVE")
            if reply["status"]!="NO_RECORD":raise RuntimeError("MISSING_ID_HARNESS_FAIL")
            snapshot="MISSING_IN_LIVE"
        elif arm=="EXPLICIT_STALE":
            reply=contract.lookup(states["LIVE"],f["idx"],f["case_sha256"],opt.model,
                                  EXPECTED_CASE_BANK,"LIVE")
            snapshot=refs["live"]
        else:
            kind=arm
            reply=contract.lookup(states[kind],f["idx"],f["case_sha256"],opt.model,
                                  EXPECTED_CASE_BANK,kind)
            snapshot=refs[kind.lower()]
        if reply["status"]=="HIT":
            msg=MEMORY_WRAPPER+reply["text"]+'"'
            text_sha=reply["content_sha256"]
        elif reply["status"]=="NO_RECORD":
            msg=MISSING_WRAPPER;text_sha=None
        else:
            raise RuntimeError("MEMORY_LOOKUP_UNEXPECTED_STATUS")
        prefix=base+[{"role":"user","content":msg},
                     {"role":"assistant","content":"Understood."}]
        return prefix,{"status":reply["status"],
          "snapshot_commit":snapshot,"text_sha256":text_sha,
          "prefix_sha256":sha(canonical(prefix)),
          "source":reply.get("source"),
          "model_visible_text":msg}
    cal=[audit(f,base) for f in calibration]
    accuracy={o:float(np.mean([v[o]["acc"] for v in cal])) for o in ORDERS}
    sensitivity=float(np.mean([v[o]["sens"] for v in cal for o in ORDERS]))
    if any(v<.9 for v in accuracy.values()) or sensitivity<1:
        emit("MPW106_READER_END",{"model":opt.model,
          "status":"CAPABILITY_GATE_FAIL","accuracy":accuracy,"sensitivity":sensitivity});return
    original=[]
    bad=[]
    for sel in selected:
        f=cases[sel["idx"]]
        x=audit(f,base);y=audit(f,base)
        for o in ORDERS:
            screen_D=sel["screen_orders"][o]["baseline"]["D"]
            a=x[o];b=y[o]
            if abs(a["D"]-b["D"])>=1e-4 or abs(a["D"]-screen_D)>=1e-4 or (
               a["D"]*screen_D<=0 or not a["acc"] or not b["acc"] or
               min(a["I_left"],a["I_right"],b["I_left"],b["I_right"])<=0):
                bad.append({"idx":sel["idx"],"order":o,"screen":screen_D,
                    "current":a["D"],"repeat":b["D"]})
        original.append((x,y))
    if bad:
        emit("MPW106_READER_END",{"model":opt.model,"status":"INVALID_ORIGINAL_BASELINE",
             "bad_cells":len(bad),"examples":bad[:12]});return
    pilot_start=time.monotonic()
    for z in selected[:4]:
        f=cases[z["idx"]]
        for arm in ARMS:
            prefix,_=retrieve(f,arm);audit(f,prefix)
    per=(time.monotonic()-pilot_start)/4
    expected=time.monotonic()-start+per*N
    emit("MPW106_READER_TIMING",{"model":opt.model,"pilot_cases":4,
         "full_arms_per_case":len(ARMS),"measured_sec_per_family":per,
         "unpadded_forecast_sec":expected,
         "padded_forecast_warn_sec":time.monotonic()-start+1.35*per*N,
         "provider_hard_sec":PROVIDER_SECONDS,"reserve_sec":RESERVE,
         "padding_is_not_a_veto":True})
    if expected>PROVIDER_SECONDS-RESERVE:
        emit("MPW106_READER_END",{"model":opt.model,
          "status":"RESOURCE_REPLAN","n_results":0});return
    rows=[]
    for i,sel in enumerate(selected):
        if time.monotonic()-start>PROVIDER_SECONDS-RESERVE:
            emit("MPW106_READER_END",{"model":opt.model,
              "status":"ACTUAL_PROVIDER_RUNTIME_ABORT","n_complete":i});return
        f=cases[sel["idx"]]
        live=contract.lookup(states["LIVE"],f["idx"],f["case_sha256"],
                opt.model,EXPECTED_CASE_BANK,"LIVE")
        if live["status"]!="HIT":raise RuntimeError("ORIGINAL_REPORT_NOT_RETRIEVABLE")
        ent=next(e for e in states["LIVE"]["entries"] if e["case_id"]==contract.case_id(f["idx"]))
        conditions={};reads={}
        for arm in ARMS:
            p,meta=retrieve(f,arm)
            reads[arm]=meta
            conditions[arm]=audit(f,p)
        if conditions["DELETED"]!=conditions["MISSING"]:
            raise RuntimeError("DELETED_AND_MISSING_FRESH_PREFIX_NOT_IDENTICAL")
        if conditions["LIVE"]!=conditions["EXPLICIT_STALE"]:
            raise RuntimeError("EXPLICIT_OLD_GIT_SNAPSHOT_CHANGED")
        rows.append({"idx":f["idx"],"label":f["label"],
           "case_sha256":f and sha(canonical(f)),
           "original_true_side":sel["true_side"],
           "original_false_side":sel["false_side"],
           "original_report_side":ent["original_report_side"],
           "original_report_sha256":ent["original_report_sha256"],
           "original_report_text":live["text"],
           "screen_orders":sel["screen_orders"],
           "clean_baseline":original[i][0],
           "clean_repeat":original[i][1],
           "conditions":conditions,"reads":reads,
           "model_process":"FRESH_HF_GPU_JOB_NO_WRITER_HISTORY"})
        if (i+1)%16==0:emit("MPW106_READER_PROGRESS",{
            "model":opt.model,"complete":i+1,"total":N,
            "elapsed_sec":time.monotonic()-start})
    fullsha=original_shards(rows)
    emit("MPW106_READER_END",{"model":opt.model,"status":"COMPLETED",
       "n":N,"raw_sha256":fullsha,"snapshot_refs":refs,
       "elapsed_sec":time.monotonic()-start,
       "scientific_inference":"INDEPENDENT_CPU_VERIFIER_REQUIRED"})
if __name__=="__main__":main()
