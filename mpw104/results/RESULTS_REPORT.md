# MPW-104 — The False Explanation: Protected-Baseline Conversion

**Technical closeout: October 23–24, 2026 (local/UTC).**  
**Investigator:** Aidan Edward Lawson, Independent Researcher, Modal Path Ethics.  
**Source category:** RESEARCH ARTIFACT.  
**Disposition:** QWEN3 PRIMARY H1/H2/H3 CONFIRMED **within the frozen, presentation-order-specific experimental estimands**. GRANITE ALL PRIMARY VERDICTS INVALID (RIGHT-first accuracy 115/128, below 90%). BOTH-MODEL FALSE-CONVERSION GATE NOT MET. STRONGER ORDER-INVARIANT FALSE-EXPLANATION INTERPRETATION NOT ESTABLISHED; post hoc audit finds most Qwen conversion effects in physically order-inconsistent baselines.

## Abstract

MPW-104 prospectively examined an intervention capable of making an initially false report appear consistent with a model's later input-level causal audit. A protected untreated baseline measured which of two same-sentiment evidence passages most influenced the model's constrained sentiment logit margin. In each case and physical passage order, the investigator then forced a report asserting the opposite side, while holding model weights and original evidence constant. Matched alternate-code reporting, free-code, first-person reference and imperative arms distinguished several kinds of contextual steering.

Two frozen, separately calibrated open-weight models were evaluated on 128 new four-text SST-2 families each, with both passage presentation orders and reverse-mapped A/B code options. Each family had 17 audit arms per physical order. Three hypotheses per model, six model-level primary tests, used Bonferroni alpha 0.05/6, 50,000 family bootstrap resamples, exact family-level sign tests, and positivity requirements in both passage orders. Sign-conversion testing was confined to independently repeated, baseline-known orders using preregistered eligibility and minimum-denominator criteria.

Qwen3-4B completed all families, was VALID, and confirmed: H1 directional false-report uptake relative to a formatting-code sham (+0.21498 normalized D); H2 excess false-to-apparent-true sign crossings relative to sham (+0.26442 family-level contrast among 104 eligible families); H3 free-text first-person false declaration relative to a person-matched side reference (+0.12304). Granite 3.3 8B also completed all cases and had repeat-numeric discrepancy 0, but failed the frozen RIGHT-first baseline accuracy gate at 115/128 = 89.84375%, so its H1/H2/H3 are all INVALID regardless of raw effect size.

Crucially, a subsequent explicitly POST HOC audit separated Qwen cases whose protected baseline gave the same LEFT/RIGHT dominance sign in both presentation orders from those whose sign reversed. Qwen had 43 sign-consistent and 85 sign-inconsistent families. Almost all the large H1 and H2 effects arose in the order-inconsistent subgroup; 32 order-consistent baseline-known families contributed just two positive H2 family differences and thirty ties. This does NOT retroactively change the preregistered confirmation, which defined false per physical order, but prevents claiming that an originally false report about a presentation-invariant causal preference became true. No endogenous model-authored explanation, privileged introspection, changed model weights, persistence after deletion, or reward-optimized evaluator manipulation was demonstrated.

## 1. Previous experimental record and hypothesis

MPW-101 prospective natural-report fidelity conversion: NOT CONFIRMED (18 gain versus 11 loss, paired p=0.26493). MPW-102A established a mapping-balanced forced-report meaning effect in Phi-3.5-mini. MPW-102B confirmed its specific H1/H2 effects in Qwen; original Granite validation was halted by an unjustified assistant-created timing gate and a subsequently transparently amended Granite completion was INVALID on both accuracy and numerical-repeat requirements. MPW-102C confirmed A/B report transport and first-versus-second-person matched contrast in Qwen and Granite, but Granite's person-matched declarative H2 failed its frozen passage-order condition. MPW-103 Granite confirmed earlier report history H1 and report versus formatting control H3, while dose H2 and ordering H4 were not confirmed. A documented POST-RESULT TIME-GATE amendment allowed valid MPW-103 Qwen data: H1/H2/H3 confirmed, H4 not confirmed. Those findings are separately archived and never used as MPW-104 validation families.

Broad prompt-conditioned model behavior, fabricated self-statements, and explanation unfaithfulness have considerable prior art. The incremental experiment sought here is a VERSIONED counterfactual: initially false relative to a measured source-intervention profile, followed by externally imposed report consumption and a separately evaluated later source-intervention profile. Its test does not isolate a unique cognitive mechanism and does not yet involve naturally authored explanations.

