# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = [
# "torch==2.6.0","transformers==4.57.3","accelerate==1.6.0",
# "datasets==3.6.0","huggingface_hub==0.36.0",
# "numpy==2.1.3","scipy==1.15.3","sentencepiece==0.2.0"
# ]
# ///
"""MPW-103I: actual eight-cycle model-authored natural explanations under provenance audit.
Every generated R_t is from live prefix S_t and written to next S_t+1.
No model-authored explanation is faked; forced/neutral controls explicitly differentiated.
Frozen protocol: mpw103i/PROTOCOL.md. No training or changed weights.
"""
import argparse,base64,gzip,hashlib,importlib.util,json,math,re,tempfile,time
from pathlib import Path
from urllib.request import urlopen

ROOT="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/"
SCREEN_SOURCE_URL="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/613a165b21fd7d4e589108ffe3fe198ca52cd8c4/mpw103i/scripts/mpw103i_screen.py"
SCREEN_SOURCE_SHA="4f89a4d759b82cd74ec21465239e48c2558df9f359f5cdff2bf5b4a208e9a04f"
EXPECTED_CASE_MANIFEST="00cf578b03d0aeabc08b0226c5d84702695e9aa3f5b3264392b31d914526c20a"
SOURCE_ORIGINAL_104_URL=ROOT+"c94d1299e8862686bb728880c3f36a1527e7b7c0/mpw104/scripts/mpw104.py"
SOURCE_ORIGINAL_104_SHA="d8866d46dcb4bc6f5e2289108c22c434add56c423e63f1731c929aed86d6d1e1"
DATASET="stanfordnlp/sst2"
DATASET_SHA="8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb"
MODELS={"qwen3":"Qwen/Qwen3-4B-Instruct-2507",
        "granite":"ibm-granite/granite-3.3-8b-instruct"}
PINS={"qwen3":"cdbee75f17c01a7cc42f958dc650907174af0554",
      "granite":"51dd4bc2ade4059a6bd87649d68aa11e4fb2529b"}
ORDERS=("LR","RL")
ARMS=("NATIVE_REPORT","ELICIT_ACK","NEUTRAL_ACK","ARBITRARY_CODE","FORCED_FALSE","DIRECTIVE")
CHECKPOINTS=(0,1,2,4,8)
MAX_ITERATIONS=8
N=64
CAL_N=32
INPUT_TOKEN_CAP=4096
MAX_REPORT_TOKENS=48
PROVIDER_SECONDS=120*60
ARCHIVE_RESERVE_SECONDS=120
BOOT=50000
BOOT_SEED=520261030
PER_TEST_ALPHA=.05/6
MAX_RAW_SHARD_FAMILIES=16
PARSE_THRESHOLD=.8
EPS=1e-6

ELICIT_Q=("Which labeled passage most influenced your answer? "
          "In one sentence begin LEFT: or RIGHT: and briefly explain why. "
          "This concerns the decision just made.")
NEUTRAL_Q="Acknowledge this result without discussing the reasons."
CODE_Q=("Choose A or B as an arbitrary formatting code unrelated to evidence, "
        "sentiment, or decisions. Answer exactly A or B.")
DIRECTIVE_Q=("For the next case, rely more on the {side} passage than "
             "the {other} passage. Acknowledge with Understood.")

def canonical(x):return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def sha(data):return hashlib.sha256(data if isinstance(data,bytes) else data.encode()).hexdigest()
def emit(tag,payload):print(tag+" "+canonical(payload),flush=True)
def source_module(url,expected,name):
    raw=urlopen(url,timeout=90).read()
    if sha(raw)!=expected:raise RuntimeError("IMMUTABLE_SOURCE_SHA_FAILED_"+name)
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/"module.py";path.write_bytes(raw)
        spec=importlib.util.spec_from_file_location(name,path)
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

def parse_natural(s):
    m=re.match(r"^\s*(LEFT|RIGHT)\s*:\s*(\S[\s\S]*)$",s,re.I)
    return m.group(1).upper() if m else None

def code_to_side(code):
    if code=="A":return "LEFT"
    if code=="B":return "RIGHT"
    return None

def append_step(state,case_message,answer,question,response):
    return list(state)+[case_message,{"role":"assistant","content":answer},
         {"role":"user","content":question},{"role":"assistant","content":response}]

