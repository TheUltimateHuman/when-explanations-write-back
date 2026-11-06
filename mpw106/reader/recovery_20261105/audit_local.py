"""Read-only external-state MPW-106 reanalysis; writes only local audit artifacts."""
import base64,copy,gzip,hashlib,importlib.util,json,math,sys
from collections import Counter
from pathlib import Path
import numpy as np
import scipy

P=Path(__file__).resolve().parent
def sha(b): return hashlib.sha256(b if isinstance(b,bytes) else b.encode()).hexdigest()
def canon(v): return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
assert np.__version__=='2.1.3' and scipy.__version__=='1.15.3'
inputs=json.loads((P/'verification_inputs.json').read_text())
metadata=json.loads((P/'RECOVERY_INTEGRITY.json').read_text())
verified_files={}
for name,v in inputs.items():
    b=v['content'].encode();blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\x00'+b).hexdigest()
    assert blob==v['sha']
    verified_files[name]={'git_blob_sha1':blob,'sha256':sha(b),'source_url':v['display_url']}
assert sha(inputs['analysis_source']['content'])=='a3b3141a134d5d30b16798bedd0f6d6e43ee216408aeb0659303f65e6c1f29b0'
assert (P/'analysis_source.py').read_bytes()==inputs['analysis_source']['content'].encode()
data={}
for name in ('qwen_writer','qwen_reader'):
    parts=[]
    for i,s in enumerate(metadata[name]['shards'],1):
        gz=base64.b64decode((P/f'{name}_shard{i:02d}.jsonl.gz.b64').read_bytes().strip(),validate=True)
        raw=gzip.decompress(gz)
        assert sha(gz)==s['compressed_sha256'] and sha(raw)==s['raw_sha256'] and len(raw.splitlines())==16
        parts.append(raw)
    raw=b''.join(parts)
    assert raw==(P/f'{name}_records.jsonl').read_bytes()
    assert sha(raw)==metadata[name]['combined_raw_sha256']==metadata[name]['terminal']['raw_sha256']
    data[name]=[json.loads(l) for l in raw.splitlines()]
rows=data['qwen_reader'];writer={r['idx']:r for r in data['qwen_writer']}
selection=json.loads(inputs['selection']['content'])
snapshots={k.upper():json.loads(inputs[k]['content']) for k in ('neutral','live','corrected','deleted')}
bank='39992256f2432492527f764a1651fbd3054420c2de73682e668b0e0fa73aed16'
assert selection['source_candidate_sha256']==bank and selection['n_selected']==64 and selection['selection_complete']
assert len(rows)==len(writer)==64
assert [r['idx'] for r in rows]==[r['idx'] for r in selection['selected']]==sorted({r['idx'] for r in rows})
assert Counter(r['label'] for r in rows)=={0:32,1:32}
previous=None
for kind,state in snapshots.items():
    assert state['kind']==kind and state['model']=='qwen3' and state['case_manifest_sha256']==bank and state['parent_state_sha256']==previous
    previous=sha(canon(state))
contract=module('memory_contract_local',P/'scripts__memory_contract.py')
for kind,state in snapshots.items(): contract.validate_store(state,kind,'qwen3',bank)
arms=('CLEAN','NEUTRAL','LIVE','CORRECTED','DELETED','MISSING','EXPLICIT_STALE');orders=('LR','RL')
neutral='In the previous session I classified sentiment. This note does not describe which passage influenced that answer.'
refs=metadata['qwen_reader']['terminal']['snapshot_refs']
for r in rows:
    w=writer[r['idx']]
    assert r['case_sha256']==w['case_sha256'] and r['label']==w['label'] and r['original_true_side']==w['true_side']
    assert r['original_report_text']==w['native']['raw'] and r['original_report_sha256']==w['native']['raw_sha256']
    for kind,state in snapshots.items():
        entry=next(e for e in state['entries'] if e['case_id']==contract.case_id(r['idx']))
        assert entry['case_sha256']==r['case_sha256'] and entry['original_report_sha256']==r['original_report_sha256']
        expected={'NEUTRAL':neutral,'LIVE':r['original_report_text'],'CORRECTED':'Correction by an external auditor: the protected original source-reliance test favored '+r['original_true_side']+'.','DELETED':None}[kind]
        assert entry['text']==expected
    for arm in arms:
        expected_ref=None if arm=='CLEAN' else 'MISSING_IN_LIVE' if arm=='MISSING' else refs['live'] if arm=='EXPLICIT_STALE' else refs[arm.lower()]
        assert r['reads'][arm]['snapshot_commit']==expected_ref
        for o in orders:
            z=r['conditions'][arm][o]
            assert z['J']==z['I_left']-z['I_right']
            assert z['sens']==abs(z['I_left'])+abs(z['I_right'])
            assert z['D']==z['J']/(z['sens']+1e-6)
    assert r['clean_baseline']==r['clean_repeat']
    for o in orders: assert r['clean_baseline'][o]==r['screen_orders'][o]['baseline']
    assert r['reads']['LIVE']['prefix_sha256']==r['reads']['EXPLICIT_STALE']['prefix_sha256']
    assert r['reads']['DELETED']['prefix_sha256']==r['reads']['MISSING']['prefix_sha256']

probe=rows[0];L=snapshots['LIVE'];blocked={}
def attempt(label,state,idx,case_sha,model='qwen3',source_bank=bank,kind='LIVE'):
    try: contract.lookup(state,idx,case_sha,model,source_bank,kind)
    except contract.RetrievalRejected as e: blocked[label]=str(e);return
    raise AssertionError('Expected rejection: '+label)