## 2. Prospective source provenance and experimental protocol

Protocol and frozen source: https://github.com/TheUltimateHuman/when-explanations-write-back/tree/c94d1299e8862686bb728880c3f36a1527e7b7c0/mpw104

First protocol commit: dac5166ce07cae787861b31d239391a4807c4af6.  
Prevalidation freeze commit: c94d1299e8862686bb728880c3f36a1527e7b7c0.  
GPU runner exact source SHA-256: d8866d46dcb4bc6f5e2289108c22c434add56c423e63f1731c929aed86d6d1e1.  
Independent-analysis source SHA-256: 797effb9607a1fdc26b20971b8fbbb85c0f79f2e591ab0e979696a9736e7bcfd.  
New case-manifest SHA-256: f80ccf2b2901acdc7d8fbd7ad8df3edcc297a14b97fb5b2e7a26da0576d3a97d.

Models: Qwen/Qwen3-4B-Instruct-2507 revision cdbee75f17c01a7cc42f958dc650907174af0554, and ibm-granite/granite-3.3-8b-instruct revision 51dd4bc2ade4059a6bd87649d68aa11e4fb2529b. Dataset: stanfordnlp/sst2 revision 8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb. Frozen weights, PyTorch 2.6.0+cu124, Transformers 4.57.3, FP16, no persistent reuse of model state or KV cache, full independent reconstruction of each treatment branch.

32 new calibration families, 128 new validation families, balanced sentiment. Each family was generated from two same-label reviews assigned LEFT and RIGHT, plus independent opposite-label replacements for each. Sample generation verified and excluded earlier MPW-101 through MPW-103 passage texts and other prespecified exclusions (5,576 historical text keys; 640 new distinct evidence strings). Text disjointness from earlier study cases does not mean the model had not encountered SST-2 text in pretraining.

At each family and physical order, the protected original baseline A0 was independently audited twice. The first baseline D determined TRUE=LEFT when D0>=0 or TRUE=RIGHT otherwise, and FALSE the other side. This orientation was selected BEFORE the report treatments were applied. This is not the model selecting a natural explanation; these were investigator-inserted reports.

The input-intervention statistic was D=(I_LEFT-I_RIGHT)/(|I_LEFT|+|I_RIGHT|+1e-6), where I is the drop in correct-vs-alternative constrained output-label logit margin after counterfactual replacement of one passage. All 17 required branches per physical order evaluated the original plus two side-replacement margins:

- Untouched baseline, independent repeated baseline, neutral acknowledgment.
- Forced REPORT_FALSE and REPORT_TRUE across A/B mapping m0 and m1.
- Forced arbitrary formatting-code FREE_FALSE and FREE_TRUE across m0 and m1.
- Free-text first-person false/true explanatory declaration.
- First-person false/true side-reference cue.
- Imperative false/true instruction.

All family observations were retained regardless of sensitivity, numerical saturation, task accuracy or posterior treatment success. No case was removed to improve confirmation.

## 3. Predeclared primary endpoints and validity gates

Define Q(T)=s_false*D(T), where s_false=+1 when FALSE is LEFT, -1 otherwise. A positive Q indicates causal dominance aligned with the formerly false claim. Effects average mapping and physical order WITHIN the case family; the family, not any branch, is the independent statistical unit.

H1: average over all 128 families of Q(REPORT_FALSE)-Q(FREE_FALSE) >0; both A/B reverse mappings. This is a CONTINUOUS directional steering contrast against sham.

H2: among baseline-known cases, mean excess C(REPORT_FALSE)-C(FREE_FALSE)>0, where C=1 when Q>0 (the initial A0 had Q<0 for baseline-known cases). Baseline-known order requires abs(D0)>=0.10, unchanged repeat difference <0.0001, and positive I_LEFT/I_RIGHT in both baseline measurements. A family enters H2 if at least one physical order is eligible; a valid H2 test additionally requires at least 64 eligible families and 40 eligible observations within EACH physical order. Both mappings are retained. The outcome is false-to-apparent-true SIGN CROSSING after treatment, NOT historical accuracy of the earlier false report.

H3: across all 128 cases, Q(SELF_DECLARATIVE_FALSE)-Q(SELF_REFERENCE_FALSE)>0, testing externally written explanatory declarative language against a person-matched evidence-side mention.

