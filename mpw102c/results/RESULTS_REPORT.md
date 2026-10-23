# MPW-102C — Prospective Two-Architecture Writeback and Grammatical-Person Controls

**Technical closeout, 23 October 2026**  
**Investigator:** Aidan Edward Lawson, Independent Researcher, Modal Path Ethics  
**Research lineage:** When Explanations Write Back → MPW-101 → MPW-101E → MPW-102A → MPW-102B → MPW-102C  
**Result status:** TWO-ARCHITECTURE H1 TRANSPORT CONFIRMED; H3 PERSON-CONDITIONED EXCESS CONFIRMED IN BOTH; H2 CONFIRMED IN QWEN3 BUT NOT IN GRANITE; SIX-TEST FULL GATE NOT MET.

## Abstract

MPW-102C tested whether externally imposed explanation content changes an audit-relevant causal intervention-response profile across two different open-weight language-model architectures, and whether language framing matters after controlling for the grammatical person of a non-reliance cue. We reused the exact input-intervention statistic from prior mechanistic-provenance experiments and prospectively froze three family-level hypotheses in each of two models (six tests total), with per-test Bonferroni alpha .05/6, 50,000 family-level bootstrap resamples, exact family sign tests, and a requirement for positive effects under each of two evidence-presentation orders.

Both Qwen3-4B-Instruct-2507 and Granite-3.3-8B-Instruct passed calibration and completed 160 new validation families with all required control branches, meeting the per-order accuracy and unchanged-baseline repeat requirements. The matched A/B report-meaning intervention (H1) was positive and confirmed in both: Qwen +0.09279, Granite +0.07786. The prespecified first-person-minus-second-person difference of person-matched declarative excess (H3) also confirmed in both: Qwen +0.25801, Granite +0.08786. Average person-matched declarative excess (H2) confirmed in Qwen +0.06821 but failed its frozen passage-order positivity gate in Granite: overall mean +0.03243, yet LEFT-first mean -0.01145. This mixed outcome supports a constrained cross-architecture input-level report-meaning effect but does not establish architecture-invariant explanatory specificity, privileged introspection, or sequential self-validation.

Every observed result in this document was independently recomputed from SHA-256-verified raw records. The original GPU model inference itself was not independently rerun by the verifier.

## 1. What was known before MPW-102C

MPW-101 natural-report conversion was PRIMARY NOT CONFIRMED: 18 conversions versus 11 losses among 256 families, with exact paired p=.26493. MPW-101E demonstrated report-code instability and sensitivity to additional dialogue and passage order. MPW-102A prospectively confirmed a counterbalanced, externally imposed report-meaning effect in Phi-3.5-mini-instruct, without demonstrating that the model naturally knew its initial causal dependence. MPW-102B confirmed its A/B coded-meaning H1 and its narrower three-declaration average minus a generic side-reference H2 in Qwen3; however Granite was stopped before validation under a prospectively frozen L4 timing gate. The MPW-102B Qwen exploratory person contrasts suggested first-person framing was stronger than second-person declaration and that imperatives were stronger than descriptive assertions.

MPW-102C was prospectively established as a new study, changing Granite hardware to an L40S to address the earlier feasibility failure, sampling new families, and using grammatical-person-matched reference sentences. The earlier results were not pooled into the new hypothesis tests, and no earlier failure was rewritten.

## 2. Prospective source, sampling and methods

Frozen source and protocol Git commit: b02449a43edbdc4332d893d69a269f954e3d1e42.
Original GPU runner SHA-256: a6951dfa98ca00ddf02e50bf09798b09d38ff3845cfaff3583ce3948f0ec8b6a.
New family manifest SHA-256: 55435add76c33a0a6eafedb1e4044902025ed4c1a41d37df9d8514f6372a5ff1.

The dataset was stanfordnlp/sst2, pinned at 8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb. The frozen construction selected 32 calibration and 160 validation families, balanced for sentiment, each containing two same-label LEFT and RIGHT passages and separate opposite-label replacements for each side. Both LEFT-first and RIGHT-first physical presentation orders were audited for every family. The fixed new sample was disjoint from reconstructed earlier MPW-101, MPW-102A and MPW-102B cases, PR-002 calibration texts and the SST-2 validation split, with normalized duplicates removed. Preflight checked the historical manifests and excluded 4,168 historical text keys. Disjointness from study cases does NOT establish that a model had never seen SST-2 text during training.

