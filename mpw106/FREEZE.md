# MPW-106 — Prospective Case, Source and Hypothesis Freeze

**Date:** 2026-11-02, before any MPW-106 GPU inference.  
**Evidence category:** PROSPECTIVE RESEARCH ARTIFACT, not an external OSF preregistration.  
**Original protocol:** mpw106/PROTOCOL.md, first committed as b84d4e0ab37108aa4ee021e89b6ad8b396c691a9.  
**Scope:** durable Git application memory across separate writer/reader model GPU processes, active correction/deletion and explicitly stale historical read. No inference of model-internal persistent weights or secure erasure.

## Frozen case bank and models

- Seed 2026110106. Thirty-two calibration plus 2,048 independent fresh baseline-screening cases (1,024 per sentiment), four evidence texts each.
- Fresh source sample SHA-256: **39992256f2432492527f764a1651fbd3054420c2de73682e668b0e0fa73aed16**.
- Exact 8,320 unique fresh evidence strings and 35,528 prior-study normalized text keys excluded. Historical MPW-101/102A/B/C/103/103I/104A/B/105 manifests reconstructed and verified; no contamination of prior case texts.
- Dataset: stanfordnlp/sst2 revision 8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb.
- Qwen/Qwen3-4B-Instruct-2507 SHA cdbee75f17c01a7cc42f958dc650907174af0554, NVIDIA L4.
- ibm-granite/granite-3.3-8b-instruct SHA 51dd4bc2ade4059a6bd87649d68aa11e4fb2529b, NVIDIA L40S.
- FP16 PyTorch 2.6.0, transformers 4.57.3, source-independent CPU verification. No shared mutable KV state between writer and reader; no weight updates.

## Frozen executable SHA-256 (exact source bytes)

All eleven source files were syntax-checked and hashed before GPU at Hugging Face job 6ae8ec110e0338d1bb7e8daf. Each pin was inspected as a literal top-level assignment; none remains unresolved.

- mpw106/scripts/mpw106_screen.py: **b2c43f5871e0eb2837ecb3b4cb9af28973c735850c9eb7c019d59913b6b52df2**
- mpw106/scripts/mpw106_writer.py: **98664ed29e6b94191c41a1c91891720d1d464e781b39239d16859dc7ac96f353**
- mpw106/scripts/mpw106_reader.py: **d68a3b43d3161587edd88d5ae388adc6e584257666aee4f4af0e3d77e508871e**
- mpw106/scripts/memory_contract.py: **1d5e781431991467a0eafbc48f62afee0bd7b19ead0c19363f99554325a40912**
- mpw106/scripts/independent_screen.py: **4d7fdfe11b3846d956e453054a6a007ae968f1c591e55a8c0054d6b69aa278fb**
- mpw106/scripts/independent_writer.py: **8fdc4e53a9296a31319089d94c1b0ea7083666a8218752a482cbd22ed4ec2a94**
- mpw106/scripts/independent_analysis.py: **a3b3141a134d5d30b16798bedd0f6d6e43ee216408aeb0659303f65e6c1f29b0**
- mpw106/scripts/build_store.py: **22329ddb1b501f35264e1f20bd4f56b14c5b24ea39b4a09a1492834b65dced3c**
- mpw106/scripts/verify_store.py: **ec854c9e13af6bc59044dcca67ee5d65d867d28e768d2e932a30323a295fed92**
- mpw106/scripts/verify_writer.py: **17f90b6deb722f988259ce7f9e5894b6df1521cc08bb85323293854adb798acf**
- mpw106/scripts/verify_screen.py: **08a28beae5fda8714fc6dd5afe32f05c6d51a828d7648995d9ee6c243df3c571**

Screen source content SHA was fixed in the writer and reader before all GPU runs; the writer and reader additionally pin the source-case bank SHA. The reader pins the exact contract source SHA.

## CPU-only preflight / provenance before model inference

