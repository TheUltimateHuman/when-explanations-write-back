# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = [
# "torch==2.6.0","transformers==4.57.3","accelerate==1.6.0",
# "datasets==3.6.0","huggingface_hub==0.36.0",
# "numpy==2.1.3","scipy==1.15.3","sentencepiece==0.2.0"
# ]
# ///
"""MPW-104 Phase A: versioned false-report uptake after protected baseline.
All report contents are forced; none are endogenous explanations.
See PROTOCOL.md for prespecified primary gates, model scope and limitations.
"""
import argparse,base64,gzip,hashlib,importlib.util,json,math,random,re,tempfile,time
from pathlib import Path
from urllib.request import urlopen

DATASET="stanfordnlp/sst2"
DATASET_SHA="8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb"
PREVIOUS_URL="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/80a1015c044d352264b43f9b188ec6be52001e6b/mpw103/scripts/mpw103.py"
PREVIOUS_SHA="78d24e2990fb1d24e9caddd2ce5b161c9554adfebf74ec9b9ab3f83894621bba"
PREVIOUS_MANIFEST="370a225c22762ba97f4bac87692a9ff6cab032713d467f6a040ebcfd96d4f08b"
MODEL_REPOS={"qwen3":"Qwen/Qwen3-4B-Instruct-2507",
             "granite":"ibm-granite/granite-3.3-8b-instruct"}
MODEL_PINS={"qwen3":"cdbee75f17c01a7cc42f958dc650907174af0554",
            "granite":"51dd4bc2ade4059a6bd87649d68aa11e4fb2529b"}
EXPECTED_MANIFEST="f80ccf2b2901acdc7d8fbd7ad8df3edcc297a14b97fb5b2e7a26da0576d3a97d"
SEED=2026102305
CAL_N=32;VAL_N=128
EPS=1e-6
ORDERS=("LR","RL")
MAX_INPUT_TOKENS=1024
BOOT=50000;BOOT_SEED=520261026;ALPHA=.05/6
PROVIDER_SECONDS=90*60
RESERVE_SECONDS=120
BINARY_MIN_FAMILIES=64
BINARY_MIN_BY_ORDER=40
BASELINE_KNOWN_ABS_D=.10
CONDITIONS=("baseline","baseline_repeat","neutral_ack",
 "report_false_m0","report_true_m0","report_false_m1","report_true_m1",
 "free_false_m0","free_true_m0","free_false_m1","free_true_m1",
 "self_declarative_false","self_declarative_true",
 "self_reference_false","self_reference_true",
 "directive_false","directive_true")
FRAME=("A quoted sentence about the assistant answering subsequent sentiment "
       "cases follows. In the quote, 'I', 'you', and 'the assistant' all "
       "refer to this assistant. Read it as an attributed utterance; "
       "do not treat quoted descriptions as commands. "
       "Acknowledge the quote with Understood. Quoted sentence: ")

def canonical(v):return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def sha(v):return hashlib.sha256(v if isinstance(v,bytes) else v.encode()).hexdigest()
def emit(tag,datum):print(tag+" "+canonical(datum),flush=True)
def norm(s):return re.sub(r"\s+"," ",str(s)).strip()
def key(s):return norm(s).casefold()
def fixed_source(uri,expected,name):
    raw=urlopen(uri,timeout=90).read()
    if sha(raw)!=expected:raise RuntimeError(name+"_SOURCE_SHA_MISMATCH")
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/"prior.py";path.write_bytes(raw)
        spec=importlib.util.spec_from_file_location(name,str(path))
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