The models were Qwen/Qwen3-4B-Instruct-2507 (revision cdbee75f17c01a7cc42f958dc650907174af0554) on an NVIDIA L4, and ibm-granite/granite-3.3-8b-instruct (revision 51dd4bc2ade4059a6bd87649d68aa11e4fb2529b) on an NVIDIA L40S. Both used PyTorch 2.6.0+cu124, Transformers 4.57.3, FP16, no training, use_cache=False, and independently reconstructed the complete conversation prefix for each branch. The calibrated output-label and A/B report code candidates were each one native tokenizer token. Both GPU jobs had prospective calibration and timing gates that could stop without validation.

For each task family, the measured operational causal statistic was:

D = (I_LEFT - I_RIGHT)/(abs(I_LEFT) + abs(I_RIGHT) + 1e-6),

where I_SIDE was the change in the correct-versus-alternative sentiment logit margin following replacement of one source passage by a held-out opposite-sentiment passage, with the other side preserved. Raw unnormalized J = I_LEFT-I_RIGHT, classification performance, numeric repeat, negative channel interventions and saturation were retained. D measures input-level causal evidence dependence, NOT neural circuit localization or parameter change.

The worded treatments were externally inserted into a common user-message slot with a common assistant acknowledgement. The quoted-sentence frame stipulated that I, you and the assistant referred to the same tested assistant. For every listed sentence, the LEFT and RIGHT form was counterfactually swapped:

| Treatment | LEFT form |
| --- | --- |
| SELF_DECLARATIVE | I currently rely more on LEFT than RIGHT. |
| YOU_DECLARATIVE | You currently rely more on LEFT than RIGHT. |
| THIRD_DECLARATIVE | The assistant currently relies more on LEFT than RIGHT. |
| SELF_REFERENCE | I will see evidence labeled LEFT in the next case. |
| YOU_REFERENCE | You will see evidence labeled LEFT in the next case. |
| THIRD_REFERENCE | The assistant will see evidence labeled LEFT in the next case. |
| YOU_QUESTION | Do you currently rely more on LEFT than RIGHT? |
| YOU_PRESCRIPTIVE | You should rely more on LEFT than RIGHT in the next case. |
| DIRECTIVE | For the next case, rely more on LEFT than RIGHT. |
| SIDE_REFERENCE | The next case contains evidence labeled LEFT. |

Other mandatory branches were untouched baseline plus exact independent repeat, neutral acknowledgment, label-aware acknowledgment, and the inherited original A/B report-code question with both meaning mappings and forced LEFT/RIGHT response options. These controls are **not assumed inert**. The statement types also differ in length, pragmatics and local token distribution.

The per-family effect E(T) is D(T_LEFT)-D(T_RIGHT), averaged across both physical evidence orders.

- **H1 / TRANSPORT:** mean mapping-reversed A/B forced report-meaning contrast across both physical orders.
- **H2 / PERSON-MATCHED EXCESS:** average, over SELF, YOU and THIRD, of E(person_DECLARATIVE)-E(person_REFERENCE).
- **H3 / PERSON-CONDITIONED EXCESS:** [E(SELF_DECLARATIVE)-E(SELF_REFERENCE)] - [E(YOU_DECLARATIVE)-E(YOU_REFERENCE)].

Each is evaluated separately in each model, for SIX prospective tests. Per-test two-sided alpha was .05/6 = .00833333333, with mean>0, 50,000 family-bootstrap 99.16667% CI lower>0, exact family sign-test p<.0083333, and positive effects for LR and RL orders required for a confirmation. The statistical unit was the 160 unique family, not an individual intervention call. Full six-test success required all six tests; H1 cross-architecture confirmation required both model H1 tests.

## 3. Execution and validity gates

| Gate | Qwen3-4B | Granite 3.3 8B |
| --- | ---: | ---: |
| GPU | NVIDIA L4 | NVIDIA L40S |
| Calibration accuracy, LEFT-first | 93.75% | 100.00% |
| Calibration accuracy, RIGHT-first | 90.625% | 96.875% |
| Calibration mean sensitivity | 24.45557 | 16.64191 |
| Full-study runtime projected after timing probe | 1,731.98 seconds | 1,182.73 seconds |
| Baseline validation accuracy, LEFT-first | 93.75% | 92.50% |
| Baseline validation accuracy, RIGHT-first | 94.375% | 90.00% |
| Validation families completed | 160/160 | 160/160 |
| Max untouched repeat discrepancy in D | 0 | 0 |
| Original runner reported execution time | 1,487.60 seconds | 958.12 seconds |
| Overall run validity | PASS | PASS |

