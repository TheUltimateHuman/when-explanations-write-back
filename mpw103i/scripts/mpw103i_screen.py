# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = [
# "torch==2.6.0","transformers==4.57.3","accelerate==1.6.0",
# "datasets==3.6.0","huggingface_hub==0.36.0",
# "numpy==2.1.3","scipy==1.15.3","sentencepiece==0.2.0"
# ]
# ///
"""MPW-103I baseline-only case screening and 64 independent selected original causal profiles.
Screening NEVER elicits or writes reports. Native 8-cycle writeback requires a separately frozen runner.
"""
import argparse,base64,gzip,hashlib,importlib.util,json,math,random,re,tempfile,time
from pathlib import Path
from urllib.request import urlopen

OLD105_URL="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/afea0481fc5615376974d4c3f375eecae49414b2/mpw105/scripts/mpw105_screen.py"
OLD105_SHA="3b3e485f7c7313a369a4521dfe9a7c53f7062e732fefc69bf35ef88595005b2c"
OLD105_MANIFEST="21dcef582979554f9b7d9d1a76c745803fdb84e8ab79111eee6a73bd14a1ac86"
OLD104B_URL="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/f23419671acd425a60cd66f1c8cd173d652ba033/mpw104b/scripts/mpw104b.py"
OLD104B_SHA="d6f102401b4f74e543df7b4339becb5c9aa8b5bfdf2d7830a8b04b8e042d1b49"
OLD104B_MANIFEST="86eee90fa35e92b82a653e74e473fa1cffae5cee5681ed2a88bcedd4f9682cae"
OLD104_URL="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/c94d1299e8862686bb728880c3f36a1527e7b7c0/mpw104/scripts/mpw104.py"
OLD104_SHA="d8866d46dcb4bc6f5e2289108c22c434add56c423e63f1731c929aed86d6d1e1"
OLD104_MANIFEST="f80ccf2b2901acdc7d8fbd7ad8df3edcc297a14b97fb5b2e7a26da0576d3a97d"
DATASET="stanfordnlp/sst2"
DATASET_SHA="8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb"
MODELS={"qwen3":"Qwen/Qwen3-4B-Instruct-2507",
        "granite":"ibm-granite/granite-3.3-8b-instruct"}
PINS={"qwen3":"cdbee75f17c01a7cc42f958dc650907174af0554",
      "granite":"51dd4bc2ade4059a6bd87649d68aa11e4fb2529b"}
EXPECTED_CANDIDATE_MANIFEST="UNSET_CPU_PREFLIGHT_REQUIRED"
SEED=2026102501
CAL_N=32
POOL_N=2048
SELECT_PER_LABEL=32
VALID_N=64
ORDERS=("LR","RL")
HARD_INPUT_TOKENS=4096
EPS=1e-6
PROVIDER_TIMEOUT_S=120*60
ARCHIVE_RESERVE_S=120
BOOT=50000
BOOT_SEED=520261027
ALPHA=.05/6
CONDITIONS=("baseline","baseline_repeat","neutral_ack",
            "report_false_m0","report_true_m0","report_false_m1","report_true_m1",
            "free_false_m0","free_true_m0","free_false_m1","free_true_m1",
            "self_declarative_false","self_declarative_true",
            "self_reference_false","self_reference_true",
            "directive_false","directive_true")
SOURCE_ROOT="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/"

def canonical(v):return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def sha(v):return hashlib.sha256(v if isinstance(v,bytes) else v.encode()).hexdigest()
def emit(label,obj):print(label+" "+canonical(obj),flush=True)
def norm(s):return re.sub(r"\s+"," ",str(s)).strip()
def key(s):return norm(s).casefold()
def parent_module(uri,expected,name):
    b=urlopen(uri,timeout=90).read()
    if sha(b)!=expected:raise RuntimeError(name+"_SHA_MISMATCH")
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/"prior.py";p.write_bytes(b)
        spec=importlib.util.spec_from_file_location(name,p)
        o=importlib.util.module_from_spec(spec);spec.loader.exec_module(o)
    return o