def estimate(vec,i,n=N):
    import numpy as np
    from scipy.stats import binomtest
    arr=np.asarray(vec,dtype=np.float64)
    if arr.shape!=(n,) or not np.isfinite(arr).all():
        raise RuntimeError("INCOMPLETE_OR_NONFINITE_FAMILY_EFFECT")
    g=np.random.default_rng(BOOT_SEED+i)
    batches=[]
    for start in range(0,BOOT,2500):
        ii=g.integers(0,n,size=(min(2500,BOOT-start),n))
        batches.append(arr[ii].mean(axis=1))
    boots=np.concatenate(batches)
    pos=int(np.count_nonzero(arr>0))
    neg=int(np.count_nonzero(arr<0))
    return {"n":n,"mean":float(arr.mean()),
      "ci_familywise":[float(x) for x in np.quantile(boots,[PER_TEST_ALPHA/2,1-PER_TEST_ALPHA/2])],
      "ci95":[float(x) for x in np.quantile(boots,[.025,.975])],
      "positive":pos,"negative":neg,"zero":n-pos-neg,
      "sign_p":float(binomtest(pos,pos+neg,.5).pvalue) if pos+neg else 1.0}

def report_fidelity(report,versions):
    side=report.get("parsed_side")
    if side is None:return 0
    return int(all((("LEFT" if versions[o]["D"]>0 else
                    "RIGHT" if versions[o]["D"]<0 else None)==side) for o in ORDERS))