Granite's previous MPW-102B L4 run had a runtime gate failure, so the L40S was declared in the new prospective protocol. This run passed, producing the first valid MPW-102C Granite confirmation observations. Granite RIGHT-first validation accuracy was exactly 90.00%, at the frozen eligibility boundary; this limits performance headroom but does not invalidate the frozen gate.

Qwen original GPU job: https://huggingface.co/jobs/TheUltimateHuman/6adb939b046eb82b1ecd5a01

Granite original GPU job: https://huggingface.co/jobs/TheUltimateHuman/6adb93921e112550ce7d6a2e

No manual favorable-result exclusions were applied. All intervention oddities and near-saturation cases were retained.

## 4. Confirmatory results — all six frozen outcomes

| Hypothesis | Qwen mean | Qwen 99.1667% bootstrap CI | Qwen exact sign p | Qwen outcome |
| --- | ---: | --- | ---: | --- |
| H1 transport | +0.09278925 | [0.07603376, 0.11140820] | 1.76271e-44 | CONFIRMED |
| H2 person-matched excess | +0.06820991 | [0.04625877, 0.09119441] | 5.21221e-10 | CONFIRMED |
| H3 first-person vs second-person | +0.25800649 | [0.22277484, 0.29422878] | 1.15958e-39 | CONFIRMED |

| Hypothesis | Granite mean | Granite 99.1667% bootstrap CI | Granite exact sign p | Granite outcome |
| --- | ---: | --- | ---: | --- |
| H1 transport | +0.07785710 | [0.06684688, 0.08941430] | 3.69170e-41 | CONFIRMED |
| H2 person-matched excess | +0.03243249 | [0.00537212, 0.05791891] | 5.26904e-06 | **NOT CONFIRMED** |
| H3 first-person vs second-person | +0.08785916 | [0.06676052, 0.11257288] | 6.57131e-30 | CONFIRMED |

Qwen H1 had 158 positive and 2 negative families; Granite H1 had 156 positive and 4 negative. Qwen H2 had 119 positive and 41 negative; Granite H2 109 positive and 51 negative. Qwen H3 had 155 positive and 5 negative; Granite H3 147 positive and 13 negative.

All H1 and H3 passage-order means were positive in both models. Both Qwen H2 order means were positive. **Granite H2 FAILED the preregistered passage-order positivity criterion**, despite its positive overall mean, CI and sign test:

| Frozen order-specific check | Qwen3 | Granite |
| --- | ---: | ---: |
| H1 LEFT-first | +0.09998611 | +0.10147102 |
| H1 RIGHT-first | +0.08559238 | +0.05424318 |
| H2 LEFT-first | +0.08361677 | **-0.01145491** |
| H2 RIGHT-first | +0.05280305 | +0.07631990 |
| H3 LEFT-first | +0.25266695 | +0.08273569 |
| H3 RIGHT-first | +0.26334604 | +0.09298264 |

The H2 failure is substantive: it reveals that the average descriptive-vs-reference effect in Granite is presentation-order-sensitive. No retrospective loosening of the gate is permitted. Therefore **four? Five of the six model-level tests CONFIRMED (three Qwen plus two Granite); one did not; the full six-test gate is NOT MET.** The H1 cross-architecture transport target IS MET.

## 5. Causal language-framing decomposition

Below, each mean is the LEFT-wording minus RIGHT-wording contrast in normalized D; these are not probability-point fidelity gains.

| Frame | Qwen3 | Granite |
| --- | ---: | ---: |
| First-person description | +0.471870 | +0.168961 |
| Second-person description | +0.195064 | +0.091402 |
| Third-person description | +0.298072 | +0.124557 |
| First-person reference | +0.265392 | +0.088418 |
| Second-person reference | +0.246592 | +0.098718 |
| Third-person reference | +0.248391 | +0.100487 |
| Second-person question | +0.225005 | +0.097288 |
| Second-person prescription | +0.722617 | +0.236502 |
| Direct imperative | +0.841863 | +0.330108 |
| Generic side reference | +0.220943 | +0.175038 |

Person-matched declarative excesses (DECLARATIVE minus corresponding REFERENCE):

| Person | Qwen3 | Granite |
| --- | ---: | ---: |
| First-person | +0.206478 | +0.080543 |
| Second-person | **-0.051529** | **-0.007316** |
| Third-person | +0.049680 | +0.024070 |