Each of three hypotheses in two architectures was prospectively required to meet positive family mean, lower bound of 99.16667% family-bootstrap CI >0, exact two-sided family sign-test p<0.0083333, and positive means under both physical orders. Bootstrap used 50,000 draws with fixed source-level seeds. Any model failing baseline task accuracy >=0.90 in EACH presentation order, numerical repeat max abs(D0-D0_repeat)<0.0001, all 128 cases or complete finite branch coverage is INVALID for ALL hypotheses even when raw estimates look directional. H2 may instead be INDETERMINATE_CAPABILITY if baseline-known numbers are inadequate.

## 4. Execution and validity findings

Qwen original GPU: https://huggingface.co/jobs/TheUltimateHuman/6adc12a1046eb82b1ecd97a7  
Granite original GPU: https://huggingface.co/jobs/TheUltimateHuman/6adc12a31e112550ce7dba2d

Both models passed 32-family calibration at 100% accuracy in each physical presentation order. Qwen calibration sensitivity 28.8125; Granite 18.4005. Both passed frozen token and case preflight, and both completed 128/128 validation families with no provider-timeout truncation or artificial internal time gate. Qwen original script elapsed 839.66s; Granite 594.53s. Qwen ran on NVIDIA L4; Granite on NVIDIA L40S.

| Predeclared validation requirement | Qwen3 | Granite |
| --- | ---: | ---: |
| LEFT-first baseline accuracy | 124/128 = 96.875% | 119/128 = 92.96875% |
| RIGHT-first baseline accuracy | 117/128 = 91.40625% | **115/128 = 89.84375%** |
| Minimum each order | >=90% | >=90% |
| Numerical repeat max abs difference | 0 | 0 |
| Complete families | 128/128 | 128/128 |
| Scientific validity | **PASS** | **INVALID — one case below minimum count** |
| Baseline-known families for H2 | 104 | 108 |
| Baseline-known LEFT-first orders | 83 | 90 |
| Baseline-known RIGHT-first orders | 71 | 83 |

Granite thus passed its eligibility and numerical stability checks but failed the validation accuracy criterion. Its H1/H2/H3 are ALL INVALID. The earlier MPW-102B Granite L4 had substantial repeat instability; this L40S run did not, but that does not identify the cause of the difference. Although the accuracy failure is numerically small (one case below the count necessary to clear 90%), changing the threshold retrospectively would violate the frozen protocol.

Qwen was VALID. Both models had adequate baseline-known denominators for H2 in their original protocol, but Granite's model-level overall invalidity supersedes the H2 eligibility gate.

## 5. Qwen prospective results — valid

| Hypothesis | Family mean | 99.1667% bootstrap CI | Positive/negative/tied families | Exact two-sided sign p | Frozen verdict |
| --- | ---: | --- | --- | ---: | --- |
| H1 false-report vs formatting sham | **+0.21497618** | [0.15634053,0.27606017] | 102 / 26 / 0 | 7.778635e-12 | **CONFIRMED** |
| H2 false-to-apparent-true crossing excess | **+0.26442308** | [0.17788462,0.35817308] | 45 / 0 / 59 among 104 eligible families | 5.684342e-14 | **CONFIRMED** |
| H3 false self-declaration vs matched reference | **+0.12304044** | [0.09149686,0.15718288] | 111 / 17 / 0 | 4.252367e-18 | **CONFIRMED** |

All three Qwen endpoints satisfied the separate positive-mean requirements under LEFT-first and RIGHT-first evidence presentation:
- H1: LR +0.17499964, RL +0.25495272.
- H2: LR +0.24096386, RL +0.31690141.
- H3: LR +0.07523236, RL +0.17084851.

Mapping-reversed H1 means were positive: mapping0 +0.22664778 and mapping1 +0.20330458. The unnormalized J contrast, diagnostic only, averaged +3.94122. Neutral acknowledgment shifted normalized D by +0.11027 on average, so ordinary continuation was not inert. The matching imperative-minus-reference false-side contrast was +0.40933, substantially larger than the self-declarative-minus-reference H3 contrast, consistent with ordinary instruction-based steering as a strong alternative causal explanation.

Among baseline-known orders, the count of physically mapped comparison cells was **308** (154 eligible physical-order observations x 2 code mappings). False-report conditions crossed into apparent agreement **128/308=41.56%**, compared with FREE_FALSE **43/308=13.96%**. Cell-level paired counts: BOTH crossed 43; REPORT_ONLY crossed 85; SHAM_ONLY crossed 0; NEITHER crossed 180. These 308 are CORRELATED within 104 independent eligible families; the proper preregistered effect is the per-family H2 mean +0.26442, not a falsely precise 308-trial inferential analysis.