def make_cases(train,valid):
    old105=parent_module(OLD105_URL,OLD105_SHA,"mpw105_frozen_original")
    c105,v105,b105,_=old105.make_cases(train,valid)
    if sha(b105)!=OLD105_MANIFEST:raise RuntimeError("MPW103I_CASE_SOURCE_MANIFEST_MISMATCH")
    oldb=parent_module(OLD104B_URL,OLD104B_SHA,"mpw104b_frozen_original")
    cb_prev,vb_prev,bb_prev,_=oldb.make_cases(train,valid)
    if sha(bb_prev)!=OLD104B_MANIFEST:raise RuntimeError("MPW103I_MANIFEST_MISMATCH")
    old=parent_module(OLD104_URL,OLD104_SHA,"mpw104_frozen_original")
    c104,v104,bytes104,_=old.sample_cases(train,valid)
    if sha(bytes104)!=OLD104_MANIFEST:raise RuntimeError("MPW104A_MANIFEST_MISMATCH")
    prior=parent_module(old.PREVIOUS_URL,old.PREVIOUS_SHA,"mpw103_frozen")
    c103,v103,m103,_=prior.make_cases(train,valid)
    if sha(m103)!=old.PREVIOUS_MANIFEST:raise RuntimeError("MPW103_MANIFEST_MISMATCH")
    old102=parent_module(prior.PARENT_URL,prior.PARENT_SHA,"mpw102_frozen")
    old102b=parent_module(prior.PREVIOUS_B_URL,prior.PREVIOUS_B_SHA,"mpw102b_frozen")
    old102c=parent_module(prior.PREVIOUS_C_URL,prior.PREVIOUS_C_SHA,"mpw102c_frozen")
    old101=old102.parent_module()
    c101,v101,m101,_=old101.sampled_families(train,valid)
    if sha(m101)!=old102.PARENT_MANIFEST:raise RuntimeError("MPW101_MANIFEST_MISMATCH")
    ca,va,ma,_=old102.draw(train,valid,old101)
    if sha(ma)!=prior.PARENT_MANIFEST:raise RuntimeError("MPW102A_MANIFEST_MISMATCH")
    cb,vb,mb,_=old102b.make_cases(train,valid)
    if sha(mb)!=prior.PREVIOUS_B_MANIFEST:raise RuntimeError("MPW102B_MANIFEST_MISMATCH")
    cc,vc,mc,_=old102c.make_cases(train,valid)
    if sha(mc)!=prior.PREVIOUS_C_MANIFEST:raise RuntimeError("MPW102C_MANIFEST_MISMATCH")
    historical=(c101+v101+ca+va+cb+vb+cc+vc+c103+v103+c104+v104+cb_prev+vb_prev+c105+v105)
    exclude={key(f[k]) for f in historical
             for k in ("left","right","flip_left","flip_right")}
    exclude.update(key(f["sentence"]) for f in valid)
    first={0:[],1:[]}
    for f in train:
        y=f["label"]
        if y in (0,1):
            s=norm(f["sentence"])
            if 4<=len(s.split())<=36:first[y].append(s)
    rr=random.Random(old101.ORIGINAL_PR002_SEED)
    for y in (0,1):rr.shuffle(first[y])
    exclude.update(key(s) for y in (0,1) for s in first[y][:48])
    seen=set(exclude)
    pool={0:[],1:[]}
    for f in train:
        y=f["label"]
        if y not in (0,1):continue
        s=norm(f["sentence"])
        if 4<=len(s.split())<=36 and key(s) not in seen:
            pool[y].append(s);seen.add(key(s))
    rng=random.Random(SEED)
    for y in (0,1):rng.shuffle(pool[y])
    needed=2*(CAL_N+POOL_N)
    if any(len(pool[y])<needed for y in (0,1)):
        raise RuntimeError("INSUFFICIENT_UNIQUE_CANDIDATE_TEXTS")
    ix={0:0,1:0}
    def take(label):
        s=pool[label][ix[label]]
        ix[label]+=1
        return s
    def batch(n,start):
        labs=[0,1]*(n//2);rng.shuffle(labs)
        out=[]
        for j,y in enumerate(labs):
            out.append({"idx":start+j,"label":y,
                        "left":take(y),"right":take(y),
                        "flip_left":take(1-y),"flip_right":take(1-y),
                        "code_orders":{"AB":rng.choice((0,1))}})
        return out
    cal=batch(CAL_N,0)
    candidates=batch(POOL_N,CAL_N)
    all_cases=cal+candidates
    texts=[key(f[k]) for f in all_cases for k in
           ("left","right","flip_left","flip_right")]
    if len(texts)!=len(set(texts)) or any(t in exclude for t in texts):
        raise RuntimeError("HISTORICAL_TEXT_OVERLAP_OR_DUPLICATE")
    manifest=canonical(all_cases).encode()
    meta={"n_cal":CAL_N,"n_candidates":POOL_N,
          "excluded_historical_text_keys":len(exclude),
          "distinct_new_texts":len(texts),
          "candidate_labels":{"0":sum(f["label"]==0 for f in candidates),
                              "1":sum(f["label"]==1 for f in candidates)},
          "prior_family_counts":{"101":len(c101+v101),"102a":len(ca+va),
              "102b":len(cb+vb),"102c":len(cc+vc),
              "103":len(c103+v103),"104a":len(c104+v104),
              "104b":len(cb_prev+vb_prev),"105":len(c105+v105)},
          "text_disjoint":True}
    return cal,candidates,manifest,meta

def select_from_screen(rows):
    """Deterministic prospective rule. Only baseline fields are inspected."""
    if len(rows)!=POOL_N or {r["idx"] for r in rows}!=set(range(CAL_N,CAL_N+POOL_N)):
        raise RuntimeError("SCREEN_NOT_COMPLETE")
    chosen={0:[],1:[]}
    reasons={}
    eligible={0:0,1:0}
    seen_case=set()
    for r in sorted(rows,key=lambda x:x["idx"]):
        if r["idx"] in seen_case:raise RuntimeError("DUPLICATED_CASE")
        seen_case.add(r["idx"])
        y=r["label"]
        if y not in (0,1):raise RuntimeError("INVALID_SENTIMENT_LABEL")
        if set(r["orders"])!=set(ORDERS):raise RuntimeError("MISSING_ORDER_IN_SCREEN")
        errors=[]
        for order in ORDERS:
            v=r["orders"][order]
            if set(v)!={"baseline","baseline_repeat"}:raise RuntimeError("SCREEN_CONTAINED_TREATMENT_OR_MISSING_REPEAT")
            for name in ("baseline","baseline_repeat"):
                z=v[name]
                if any(not math.isfinite(float(z[k])) for k in ("D","J","I_left","I_right","sens")):
                    errors.append("NONFINITE")
            b=v["baseline"];repeat=v["baseline_repeat"]
            if not(b["acc"] and repeat["acc"]):errors.append("INCORRECT_TASK_"+order)
            if abs(b["D"])<.10:errors.append("LOW_D_"+order)
            if abs(b["D"]-repeat["D"])>=1e-4:errors.append("NOISY_D_"+order)
            if not all(z["I_left"]>0 and z["I_right"]>0 for z in (b,repeat)):
                errors.append("NONPOSITIVE_CAUSAL_CHANNEL_"+order)
        d_lr=r["orders"]["LR"]["baseline"]["D"]
        d_rl=r["orders"]["RL"]["baseline"]["D"]
        if not(d_lr*d_rl>0):errors.append("ORDER_SIGN_INCONSISTENT")
        if errors:
            for e in set(errors):reasons[e]=reasons.get(e,0)+1
            continue
        eligible[y]+=1
        if len(chosen[y])<SELECT_PER_LABEL:
            true="LEFT" if d_lr>0 else "RIGHT"
            chosen[y].append({"idx":r["idx"],"label":y,
                "case_sha256":r["case_sha256"],"true_side":true,
                "false_side":"RIGHT" if true=="LEFT" else "LEFT",
                "screen_orders":r["orders"]})
    selected=sorted(chosen[0]+chosen[1],key=lambda x:x["idx"])
    return {"schema":"MPW103I_SCREEN_SELECTION_V1",
         "source_candidate_sha256":EXPECTED_CANDIDATE_MANIFEST,
         "n_candidates":POOL_N,"n_selected":len(selected),
         "eligible_per_label":{"0":eligible[0],"1":eligible[1]},
         "selected_per_label":{"0":len(chosen[0]),"1":len(chosen[1])},
         "rejection_reason_counts":dict(sorted(reasons.items())),
         "selection_complete":len(chosen[0])==SELECT_PER_LABEL and len(chosen[1])==SELECT_PER_LABEL,
         "selected":selected}

def emit_shards(prefix,records,per_shard):
    if len(records)%per_shard:raise RuntimeError("SHARD_CARDINALITY")
    raw=("\n".join(canonical(r) for r in records)+"\n").encode()
    for begin in range(0,len(records),per_shard):
        part=("\n".join(canonical(r) for r in records[begin:begin+per_shard])+"\n").encode()
        base=base64.b64encode(gzip.compress(part,compresslevel=9,mtime=0)).decode()
        for i in range(0,len(base),10000):
            emit(prefix+"_B64",{"part":i//10000,
                                "total":(len(base)+9999)//10000,
                                "sha256":sha(part),"data":base[i:i+10000]})
        emit(prefix+"_SHARD",{"part":begin//per_shard,"n":per_shard,
                 "range":[begin,begin+per_shard-1],"sha256":sha(part)})
    return sha(raw)

def infer(values,index):
    import numpy as np
    from scipy.stats import binomtest
    x=np.asarray(values,dtype=float)
    if x.shape!=(VALID_N,) or not np.all(np.isfinite(x)):
        raise RuntimeError("WRONG_TEST_VECTOR")
    rng=np.random.default_rng(BOOT_SEED+index)
    bs=[]
    for j in range(0,BOOT,2500):
        ix=rng.integers(0,len(x),size=(min(2500,BOOT-j),len(x)))
        bs.append(x[ix].mean(axis=1))
    boots=np.concatenate(bs)
    pos=int((x>0).sum());neg=int((x<0).sum())
    return {"n":len(x),"mean":float(x.mean()),"median":float(np.median(x)),
      "ci_familywise":[float(v) for v in np.quantile(boots,[ALPHA/2,1-ALPHA/2])],
      "ci95":[float(v) for v in np.quantile(boots,[.025,.975])],
      "positive":pos,"negative":neg,"zero":VALID_N-pos-neg,
      "sign_p":float(binomtest(pos,pos+neg,.5).pvalue) if pos+neg else 1.0}

def aggregate_treatment(rows,selection,model_name):
    import numpy as np
    if len(rows)!=VALID_N or len(selection["selected"])!=VALID_N:
        raise RuntimeError("MISSING_TREATMENT_FAMILIES")
    expected={x["idx"]:x for x in selection["selected"]}
    if {x["idx"] for x in rows}!=set(expected):raise RuntimeError("WRONG_SELECTED_CASE_SET")
    vectors={h:[] for h in ("H1","H2","H3")}
    per_order={h:{o:[] for o in ORDERS} for h in vectors}
    per_mapping={0:[],1:[]}
    diag={k:[] for k in ("report_false_minus_true","free_false_minus_true",
                       "directive_vs_reference","neutral_shift","raw_J")}
    crossover={"both":0,"neither":0,"report_only":0,"sham_only":0,"report":0,"sham":0}
    partial_report={k:0 for k in range(5)}
    partial_sham={k:0 for k in range(5)}
    num_repeat=[];screen_drift=[];invalid_sign=0;incorrect=0
    nonpos=0;sat=0
    for r in sorted(rows,key=lambda x:x["idx"]):
        src=expected[r["idx"]]
        if src["case_sha256"]!=r["case_sha256"] or src["label"]!=r["label"]:
            raise RuntimeError("TREATMENT_CASE_NOT_SELECTED")
        if r["true_side"]!=src["true_side"] or r["false_side"]!=src["false_side"]:
            raise RuntimeError("TREATMENT_TRUTH_WAS_REORIENTED")
        sign=1 if src["false_side"]=="LEFT" else -1
        v1=[];v3=[];rc=[];sc=[]
        local={x:[] for x in diag}
        for order in ORDERS:
            obs=r["orders"][order]
            if set(obs)!=set(CONDITIONS):raise RuntimeError("MISSING_TREATMENT_ARM")
            b=obs["baseline"];repeat=obs["baseline_repeat"];screen=src["screen_orders"][order]["baseline"]
            if not b["acc"] or not repeat["acc"]:incorrect+=1
            if b["D"]*screen["D"]<=0:invalid_sign+=1
            num_repeat.append(abs(b["D"]-repeat["D"]))
            screen_drift.append(abs(b["D"]-screen["D"]))
            nonpos+=int(b["I_left"]<=0 or b["I_right"]<=0)
            sat+=int(abs(b["D"])>=.95)
            def q(name):return sign*obs[name]["D"]
            for m in (0,1):
                pair=q(f"report_false_m{m}")-q(f"free_false_m{m}")
                v1.append(pair);per_order["H1"][order].append(pair);per_mapping[m].append(pair)
                rc.append(int(q(f"report_false_m{m}")>0))
                sc.append(int(q(f"free_false_m{m}")>0))
                local["report_false_minus_true"].append(q(f"report_false_m{m}")-q(f"report_true_m{m}"))
                local["free_false_minus_true"].append(q(f"free_false_m{m}")-q(f"free_true_m{m}"))
                local["raw_J"].append(sign*(obs[f"report_false_m{m}"]["J"]-obs[f"free_false_m{m}"]["J"]))
            h3=q("self_declarative_false")-q("self_reference_false")
            v3.append(h3);per_order["H3"][order].append(h3)
            local["directive_vs_reference"].append(q("directive_false")-q("self_reference_false"))
            local["neutral_shift"].append(q("neutral_ack")-q("baseline"))
        rj=int(sum(rc)==4);sj=int(sum(sc)==4)
        partial_report[sum(rc)]+=1;partial_sham[sum(sc)]+=1
        crossover["both"]+=rj*sj;crossover["neither"]+=(1-rj)*(1-sj)
        crossover["report_only"]+=rj*(1-sj);crossover["sham_only"]+=(1-rj)*sj
        crossover["report"]+=rj;crossover["sham"]+=sj
        vectors["H1"].append(float(np.mean(v1)))
        vectors["H2"].append(float(rj-sj))
        vectors["H3"].append(float(np.mean(v3)))
        for k in diag:diag[k].append(float(np.mean(local[k])))
    stats={h:infer(x,i) for i,(h,x) in enumerate(vectors.items(),1)}
    per_order_means={h:{o:float(np.mean(v)) if v else None for o,v in tab.items()}
                     for h,tab in per_order.items()}
    mapmeans={str(m):float(np.mean(x)) for m,x in per_mapping.items()}
    valid=(incorrect==0 and invalid_sign==0 and max(num_repeat)<1e-4
        and max(screen_drift)<1e-4 and len(rows)==VALID_N)
    verdict={}
    for h,est in stats.items():
        checks=est["mean"]>0 and est["ci_familywise"][0]>0 and est["sign_p"]<ALPHA
        if h in ("H1","H3"):
            checks=checks and all(per_order_means[h][o]>0 for o in ORDERS)
        if h=="H1":
            checks=checks and all(v>0 for v in mapmeans.values())
        verdict[h]="CONFIRMED" if valid and checks else ("INVALID" if not valid else "NOT_CONFIRMED")
    return {"model":model_name,"n":VALID_N,"valid":bool(valid),"verdicts":verdict,
        "estimates":stats,"per_order":per_order_means,"per_mapping_H1":mapmeans,
        "joint_crossing":crossover,"partial_crossing_report":partial_report,
        "partial_crossing_sham":partial_sham,"invalid_remeasured_accuracy_cells":incorrect,
        "screen_sign_flip_cells":invalid_sign,
        "max_abs_baseline_repeat_D":float(max(num_repeat)),
        "max_abs_screen_to_treatment_D":float(max(screen_drift)),
        "saturated_baselines":sat,"nonpositive_baseline_interventions":nonpos,
        "diagnostics":{k:float(np.mean(v)) for k,v in diag.items()},
        "full_model_gate":all(x=="CONFIRMED" for x in verdict.values())}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("mode",choices=("preflight","screen"))
    ap.add_argument("--model",choices=tuple(MODELS),default="qwen3")
    opt=ap.parse_args()
    t0=time.monotonic()
    from huggingface_hub import model_info,dataset_info
    from datasets import load_dataset
    from transformers import AutoTokenizer
    from numpy import mean
    current={k:model_info(v).sha for k,v in MODELS.items()}
    if any(current[k]!=PINS[k] for k in PINS):
        raise RuntimeError("MODEL_SHA_CHANGED")
    if dataset_info(DATASET).sha!=DATASET_SHA:raise RuntimeError("DATASET_SHA_CHANGED")
    train=load_dataset(DATASET,split="train",revision=DATASET_SHA)
    val=load_dataset(DATASET,split="validation",revision=DATASET_SHA)
    cal,pool,raw,meta=make_cases(train,val)
    candidate_sha=sha(raw)
    old104=parent_module(OLD104_URL,OLD104_SHA,"mpw104_parent_runtime")
    old,base=old104.prior_artifacts()
    emit("MPW103I_SOURCE",{"mode":opt.mode,"model":opt.model,
       "case_manifest_sha256":candidate_sha,
       "expected_manifest_sha256":EXPECTED_CANDIDATE_MANIFEST,
       "model_pins":PINS,"dataset_sha":DATASET_SHA,
       "source_sha256":sha(Path(__file__).read_bytes()),"meta":meta})
    if opt.mode=="preflight":
        for m,repo in MODELS.items():
            tok=AutoTokenizer.from_pretrained(repo,revision=PINS[m],trust_remote_code=True)
            names=("positive","negative","A","B")
            ids={k:tok.encode(k,add_special_tokens=False) for k in names}
            if any(len(v)!=1 for v in ids.values()):raise RuntimeError("NONATOMIC_TOKENS_"+m)
            max_tokens=0
            # Candidate source texts are bounded to <=36 words, independent of selection.
            # Scan every candidate in both orders under untouched prompts, with exact
            # token lengths checked again for all selected treatment cases after screen.
            for f in cal+pool:
                for order in ORDERS:
                    text=tok.apply_chat_template(base+[old104.case_text(f,order,f["left"],f["right"])],
                                                 tokenize=False,add_generation_prompt=True)
                    n=len(tok.encode(text,add_special_tokens=False))
                    max_tokens=max(n,max_tokens)
                    if n>HARD_INPUT_TOKENS:raise RuntimeError("CANDIDATE_LONGER_THAN_INPUT_CAP")
            emit("MPW103I_PREFLIGHT_MODEL",{"model":m,"token_ids":ids,
                "max_baseline_tokens":max_tokens,"n_cases":len(cal)+len(pool)})
        emit("MPW103I_PREFLIGHT_COMPLETE",{"status":"NO_MODEL_INFERENCE","case_manifest_sha256":candidate_sha})
        return
    if EXPECTED_CANDIDATE_MANIFEST=="UNSET_CPU_PREFLIGHT_REQUIRED" or candidate_sha!=EXPECTED_CANDIDATE_MANIFEST:
        raise RuntimeError("CANDIDATE_CASE_MANIFEST_NOT_FROZEN")
    import numpy as np,torch,transformers
    name=opt.model;repo=MODELS[name]
    tok=AutoTokenizer.from_pretrained(repo,revision=PINS[name],trust_remote_code=True)
    tok.padding_side="left";tok.pad_token=tok.pad_token or tok.eos_token
    codes={k:tok.encode(k,add_special_tokens=False) for k in ("positive","negative","A","B")}
    if any(len(v)!=1 for v in codes.values()):raise RuntimeError("NONATOMIC_TOKENS")
    ids={k:v[0] for k,v in codes.items()}
    if not torch.cuda.is_available():raise RuntimeError("CUDA_REQUIRED")
    model=transformers.AutoModelForCausalLM.from_pretrained(repo,revision=PINS[name],
           trust_remote_code=True,torch_dtype=torch.float16,device_map="auto",
           low_cpu_mem_usage=True,attn_implementation="sdpa")
    model.eval()
    batch_size=8
    emit("MPW103I_HARDWARE",{"model":name,"gpu":torch.cuda.get_device_name(0),
         "torch":torch.__version__,"transformers":transformers.__version__,
         "dtype":"float16","batch_size":batch_size,"provider_timeout_seconds":PROVIDER_TIMEOUT_S})
    def logit_margins(prefix_sets,label):
        out=[]
        for j in range(0,len(prefix_sets),batch_size):
            messages=prefix_sets[j:j+batch_size]
            rendered=[tok.apply_chat_template(m,tokenize=False,add_generation_prompt=True)
                      for m in messages]
            enc=tok(rendered,return_tensors="pt",padding=True,truncation=False,
                    add_special_tokens=False)
            if int(enc.attention_mask.sum(dim=1).max())>HARD_INPUT_TOKENS:
                raise RuntimeError("INPUT_CONTEXT_CAP_EXCEEDED")
            enc=enc.to(model.device)
            with torch.inference_mode():
                y=model(**enc,use_cache=False).logits[:,-1,:].float()
                differences=y[:,ids["positive"]]-y[:,ids["negative"]]
                out.extend(differences.cpu().tolist())
        return [float(v if label==1 else -v) for v in out]
    def audit(f,order,prefix):
        msgsets=[prefix+[old104.case_text(f,order,f["left"],f["right"])],
                 prefix+[old104.case_text(f,order,f["flip_left"],f["right"])],
                 prefix+[old104.case_text(f,order,f["left"],f["flip_right"])]]
        a,b,c=logit_margins(msgsets,f["label"])
        il=a-b;ir=a-c;total=abs(il)+abs(ir)
        return {"D":float((il-ir)/(total+EPS)),"J":float(il-ir),
                "I_left":float(il),"I_right":float(ir),"sens":float(total),
                "acc":int(a>=0)}
    def screen_one(f):
        return {"idx":f["idx"],"label":f["label"],"case_sha256":sha(canonical(f)),
                "orders":{o:{"baseline":audit(f,o,base),
                             "baseline_repeat":audit(f,o,base)} for o in ORDERS}}
    calrows=[screen_one(f) for f in cal]
    acc={o:sum(row["orders"][o]["baseline"]["acc"] for row in calrows)/CAL_N for o in ORDERS}
    sens=float(np.mean([row["orders"][o]["baseline"]["sens"] for row in calrows for o in ORDERS]))
    eligible=all(v>=.90 for v in acc.values()) and sens>=1
    emit("MPW103I_CALIBRATION",{"model":name,"n":CAL_N,"accuracy":acc,
        "mean_sensitivity":sens,"capability_eligible":eligible})
    if not eligible:
        emit("MPW103I_END",{"model":name,"status":"CAPABILITY_GATE_FAIL","no_validation":True})
        return
    if opt.mode=="screen":
        started=time.monotonic()
        for f in pool[:4]:screen_one(f)
        per=(time.monotonic()-started)/4
        elapsed=time.monotonic()-t0
        forecast=elapsed+per*POOL_N
        emit("MPW103I_SCREEN_TIMING",{"model":name,"seconds_per_case":per,
            "unpadded_sec":forecast,"padded_sec":elapsed+1.35*per*POOL_N,
            "provider_cap_sec":PROVIDER_TIMEOUT_S,"reserve_sec":ARCHIVE_RESERVE_S,
            "padding_veto":False})
        if forecast>PROVIDER_TIMEOUT_S-ARCHIVE_RESERVE_S:
            emit("MPW103I_END",{"model":name,"status":"RESOURCE_REPLAN",
                "no_treatment":True,"n_screened":0})
            return
        rows=[]
        for i,f in enumerate(pool):
            if time.monotonic()-t0>PROVIDER_TIMEOUT_S-ARCHIVE_RESERVE_S:
                emit("MPW103I_END",{"model":name,"status":"ACTUAL_PROVIDER_RUNTIME_ABORT",
                     "n_screened":i})
                return
            rows.append(screen_one(f))
            if (i+1)%256==0:
                emit("MPW103I_SCREEN_PROGRESS",{"model":name,"completed":i+1,"total":POOL_N,
                    "elapsed_sec":time.monotonic()-t0})
        selected=select_from_screen(rows)
        raw_sha=emit_shards("MPW103I_SCREEN",rows,256)
        selection_json=canonical(selected)
        for offset in range(0,len(selection_json),9000):
            emit("MPW103I_SELECTION_CHUNK",{"model":name,"part":offset//9000,
                "total":(len(selection_json)+8999)//9000,
                "selection_sha256":sha(selection_json),
                "data":selection_json[offset:offset+9000]})
        emit("MPW103I_SCREEN_SELECTED",{"model":name,
            "selected_manifest_sha256":sha(selection_json),
            "n_selected":selected["n_selected"],
            "counts":selected["selected_per_label"],
            "eligible":selected["eligible_per_label"],
            "selection_complete":selected["selection_complete"],
            "selected_indices":[s["idx"] for s in selected["selected"]],
            "selected_indices":[s["idx"] for s in selected["selected"]]})
        emit("MPW103I_END",{"status":"SCREEN_COMPLETED","model":name,
            "n_candidates":len(rows),"n_selected":selected["n_selected"],
            "selected_complete":selected["selection_complete"],
            "candidate_manifest_sha256":candidate_sha,"raw_sha256":raw_sha,
            "elapsed_sec":time.monotonic()-t0})
        return
if __name__=="__main__":main()