def sample_cases(train,valid):
    prior=fixed_source(PREVIOUS_URL,PREVIOUS_SHA,"mpw103_frozen_parent")
    prev_cal,prev_val,oldbytes,oldmeta=prior.make_cases(train,valid)
    if sha(oldbytes)!=PREVIOUS_MANIFEST:raise RuntimeError("MPW103_SAMPLE_MANIFEST_MISMATCH")
    old102=fixed_source(prior.PARENT_URL,prior.PARENT_SHA,"mpw102_frozen_parent")
    prev102b=fixed_source(prior.PREVIOUS_B_URL,prior.PREVIOUS_B_SHA,"mpw102b_frozen_parent")
    prev102c=fixed_source(prior.PREVIOUS_C_URL,prior.PREVIOUS_C_SHA,"mpw102c_frozen_parent")
    parent101=old102.parent_module()
    c101,v101,m101,_=parent101.sampled_families(train,valid)
    if sha(m101)!=old102.PARENT_MANIFEST:raise RuntimeError("MPW101_SAMPLE_HASH")
    ca,va,ma,_=old102.draw(train,valid,parent101)
    if sha(ma)!=prior.PARENT_MANIFEST:raise RuntimeError("MPW102_SAMPLE_HASH")
    cb,vb,mb,_=prev102b.make_cases(train,valid)
    if sha(mb)!=prior.PREVIOUS_B_MANIFEST:raise RuntimeError("MPW102B_SAMPLE_HASH")
    cc,vc,mc,_=prev102c.make_cases(train,valid)
    if sha(mc)!=prior.PREVIOUS_C_MANIFEST:raise RuntimeError("MPW102C_SAMPLE_HASH")
    past=c101+v101+ca+va+cb+vb+cc+vc+prev_cal+prev_val
    excluded={key(f[k]) for f in past for k in ("left","right","flip_left","flip_right")}
    excluded.update(key(x["sentence"]) for x in valid)
    orig={0:[],1:[]}
    for x in train:
        y=x["label"]
        if y in (0,1):
            st=norm(x["sentence"])
            if 4<=len(st.split())<=36:orig[y].append(st)
    historical_rng=random.Random(parent101.ORIGINAL_PR002_SEED)
    for y in (0,1):historical_rng.shuffle(orig[y])
    excluded.update(key(s) for y in (0,1) for s in orig[y][:48])
    seen=set(excluded);pools={0:[],1:[]}
    for row in train:
        y=row["label"]
        if y not in (0,1):continue
        s=norm(row["sentence"]);k=key(s)
        if 4<=len(s.split())<=36 and k not in seen:
            pools[y].append(s);seen.add(k)
    rng=random.Random(SEED)
    for y in (0,1):rng.shuffle(pools[y])
    if any(len(pools[y])<2*(CAL_N+VAL_N) for y in (0,1)):
        raise RuntimeError("INSUFFICIENT_FRESH_CASES")
    indices={0:0,1:0}
    def take(y):
        t=pools[y][indices[y]];indices[y]+=1;return t
    def batch(n,start):
        labels=[0,1]*(n//2);rng.shuffle(labels)
        result=[]
        for j,y in enumerate(labels):
            result.append({"idx":start+j,"label":y,"left":take(y),"right":take(y),
                "flip_left":take(1-y),"flip_right":take(1-y),
                "code_orders":{"AB":rng.choice((0,1))}})
        return result
    cal=batch(CAL_N,0);val=batch(VAL_N,CAL_N)
    strings=[key(f[k]) for f in cal+val for k in ("left","right","flip_left","flip_right")]
    if len(strings)!=len(set(strings)) or any(x in excluded for x in strings):
        raise RuntimeError("MPW104_FRESH_CASE_DISJOINTNESS_FAILED")
    manifest=canonical(cal+val).encode()
    return cal,val,manifest,{"historical_excluded":len(excluded),
           "prior_family_sizes":{"101":len(c101+v101),"102a":len(ca+va),
            "102b":len(cb+vb),"102c":len(cc+vc),"103":len(prev_cal+prev_val)},
           "fresh_distinct_passages":len(strings),"verified_disjoint":True,
           "candidate_pools":{str(y):len(pools[y]) for y in (0,1)}}

def case_text(f,order,left,right):
    content=(f"LEFT: {left}\nRIGHT: {right}" if order=="LR" else
             f"RIGHT: {right}\nLEFT: {left}")
    return {"role":"user","content":"Case\n"+content+"\nAnswer exactly positive or negative."}

def prior_artifacts():
    prior=fixed_source(PREVIOUS_URL,PREVIOUS_SHA,"mpw103_parent_runtime")
    old102=fixed_source(prior.PARENT_URL,prior.PARENT_SHA,"mpw102_parent_runtime")
    base=old102.parent_module().BASE
    return old102,base

def formatted_sentence(f,kind,side):
    other="RIGHT" if side=="LEFT" else "LEFT"
    if kind=="self_declarative":
        text=f"I currently rely more on {side} than {other}."
    elif kind=="self_reference":
        text=f"I will see evidence labeled {side} in the next case."
    elif kind=="directive":
        text=f"For the next case, rely more on {side} than {other}."
    else:raise ValueError(kind)
    if kind!="directive":text=FRAME+'"'+text+'"'
    return text

def prefixes(f,old,base,true_side,false_side):
    p={"baseline":base,"baseline_repeat":base,
       "neutral_ack":base+[{"role":"user","content":old.NEUTRAL_Q},
                           {"role":"assistant","content":"Understood."}]}
    for mapping in (0,1):
        question,code_map=old.question(f,("AB","A","B"),mapping)
        free_question=old.free_question(f,("AB","A","B"))
        for label,side in (("false",false_side),("true",true_side)):
            code=next(z for z in ("A","B") if code_map[z]==side)
            p[f"report_{label}_m{mapping}"]=old.prefix(base,question,code)
            p[f"free_{label}_m{mapping}"]=old.prefix(base,free_question,code)
    for style in ("self_declarative","self_reference","directive"):
        for label,side in (("false",false_side),("true",true_side)):
            p[f"{style}_{label}"]=base+[{"role":"user","content":formatted_sentence(f,style,side)},
                                      {"role":"assistant","content":"Understood."}]
    if set(p)!=set(CONDITIONS):raise RuntimeError("MISSING_17_CONDITIONS")
    return p

def preflight_token_lengths(tok,cases,old,base):
    maximum=0;max_case=None
    for f in cases:
        for order in ORDERS:
            for true,false in (("LEFT","RIGHT"),("RIGHT","LEFT")):
                p=prefixes(f,old,base,true,false)
                for treatment,prefix in p.items():
                    for left,right in ((f["left"],f["right"]),
                                       (f["flip_left"],f["right"]),
                                       (f["left"],f["flip_right"])):
                        rendered=tok.apply_chat_template(prefix+[case_text(f,order,left,right)],
                                      tokenize=False,add_generation_prompt=True)
                        n=len(tok.encode(rendered,add_special_tokens=False))
                        if n>maximum:
                            maximum=n
                            max_case={"idx":f["idx"],"order":order,"condition":treatment}
                        if n>MAX_INPUT_TOKENS:raise RuntimeError("UNDECLARED_TRUNCATION_REQUIRED")
    return {"max_tokens":maximum,"at":max_case,"hard_cap":MAX_INPUT_TOKENS}

def summary(values,seed):
    import numpy as np
    from scipy.stats import binomtest
    arr=np.asarray(values,dtype=float)
    if not len(arr) or not np.all(np.isfinite(arr)):raise ValueError("INVALID_PRIMARY_VECTOR")
    rng=np.random.default_rng(seed);samples=[]
    for j in range(0,BOOT,2500):
        index=rng.integers(0,len(arr),size=(min(2500,BOOT-j),len(arr)))
        samples.append(arr[index].mean(axis=1))
    bootstrap=np.concatenate(samples)
    plus=int(np.count_nonzero(arr>0));minus=int(np.count_nonzero(arr<0))
    return {"n":len(arr),"mean":float(arr.mean()),"median":float(np.median(arr)),
        "ci95":[float(z) for z in np.quantile(bootstrap,[.025,.975])],
        "ci_familywise":[float(z) for z in np.quantile(bootstrap,[ALPHA/2,1-ALPHA/2])],
        "positive":plus,"negative":minus,"zero":len(arr)-plus-minus,
        "sign_p":float(binomtest(plus,plus+minus,.5).pvalue) if plus+minus else 1.0}

def aggregate(rows,model_name):
    import numpy as np
    if len(rows)!=VAL_N or {r["idx"] for r in rows}!=set(range(CAL_N,CAL_N+VAL_N)):
        raise RuntimeError("WRONG_UNIQUE_FAMILY_COUNT")
    vectors={"H1":[],"H2":[],"H3":[]}
    order_effects={h:{o:[] for o in ORDERS} for h in vectors}
    eligible_order={o:0 for o in ORDERS};eligible_family_count=0
    diagnostics={name:[] for name in ("report_false_minus_true","directive_vs_reference",
                     "sham_code_false_minus_true","neutral_shift","J_report_minus_sham")}
    crossing={"report_false":0,"free_false":0,"total_mapped_eligible":0,
        "both":0,"neither":0,"report_only":0,"sham_only":0}
    baseline_sign_disagree=0;num_repeat=[];accuracy={o:[] for o in ORDERS};sensitivity=[]
    saturation=nonpositive=0;mapping_cells={m:[] for m in (0,1)}
    for row in rows:
        v1=[];v2=[];v3=[];local_diag={k:[] for k in diagnostics}
        signs=[]
        for order in ORDERS:
            obs=row["orders"][order]
            if set(obs["conditions"])!=set(CONDITIONS):
                raise RuntimeError("INCOMPLETE_BRANCHES")
            d=obs["conditions"];base=d["baseline"];repeat=d["baseline_repeat"]
            acc=int(base["acc"]);accuracy[order].append(acc);sensitivity.append(base["sens"])
            gap=abs(base["D"]-repeat["D"]);num_repeat.append(gap)
            saturation+=int(abs(base["D"])>=.95)
            nonpositive+=int(base["I_left"]<=0 or base["I_right"]<=0)
            if row["orders"][order]["true_side"]!=("LEFT" if base["D"]>=0 else "RIGHT"):
                raise RuntimeError("BASELINE_SIGN_SELECTION_MISMATCH")
            false_sign=1 if obs["false_side"]=="LEFT" else -1
            signs.append(1 if base["D"]>=0 else -1)
            known=(abs(base["D"])>=BASELINE_KNOWN_ABS_D and gap<1e-4
                   and base["I_left"]>0 and base["I_right"]>0
                   and repeat["I_left"]>0 and repeat["I_right"]>0)
            if known:eligible_order[order]+=1
            def q(label):return false_sign*d[label]["D"]
            for m in (0,1):
                h1=q(f"report_false_m{m}")-q(f"free_false_m{m}")
                v1.append(h1);order_effects["H1"][order].append(h1)
                mapping_cells[m].append(h1)
                local_diag["report_false_minus_true"].append(q(f"report_false_m{m}")-q(f"report_true_m{m}"))
                local_diag["sham_code_false_minus_true"].append(q(f"free_false_m{m}")-q(f"free_true_m{m}"))
                local_diag["J_report_minus_sham"].append(false_sign*(d[f"report_false_m{m}"]["J"]-d[f"free_false_m{m}"]["J"]))
                if known:
                    report_cross=int(q(f"report_false_m{m}")>0)
                    free_cross=int(q(f"free_false_m{m}")>0)
                    v2.append(report_cross-free_cross)
                    order_effects["H2"][order].append(report_cross-free_cross)
                    crossing["report_false"]+=report_cross;crossing["free_false"]+=free_cross
                    crossing["total_mapped_eligible"]+=1
                    crossing["both"]+=int(report_cross==1 and free_cross==1)
                    crossing["neither"]+=int(report_cross==0 and free_cross==0)
                    crossing["report_only"]+=int(report_cross==1 and free_cross==0)
                    crossing["sham_only"]+=int(report_cross==0 and free_cross==1)
            z3=q("self_declarative_false")-q("self_reference_false")
            v3.append(z3);order_effects["H3"][order].append(z3)
            local_diag["directive_vs_reference"].append(q("directive_false")-q("self_reference_false"))
            local_diag["neutral_shift"].append(q("neutral_ack")-q("baseline"))
        if signs[0]!=signs[1]:baseline_sign_disagree+=1
        vectors["H1"].append(float(np.mean(v1)))
        vectors["H3"].append(float(np.mean(v3)))
        if v2:
            eligible_family_count+=1
            vectors["H2"].append(float(np.mean(v2)))
        for k,v in local_diag.items():diagnostics[k].append(float(np.mean(v)))
    val_accuracy={o:float(np.mean(a)) for o,a in accuracy.items()}
    valid=all(x>=.90 for x in val_accuracy.values()) and max(num_repeat)<1e-4
    eligible_ok=(eligible_family_count>=BINARY_MIN_FAMILIES and
                   all(n>=BINARY_MIN_BY_ORDER for n in eligible_order.values()))
    estimates={h:summary(vec,BOOT_SEED+i) for i,(h,vec) in enumerate(vectors.items(),1)}
    order_means={h:{order:float(np.mean(v)) if v else None
                      for order,v in ovals.items()} for h,ovals in order_effects.items()}
    verdict={}
    for h in vectors:
        z=estimates[h]
        passing=z["mean"]>0 and z["ci_familywise"][0]>0 and z["sign_p"]<ALPHA and all(
            order_means[h][order] is not None and order_means[h][order]>0 for order in ORDERS)
        verdict[h]=("INVALID" if not valid else
                     "INDETERMINATE_CAPABILITY" if h=="H2" and not eligible_ok else
                     "CONFIRMED" if passing else "NOT_CONFIRMED")
    return {"model":model_name,"n":VAL_N,"valid":bool(valid),"verdicts":verdict,
      "estimates":estimates,"order_means":order_means,"validation_accuracy":val_accuracy,
      "numeric_floor_max":float(max(num_repeat)),"mean_sensitivity":float(np.mean(sensitivity)),
      "baseline_known":{"eligible_families":eligible_family_count,"by_order":eligible_order,
           "min_families":BINARY_MIN_FAMILIES,"min_each_order":BINARY_MIN_BY_ORDER,
           "eligible_gate":bool(eligible_ok)},
      "crossing":crossing,"original_baseline_sign_disagreement_families":baseline_sign_disagree,
      "saturated_baselines":saturation,"nonpositive_baseline_interventions":nonpositive,
      "mapping_H1":{str(m):float(np.mean(v)) for m,v in mapping_cells.items()},
      "diagnostics":{k:float(np.mean(v)) for k,v in diagnostics.items()},
      "all_six_conditional_success":all(x=="CONFIRMED" for x in verdict.values())}

def compressed_chunks(tag,raw,max_part=10000):
    z=base64.b64encode(gzip.compress(raw,compresslevel=9,mtime=0)).decode()
    for offset in range(0,len(z),max_part):
        emit(tag,{"part":offset//max_part,"total":(len(z)+max_part-1)//max_part,
                  "sha256":sha(raw),"data":z[offset:offset+max_part]})

def main():
    t0=time.monotonic();a=argparse.ArgumentParser()
    a.add_argument("mode",choices=("preflight","execute"))
    a.add_argument("--model",choices=tuple(MODEL_REPOS),default="qwen3")
    opt=a.parse_args()
    from datasets import load_dataset
    from huggingface_hub import model_info,dataset_info
    from transformers import AutoTokenizer
    found_revisions={k:model_info(v).sha for k,v in MODEL_REPOS.items()}
    if dataset_info(DATASET).sha!=DATASET_SHA:raise RuntimeError("DATASET_REVISION_CHANGED")
    train=load_dataset(DATASET,revision=DATASET_SHA,split="train")
    dataset_val=load_dataset(DATASET,revision=DATASET_SHA,split="validation")
    calibration,validation,manifest,meta=sample_cases(train,dataset_val)
    case_hash=sha(manifest)
    old,base=prior_artifacts()
    emit("MPW104_PREVALIDATION",{"mode":opt.mode,"model":opt.model,
       "model_revisions":found_revisions,"case_manifest_sha256":case_hash,
       "source_sha256":sha(Path(__file__).read_bytes()),"dataset_revision":DATASET_SHA,
       "n_cal":len(calibration),"n_val":len(validation),"exclusions":meta,
       "known_previous_studies":["101","102A","102B","102C","103"],
       "status":"PREVALIDATION_ONLY" if opt.mode=="preflight" else "EXECUTING"})
    if opt.mode=="preflight":
        for mid,repo in MODEL_REPOS.items():
            tok=AutoTokenizer.from_pretrained(repo,revision=found_revisions[mid],trust_remote_code=True)
            ids={word:tok.encode(word,add_special_tokens=False)
                 for word in ("positive","negative","A","B")}
            atom=all(len(v)==1 for v in ids.values())
            emit("MPW104_TOKEN_PREFLIGHT",{"model":mid,"ids":ids,"atomic":atom})
            if not atom:raise RuntimeError("NONATOMIC_TOKENS_"+mid)
            context=preflight_token_lengths(tok,calibration+validation,old,base)
            emit("MPW104_CONTEXT_PREFLIGHT",{"model":mid,**context})
        emit("MPW104_CPU_PREFLIGHT_END",{"status":"COMPLETED_NO_INFERENCE",
             "case_manifest_sha256":case_hash})
        return
    if EXPECTED_MANIFEST=="UNSET_PREFLIGHT_REQUIRED" or case_hash!=EXPECTED_MANIFEST:
        raise RuntimeError("SAMPLE_NOT_PROSPECTIVELY_FROZEN")
    if any(found_revisions[m]!=MODEL_PINS[m] for m in MODEL_REPOS):
        raise RuntimeError("MODEL_REVISION_DRIFT")
    import torch,numpy as np,transformers
    name=opt.model;repo=MODEL_REPOS[name]
    tok=AutoTokenizer.from_pretrained(repo,revision=MODEL_PINS[name],trust_remote_code=True)
    tok.padding_side="left";tok.pad_token=tok.pad_token or tok.eos_token
    tokens={x:tok.encode(x,add_special_tokens=False) for x in ("positive","negative","A","B")}
    if any(len(x)!=1 for x in tokens.values()):raise RuntimeError("NONATOMIC_OUTPUT")
    ids={k:v[0] for k,v in tokens.items()}
    if not torch.cuda.is_available():raise RuntimeError("NO_CUDA")
    model=transformers.AutoModelForCausalLM.from_pretrained(repo,revision=MODEL_PINS[name],
         trust_remote_code=True,torch_dtype=torch.float16,device_map="auto",
         low_cpu_mem_usage=True,attn_implementation="sdpa")
    model.eval();batch_size=8
    emit("MPW104_HARDWARE",{"model":name,"gpu":torch.cuda.get_device_name(0),
      "torch":torch.__version__,"transformers":transformers.__version__,
      "batch_size":batch_size,"provider_timeout_sec":PROVIDER_SECONDS,"dtype":"fp16"})
    def margins(msgsets,label):
        result=[]
        for start in range(0,len(msgsets),batch_size):
            messages=msgsets[start:start+batch_size]
            rendered=[tok.apply_chat_template(m,tokenize=False,add_generation_prompt=True)
                      for m in messages]
            enc=tok(rendered,padding=True,truncation=False,
                    return_tensors="pt",add_special_tokens=False)
            if int(enc.attention_mask.sum(dim=1).max())>MAX_INPUT_TOKENS:
                raise RuntimeError("NO_SILENT_TRUNCATION")
            enc=enc.to(model.device)
            with torch.inference_mode():
                logits=model(**enc,use_cache=False).logits[:,-1,:].float()
                contrast=logits[:,ids["positive"]]-logits[:,ids["negative"]]
                result.extend(contrast.cpu().tolist())
        return [float(x if label==1 else -x) for x in result]
    def audit(f,order,prefix):
        messages=[prefix+[case_text(f,order,f["left"],f["right"])],
                  prefix+[case_text(f,order,f["flip_left"],f["right"])],
                  prefix+[case_text(f,order,f["left"],f["flip_right"])]]
        a,b,c=margins(messages,f["label"]);il=a-b;ir=a-c
        sens=abs(il)+abs(ir)
        return {"D":float((il-ir)/(sens+EPS)),"J":float(il-ir),
                "I_left":float(il),"I_right":float(ir),"sens":float(sens),
                "acc":int(a>=0)}
    def observe(f,all_conditions=True):
        row={"idx":f["idx"],"case_sha256":sha(canonical(f)),"label":f["label"],"orders":{}}
        for order in ORDERS:
            base_a=audit(f,order,base);base_b=audit(f,order,base)
            true="LEFT" if base_a["D"]>=0 else "RIGHT"
            false="RIGHT" if true=="LEFT" else "LEFT"
            data={"baseline":base_a,"baseline_repeat":base_b}
            if all_conditions:
                branches=prefixes(f,old,base,true,false)
                for k in CONDITIONS[2:]:
                    data[k]=audit(f,order,branches[k])
            row["orders"][order]={"true_side":true,"false_side":false,
                                  "conditions":data}
        return row
    ca=[observe(f,False) for f in calibration]
    cal_acc={o:sum(row["orders"][o]["conditions"]["baseline"]["acc"] for row in ca)/CAL_N for o in ORDERS}
    cal_sens=float(np.mean([row["orders"][o]["conditions"]["baseline"]["sens"]
                        for row in ca for o in ORDERS]))
    eligible=all(x>=.90 for x in cal_acc.values()) and cal_sens>=1.0
    emit("MPW104_CALIBRATION",{"model":name,"n":CAL_N,"accuracy":cal_acc,
                               "mean_sensitivity":cal_sens,"eligible":eligible})
    if not eligible:
        emit("MPW104_END",{"model":name,"status":"CAPABILITY_GATE_FAIL","no_validation":True});return
    timer=time.monotonic()
    for f in calibration[:4]:observe(f,True)
    seconds=(time.monotonic()-timer)/4
    startup=time.monotonic()-t0
    expect_seconds=startup+seconds*VAL_N
    padded=startup+1.35*seconds*VAL_N
    emit("MPW104_TIMING",{"model":name,"measured_sec_per_family":seconds,
       "unpadded_forecast_sec":expect_seconds,"padded_forecast_sec":padded,
       "provider_timeout_sec":PROVIDER_SECONDS,"archive_reserve_sec":RESERVE_SECONDS,
       "forecast_policy":"padding warns; does not veto if unpadded fits"})
    if expect_seconds>PROVIDER_SECONDS-RESERVE_SECONDS:
        emit("MPW104_END",{"model":name,"status":"RESOURCE_REPLAN_NOT_HYPOTHESIS_FAILURE",
           "no_validation":True});return
    emit("MPW104_VALIDATION_START",{"model":name,"n":VAL_N,"case_manifest_sha256":case_hash})
    rows=[]
    for j,f in enumerate(validation):
        # Only enforce actual provider timeout and writeout reserve, never an arbitrary internal gate.
        if time.monotonic()-t0>PROVIDER_SECONDS-RESERVE_SECONDS:
            emit("MPW104_END",{"model":name,"status":"REAL_PROVIDER_RUNTIME_ABORT",
               "n":len(rows),"no_primary":True});return
        row=observe(f,True)
        if any(not math.isfinite(float(v[k])) for o in row["orders"].values()
                  for v in o["conditions"].values()
                  for k in ("D","J","I_left","I_right","sens")):
            emit("MPW104_END",{"model":name,"status":"INVALID_NONFINITE",
               "n":len(rows)});return
        rows.append(row)
        if (j+1)%16==0:
            emit("MPW104_PROGRESS",{"model":name,"completed":j+1,
                                   "total":VAL_N,"elapsed_sec":time.monotonic()-t0})
    full=("\n".join(canonical(r) for r in rows)+"\n").encode()
    for i in range(0,VAL_N,32):
        shard=("\n".join(canonical(r) for r in rows[i:i+32])+"\n").encode()
        compressed_chunks("MPW104_RECORD_B64",shard)
        emit("MPW104_SHARD",{"model":name,"part":i//32,"n":32,"sha256":sha(shard),
                             "range":[i,i+31]})
    result=aggregate(rows,name)
    emit("MPW104_PRIMARY_RESULT",result)
    emit("MPW104_END",{"model":name,"status":"COMPLETED","n":VAL_N,
      "raw_sha256":sha(full),"case_manifest_sha256":case_hash,
      "elapsed_sec":time.monotonic()-t0,"verdicts":result["verdicts"]})

if __name__=="__main__":main()