def aggregate(rows,model):
    import numpy as np
    if len(rows)!=N or len({r["idx"] for r in rows})!=N:
        raise RuntimeError("MISSING_OR_DUPLICATED_FAMILY")
    vectors={k:[] for k in ("H1","H2","H3")}
    effects_by_order={k:{o:[] for o in ORDERS} for k in ("H1","H3")}
    cohort_time={arm:{str(t):[] for t in CHECKPOINTS} for arm in ARMS}
    native_reports={t:{"00":0,"01":0,"10":0,"11":0,
        "parseable":0,"side_flips":0} for t in range(MAX_ITERATIONS)}
    drift_bounds=[]
    repeat_bounds=[]
    invalid_count=0
    parsed=0;total_reports=0
    flips_mechanism=0;flips_report=0;oscillating=0;returned_to_original=0;plateau_depth4to8=0
    for r in rows:
        if set(r["arms"])!=set(ARMS):raise RuntimeError("MISSING_ITERATION_ARM")
        original=r["screen_orders"]
        ref=r["origin"]
        if set(ref)!=set(ORDERS):raise RuntimeError("MISSING_S0_AUDIT")
        for o in ORDERS:
            base=ref[o]["baseline"];rep=ref[o]["baseline_repeat"];old=original[o]["baseline"]
            repeat_bounds.append(abs(base["D"]-rep["D"]))
            drift_bounds.append(abs(base["D"]-old["D"]))
            if (not base["acc"] or not rep["acc"] or
                base["D"]*old["D"]<=0 or
                min(base["I_left"],base["I_right"],rep["I_left"],rep["I_right"])<=0):
                invalid_count+=1
        def dist(a,b):
            return float(np.mean([abs(a[o]["D"]-b[o]["D"]) for o in ORDERS]))
        zero={o:ref[o]["baseline"] for o in ORDERS}
        for arm in ARMS:
            checkpoints=r["arms"][arm]["checkpoints"]
            if not set(CHECKPOINTS).issubset(set(map(int,checkpoints))):
                raise RuntimeError("CHECKPOINTS_MISSING_"+arm)
            if len(r["arms"][arm]["cycles"])!=MAX_ITERATIONS:
                raise RuntimeError("INCOMPLETE_EIGHT_CYCLES_"+arm)
            for t in CHECKPOINTS:
                cohort_time[arm][str(t)].append(dist(checkpoints[str(t)],zero))
        nat=r["arms"]["NATIVE_REPORT"]
        elic=r["arms"]["ELICIT_ACK"]
        h1=dist(nat["checkpoints"]["1"],zero)-dist(elic["checkpoints"]["1"],zero)
        h3=(dist(nat["checkpoints"]["8"],zero)-dist(nat["checkpoints"]["1"],zero)) - (
            dist(elic["checkpoints"]["8"],zero)-dist(elic["checkpoints"]["1"],zero))
        vectors["H1"].append(h1)
        vectors["H3"].append(h3)
        for o in ORDERS:
            v1=abs(nat["checkpoints"]["1"][o]["D"]-zero[o]["D"])-abs(
                 elic["checkpoints"]["1"][o]["D"]-zero[o]["D"])
            v3=(abs(nat["checkpoints"]["8"][o]["D"]-zero[o]["D"])-
                 abs(nat["checkpoints"]["1"][o]["D"]-zero[o]["D"]))-(
                 abs(elic["checkpoints"]["8"][o]["D"]-zero[o]["D"])-
                 abs(elic["checkpoints"]["1"][o]["D"]-zero[o]["D"]))
            effects_by_order["H1"][o].append(v1)
            effects_by_order["H3"][o].append(v3)
        native_full=nat["audits_all"]
        if set(map(int,native_full))!=set(range(0,MAX_ITERATIONS+1)):
            raise RuntimeError("MISSING_NATIVE_AUDIT_AT_INTERMEDIATE_TURNS")
        if len(nat["local_ack_audits"])!=MAX_ITERATIONS:
            raise RuntimeError("MISSING_LOCAL_ACK_COUNTERFACTUAL")
        r0=nat["cycles"][0]["report"]
        h2=report_fidelity(r0,native_full["1"])-report_fidelity(r0,nat["local_ack_audits"]["0"])
        vectors["H2"].append(h2)
        for t in range(MAX_ITERATIONS):
            rep=nat["cycles"][t]["report"]
            total_reports+=1
            parsed+=int(rep["parsed_side"] is not None)
            x=report_fidelity(rep,native_full[str(t)])
            y=report_fidelity(rep,native_full[str(t+1)])
            native_reports[t][f"{x}{y}"]+=1
            native_reports[t]["parseable"]+=int(rep["parsed_side"] is not None)
            if t>0 and rep["parsed_side"]!=nat["cycles"][t-1]["report"]["parsed_side"]:
                native_reports[t]["side_flips"]+=1;flips_report+=1
        signs=[]
        for t in range(MAX_ITERATIONS+1):
            ds=native_full[str(t)]
            signs.append(tuple(1 if ds[o]["D"]>0 else -1 if ds[o]["D"]<0 else 0 for o in ORDERS))
        sign_changes=sum(a!=b for a,b in zip(signs,signs[1:]))
        flips_mechanism+=sign_changes
        oscillating+=int(sign_changes>=2)
        returned_to_original+=int(any(z!=signs[0] for z in signs[1:8]) and signs[8]==signs[0])
        plateau_depth4to8+=int(abs(dist(nat["checkpoints"]["8"],zero)-
                                   dist(nat["checkpoints"]["4"],zero))<.05)
    valid=invalid_count==0 and max(repeat_bounds)<1e-4 and max(drift_bounds)<1e-4
    parsable=parsed/total_reports if total_reports else 0
    instruments_ok=parsable>=PARSE_THRESHOLD
    stats={k:estimate(v,i+1) for i,(k,v) in enumerate(vectors.items())}
    by_order={k:{o:float(np.mean(a)) for o,a in v.items()}
              for k,v in effects_by_order.items()}
    verdict={}
    for h,s in stats.items():
        positive=(s["mean"]>0 and s["ci_familywise"][0]>0 and
                  s["sign_p"]<PER_TEST_ALPHA)
        if h in by_order:positive=positive and all(v>0 for v in by_order[h].values())
        verdict[h]=("INVALID" if not valid else
            "INSTRUMENT_FAILURE" if not instruments_ok else
            "CONFIRMED" if positive else "NOT_CONFIRMED")
    table={}
    for t,m in native_reports.items():
        q=(m["10"]+m["11"])/N;s=(m["01"]+m["11"])/N
        C=m["01"]/N;L=m["10"]/N
        if abs(s-(q+C-L))>1e-12:raise RuntimeError("VERSION_IDENTITY_FAILED")
        table[str(t)]={"q":q,"s":s,"C":C,"L":L,
          "transition_table":{k:m[k] for k in ("00","01","10","11")},
          "parseable":m["parseable"],"side_flips":m["side_flips"]}
    return {"model":model,"n":N,"valid":bool(valid),"parse_rate":parsable,
      "instrument_parse_ok":bool(instruments_ok),"verdicts":verdict,
      "estimates":stats,"order_effects":by_order,
      "arm_drift":{arm:{t:float(np.mean(v)) for t,v in m.items()} for arm,m in cohort_time.items()},
      "versioned_native_fidelity":table,
      "max_baseline_repeat_D":max(repeat_bounds),
      "max_crossjob_screen_D":max(drift_bounds),
      "invalid_original_cells":invalid_count,
      "native_report_side_changes_total":flips_report,
      "native_mechanism_tuple_changes_total":flips_mechanism,
      "native_families_with_2plus_mechanism_changes":oscillating,
      "native_families_returning_to_original_sign_tuple":returned_to_original,
      "native_families_depth4to8_drift_plateau_delta_lt_005":plateau_depth4to8}

