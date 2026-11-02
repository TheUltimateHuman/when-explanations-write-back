# MPW-103I — Genuine Iterated Explanations: Eight-Cycle Causal-Provenance Audit

**Investigator:** Aidan Edward Lawson, Independent Researcher, Modal Path Ethics  
**GPU execution:** October 25–26, 2026 (local/UTC); **archival closeout:** November 1–2, 2026 (local/UTC)  
**Source category:** RESEARCH ARTIFACT; not a published Modal Path Ethics article  
**Scientific disposition:** QWEN3 COMPLETE, VALID, H1/H2/H3 **NOT CONFIRMED**. GRANITE **CAPABILITY_GATE_FAIL / NO SCREEN / NO ITERATION**, H1/H2/H3 UNKNOWN. Cross-model and all-six gates NOT MET.

## Abstract

MPW-103I returned to the unfinished genuine-iteration requirement of the original *When Explanations Write Back* research roadmap. Earlier MPW-103 simulated sequential explanation history by externally inserting report codes. MPW-103I instead elicited a new, model-generated one-sentence explanatory report **from each current conversational state** and inserted that exact report into the next state before generating the next report. Eight iterations were performed for each case, preserving model-generated words/token IDs, task answers, state hashes, independently measured input-intervention causal profiles, and local same-history acknowledgment counterfactuals.

The protocol was frozen before model inference and selected fresh cases with order-invariant causal-source preference, positive input-intervention channels, task competence and numerical stability. Qwen3-4B-Instruct-2507 completed 2,048 baseline-only screening cases; 191 were eligible (105 sentiment-class 0, 86 class 1), and 64 were selected by the prospective first-32-per-class rule. The full raw screening archive was reconstructed and independently verified **before** the eight-cycle trial. IBM Granite 3.3 8B failed the original LEFT-first calibration ability gate (27/32=84.375%, requirement >=90%) and did not undergo screening or generated iteration.

Qwen subsequently completed 64/64 eight-cycle original-model trials, all six control histories per case, both physical evidence orders, independent protected baseline repeats, and all native model-authored report/audit versions. Native report parseability was 505/512=98.63%. Original baseline numerical repeat and screen-to-run drift were both exactly zero. All three preregistered Qwen model-level hypotheses returned **NOT CONFIRMED**:

- H1 first native report incremental drift over matched elicitation+acknowledgment: **−0.0254377** (99.1667% familywise CI **[−0.075867,+0.030482]**, exact two-sided family sign p=.10342).
- H2 report-induced first-step fidelity advantage relative to a same-state question+acknowledgment fork: **+0.0625** (4 positive / 0 negative / 60 tied families, familywise CI **[0,+0.15625]**, sign p=.125).
- H3 incremental drift from steps 1→8 beyond repeated elicitation+acknowledgment: **−0.0167514** (CI **[−0.077422,+0.039160]**, sign p=.90065).

The full eight-step q_t, s_t, C_t and L_t accounting was reproduced from the original hash-verified GPU observations, and each step satisfied the identity s_t=q_t+C_t−L_t exactly. Contrary to an accumulation or self-validation narrative, fidelity to the next version did not increase monotonically, and report-specific incremental drift was not established. A separate explicitly **post hoc** content audit found that 62/64 cases kept the same LEFT/RIGHT report side across eight explanations even though the prose wording changed in 63/64 cases. Average first-step absolute causal drift after an ordinary directive was substantially larger than after model-authored explanation writeback.

This is the first actual model-generated *iterative conversational* loop in the MPW sequence, completing the previously omitted methodological class. It does **not** establish autonomous mechanistic introspection, neural circuit rewiring, parametric memory, robust natural self-validation, or model-general behavior.

## 1. Restored experimental target and original limitation

*When Explanations Write Back* v1.1 defines a protected source state S0 with causal organization A0, then model-generated R0, then uptake by W to produce S1 and A1, then model-generated R1 from S1, etc. The original plan required studying accumulation, oscillation, reversal, saturation and conversion/loss of fidelity **across genuinely generated successive explanations**, not simply repeated externally inserted assertions.

Earlier MPW-103 established causal effects of forced history and a report-versus-formatting contrast; MPW-104B, using 80 prospectively screened order-stable baseline cases per model, failed to confirm strict false-report-to-stable-sign conversion in both Qwen and Granite; MPW-105 found descriptively q=.675, s=.7375, C=.0625, L=0 for Qwen natural report prose but its post-score optimizer selected the natural comparator P0 and did not produce a selected-policy gain. Those earlier results remained separate from MPW-103I's fresh cohort.

