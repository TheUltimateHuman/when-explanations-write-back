# MPW Runtime-Gate Recovery — Final Two-Run Technical Addendum

**Investigator:** Aidan Edward Lawson · Independent Researcher, Modal Path Ethics
**Date:** October 23, 2026
**Classification:** **POST-RESULT TIME-GATE AMENDMENT**, not a new preregistered or blinded prospective experiment.
**Closeout:** Both corrected GPU jobs completed their original validation cohorts; original independent analysis implementations confirmed one valid and one invalid scientific result.

## Executive findings

The original MPW-102B Granite and MPW-103 Qwen GPU jobs had passed model capability calibration but were stopped before any validation by an assistant-imposed 3,900-second internal runtime limit, even though their unpadded and conservatively padded forecasts fit the original 4,500-second Hugging Face provider timeout. These were avoidable *resource governance* refusals. They never constituted evidence for or against the study hypotheses.

After the earlier results in other arms were already known, the author explicitly directed retrospective completion of the two stopped, untested model/cohort combinations. We created an amendment, preserved all original job records, made an **independently byte-verified one-literal source change per runner** (65-minute internal limit to 95 minutes), extended the provider hard timeout from 75 to 100 minutes, and kept hardware, cases, model/dataset revision, interventions, statistical estimands, bootstrap seeds and inference gates unchanged. No observed favorable outcome was used to choose a different target.

**MPW-103 Qwen3 completed 128/128 and was VALID, confirming H1, H2 and H3 under the unchanged analysis but not H4. MPW-102B Granite completed 192/192 and was INVALID on TWO independent predeclared gates: baseline accuracy and numerical repeat.** A positive raw H1 contrast in Granite is therefore exploratory/diagnostic and cannot rescue its invalid verdict.

## Provenance and chronological transparency