- Original historical-exclusion screen preflight: https://huggingface.co/jobs/TheUltimateHuman/6ae821bfc78863f9c6301405, PASS.
- Optimized historical-source reconstruction preflight with same exact case bank: https://huggingface.co/jobs/TheUltimateHuman/6ae82688c78863f9c6301642, PASS.
- The two preflights had identical new canonical case manifest SHA, sample n and exclusion counts. The optimized version removes redundant source regeneration; no cohort or gate changed.
- Screen-selection synthetic independent replay: https://huggingface.co/jobs/TheUltimateHuman/6ae826e6c78863f9c63016c2, PASS.
- Model-authored writer report integrity regressions: https://huggingface.co/jobs/TheUltimateHuman/6ae82500c78863f9c63014e0, PASS.
- Independent memory causal-analysis synthetic positive, negative and bad-source tests: https://huggingface.co/jobs/TheUltimateHuman/6ae823f00e0338d1bb7dcbb4, PASS.
- Final exact 11-file AST and source-hash test: https://huggingface.co/jobs/TheUltimateHuman/6ae8ec110e0338d1bb7e8daf, PASS.
- Preflight baseline maximum input tokens Qwen 182 and Granite 253; both positive/negative and A/B native answer codes atomic. Model generation has a declared 48-token greedy report limit and declared input caps.

These are engineering/synthetic checks, **not empirical results** of any MPW-106 hypothesis.

## Immutable experimental gates

Baseline-only screen per eligible model: calibrate original task with 32 cases (>=90% accuracy separately LR/RL, sensitivity>=1), screen all 2,048 candidates twice under both physical orders, and choose first 32 eligible per sentiment class. Exactly 64 selected families/model; independent CPU recovery and recomputation MUST PASS before writer can begin. No report generation in SCREEN.

Writer stage: a different GPU model process remeasures the frozen source baseline with strict <1e-4 cross-job repeat and original sign/task checks, elicits each model's own classification and one-sentence explanation and archives all 64 raw reports with generated token IDs and exact text hashes. At least 80% of calibration and 80% of selected reports must parse. A separate CPU source verifier MUST PASS before the externally authorized harness writes any memory.

Git external memory: four separately committed immutable versions of the same active store path mpw106/store/state.json, in neutral → live → externally corrected → deleted order. Original model-authored report text persists exactly only in the LIVE active state; CORRECTED contains declared external oracle correction and DELETED tombstones its entries without global Git erasure. Independently verify exact contents, source hashes, each commit and stale-live access before READER.

Fresh reader stage: separate new GPU job loading the model with no writer transcript/cache; receives only case bank and declared N/L/C/D SHA-commit references and uses exact-key/hash-verified retrieval. Conditions CLEAN/NEUTRAL/LIVE/CORRECTED/DELETED/MISSING/EXPLICIT_STALE as frozen in executing reader (MISSING is a separate procedural control; no extra primary test). D and MISSING must have identical unavailable messages and intervention results. Every condition records both LR/RL input-causal D,J,I values. Reader returns full original 64-family raw records before CPU reanalysis.

Three primary hypotheses/model: H1 LIVE minus NEUTRAL report-side directed D displacement (all 64); H2 LIVE minus NEUTRAL sign crossing among >=16 baseline-unfaithful, parseable reports; H3 externally corrected source-direction displacement over LIVE among the same >=16. Six total prospective tests at alpha=.05/6, 50k family bootstrap, adjusted 99.1667% CI lower>0, two-sided exact family sign p<alpha and both-order positivity where applicable. If under 16 baseline-unfaithful parseable, H2/H3 INDETERMINATE_CAPABILITY; cannot alter selection. Source q,s,C,L exact accounting checked, not treated as independent proof.

Provider hard caps: 90m each screen/writer/reader job, 120 seconds actual archival reserve, 35% padded warning not a veto. No arbitrary 65m cap or post-result paid retry to obtain positive evidence. Preserve all negative, incomplete, invalid and indeterminate outcomes.

## External prior art and scope ceiling

See mpw106/PRIOR_ART.md for MemGPT, MemSecBench, AfterDeleteBench, MemForm and sleeper poisoning. Deletion here means active namespace tombstone; old Git snapshots remain readable. Model-authored content is externally committed by a research harness, not an autonomous memory tool choice. A positive causal effect after retrieval cannot be called changed model weights, privileged introspection or intrinsic persistence. The original manuscript's Baseline Write Barrier remains the governing principle.