This phase restores the missing question by requiring model-authored report R_t to be generated from the exact state S_t, with no oracle-provided explanation, after an actual model-chosen task answer. The next cycle sees the accumulated earlier reports in its conversation prefix. The model's weights remain frozen, so the measured updates are input-context-conditioned intervention-response changes, not weight updates.

## 2. Source, sample and method freeze

- Prospective experimental protocol and fixed H1/H2/H3: [original MPW-103I protocol](https://github.com/TheUltimateHuman/when-explanations-write-back/blob/47e26cf4da4c5ce354d38cf2babf52bd7bd7ea53/mpw103i/PROTOCOL.md).
- Original executable source/case freeze: [MPW-103I freeze](https://github.com/TheUltimateHuman/when-explanations-write-back/blob/f0a12228e223a0a41948935dc3b1ef75f73574c4/mpw103i/FREEZE.md).
- Native eight-cycle GPU runner exact SHA-256: **6fc0467425777a8c5e7ae7c32878a53c886a6f808306f734a4e58badf3763206**.
- Baseline-only screening runner exact SHA-256: **4f89a4d759b82cd74ec21465239e48c2558df9f359f5cdff2bf5b4a208e9a04f**.
- Independent CPU analysis exact SHA-256: **bec4c408964163e96ccd9bb92b6c05326979828e31f0b55b6b885c6acfeeb4e7**.
- Frozen candidate/calibration manifest SHA-256: **00cf578b03d0aeabc08b0226c5d84702695e9aa3f5b3264392b31d914526c20a**.
- Original dataset: stanfordnlp/sst2 at revision **8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb**.
- Primary model: Qwen/Qwen3-4B-Instruct-2507, revision **cdbee75f17c01a7cc42f958dc650907174af0554**, NVIDIA L4, FP16; pinned PyTorch 2.6.0 / Transformers 4.57.3.
- Candidate independent architecture: ibm-granite/granite-3.3-8b-instruct, revision **51dd4bc2ade4059a6bd87649d68aa11e4fb2529b**, NVIDIA L40S.
- Seed 2026102501; 32 new calibration families plus 2,048 independent screening candidates, 1,024 each sentiment class; 8,320 distinct newly sampled evidence passages. All prior MPW-101 through MPW-105 cohorts were regenerated and hash checked; 27,208 previously used normalized text keys were excluded. Text disjointness from previous trials is not certification of training-time nonexposure.

For each family and physically distinct LEFT-first / RIGHT-first passage order, the input-causal response measure was

D_t = (I_LEFT(t)−I_RIGHT(t))/(|I_LEFT(t)|+|I_RIGHT(t)|+1e−6)

where I_side is the change in correct-minus-alternative constrained sentiment logit margin when only the corresponding evidence passage is replaced by an independent opposite-sentiment passage. Raw J=I_LEFT−I_RIGHT, individual I values, sensitivity, task accuracy, saturation and all numerical repeats were retained. D is an operational input-intervention response, not a localized neural circuit.

The baseline screen required correct original task answers, same causal sign under both physical presentation orders, |D0|>=.10, both strictly positive I channels, unchanged repeat abs(D0−D0_REPEAT)<1e−4, and finite measurements. The **first 32 eligible per label by frozen index** were selected before any report elicitation. No ranking by outcome or favorable response to explanation.

### GPU screens

Qwen original baseline-only screen: https://huggingface.co/jobs/TheUltimateHuman/6ade9c09046eb82b1ece9553

- Calibration: LR 31/32=96.875%, RL 31/32=96.875%, mean sensitivity 26.3643; passed.
- Complete screen: 2,048/2,048 original family records; eligible class 0: 105, class 1: 86, total 191/2,048=9.33%; selected 32+32=64.
- Screen rejection counts are NOT mutually exclusive: 1,383 physically order-inconsistent source-sign cases; 114/136 task-inaccurate LR/RL; 324/693 nonpositive causal channels LR/RL; 308/138 low absolute D LR/RL.
- Original screening raw SHA-256: **1caf96300c109d5d619827898883c908c9bd7afaa6d522b21590266a8477bcc1**.
- Original selection JSON SHA-256: **9ffe21f78add86b1f4e079637d680af5702d25d46a1f5a24f79c6a0c4a7ebf0a**.

Granite original screening job: https://huggingface.co/jobs/TheUltimateHuman/6ade9c0b046eb82b1ece9555

- LR calibration **27/32=84.375%** (<90% rule), RL 31/32=96.875%, sensitivity 15.6638; **CAPABILITY_GATE_FAIL**. No baseline screening, no native reports, and NO Granite H1/H2/H3 observations. Not a scientific null.

**Immutable Qwen screen records and selection:**
https://github.com/TheUltimateHuman/when-explanations-write-back/tree/064e9f5ce3610f6a38332987e459d393b669a56a/mpw103i

CPU screen reanalysis independently recovered the eight original 256-family GPU shards, verified all per-shard/combined raw SHA-256 anchors and exactly reproduced all 64 selected case IDs, signs and screening baseline values **before native iteration**:
https://huggingface.co/jobs/TheUltimateHuman/6adec9aa1e112550ce7f1e5f

## 3. True sequential writeback and six controls

Every selected Qwen family started each of SIX controlled conversational histories at the same independently reconstructed source prefix S0. Eight sequential cycles were completed in every history. At each cycle, the frozen model first generated its own constrained sentiment answer; the task label was NOT inserted as an oracle response. The NATIVE_REPORT arm then generated the model's own actual greedy text (maximum 48 newly generated tokens) in response to a fixed prompt asking which source influenced the just-issued decision. That exact original text was inserted as the assistant explanation before the next cycle. R_t+1 thus depended on S_t+1 containing R_t.

Six concurrently run, independently rooted history arms:
1. NATIVE_REPORT: eight successive naturally generated prose reports, with every raw text, generated token IDs, state hashes, 0..8 causal audit versions, and local same-state acknowledgment counterfactual.
2. ELICIT_ACK: same explanation question, fixed "Understood." instead of report, eight cycles.
3. NEUTRAL_ACK: repetitive decisions and acknowledgment without causal explanation question.
4. ARBITRARY_CODE: model-generated A/B formatting token without source-reliance meaning.
5. FORCED_FALSE: experimenter-supplied originally false source-reliance text (explicitly NOT model-generated).
6. DIRECTIVE: standard instruction to rely on the original false side.

All six histories generated model task answers and contained the same count of user/assistant turn scaffolds. They were **not** matched for exact token length or pragma; a difference in context length and wording remains a competing explanation. For native reports, additionally forked at each S_t after the SAME model-generated task answer and explanation-question input, the exact report was replaced with "Understood.", then A_t+1 was independently audited. This local control isolates the incremental consumed-report content under the declared conversational format, but does not isolate a unique internal mental mechanism.

The original A0 was separately measured and repeated, and compared to the earlier screening A0 before report consumption. The source's original screen-defined historical TRUE/FALSE sign was not recalculated from treated observations.

## 4. Qwen complete execution and source validity

Original eight-cycle Qwen GPU job:
https://huggingface.co/jobs/TheUltimateHuman/6adec9c71e112550ce7f1e63

- Provider GPU stage: COMPLETED; actual runner status: COMPLETED.
- Original protocol and model/dataset/case hashes passed.
- 32-family task calibration accuracy: 96.875% separately in LR and RL; sensitivity 26.3643.
- Frozen full-cycle runtime feasibility probe measured 51.676 seconds/family on **two calibration families**; projected unpadded runtime 4,275.23 seconds, padded WARN-only 5,432.78 seconds. Both fit the real 7,200-second provider limit with 120-second archival reserve. No assistant-imposed 3,900-second veto.
- **Compliance qualification:** the protocol text specified a FOUR-family runtime pilot, while the frozen executable used TWO calibration families. This was explicitly logged prior to scientific results in [execution compliance note](https://github.com/TheUltimateHuman/when-explanations-write-back/blob/529a9faa879e3e18cec48621da9376f5146e5b62/mpw103i/EXECUTION_COMPLIANCE_NOTE.md). It affects feasibility forecasting, not sample or hypothesis design. The two pilot-calibration cases generated screen-baseline ANOMALY warnings under dummy screen metadata; these are NOT among the 64 frozen selected validation cases.
- 64/64 selected families executed; complete all 6 histories ×8 cycles plus native local acknowledgment counterfactuals.
- Actual original model runner elapsed time **4,091.99 seconds**.
- Original baseline repeat max absolute D discrepancy **0**.
- Cross-job original SCREEN-to-treatment D discrepancy **0**.
- Original task/source validity errors **0**.
- Model-generated native prose parseability **505/512=98.6328%**, above frozen >=80% usability gate.
- Scientific status: VALID, not resource-limited.

## 5. Qwen three frozen prospective primary tests

Each model had 64 independently selected families; H1/H2/H3 each required positive mean, exact two-sided family-level sign p<.0083333333, 50,000-bootstrap adjusted two-sided 99.1667% percentile CI lower>0, and positive estimates separately by physical order when defined. The six-test Bonferroni correction included the unexecuted Granite endpoints. Ties are excluded from the sign-test denominator.

| Test | Mean | Adjusted 99.1667% CI | Families +/−/0 | Exact two-sided sign p | Frozen verdict |
| --- | ---: | --- | --- | ---: | --- |
| H1 first-model-authored-report incremental absolute D drift over same-question ACK | **−0.02543772** | [−0.07586703,+0.03048203] | 25/39/0 | .10342188 | **NOT CONFIRMED** |
| H2 first report fidelity to genuine successor vs SAME original-state question+ACK fork | **+0.06250000** | [0,+0.15625] | 4/0/60 | .125 | **NOT CONFIRMED** |
| H3 additional t=1→8 native drift relative to accumulating explanation-question+ACK controls | **−0.01675142** | [−0.07742159,+0.03916002] | 31/33/0 | .90065325 | **NOT CONFIRMED** |

H1 measured different signs by physical evidence order: LEFT-first +.030467, RIGHT-first −.081342, also failing the required separate order positivity. H3 LEFT-first −.0448073, RIGHT-first +.0113045, failing the same requirement. These signs and exact test results were reproduced by independent CPU analysis, rather than inferred from a pooled 8×64 set of correlated steps.

H2 is an especially informative modest indication: after ONE model-generated report, the SAME report matched native successor A1 under both evidence orders in FOUR families in which its identical-history acknowledgment counterfactual did not; no families showed the reverse. But 60/64 were ties, and the adjusted bootstrap lower confidence bound equaled zero. The frozen two-sided sign test is p=.125, not <.00833. Therefore NOT CONFIRMED. An exploratory one-sided or per-branch reanalysis cannot rescue that original failure.

## 6. Drift magnitude: report-content effect versus ordinary language controls

The average across 64 families of absolute normalized D displacement from protected A0:

| Arm | t=1 | t=2 | t=4 | t=8 |
| --- | ---: | ---: | ---: | ---: |
| NATIVE_REPORT | .278117 | .267983 | .318072 | .339959 |
| ELICIT_ACK | .303555 | .317260 | .358766 | .382149 |
| NEUTRAL_ACK | .250793 | .260424 | .306653 | .339748 |
| ARBITRARY_CODE | .241414 | .253021 | .286501 | .313571 |
| FORCED_FALSE | .332741 | .368846 | .426721 | .437262 |
| DIRECTIVE | **.837802** | .751243 | .710314 | .700460 |

The explanatory question plus forced acknowledgment was on average more disruptive than model-generated prose at t=1 and t=8. The ordinary explicit directive was far stronger at the first step. H1 and H3 were both negative in their intended mean contrasts.

Drift is a descriptive magnitude. It need not indicate movement in the explanation's claimed direction, a genuine neural circuit rewrite, better predictive behavior, or beneficial self-correction. The native and matched-ack history both added text and repeated decisions, and the selection of a stable original A0 population does not make these controls inert.

## 7. Version-by-version fidelity: q_t, s_t, C_t, L_t

For each naturally generated R_t, historical-in-that-cycle fidelity q_t=F(R_t,A_t), next-version fidelity s_t=F(R_t,A_t+1), conversion C_t=1[F0=0,F1=1], loss L_t=1[F0=1,F1=0]. Fidelity requires agreement with BOTH physical source-order intervention signs; an unparseable report scores 0 on both sides. All 64 families contribute to every row. Every row satisfies the exact accounting identity s_t=q_t+C_t−L_t by construction and independent verification.

| Report version | q_t | s_t | Conversions | Losses | Counts (00,01,10,11) |
| --- | ---: | ---: | ---: | ---: | --- |
| R0 | 46/64 = .71875 | 45/64 = .703125 | 1 | 2 | (17,1,2,44) |
| R1 | 46/64 = .71875 | 46/64 = .71875 | 1 | 1 | (17,1,1,45) |
| R2 | 46/64 = .71875 | 45/64 = .703125 | 0 | 1 | (18,0,1,45) |
| R3 | 45/64 = .703125 | 43/64 = .671875 | 0 | 2 | (19,0,2,43) |
| R4 | 43/64 = .671875 | 43/64 = .671875 | 0 | 0 | (21,0,0,43) |
| R5 | 43/64 = .671875 | 44/64 = .6875 | 1 | 0 | (20,1,0,43) |
| R6 | 44/64 = .6875 | 41/64 = .640625 | 1 | 4 | (19,1,4,40) |
| R7 | 41/64 = .640625 | 42/64 = .65625 | 2 | 1 | (21,2,1,40) |

These are eight *within-family correlated* checkpoints, not 512 independent scientific cases. The sequence does not establish monotone increase in either historical or post-writeback explanatory fidelity; there were losses as well as conversions, and the score declined substantially across several middle/later versions. In particular R6 lost historical fidelity in four families while converting one.

The exact identity at each t is a faithful calculation of the reported two-by-two table, not a validation of the model's internal understanding. Historical fidelity means before the report was consumed **for that step**, not a claim that A0 from the original screen is unchanged across all subsequent cycles.

## 8. Observed model-generated language and causal-sign dynamics — strictly exploratory audit

The full GPU runner recorded:
- Eight reports ×64 families = **512 model-generated native prose explanations**.
- 505/512 reports parsed with a leading LEFT: or RIGHT:; seven could not be parsed.
- **Two** report-side changes across 448 adjacent report pairs (the eight-step chain has seven transitions per family), among only two families.
- Thirty-two changes in the LR/RL causal-sign *tuple* across native successive mechanism versions, over the full cohort; nine families showed >=2 sign changes, and five eventually returned to their original sign tuple after an intermediate deviation.
- Thirty-seven families had less than .05 change in absolute displacement magnitude between t=4 and t=8 (a descriptive plateau proxy fixed before GPU results, not a significance test).

A separate **post hoc**, exploratory source-text audit inspected original GPU raw reports without changing primary outcomes:
- **62/64 families retained exactly the same parsed report side across all eight reports.**
- Only **1/64 family** used identical complete explanatory wording all eight times; 63/64 families changed words while preserving their report side in almost every case.
- Just 13 of 448 adjacent pairs of full raw report text were byte-identical.
- At the first iteration, reported LEFT in 50/64 families, RIGHT in 14/64; protected original true sign in the frozen selection was LEFT in 46/64, RIGHT in 18/64.
- Overall side count: LEFT 386 reports, RIGHT 119, unparseable 7; mean 31.70 generated tokens, median 31, max 48.
- At the first locally controlled report uptake comparison: native faithful and ACK faithful 41 families; native-only faithful four; ACK-only faithful zero; neither faithful 19.

Thus **the prose changed extensively while reported causal side remained nearly fixed**. An invariant reported side is compatible with an actual stable preference, anchoring from earlier reports, a lexical/default LEFT bias, instruction conditioning, or an evaluator instrument insensitive to narrative variation. The data do not distinguish these possibilities. The strong DIRECTIVE control and mixed measured causal sign behavior prohibit framing repetition as a novel self-stabilizing explanatory mechanism.

**Explicitly post-outcome script and CPU audit:**
https://github.com/TheUltimateHuman/when-explanations-write-back/blob/f1afc7e9b3d59d30572166eb286b9a2e135e8179/mpw103i/results/posthoc_content_audit.py

https://huggingface.co/jobs/TheUltimateHuman/6ae81881c78863f9c6300f87

## 9. Complete original raw archive and independent CPU verification

Original GPU model inference finished with all 64 cases and four original gzip/Base64 compressed raw JSONL shards (16 cases per shard), including every one of 6×8 branch histories, native generated text/tokens, code controls, local same-S_t acknowledgments, intermediate causal profiles, state-chain hashes, source/task labels, and complete primary summary.

Original complete raw Qwen JSONL SHA-256:
**d2ba98a60e504a4e8cc1d422c61c31b280e4fe26b05ed65bc2a9e744ba8bff87**

Raw shard SHA-256:
1. 24d1a75ae877869fb3f02dd819fe09a58b6dfb90ac678f0ad19ef5a9d9e5865e
2. 73262b72bb54dd3b46b3c955ab4cca9ad3cbd8cc8d1301da912f1f0859f67ad5
3. 7a1dfd55aa531d890fa12746a91bb27f795ebb9fbb1837e457f2d50c35a9bfac
4. a125a877608fd696f329ac39323aee2b3e10511ab366a8e58910c8f7311fb5e8

**Immutable original GPU source records and machine manifest:**
https://github.com/TheUltimateHuman/when-explanations-write-back/tree/923b024055403fb031e673c4de373878bb81f6f5/mpw103i/results

The initial independent CPU verification attempt failed on an **archive-manifest schema issue**: the verifier expected screen_selection_commit inside the per-model object, while the manifest supplied it only at top level. The manifest was repaired to include this reference for both model objects. No raw shard, study method, CPU scientific source, GPU result, case selection, or hypothesis acceptance rule changed. The first attempt and repair remain in job/Git history.

**Successful independent original-GPU record recomputation:**
https://huggingface.co/jobs/TheUltimateHuman/6ae818310e0338d1bb7dc84c

This separate CPU job COMPLETED, recovered the exact four original raw shards, matched each raw SHA and combined digest, retrieved the immutable screen selection, checked every selected case and original historical TRUE/FALSE sign, and imported ONLY the independently authored MPW-103I analysis, not the GPU inference runner. It exactly reproduced H1/H2/H3 family effects, 50k bootstrap confidence intervals, sign p-values, overall validity, native prose parse rate, all eight q/s/C/L transition tables, mechanism/sign-flip and return/plateau statistics.

This is **independent statistical reanalysis and provenance verification of the original model-generated observations**. It is not independent repetition of the model inference by another lab.

## 10. Limitations, negative evidence and scientific decision

**Exactly observed:** genuine model-generated iterative reports R0..R7 were produced in a recorded continuing conversational state with original model-chosen answers, unlike MPW-103's externally inserted histories. Every report and each versioned input-intervention response was audited. The original A0 was order-stable, task-correct, numerically repeatable, screen-frozen and independently reverified. The study was valid. Report language frequently changed but report sides usually did not.

**Failed to confirm:** H1 additional first-step drift from native explanatory content over the elicitation+ACK scaffold; H2 first report improving immediate successor fidelity over its identical-history ACK counterfactual; H3 cumulative explanation-specific drift across eight cycles beyond repeated elicitation+ACK. The data do not establish monotone accumulation, stable self-validation or a positive general explanation rewrite effect.

**Other model unknown:** Granite capability screen failed before candidate screening. No Granite native iteration observations exist. No two-model genuine-iteration generality claim is justified.

**Alternative explanations:** ordinary context conditioning, prompt and role differences, native code/lexical biases, model answer elicitation, token-length and repeated instructions, physical evidence-order effects, intervention-definition artifacts, and selection toward stable original mechanism profiles remain possible. The model has frozen weights and no long-term external memory; no autonomous self-reflection, privileged introspection, neural-circuit localization, or inherently self-certifying evaluation was demonstrated. Known iterative self-explanation refinement, faithfulness and self-correction literature prevents a generic novelty claim for iterative prompting itself.

**Status classification:**
- MPW-103I Qwen: **COMPLETE, VALID, H1/H2/H3 ALL NOT_CONFIRMED**.
- MPW-103I Granite: **CAPABILITY_GATE_FAIL / NO SCREEN / NO ITERATION / ALL H UNKNOWN_NOT_EXECUTED**.
- Overall full two-model gate: **NOT MET**.
- Original missing methodological class (*actual endogenous report succession*) has now been experimentally executed and independently archived; the study can close as a completed **negative/indeterminate result**, without claiming its motivating hypotheses succeeded.

## 11. Research roadmap after MPW-103I

The sequential externally generated report loop and the separately selected post-writeback evaluator experiment have both been carried through the original intended stages and negatively tested under their initial frozen criteria. Further targeted experimentation is justified only by a new technical mechanism or counterexample, not automatically because results were null.

The original roadmap continues to **MPW-106 persistent memory**, **MPW-107 naturalistic decisions**, and **MPW-108 provenance certification**. A prospective MPW-106 should define actual durable external write/retrieval state, distinguish a report preserved in external memory from an in-context conversational report, and explicitly measure audit history across retrieval and deletion boundaries. The current results do not imply such persistence exists or that score optimization was successful.

**Final MPW-103I ruling: VALID QWEN EIGHT-CYCLE TRIAL, THREE PRIMARY HYPOTHESES NOT CONFIRMED, GRANITE NOT EXECUTED AFTER FAILED CALIBRATION, ORIGINAL RAW EVIDENCE AND NEGATIVE OUTCOMES PRESERVED.**