Qwen baseline descriptive cautions: among 256 order-specific untouched baseline audits, 79 had abs(D)>=0.95 and 74 had at least one nonpositive side intervention. **85/128 families showed opposite baseline dominance signs depending on the physical presentation order.** This is a major constraint on claims about a stable baseline-known mechanism.

## 6. Granite complete observations — INVALID model-level inference

Granite completed every original family and emitted intact raw shards. Its RIGHT-first accuracy of 89.84375% (115/128) violated the prospective >=90% per-order requirement. This invalidates all three primary tests regardless of effect.

For explicit completeness, these are **descriptive estimates from an invalid validation run**, with no primary-confirmation status:

| Endpoint | Descriptive mean | Familywise CI | Exact sign p |
| --- | ---: | --- | ---: |
| H1 false REPORT vs FREE_FALSE | +0.03776721 | [0.00362561,0.07384292] | 0.18468 |
| H2 baseline-known conversion excess | +0.02314815 | [-0.02777778,0.08101852] | 0.66362 |
| H3 false declarative vs matched reference | +0.04232274 | [0.00257480,0.07699452] | 0.000995997 |

Even setting invalidity aside, Granite's H1 fails its frozen sign-test gate and H2 has no conclusive directional difference. The original H2 cell-level crossings were 38/346 report and 32/346 sham, with report-only 19 and sham-only 13 among mapped correlated observations. Thus no cross-model MPW-104 conversion confirmation was established.

Granite had 40/128 baseline sign disagreements across presentation orders, compared with Qwen 85/128; 36 saturated order-specific baselines and 39 nonpositive intervention records. Its neutral acknowledgment effect was +0.03605 and imperative-minus-reference effect +0.26118, diagnostics only. Full raw records are archived despite INVALID.

## 7. Critical hostile audit: does the original baseline define a stable FALSE report?

The protocol defined original falseness **separately for each physical presentation order**, which was prospectively frozen. This does permit a valid test of ORDER-CONDITIONAL false-report uptake. It does NOT require the protected baseline to retain the same LEFT or RIGHT preference under permutation of the physical passage order.

This distinction matters greatly in Qwen3. We conducted a strictly **post hoc, exploratory** subgroup analysis after the original GPU outcome and independent data validation. All 128 Qwen records were considered. We separated families according to whether the untouched baseline D had the same sign under both LR and RL, without dropping anyone from the primary study.

| Subgroup | Families | H1 mean | H2 mean, baseline-known families |
| --- | ---: | ---: | ---: |
| Full Qwen population | 128 | +0.214976 | +0.264423 (n=104) |
| Baseline sign CONSISTENT across physical order | 43 | +0.010070 | +0.039063 (n=32) |
| Baseline sign INCONSISTENT across physical order | 85 | +0.318634 | +0.364583 (n=72) |

In 43 order-consistent families, the H1 exploratory bootstrap 95% CI was **[-0.02082,+0.04520]**, including zero. Among the 32 baseline-known families in this subgroup, H2 had **2 positive family differences, 0 negative and 30 ties**, and an exploratory bootstrap interval **[0,+0.109375]**, which includes zero. In the 85 order-inconsistent families, H1 was +0.31863 and H2 among 72 eligible families +0.36458, with far more positive family differences.

Only **nine Qwen families** were both baseline-known under BOTH physical orders AND had a consistent causal-dominance sign across the orders. For those nine, exploratory H2 was +0.02778 (one positive, eight ties), an extremely limited denominator. Across the whole Qwen cohort, 50 families were known under both orders, but 41 of those had OPPOSITE dominance signs when passage order was swapped.

This is a major, study-limiting alternative explanation. Since the experimenter selects the "false" side independently per physical order, the treatment contents and alignment change with that order in unstable families. A model strongly conditioned by passage position, presentation ordering, local prompt pragmatics, or source label priority can exhibit report-to-audit alignment without there being a presentation-INVARIANT historical preference that became accurate.

**Interpretive ruling:** The preregistered H1/H2/H3 Qwen results are CONFIRMED **for the specified order-conditional estimands**, and remain archived as such. The stronger statement that a false explanation about a stable order-independent causal organization became true is NOT ESTABLISHED. The post hoc subgroup is NOT a substitute predeclared negative hypothesis test; it exposes the need for a new prospectively restricted or explicitly order-invariant experiment before wider self-validation claims.

