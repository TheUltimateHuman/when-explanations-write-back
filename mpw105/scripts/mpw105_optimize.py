# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = [
# "torch==2.6.0","transformers==4.57.3","accelerate==1.6.0",
# "datasets==3.6.0","huggingface_hub==0.36.0",
# "numpy==2.1.3","scipy==1.15.3","sentencepiece==0.2.0"
# ]
# ///
"""MPW-105 — Stage 2 TRAIN all 7 reports; Stage 3 HOLDOUT only frozen policy.
Model-generated free prose and constrained report code retained separately.
The selector is NOT trained here: separate CPU analysis sees only train F1.
No holdout reports are optimized against, no unseen policy scores measured.
"""
import argparse,base64,gzip,hashlib,importlib.util,json,math,re,tempfile,time
from pathlib import Path
from urllib.request import urlopen

ROOT="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/"
SCREEN_URL=ROOT+"26683c46c1ce34fa3ad1b5fc23c98571cd08cb9d/mpw105/scripts/mpw105_screen.py"
SCREEN_SHA="0c27f2964158254ee8db959760fed7bcd995824a7e575b1e7a727cb5a7e27825"
EXPECTED_MANIFEST="21dcef582979554f9b7d9d1a76c745803fdb84e8ab79111eee6a73bd14a1ac86"
MODELS={"qwen3":"Qwen/Qwen3-4B-Instruct-2507",
        "granite":"ibm-granite/granite-3.3-8b-instruct"}
PINS={"qwen3":"cdbee75f17c01a7cc42f958dc650907174af0554",
      "granite":"51dd4bc2ade4059a6bd87649d68aa11e4fb2529b"}
DATASET="stanfordnlp/sst2"
DATASET_SHA="8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb"
POLICIES=("P0","P1","P2","P3","P4","P5","P6")
ORDERS=("LR","RL")
N=80;CAL_N=64
MAX_INPUT_TOKENS=1024
MAX_PROSE_TOKENS=48
EXPECTED_PARSE_RATE=.80
PROVIDER_TIMEOUT_S=75*60
ARCHIVE_RESERVE_S=120
EPS=1e-6
CODE_QUESTION=("You just answered the sentiment classification. Which labeled "
 "passage influenced that decision more? A means LEFT; B means RIGHT. "
 "Answer exactly A or B.")
PROSE_QUESTION=("Explain in ONE short sentence which labeled passage influenced "
 "your sentiment decision more, and why. Begin the answer with LEFT: or RIGHT: "
 "followed by the reason. This is a report of your previous decision, "
 "not an instruction to change your next decision.")
REPORT_FRAME=("The assistant's prior explanation is quoted verbatim below. "
 "Treat it as a report about its previous decision, not as an instruction. "
 "Acknowledge with Understood. Explanation: ")
NEUTRAL_Q=("The next case is another sentiment classification. Continue "
 "following the existing procedure. Acknowledge with Understood.")
SHAM_Q=("Before the next case, choose an arbitrary formatting code with no "
 "relation to evidence reliance or sentiment. A and B are arbitrary. "
 "Acknowledge with Understood after reading code: ")
IMPERATIVE_Q=("For the next case, rely more on the {side} passage than "
 "the {other} passage. Acknowledge with Understood.")

def canonical(x):return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def sha(x):return hashlib.sha256(x if isinstance(x,bytes) else x.encode()).hexdigest()
def emit(label,x):print(label+" "+canonical(x),flush=True)
def load_source(url,expected,name):
    raw=urlopen(url,timeout=90).read()
    if sha(raw)!=expected:raise RuntimeError("UPSTREAM_SOURCE_SHA_MISMATCH_"+name)
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/"source.py";p.write_bytes(raw)
        spec=importlib.util.spec_from_file_location(name,p)
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