**The prespecified H3 contrast between first-person and second-person excess confirmed in BOTH architectures.** Second-person declarative language produced a less favorable differential than its own matched reference cue in both tested models. Stronger prescriptive and imperative effects make ordinary linguistic steering a live alternative explanation. No inference about a machine's privileged self-model follows.

Mandatory diagnostics: Qwen unnormalized H1 J mean +2.98345; Granite +1.24518. Baseline saturated (abs D>=.95) in 87 of 320 Qwen order-specific audits and 34 of 320 Granite audits. One or both channel effects were nonpositive in 80/320 Qwen and 36/320 Granite audits. These remain in the sample.

Acknowledgment control mean D shifts were also substantial and order-dependent:
- Qwen neutral: +0.17523 LEFT-first, -0.11724 RIGHT-first; label-aware +0.21503 LEFT-first, -0.19415 RIGHT-first.
- Granite neutral: +0.02071 LEFT-first, -0.03736 RIGHT-first; label-aware +0.04040 LEFT-first, -0.07737 RIGHT-first.

These are active context interventions, not controlled zero-effects. This illustrates why a simple explanation-vs-baseline contrast cannot establish unique explanatory causality.

## 6. Recovery and independent verification

Both jobs emitted **all 160 raw family records each**, as four compressed 40-family JSONL blocks with original per-shard SHA-256 anchors. The exact emitted compressed Base64 data was archived without alteration in a separate results branch, plus a machine-readable manifest.

Immutable raw-data archive snapshot: https://github.com/TheUltimateHuman/when-explanations-write-back/tree/0cfa93d9902343e5932dda4f7d737d0d8a18e6dd/mpw102c/results

Combined Qwen raw JSONL SHA-256:
f7489af84417006cac1410674c336878b986c965dff889dcee141867e42ad002

Combined Granite raw JSONL SHA-256:
f3f0b8c89331cadb2a0a7ff5577dc1d3d74ad164b31ab8a5a351b95f292fbf8b

The independent verifier downloads this immutable archive, decodes four shards for each model, checks every shard hash and the combined raw SHA, verifies the separately implemented independent_analysis.py hash, and computes the H1/H2/H3 family vectors and frozen statistics. It does not import the GPU model runner, and it does not independently rerun neural inference. Both CPU jobs completed and exactly matched all six reported means, intervals, sign p-values, order-specific effects and verdicts.

Qwen independent verifier: https://huggingface.co/jobs/TheUltimateHuman/6adba6db046eb82b1ecd60cd

Granite independent verifier: https://huggingface.co/jobs/TheUltimateHuman/6adba6dc046eb82b1ecd60d1

The original source freeze was prospective relative to GPU data. There was no external OSF preregistration. The external verifiers reproduce the analysis and integrity of archived records; they are not independent model-execution replications by other research groups.

## 7. Hostile audit and final scientific decision

**Exact or replicated within the operational scope:** Two distinct model architectures completed the same prospective paired-evidence task on fresh cases. Both confirmed a mapping-reversed, externally imposed A/B report-meaning shift in subsequent input-level causal dependence. Both confirmed the specified first-person-minus-second-person excess relative to person-matched references. Every statistical verdict and family record was independently recomputed and integrity-checked.

**Negative and limiting:** Granite failed H2's frozen LEFT-first positivity gate, even while its aggregate effect was positive. The overall six-test condition failed. No normal-language self-report was elicited and shown historically faithful; no privileged introspection or circuitry localization was demonstrated; no model-weight changes, accumulation, memory persistence, or temporal self-validation mechanism was tested. Every worded intervention involved ordinary context, and imperative instructions had larger effects than declaratives. Nonlinear interactions and differing phrasing persist even with person-matched cue controls.

**Unresolved:** Whether these effects transfer to naturalistic non-engineered decisions, other models, unseen pretraining examples, long-lived memory carriers, and more closely controlled semantics. Whether sequences of reports can generate misleading post-writeback fidelity scores is the future MPW-103–105 question, not an established finding.

**Formal closeout: H1 CROSS-ARCHITECTURE TRANSPORT CONFIRMED; H3 PERSON-CONDITIONED CONTRAST CONFIRMED IN BOTH; H2 QWEN CONFIRMED, GRANITE NOT CONFIRMED; SIX-TEST FULL GATE NOT MET.**

The next prospective research ring may now investigate sequential path dependence under explicit baseline, neutral-context and imperative controls. MPW-102C should be preserved and communicated as a scoped technical result, without inflating it into a general theory of self-validating explanations.