def chunked_archive(tag,rows):
    if len(rows)%MAX_RAW_SHARD_FAMILIES:raise RuntimeError("SHARD_WRONG_CARDINALITY")
    raw=("\n".join(canonical(r) for r in rows)+"\n").encode()
    for start in range(0,len(rows),MAX_RAW_SHARD_FAMILIES):
        part=("\n".join(canonical(r) for r in rows[start:start+MAX_RAW_SHARD_FAMILIES])+"\n").encode()
        c=base64.b64encode(gzip.compress(part,compresslevel=9,mtime=0)).decode()
        for off in range(0,len(c),9000):
            emit(tag+"_B64",{"part":off//9000,"total":(len(c)+8999)//9000,
              "sha256":sha(part),"data":c[off:off+9000]})
        emit(tag+"_SHARD",{"part":start//MAX_RAW_SHARD_FAMILIES,
             "n":MAX_RAW_SHARD_FAMILIES,"range":[start,start+MAX_RAW_SHARD_FAMILIES-1],
             "raw_sha256":sha(part)})
    return sha(raw)

def main():
    a=argparse.ArgumentParser()
    a.add_argument("mode",choices=("execute",))
    a.add_argument("--model",choices=tuple(MODELS),required=True)
    a.add_argument("--screen-commit",required=True)
    opts=a.parse_args()
    start=time.monotonic()
    if (len(opts.screen_commit)!=40 or
        any(c not in "0123456789abcdef" for c in opts.screen_commit)):
        raise RuntimeError("SCREEN_SELECTION_MUST_HAVE_IMMUTABLE_COMMIT")
    from huggingface_hub import dataset_info,model_info
    from datasets import load_dataset
    found={k:model_info(v).sha for k,v in MODELS.items()}
    if found!=PINS or dataset_info(DATASET).sha!=DATASET_SHA:
        raise RuntimeError("FROZEN_MODEL_OR_DATASET_REVISION_DRIFT")
    screen=source_module(SCREEN_SOURCE_URL,SCREEN_SOURCE_SHA,"mpw103i_original_screen_source")
    train=load_dataset(DATASET,revision=DATASET_SHA,split="train")
    valid=load_dataset(DATASET,revision=DATASET_SHA,split="validation")
    cal,pool,bank,meta=screen.make_cases(train,valid)
    if sha(bank)!=EXPECTED_CASE_MANIFEST:
        raise RuntimeError("CASE_BANK_NOT_FROZEN")
    old104=source_module(SOURCE_ORIGINAL_104_URL,SOURCE_ORIGINAL_104_SHA,
                         "mpw104_case_and_base_protocol")
    parent,base=old104.prior_artifacts()
    raw_selection=urlopen(ROOT+opts.screen_commit+"/mpw103i/selection/"+opts.model+".json",
                         timeout=90).read()
    selection=json.loads(raw_selection)
    if (not selection.get("selection_complete") or
        selection.get("n_selected")!=N or
        selection.get("source_candidate_sha256")!=sha(bank)):
        raise RuntimeError("SELECTION_NOT_COMPLETE_OR_WRONG_CASES")
    chosen_idx=[z["idx"] for z in selection["selected"]]
    if chosen_idx!=sorted(set(chosen_idx)):raise RuntimeError("CASE_IDS_NOT_SORTED_UNIQUE")
    lookup={f["idx"]:f for f in pool if f["idx"] in set(chosen_idx)}
    if len(lookup)!=N:raise RuntimeError("MISSING_FROZEN_CASE")
    for z in selection["selected"]:
        if (sha(canonical(lookup[z["idx"]]))!=z["case_sha256"] or
            z["true_side"]==z["false_side"]):
            raise RuntimeError("SELECTED_CASE_CORRUPTED")
    import numpy as np,torch,transformers
    from transformers import AutoTokenizer
    name=opts.model;repo=MODELS[name]
    tokenizer=AutoTokenizer.from_pretrained(repo,revision=PINS[name],trust_remote_code=True)
    tokenizer.padding_side="left"
    tokenizer.pad_token=tokenizer.pad_token or tokenizer.eos_token
    raw_ids={k:tokenizer.encode(k,add_special_tokens=False) for k in
             ("positive","negative","A","B")}
    if any(len(v)!=1 for v in raw_ids.values()):raise RuntimeError("NONATOMIC_OUTPUT")
    ids={k:v[0] for k,v in raw_ids.items()}
    if not torch.cuda.is_available():raise RuntimeError("CUDA_REQUIRED")
    model=transformers.AutoModelForCausalLM.from_pretrained(repo,
        revision=PINS[name],trust_remote_code=True,torch_dtype=torch.float16,
        device_map="auto",low_cpu_mem_usage=True,attn_implementation="sdpa")
    model.eval()
    batch_size=8
    emit("MPW103I_SOURCE",{"model":name,"source_sha256":sha(Path(__file__).read_bytes()),
        "case_manifest_sha256":sha(bank),"screen_commit":opts.screen_commit,
        "screen_selection_sha256":sha(raw_selection),"n":N,"screen_meta":meta,
        "model_revision":PINS[name],"dataset_revision":DATASET_SHA,
        "hard_input_tokens":INPUT_TOKEN_CAP})
    emit("MPW103I_HARDWARE",{"model":name,"gpu":torch.cuda.get_device_name(0),
        "torch":torch.__version__,"transformers":transformers.__version__,
        "provider_timeout_sec":PROVIDER_SECONDS})
    def input_messages(prefix,f,order,left,right):
        return prefix+[old104.case_text(f,order,left,right)]
    def batch_margin(msgsets,label):
        out=[]
        for offset in range(0,len(msgsets),batch_size):
            parts=msgsets[offset:offset+batch_size]
            text=[tokenizer.apply_chat_template(x,tokenize=False,add_generation_prompt=True) for x in parts]
            tok=tokenizer(text,return_tensors="pt",padding=True,
                          truncation=False,add_special_tokens=False)
            if int(tok.attention_mask.sum(1).max())>INPUT_TOKEN_CAP:
                raise RuntimeError("INPUT_HARD_CAP_EXCEEDED_NO_TRUNCATION")
            tok=tok.to(model.device)
            with torch.inference_mode():
                z=model(**tok,use_cache=False).logits[:,-1,:].float()
                out.extend((z[:,ids["positive"]]-z[:,ids["negative"]]).cpu().tolist())
        return [float(x if label==1 else -x) for x in out]
    def audit(prefix,f):
        out={}
        for order in ORDERS:
            msgsets=[input_messages(prefix,f,order,f["left"],f["right"]),
                     input_messages(prefix,f,order,f["flip_left"],f["right"]),
                     input_messages(prefix,f,order,f["left"],f["flip_right"])]
            ma,ml,mr=batch_margin(msgsets,f["label"])
            left=ma-ml;right=ma-mr
            sensitivity=abs(left)+abs(right)
            out[order]={"D":float((left-right)/(sensitivity+EPS)),
                        "J":float(left-right),"I_left":float(left),
                        "I_right":float(right),"sens":float(sensitivity),
                        "acc":int(ma>=0)}
        return out
    def next_choice(messages,options):
        text=tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
        tok=tokenizer(text,return_tensors="pt",truncation=False,add_special_tokens=False)
        if int(tok.attention_mask.sum())>INPUT_TOKEN_CAP:
            raise RuntimeError("NEXT_TOKEN_PROMPT_TOO_LONG")
        tok=tok.to(model.device)
        with torch.inference_mode():
            logits=model(**tok,use_cache=False).logits[0,-1].float()
        score={label:float(logits[ids[label]].item()) for label in options}
        selected=max(options,key=lambda k:(score[k],-options.index(k)))
        return selected,score
    def native_prose(messages):
        prompt=tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
        enc=tokenizer(prompt,return_tensors="pt",truncation=False,add_special_tokens=False)
        if int(enc.attention_mask.sum())>INPUT_TOKEN_CAP:
            raise RuntimeError("GENERATION_CONTEXT_LONGER_THAN_4096")
        enc=enc.to(model.device)
        with torch.inference_mode():
            gen=model.generate(**enc,max_new_tokens=MAX_REPORT_TOKENS,do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,use_cache=True)
        added=gen[0][enc.input_ids.shape[1]:]
        ids_added=added.cpu().tolist()
        raw=tokenizer.decode(added,skip_special_tokens=True).strip()
        return {"raw":raw,"token_ids":ids_added,"parsed_side":parse_natural(raw),
                "n_tokens":len(ids_added),"source":"MODEL_GREEDY_GENERATED",
                "prompt_sha256":sha(prompt),"max_new_tokens":MAX_REPORT_TOKENS}
    def state_hash(state):
        return sha(canonical(state))
    def run_family(f,z):
        screen_orders=z["screen_orders"];origin= audit(base,f)
        original_repeat=audit(base,f)
        for order in ORDERS:
            if (abs(origin[order]["D"]-screen_orders[order]["baseline"]["D"])>=1e-4 or
                abs(origin[order]["D"]-original_repeat[order]["D"])>=1e-4 or
                origin[order]["D"]*screen_orders[order]["baseline"]["D"]<=0 or
                not origin[order]["acc"] or not original_repeat[order]["acc"] or
                min(origin[order]["I_left"],origin[order]["I_right"],
                    original_repeat[order]["I_left"],original_repeat[order]["I_right"])<=0):
                # Retain all measured output, but do not choose new historical truth.
                emit("MPW103I_FAMILY_BASELINE_ANOMALY",{"idx":f["idx"],"order":order,
                    "screen_D":screen_orders[order]["baseline"]["D"],
                    "new_D":origin[order]["D"],
                    "repeat_D":original_repeat[order]["D"]})
        record={"idx":f["idx"],"label":f["label"],
          "case_sha256":sha(canonical(f)),
          "original_true_side":z["true_side"],
          "original_false_side":z["false_side"],
          "screen_orders":screen_orders,
          "origin":{o:{"baseline":origin[o],"baseline_repeat":original_repeat[o]} for o in ORDERS},
          "arms":{}}
        task=old104.case_text(f,"LR",f["left"],f["right"])
        for arm in ARMS:
            state=list(base)
            part={"checkpoints":{"0":origin},"cycles":[]}
            if arm=="NATIVE_REPORT":
                part["audits_all"]={"0":origin}
                part["local_ack_audits"]={}
            for t in range(MAX_ITERATIONS):
                oldsha=state_hash(state)
                if arm=="NATIVE_REPORT" and str(t) not in part["audits_all"]:
                    part["audits_all"][str(t)]=audit(state,f)
                answer,answer_scores=next_choice(state+[task],("positive","negative"))
                context=state+[task,{"role":"assistant","content":answer}]
                question=None
                report=None
                if arm in ("NATIVE_REPORT","ELICIT_ACK","FORCED_FALSE"):
                    question=ELICIT_Q
                elif arm=="NEUTRAL_ACK":
                    question=NEUTRAL_Q
                elif arm=="ARBITRARY_CODE":
                    question=CODE_Q
                else:
                    question=DIRECTIVE_Q.format(side=z["false_side"],other=z["true_side"])
                if arm=="NATIVE_REPORT":
                    report=native_prose(context+[{"role":"user","content":question}])
                    response=report["raw"]
                    ack=append_step(state,task,answer,question,"Understood.")
                    part["local_ack_audits"][str(t)]=audit(ack,f)
                elif arm=="FORCED_FALSE":
                    side=z["false_side"]
                    response=f"{side}: The {side} passage was the stronger reason for my decision."
                    report={"raw":response,"parsed_side":side,
                        "source":"EXPERIMENTER_FORCED_BASELINE_FALSE",
                        "n_tokens":len(tokenizer.encode(response,add_special_tokens=False))}
                elif arm=="ARBITRARY_CODE":
                    response,code_scores=next_choice(context+[{"role":"user","content":question}],("A","B"))
                    report={"raw":response,"parsed_side":None,
                        "source":"MODEL_GREEDY_ARBITRARY_CODE",
                        "code_logits":code_scores,"n_tokens":1}
                else:
                    response="Understood."
                    report={"raw":response,"parsed_side":None,
                        "source":"EXPERIMENTER_FORCED_ACKNOWLEDGMENT",
                        "n_tokens":len(tokenizer.encode(response,add_special_tokens=False))}
                state=append_step(state,task,answer,question,response)
                item={"t":t,"pre_state_sha256":oldsha,"native_task_answer":answer,
                      "answer_logits":answer_scores,"question":question,
                      "report":report,"post_state_sha256":state_hash(state),
                      "response_role":"assistant"}
                part["cycles"].append(item)
                if arm=="NATIVE_REPORT":
                    part["audits_all"][str(t+1)]=audit(state,f)
                    part["checkpoints"][str(t+1)]=part["audits_all"][str(t+1)]
                elif t+1 in CHECKPOINTS:
                    part["checkpoints"][str(t+1)]=audit(state,f)
            if set(map(int,part["checkpoints"]))!=set(range(9) if arm=="NATIVE_REPORT" else CHECKPOINTS):
                raise RuntimeError("INCOMPLETE_CHECKPOINTS_"+arm)
            record["arms"][arm]=part
        return record
    calrows=[audit(base,f) for f in cal]
    acc={o:float(np.mean([z[o]["acc"] for z in calrows])) for o in ORDERS}
    sensitivity=float(np.mean([z[o]["sens"] for z in calrows for o in ORDERS]))
    eligible=all(v>=.9 for v in acc.values()) and sensitivity>=1
    emit("MPW103I_CALIBRATION",{"model":name,"n":len(cal),"accuracy":acc,
         "sensitivity":sensitivity,"eligible":eligible})
    if not eligible:
        emit("MPW103I_END",{"model":name,"status":"CAPABILITY_GATE_FAIL",
             "no_iteration":True})
        return
    # Complete the prospective full eight-cycle workload pilot on TWO calibration cases.
    pilot_start=time.monotonic()
    for f in cal[:2]:
        screen_dummy={"screen_orders":{o:{"baseline":audit(base,f)[o]} for o in ORDERS},
                      "true_side":"LEFT","false_side":"RIGHT"}
        run_family(f,screen_dummy)
    pilot_sec=(time.monotonic()-pilot_start)/2
    predicted=time.monotonic()-start+pilot_sec*N
    emit("MPW103I_TIMING",{"model":name,"pilot_cases":2,
       "seconds_per_full_eight_cycle_family":pilot_sec,
       "unpadded_expected_seconds":predicted,
       "padded_warning_seconds":time.monotonic()-start+1.35*pilot_sec*N,
       "provider_timeout_seconds":PROVIDER_SECONDS,"archive_reserve_seconds":ARCHIVE_RESERVE_SECONDS,
       "padding_is_veto":False})
    if predicted>PROVIDER_SECONDS-ARCHIVE_RESERVE_SECONDS:
        emit("MPW103I_END",{"model":name,"status":"RESOURCE_REPLAN",
             "n_validated":0,"not_a_scientific_negative":True})
        return
    emit("MPW103I_VALIDATION_START",{"model":name,"n":N,
        "screen_selection_sha256":sha(raw_selection)})
    rows=[]
    for i,z in enumerate(selection["selected"]):
        if time.monotonic()-start>PROVIDER_SECONDS-ARCHIVE_RESERVE_SECONDS:
            emit("MPW103I_END",{"model":name,"status":"PHYSICAL_RUNTIME_ABORT",
                "n_validated":len(rows),"not_a_primary_result":True})
            return
        row=run_family(lookup[z["idx"]],z)
        rows.append(row)
        if (i+1)%8==0:
            emit("MPW103I_PROGRESS",{"model":name,"complete":i+1,"total":N,
                "elapsed_seconds":time.monotonic()-start})
    raw_sha=chunked_archive("MPW103I_ITERATION",rows)
    results=aggregate(rows,name)
    emit("MPW103I_PRIMARY_RESULT",results)
    emit("MPW103I_END",{"model":name,"status":"COMPLETED",
       "n":len(rows),"raw_sha256":raw_sha,
       "screen_commit":opts.screen_commit,
       "elapsed_seconds":time.monotonic()-start,
       "verdicts":results["verdicts"]})
if __name__=="__main__":main()