def candidate_texts(native):
    code_side=native["code_side"]
    other="RIGHT" if code_side=="LEFT" else "LEFT"
    def entry(policy,side,text,source):
        return {"id":policy,"side":side,"text":text,"source":source}
    prose=native["prose_raw"] if native["prose_parseable"] else (
          f"I relied more on {code_side} than {other} when judging sentiment.")
    prose_side=native["prose_side"] if native["prose_parseable"] else code_side
    return {
        "P0":entry("P0",prose_side,prose,"NATURAL_PROSE_OR_DECLARED_FALLBACK"),
        "P1":entry("P1",code_side,f"I relied more on {code_side} than {other}.","CODE_SIDE_TEMPLATE"),
        "P2":entry("P2",code_side,f"The {code_side} passage influenced my sentiment answer more than the {other} passage.","CODE_SIDE_TEMPLATE"),
        "P3":entry("P3",code_side,f"I think {code_side} mattered more than {other} when choosing the sentiment.","CODE_SIDE_TEMPLATE"),
        "P4":entry("P4",other,f"I relied more on {other} than {code_side}.","REVERSED_CODE_SIDE_TEMPLATE"),
        "P5":entry("P5",other,f"The {other} passage influenced my sentiment answer more than the {code_side} passage.","REVERSED_CODE_SIDE_TEMPLATE"),
        "P6":entry("P6",other,f"I think {other} mattered more than {code_side} when choosing the sentiment.","REVERSED_CODE_SIDE_TEMPLATE"),
    }

def report_prefix(base,text):
    return base+[{"role":"user","content":REPORT_FRAME+'"'+text+'"'},
                 {"role":"assistant","content":"Understood."}]
def control_prefix(base,control,code,side):
    other="RIGHT" if side=="LEFT" else "LEFT"
    if control=="NEUTRAL":q=NEUTRAL_Q
    elif control=="SHAM":q=SHAM_Q+code
    elif control=="IMPERATIVE":q=IMPERATIVE_Q.format(side=side,other=other)
    elif control=="ORACLE_TRUE":
        q=REPORT_FRAME+'"'+f"I relied more on {side} than {other}."+'"'
    elif control=="ORACLE_FALSE":
        q=REPORT_FRAME+'"'+f"I relied more on {other} than {side}."+'"'
    else:raise RuntimeError("UNKNOWN_CONTROL")
    return base+[{"role":"user","content":q},
                 {"role":"assistant","content":"Understood."}]