attempt('wrong_case_sha',L,probe['idx'],'0'*64)
attempt('wrong_existing_id',L,rows[1]['idx'],probe['case_sha256'])
attempt('wrong_bank',L,probe['idx'],probe['case_sha256'],source_bank='0'*64)
attempt('wrong_model',L,probe['idx'],probe['case_sha256'],model='granite')
attempt('implicit_stale_live_as_deleted',L,probe['idx'],probe['case_sha256'],kind='DELETED')
for label,field,value in [('bad_schema','schema','BAD'),('unsupported_kind','kind','FUTURE')]:
    state=copy.deepcopy(L);state[field]=value;attempt(label,state,probe['idx'],probe['case_sha256'])
state=copy.deepcopy(L);state['entries'][0]['text']='TAMPER';attempt('changed_content',state,probe['idx'],probe['case_sha256'])
assert contract.lookup(L,999999,probe['case_sha256'],'qwen3',bank,'LIVE')=={'status':'NO_RECORD','text':None}
assert contract.lookup(snapshots['DELETED'],probe['idx'],probe['case_sha256'],'qwen3',bank,'DELETED')=={'status':'NO_RECORD','text':None}

frozen=module('independent_frozen',P/'analysis_source.py')
result=frozen.analyze(rows,selection,snapshots,'qwen3',bank)
(P/'independent_local_result_pinned.json').write_text(json.dumps(result,indent=2)+'\n')
# Independently recompute the primary statistic without using analyzer helpers.
sign=lambda side:1 if side=='LEFT' else -1 if side=='RIGHT' else 0
h1=np.array([sum(sign(r['original_report_side'])*(r['conditions']['LIVE'][o]['D']-r['conditions']['NEUTRAL'][o]['D']) for o in orders)/2 for r in rows])
npos=sum(v>0 for v in h1);nneg=sum(v<0 for v in h1);nt=npos+nneg
p_exact=2*sum(math.comb(nt,k) for k in range(min(npos,nneg)+1))/2**nt
rng=np.random.default_rng(520261107)
samples=h1[rng.integers(0,64,size=(50000,64))].mean(axis=1);samples.sort()
def percentile(q):
    j=(len(samples)-1)*q;k=math.floor(j);return float(samples[k]+(j-k)*(samples[min(k+1,len(samples)-1)]-samples[k]))
ci=[percentile(.05/12),percentile(1-.05/12)]
assert abs(p_exact-result['primary']['H1']['estimate']['sign_p'])<1e-15
assert abs(h1.mean()-result['primary']['H1']['estimate']['mean'])<1e-15
assert np.allclose(ci,result['primary']['H1']['estimate']['ci_familywise'],rtol=0,atol=1e-15)

def fidelity(r,arm): return r['original_report_side'] is not None and all(sign(r['original_report_side'])*r['conditions'][arm][o]['D']>0 for o in orders)
diagnostics={}
for arm in arms:
    d={}
    for metric in ('D','J'):
        diffs=[sum(r['conditions'][arm][o][metric]-r['clean_baseline'][o][metric] for o in orders)/2 for r in rows]
        d[metric]={'mean_raw_shift_from_clean':float(np.mean(diffs)),'mean_abs_shift_from_clean':float(np.mean([sum(abs(r['conditions'][arm][o][metric]-r['clean_baseline'][o][metric]) for o in orders)/2 for r in rows])),'mean_report_directed_shift':float(np.mean([sign(r['original_report_side'])*v for r,v in zip(rows,diffs)]))}
    d['task_accuracy']={o:sum(r['conditions'][arm][o]['acc'] for r in rows)/64 for o in orders}
    d['conversion_ids']=[r['idx'] for r in rows if r['original_report_side']!=r['original_true_side'] and fidelity(r,arm)]
    d['loss_ids']=[r['idx'] for r in rows if r['original_report_side']==r['original_true_side'] and not fidelity(r,arm)]
    diagnostics[arm]=d
false=[r for r in rows if r['original_report_side'] is not None and r['original_report_side']!=r['original_true_side']]
audit={'scope':'LOCAL_REANALYSIS_OF_ORIGINAL_RECORDS_NOT_IMMUTABLE_READER_ARCHIVE_VERIFIER','python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'verified_inputs':verified_files,'all_64_exact_screen_baselines':True,'all_896_arm_order_metric_relations_exact':True,'all_64_reader_reports_match_writer':True,'all_256_store_entries_match_exact_protocol_text':True,'read_binding_tests':blocked,'independent_h1':{'mean':float(h1.mean()),'positive':int(npos),'negative':int(nneg),'zero':int(64-nt),'sign_p_exact_combinatorial':p_exact,'ci_familywise_independent':ci},'source_side_counts':dict(Counter(r['original_true_side'] for r in rows)),'report_side_counts':dict(Counter(str(r['original_report_side']) for r in rows)),'descriptive_only_ineligible_false_cohort':{'n':len(false),'live_fidelity_count':sum(fidelity(r,'LIVE') for r in false),'neutral_fidelity_count':sum(fidelity(r,'NEUTRAL') for r in false),'corrected_fidelity_count':sum(fidelity(r,'CORRECTED') for r in false),'no_confirmatory_H2_H3_test':True},'arm_diagnostics':diagnostics}
(P/'independent_audit_details.json').write_text(json.dumps(audit,indent=2)+'\n')
print(json.dumps({'result':result['primary'],'audit':{k:v for k,v in audit.items() if k not in ('verified_inputs','arm_diagnostics')}},indent=2))