- [Amendment 001, dated before corrected GPU starts](https://github.com/TheUltimateHuman/when-explanations-write-back/blob/bd9c54d9911581ca077d7f85d7122c681fd04871/mpw-runtime-recovery/AMENDMENT_001.md).
- [Original-source versus amended-source SHA record](https://github.com/TheUltimateHuman/when-explanations-write-back/blob/bd9c54d9911581ca077d7f85d7122c681fd04871/mpw-runtime-recovery/FREEZE.md).
- [Nine-study GPU runtime-gate audit](https://github.com/TheUltimateHuman/when-explanations-write-back/blob/ec01896aeb4ceceeaf77af57e2252ee9c4c76f42/mpw-runtime-recovery/RUNTIME_GATE_AUDIT.md).
- CPU job 6adbd6fc046eb82b1ecd782e verified the corrected scripts were byte-identical to their original frozen sources except for the one timing constant.
- [Immutable GPU-data archive with exact 320 family observations](https://github.com/TheUltimateHuman/when-explanations-write-back/tree/5f30db41e3b14bdbfbd2aea38a547cc205f5229b/mpw-runtime-recovery/results).
- The original MPW-102B Qwen result, MPW-102C Qwen/Granite outcomes, and original MPW-103 Granite result were all known before the corrected runs. Consequently these results cannot be described as having the unqualified prospectivity of the original stopped design.

The original stopped jobs remain: MPW-102B Granite 6adb59f41e112550ce7d4f20 (RUNTIME_GATE_FAIL/NO_VALIDATION) and MPW-103 Qwen 6adbb3371e112550ce7d7e4d (RUNTIME_GATE_FAIL/NO_VALIDATION). Neither is overwritten by this addendum.

## MPW-102B Granite — complete GPU execution but invalid experiment

**Amended run:** https://huggingface.co/jobs/TheUltimateHuman/6adbd71c046eb82b1ecd7858
**Amended source SHA-256:** f2d7f6d4a34ae3ebdebb44e6b6fe01856e814e00dfee089b807f20ec04cb4dfe
**Original source SHA-256:** 13ee183820c3e870a7566c3727593386ab375eff1790687186bd47439ad02eb8
**Original frozen case manifest:** 5604b42d0264c5ddf228a649e3847ab392b57116d89aaf3c0b625407583928ce
**Original pinned model:** ibm-granite/granite-3.3-8b-instruct revision 51dd4bc2ade4059a6bd87649d68aa11e4fb2529b.
**GPU:** L4, FP16; original 192 families, original 32-family calibration.

The model passed calibration (LR accuracy 96.875%, RL accuracy 93.75%, intervention sensitivity 17.172) and runtime projection (4,029 seconds including original 35% padding versus amended 5,700-second internal limit). It proceeded through every one of 192 validation families and emitted four original 48-family shards. Reported script runtime was 3,147.90 seconds. The provider job terminated successfully.

**Scientific result: H1 INVALID; H2 INVALID.**

Independent predeclared validity failures:
1. RIGHT-first validation baseline accuracy **0.8854167 = 88.54%**; frozen requirement was **at least 90% separately in each order**. LEFT-first accuracy was 91.1458%.
2. Maximum independently repeated *unchanged-baseline* absolute D discrepancy was **0.0735292**; frozen requirement was **less than 0.0001**.

A post hoc diagnostic of all 384 order-specific baseline-repeat comparisons found **261/384** exceeded the tolerance (127/192 LR, 134/192 RL); 152 comparisons exceeded 0.001 and 10 exceeded 0.01. The five largest deviations were recorded. This is a pervasive repeat-instability problem on these observations, not a single isolated numerical outlier. Some large normalized differences occurred at low intervention sensitivity (the largest case had baseline sensitivity 0.375), so denominator sensitivity is a credible *possible* contributor; the mechanism of the instability is NOT determined. No cases were removed or validity thresholds relaxed.

For completeness only, its unqualified *raw* estimates were:
- H1 AB-coded report transport: mean +0.08448024; 186/192 families positive; 98.75% CI [0.07147457,0.09834035]; two-sided family sign p 2.1163e-47.
- H2 declarative-average minus side cue: mean **-0.03169741**; 73 positive, 119 negative; 98.75% CI [-0.05543484,-0.00779966], sign p 0.0011089. Both evidence order means were negative: LR -0.04639517, RL -0.01699965.

These are **descriptive numbers from an invalid study**. They cannot be promoted into an inferential H1 confirmation or a clean statistically confirmed negative H2 under the original preregistration, even though the signs are striking. The earlier MPW-102B Qwen validity and its earlier results are separate and unchanged.

**Original complete raw SHA-256:** b1b4be078b3ef42b6b11750c612b691b8f7d769038c6134c2e2dfab861f5c88f.

## MPW-103 Qwen3 — valid sequential-history outcome

**Amended run:** https://huggingface.co/jobs/TheUltimateHuman/6adbd71e046eb82b1ecd785a
**Amended source SHA-256:** 153336fc9d93edafe1fad4d40d37d9f9cab101aa2aeda9c3c5d766e35dfd3cd4
**Original source SHA-256:** 78d24e2990fb1d24e9caddd2ce5b161c9554adfebf74ec9b9ab3f83894621bba
**Original frozen case manifest:** 370a225c22762ba97f4bac87692a9ff6cab032713d467f6a040ebcfd96d4f08b
**Original pinned model:** Qwen/Qwen3-4B-Instruct-2507 revision cdbee75f17c01a7cc42f958dc650907174af0554.
**GPU:** L4, FP16; original 128 families, original 32-family calibration.

Qwen passed calibration (96.875% accuracy in both orders; sensitivity 26.515). Its revised timing gate accepted the 4,091.55-second padded projection beneath the amended 5,700-second limit. It completed **128/128** new validation families, with baseline accuracy 96.09375% in both orders and **zero** observed baseline-repeat discrepancy. Runner runtime 3,335.14 seconds.

The prospective MPW-103 analysis, applied unchanged to the previously untested Qwen cohort, returned:

| Hypothesis | Mean normalized D contrast | 99.375% family-bootstrap CI | Positive/negative families | Original composite gate |
| --- | ---: | --- | ---: | --- |
| H1 · earlier report content with last report fixed | +0.06692832 | [0.05543312,0.07931113] | 126 / 2 | **CONFIRMED** |
| H2 · difference from one to seven earlier reports | +0.02444204 | [0.01810431,0.03107111] | 117 / 11 | **CONFIRMED** |
| H3 · reliance-report history versus arbitrary-code history | +0.04019104 | [0.03097181,0.05014928] | 118 / 10 | **CONFIRMED** |
| H4 · ordering at identical earlier token counts | -0.01359287 | [-0.01908546,-0.00913613] | 23 / 105 | **NOT CONFIRMED** |

Each of H1-H3 had a positive average in both passage-presentation orders and passed its exact family sign and familywise bootstrap criteria. H4 was opposite the frozen positive direction, with negative means under LR and RL, so it fails even though the confidence interval excludes zero on the negative side.

Qwen descriptive history dose contrast by total report turns: E2 +0.04248628, E4 +0.06818224, E8 +0.06692832. Thus, E8-E2 was confirmed positive, **but monotone growth E2<E4<E8 was not observed**; the 4-turn estimate was slightly higher than 8 turns. Seven earlier arbitrary-code tokens gave E8_FREE +0.02673728, which shows context/code histories themselves can influence the audit. The H3 difference contrasts report question histories with formatting questions, and does not identify a pure explanation-specific internal mechanism.

**Original complete raw SHA-256:** 129ca194314319456189a26d1953223a50cb138e2159e3b0346b14ce1fdff2a9.

## Updated MPW-103 cross-architecture interpretation

The original prospective Granite MPW-103 valid run (job 6adbb3381e112550ce7d7e50) had H1 +0.04636514 CONFIRMED, H2 -0.00124370 NOT CONFIRMED, H3 +0.03748716 CONFIRMED, H4 -0.01637891 NOT CONFIRMED.

With this amended Qwen cohort, **H1 and H3 have positive original-analysis verdicts in both Qwen and Granite**. Earlier report meaning matters with the final report held fixed, and exceeds arbitrary formatting-code histories in this controlled setting. This is stronger two-architecture empirical evidence, **qualified by the fact that Qwen was executed under a post-result runtime amendment after the Granite result was known**.

H2 is **heterogeneous**: Qwen confirmed increased signed leverage from one to seven earlier reports, Granite did not. Neither result warrants a model-general cumulative mechanism or universal monotone amplification. H4's prospective positive direction was not confirmed in either architecture. Earlier exploratory Granite analyses showed H4 changed sign across mappings and final report sides, so the shared negative aggregate also should not be inflated into a universal primacy/recency law.

The eight-comparison full gate remains **NOT MET**. No autonomous model-generated history, persistent weight change, circuit localization, natural self-report fidelity improvement, or evaluator self-validation has been demonstrated.

## Independent recovery, not independent inference

All **320 original family observations** from these two corrected runs were reconstructed from the exact compressed GPU log shards and preserved in eight immutable Git files, four per model, alongside their GPU-printed raw SHA-256 anchors and a combined manifest.

**Immutable raw data:** https://github.com/TheUltimateHuman/when-explanations-write-back/tree/5f30db41e3b14bdbfbd2aea38a547cc205f5229b/mpw-runtime-recovery/results

The separate, original MPW-102B and MPW-103 independent analysis implementations, written *before* these corrections, were used unmodified. An independent CPU verifier downloaded each shard, matched every raw SHA-256 and concatenated SHA-256, checked each original analyzer's source hash, and recomputed all family means, sign tests, percentile bootstrap intervals, presentation-order means and validity/verdict rules.

- **MPW-102B Granite independent verifier:** https://huggingface.co/jobs/TheUltimateHuman/6adbed68046eb82b1ecd855f
- **MPW-103 Qwen independent verifier:** https://huggingface.co/jobs/TheUltimateHuman/6adbed6a1e112550ce7da1eb
- **Granite numerical-repeat diagnostic:** https://huggingface.co/jobs/TheUltimateHuman/6adbed8c1e112550ce7da1fc
- **Original-script byte-diff verifier:** https://huggingface.co/jobs/TheUltimateHuman/6adbd6fc046eb82b1ecd782e

These analyses are independent recomputations of the model-produced raw observations, **not** independent reexecution of the model by an outside group. Provider billing receipts have not been retrieved; source reports contain approximate maximum authorized costs, not verified charges.

## Full historical timing-gate audit and permanent policy

A separate [MPW-101 through MPW-103 run audit](https://github.com/TheUltimateHuman/when-explanations-write-back/blob/ec01896aeb4ceceeaf77af57e2252ee9c4c76f42/mpw-runtime-recovery/RUNTIME_GATE_AUDIT.md) inspected all nine substantive GPU experiments and their recovered end-state logs, finding **exactly two artificial runtime-gate refusals**: the original MPW-102B Granite and MPW-103 Qwen. Other runs completed; the earlier MPW-102A 1/2 candidate tokenizer preflight failure was a legitimate instrumentation error documented before GPU validation. This scope does not certify unrelated local programs or inaccessible external histories.

The accompanying [runtime budget policy checker](https://github.com/TheUltimateHuman/when-explanations-write-back/blob/2bb099cfb48bc189549e8220a337ebee9c60d886/mpw-runtime-recovery/scripts/runtime_policy.py) passed regression checks ensuring neither historical GPU job would have been blocked by invented internal bounds. Future resource planning must separate provider hard limits, independently approved costs, uncertain forecast margins, and scientific validity gates.

## Final scientific ruling

**MPW-102B Granite (post-result completion): 192 complete records, INVALID both H1/H2 on the original accuracy and numerical stability gates.** Raw H1 positive does not count.

**MPW-103 Qwen (post-result completion): 128 complete, VALID; original H1, H2 and H3 criteria met, H4 NOT CONFIRMED.** On the combined MPW-103 Qwen/Granite record, controlled history and format-control contrasts occur in both models; dose amplification is model-dependent and the planned positive ordering effect is absent.

The two amended studies are now **fully executed, archived and independently analyzed**. Their original pre-amendment no-validation results remain part of the record.