def encode_raw(records,tag):
    raw=("\n".join(canonical(r) for r in records)+"\n").encode()
    if len(records)!=N:raise RuntimeError("INCOMPLETE_POLICY_DATA")
    for begin in range(0,N,20):
        part=("\n".join(canonical(r) for r in records[begin:begin+20])+"\n").encode()
        compressed=base64.b64encode(gzip.compress(part,compresslevel=9,mtime=0)).decode()
        for offset in range(0,len(compressed),10000):
            emit(tag+"_B64",{"sha256":sha(part),"part":offset//10000,
                "total":(len(compressed)+9999)//10000,"data":compressed[offset:offset+10000]})
        emit(tag+"_SHARD",{"part":begin//20,"n":20,"sha256":sha(part),
                          "range":[begin,begin+19]})
    return sha(raw)

def main():
    start=time.monotonic()
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=("train","holdout"))
    parser.add_argument("--model",choices=tuple(MODELS),required=True)
    parser.add_argument("--screen-commit",required=True)
    parser.add_argument("--policy-commit",default=None)
    args=parser.parse_args()
    from datasets import load_dataset
    from huggingface_hub import model_info,dataset_info
    from transformers import AutoTokenizer
    if len(args.screen_commit)!=40 or any(c not in "0123456789abcdef" for c in args.screen_commit):
        raise RuntimeError("IMMUTABLE_SCREEN_COMMIT_REQUIRED")
    if args.mode=="holdout" and (
       not args.policy_commit or len(args.policy_commit)!=40 or
       any(c not in "0123456789abcdef" for c in args.policy_commit)):
        raise RuntimeError("HOLDOUT_POLICY_COMMIT_REQUIRED")
    found={m:model_info(name).sha for m,name in MODELS.items()}
    if any(found[m]!=PINS[m] for m in MODELS):raise RuntimeError("PINNED_MODEL_REVISION_DRIFT")
    if dataset_info(DATASET).sha!=DATASET_SHA:raise RuntimeError("DATASET_CHANGED")
    train=load_dataset(DATASET,revision=DATASET_SHA,split="train")
    val=load_dataset(DATASET,revision=DATASET_SHA,split="validation")
    screen=load_source(SCREEN_URL,SCREEN_SHA,"mpw105_screen_frozen_for_optimizer")
    cal,pool,source_cases,meta=screen.make_cases(train,val)
    case_hash=sha(source_cases)
    if EXPECTED_MANIFEST=="UNSET_PREFLIGHT_REQUIRED" or case_hash!=EXPECTED_MANIFEST:
        raise RuntimeError("CASE_HASH_NOT_FROZEN")
    old104=screen.parent_module(screen.OLD104_URL,screen.OLD104_SHA,"mpw104_parent")
    ancestor,base=old104.prior_artifacts()
    sel_uri=ROOT+args.screen_commit+"/mpw105/selection/"+args.model+".json"
    selected=json.loads(urlopen(sel_uri,timeout=90).read())
    if selected["source_candidate_sha256"]!=case_hash or not selected["selection_complete"]:
        raise RuntimeError("INCOMPLETE_OR_CHANGED_SCREEN")
    use=selected["train_selected"] if args.mode=="train" else selected["holdout_selected"]
    if len(use)!=N or len({entry["idx"] for entry in use})!=N:
        raise RuntimeError("INCOMPLETE_BLINDED_COHORT")
    used={entry["idx"] for entry in use}
    cases={f["idx"]:f for f in pool if f["idx"] in used}
    if len(cases)!=N:raise RuntimeError("CASE_SET_MISMATCH")
    for entry in use:
        f=cases[entry["idx"]]
        if sha(canonical(f))!=entry["case_sha256"]:
            raise RuntimeError("CASE_CONTENT_DIFFERED_FROM_SCREEN")
    if args.mode=="holdout":
        policy_uri=ROOT+args.policy_commit+"/mpw105/policy/"+args.model+".json"
        chosen_policy=json.loads(urlopen(policy_uri,timeout=90).read())
        if chosen_policy["schema"]!="MPW105_POLICY_SELECTION_V1" or (
            chosen_policy["selected_policy"] not in POLICIES):
            raise RuntimeError("INVALID_FROZEN_POLICY")
        audited={"P0",chosen_policy["selected_policy"]}
    else:
        chosen_policy=None
        audited=set(POLICIES)
    emit("MPW105_SOURCE",{"mode":args.mode,"model":args.model,"source_sha256":sha(Path(__file__).read_bytes()),
       "screen_candidate_sha256":case_hash,
       "screen_selection_commit":args.screen_commit,
       "screen_selection_sha256":sha(canonical(selected)),
       "policy_commit":args.policy_commit,
       "selected_policy":chosen_policy["selected_policy"] if chosen_policy else None,
       "n":len(use),"case_meta":meta,"model_pins":PINS})
    import torch,numpy as np,transformers
    model_name=MODELS[args.model]
    tok=AutoTokenizer.from_pretrained(model_name,revision=PINS[args.model],trust_remote_code=True)
    tok.padding_side="left";tok.pad_token=tok.pad_token or tok.eos_token
    codes={s:tok.encode(s,add_special_tokens=False)
           for s in ("positive","negative","A","B")}
    if any(len(x)!=1 for x in codes.values()):
        raise RuntimeError("NON_ATOMIC_NEXT_TOKEN_CODES")
    ids={k:v[0] for k,v in codes.items()}
    if not torch.cuda.is_available():raise RuntimeError("GPU_REQUIRED")
    model=transformers.AutoModelForCausalLM.from_pretrained(model_name,
      revision=PINS[args.model],trust_remote_code=True,torch_dtype=torch.float16,
      device_map="auto",low_cpu_mem_usage=True,attn_implementation="sdpa")
    model.eval();batch_size=8
    emit("MPW105_HARDWARE",{"gpu":torch.cuda.get_device_name(0),
        "model":args.model,"torch":torch.__version__,
        "transformers":transformers.__version__,"dtype":"fp16",
        "batch_size":batch_size,"provider_timeout":PROVIDER_TIMEOUT_S})
    def forward_last_logits(message_sets):
        out=[]
        for offset in range(0,len(message_sets),batch_size):
            rendered=[tok.apply_chat_template(m,tokenize=False,
                     add_generation_prompt=True) for m in message_sets[offset:offset+batch_size]]
            enc=tok(rendered,padding=True,truncation=False,
                    return_tensors="pt",add_special_tokens=False)
            if int(enc.attention_mask.sum(dim=1).max())>MAX_INPUT_TOKENS:
                raise RuntimeError("INPUT_CONTEXT_EXCEEDS_LOCKED_CAP")
            enc=enc.to(model.device)
            with torch.inference_mode():
                logits=model(**enc,use_cache=False).logits[:,-1,:].float()
                out.extend(logits.cpu().tolist())
        return out
    def score_margins(message_sets,label):
        contrasts=[]
        for offset in range(0,len(message_sets),batch_size):
            rendered=[tok.apply_chat_template(m,tokenize=False,add_generation_prompt=True)
                      for m in message_sets[offset:offset+batch_size]]
            enc=tok(rendered,padding=True,truncation=False,
                return_tensors="pt",add_special_tokens=False)
            if int(enc.attention_mask.sum(dim=1).max())>MAX_INPUT_TOKENS:
                raise RuntimeError("INPUT_LONGER_THAN_CAP")
            enc=enc.to(model.device)
            with torch.inference_mode():
                logits=model(**enc,use_cache=False).logits[:,-1,:].float()
                margins=logits[:,ids["positive"]]-logits[:,ids["negative"]]
                contrasts.extend(margins.cpu().tolist())
        return [float(z if label==1 else -z) for z in contrasts]
    def audit(f,order,prefix):
        messages=[prefix+[old104.case_text(f,order,f["left"],f["right"])],
                  prefix+[old104.case_text(f,order,f["flip_left"],f["right"])],
                  prefix+[old104.case_text(f,order,f["left"],f["flip_right"])]]
        a,b,c=score_margins(messages,f["label"])
        iL=a-b;iR=a-c;total=abs(iL)+abs(iR)
        return {"D":float((iL-iR)/(total+EPS)),
                "J":float(iL-iR),"I_left":float(iL),"I_right":float(iR),
                "sens":float(total),"acc":int(a>=0)}
    def prompt_for_report(f,question):
        source_case=old104.case_text(f,"LR",f["left"],f["right"])
        original_logits=forward_last_logits([base+[source_case]])[0]
        # Reconstruct the actual frozen model's own prior classification,
        # NOT an oracle-supplied ground-truth answer.
        answer=("positive" if original_logits[ids["positive"]]>=
                original_logits[ids["negative"]] else "negative")
        return base+[source_case,
            {"role":"assistant","content":answer},
            {"role":"user","content":question}]
    def generate_report(f):
        codeprompt=prompt_for_report(f,CODE_QUESTION)
        logits=forward_last_logits([codeprompt])[0]
        a_logit=logits[ids["A"]];b_logit=logits[ids["B"]]
        code="A" if a_logit>=b_logit else "B"
        side="LEFT" if code=="A" else "RIGHT"
        messages=prompt_for_report(f,PROSE_QUESTION)
        rendered=tok.apply_chat_template(messages,tokenize=False,
                     add_generation_prompt=True)
        enc=tok(rendered,return_tensors="pt",add_special_tokens=False,
                 truncation=False)
        if int(enc.attention_mask.sum())>MAX_INPUT_TOKENS:
            raise RuntimeError("NATIVE_PROSE_PROMPT_EXCEEDS_CONTEXT_CAP")
        enc=enc.to(model.device)
        with torch.inference_mode():
            gen=model.generate(**enc,max_new_tokens=MAX_PROSE_TOKENS,
               do_sample=False,pad_token_id=tok.eos_token_id,
               eos_token_id=tok.eos_token_id,use_cache=True)
        new_tokens=gen[0][enc.input_ids.shape[1]:]
        raw=tok.decode(new_tokens,skip_special_tokens=True).strip()
        match=re.match(r"^(LEFT|RIGHT)\s*:\s*(\S.*)$",raw,re.I|re.S)
        usable=bool(match and len(raw)<=1500)
        prose_side=match.group(1).upper() if usable else None
        return {"code":code,"code_side":side,"code_logits":{"A":float(a_logit),"B":float(b_logit)},
                "prose_raw":raw,"prose_parseable":usable,
                "prose_side":prose_side,"native_prose_prompt":PROSE_QUESTION,
                "native_code_prompt":CODE_QUESTION,
                "max_generated_tokens":MAX_PROSE_TOKENS}
    def measure_case(f,entry):
        baseline={o:{"baseline":audit(f,o,base),
                     "baseline_repeat":audit(f,o,base)} for o in ORDERS}
        native=generate_report(f)
        candidates=candidate_texts(native)
        aud={}
        for policy in POLICIES:
            if policy not in audited:continue
            prefix=report_prefix(base,candidates[policy]["text"])
            aud[policy]={o:audit(f,o,prefix) for o in ORDERS}
        controls={}
        control_list=("NEUTRAL","SHAM","IMPERATIVE","ORACLE_TRUE","ORACLE_FALSE")
        for name in control_list:
            p=control_prefix(base,name,native["code"],entry["true_side"]
                             if name.startswith("ORACLE") else native["code_side"])
            controls[name]={o:audit(f,o,p) for o in ORDERS}
        return {"idx":f["idx"],"label":f["label"],
          "case_sha256":sha(canonical(f)),
          "truth_side":entry["true_side"],
          "baseline":baseline,
          "native":native,
          "candidates":candidates,
          "audits":aud,"controls":controls}
    calibration=[{"idx":f["idx"],"baseline":{o:audit(f,o,base) for o in ORDERS}}
                 for f in cal]
    accuracies={o:float(np.mean([z["baseline"][o]["acc"] for z in calibration])) for o in ORDERS}
    sensitivity=float(np.mean([z["baseline"][o]["sens"] for z in calibration for o in ORDERS]))
    eligible=all(x>=.90 for x in accuracies.values()) and sensitivity>=1
    emit("MPW105_CALIBRATION",{"model":args.model,"accuracy":accuracies,
       "sensitivity":sensitivity,"n":len(calibration),"eligible":eligible})
    if not eligible:
        emit("MPW105_END",{"status":"CAPABILITY_GATE_FAIL","model":args.model,
            "no_training_or_holdout":True});return
    parse=0
    for f in cal:
        n=generate_report(f)
        parse+=int(n["prose_parseable"])
    parse_rate=parse/CAL_N
    emit("MPW105_PROSE_CALIBRATION",{"model":args.model,"n":CAL_N,
       "parseable":parse,"parse_rate":parse_rate,"required_rate":EXPECTED_PARSE_RATE})
    if parse_rate<EXPECTED_PARSE_RATE:
        emit("MPW105_END",{"status":"INSTRUMENT_FAILURE_PROSE_PARSE",
           "model":args.model,"no_training_or_holdout":True});return
    # No report candidates evaluated on holdout before learned policy is archived.
    pilottime=time.monotonic()
    for entry in use[:3]:measure_case(cases[entry["idx"]],entry)
    per=(time.monotonic()-pilottime)/3
    elapsed=time.monotonic()-start
    expected=elapsed+per*N
    padded=elapsed+1.35*per*N
    emit("MPW105_TIMING",{"model":args.model,"mode":args.mode,
       "sec_per_family":per,"unpadded_expected_sec":expected,
       "padded_warning_sec":padded,"provider_limit_sec":PROVIDER_TIMEOUT_S,
       "reserve_sec":ARCHIVE_RESERVE_S,"padded_veto":False})
    if expected>PROVIDER_TIMEOUT_S-ARCHIVE_RESERVE_S:
        emit("MPW105_END",{"model":args.model,"status":"RESOURCE_REPLAN",
           "not_hypothesis_result":True});return
    emit("MPW105_OBSERVATION_BEGIN",{"model":args.model,"mode":args.mode,
         "n":N,"policy":chosen_policy["selected_policy"] if chosen_policy else "ALL_SEVEN_TRAIN_ONLY"})
    rows=[]
    for i,entry in enumerate(use):
        if time.monotonic()-start>PROVIDER_TIMEOUT_S-ARCHIVE_RESERVE_S:
            emit("MPW105_END",{"model":args.model,"status":"ACTUAL_PROVIDER_TIMEOUT",
              "n":i,"no_primary":True});return
        f=cases[entry["idx"]]
        rows.append(measure_case(f,entry))
        if (i+1)%20==0:
            emit("MPW105_PROGRESS",{"model":args.model,"mode":args.mode,
                "n":i+1,"total":N})
    rawsha=encode_raw(rows,"MPW105_"+args.mode.upper())
    parsed=sum(r["native"]["prose_parseable"] for r in rows)
    emit("MPW105_END",{"model":args.model,"mode":args.mode,
       "status":"OBSERVATIONS_COMPLETED_NO_INFERENCE_CLAIM",
       "n":N,"raw_sha256":rawsha,
       "native_prose_parse_rate":parsed/N,
       "source_candidate_sha256":case_hash,
       "selection_commit":args.screen_commit,
       "policy_commit":args.policy_commit,
       "elapsed_seconds":time.monotonic()-start})
if __name__=="__main__":main()