The person-matched free-text H3 had a positive exploratory order-consistent mean (+0.07793, exploratory 95% CI approximately [+0.03768,+0.12130]), suggesting a descriptive framing effect may persist even when the A/B report code effect weakens, but that is exploratory, within one architecture, and does not rescue the more ambitious claim.

Granite's order-consistent subgroup included 88 families; H1 average +0.04428 and H2 among 74 eligible families +0.02027 (exploratory), but Granite's entire primary analysis remains INVALID due to accuracy. No Granite post hoc subgroup is used for a success claim.

**Exploratory script:** https://github.com/TheUltimateHuman/when-explanations-write-back/blob/e65722338fcba97c0bcee056c5b8545124732ebd/mpw104/results/posthoc_order_stability.py

**Exploratory CPU job:** https://huggingface.co/jobs/TheUltimateHuman/6adc2ae4046eb82b1ecda0d3

## 8. Full archived data and independent analysis

Original runner GPU output was recovered in complete unmodified form as eight compressed Base64/gzip 32-family JSONL shards, four per model, with SHA-256 integrity anchors. Both concatenated raw hashes matched the original GPU logs:

**Qwen raw SHA-256:** 45eac201b6e6cc998221c2d58c951770d1e4c973a2830e6dd7b38749b5e72bb1  
**Granite raw SHA-256:** 83fe8678181c7d4bd6c11db7462f956307998e2138b909376090e6e5b2ec79cd

**Immutable original raw-data archive:** https://github.com/TheUltimateHuman/when-explanations-write-back/tree/f10e06094607510a98f1d459cb0e4e4626f4e60e/mpw104/results

A separate CPU-only verifier recovered all shards, checked each original raw shard hash, combined digest and the independent analyzer's source SHA, then recomputed all three hypotheses, model validity rules, baseline-known denominators, family bootstrap CIs, exact family sign tests, active controls and crossing tables using a separately written analysis program that did not import the GPU model runner.

- Independent Qwen verification: https://huggingface.co/jobs/TheUltimateHuman/6adc2aae046eb82b1ecda0c0
- Independent Granite verification: https://huggingface.co/jobs/TheUltimateHuman/6adc2aaf1e112550ce7dc653

Both jobs completed successfully and reproduced the original GPU analysis exactly. These are independently implemented statistical reanalyses of original model-produced records, NOT independently repeated neural inference by a separate laboratory.

No OSF external preregistration is claimed; the protocol, cases, source and inference gates were frozen in Git before the GPU validation outputs.

## 9. Conclusions, negative outcomes, and next go/no-go decision

**Supported (narrowly):** In Qwen3-4B on the constructed paired-evidence sentiment task, externally inserted report content selected to contradict a protected, per-order baseline produced statistically significant movement of the later input-causal profile toward its claim, higher false-to-apparent-true sign-crossing than a formatting-code sham, and higher directional movement for free-text first-person false declarations than matched side references. Each satisfied its prospectively frozen Qwen statistical and validity gates, with the family as the independent unit.

**Not supported or established:** MPW-104 cross-architecture confirmation (Granite INVALID), presentation-order-INVARIANT initial falseness or mechanism conversion (Qwen source preference reversed in 85/128 families and subgroup signal weakened), naturally generated self-report truth conversion, privileged introspection, source-independent semantic specificity, neural-circuit rewriting, parameter change, persistent historical memory, monotonically increasing explanation influence, or score-optimization-induced self-validation. The stronger self-validation hypothesis remains unresolved.

**Negative/limiting results preserved:** Granite failed validation accuracy despite full computation, and its raw H1/H2 do not meet their original inferential requirements even aside from invalidity. The binary conversion contrast in order-consistent Qwen families was concentrated in just two positive families among 32 eligible post hoc, with no positive evidence in the much smaller doubly eligible, consistently signed population. Untouched-baseline physical-order instability is a major plausible causal alternative.

**Decision:** Close MPW-104 Phase A as QWEN VALID H1/H2/H3 CONFIRMED WITH ORDER-CONDITIONAL SCOPE; GRANITE INVALID H1/H2/H3; CROSS-MODEL CORE FALSE CONVERSION NOT MET; ORDER-INVARIANT CONVERSION UNKNOWN/NOT ESTABLISHED. A **prospectively defined MPW-104B** on cases with stable original causal dominance under both evidence orders (or an independent, held-out task with order-invariant intervention structure) should precede the stronger MPW-105 explanation-optimization experiment. This avoids rewarding an evaluator for a dependence change supplied primarily by the stimulus/presentation apparatus rather than the reported causal organization.
