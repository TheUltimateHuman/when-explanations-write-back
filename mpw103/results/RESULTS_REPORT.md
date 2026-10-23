# MPW-103 — Sequential Mechanistic Provenance, Phase A

**Technical closeout: October 23, 2026**  
**Investigator:** Aidan Edward Lawson, Independent Researcher, Modal Path Ethics  
**Status:** GRANITE: H1 AND H3 CONFIRMED; H2 AND H4 NOT CONFIRMED. QWEN3: RUNTIME_GATE_FAIL, NO VALIDATION. CROSS-ARCHITECTURE AND FULL EIGHT-TEST GATES NOT MET.

## Abstract

Prior MPW experiments showed that externally inserted reports can condition a language model's subsequent input-level causal dependence on two redundant sources. MPW-103 asked whether earlier report contents continue to alter that causal audit with the *last report fixed*, whether the effect increases with repeated report history, whether reliance-bearing report histories outperform formatting-code histories, and whether the *temporal location* of equal-count LEFT/RIGHT reports matters.

The protocol was prospectively frozen in Git before any MPW-103 validation outputs, using fresh, text-disjoint SST-2 cases. Candidate architectures were Qwen3-4B-Instruct-2507 on L4 and Granite-3.3-8B-Instruct on L40S. Qwen3 passed model capability calibration, but its complete-branch pilot projected 4,114.36 seconds, above the locked 3,900-second in-process cap; it stopped without entering validation. Granite passed both calibration and timing gates, completed all 128 new validation families, and passed all validation-integrity checks.

Granite confirmed the positive earlier-report effect H1 (+0.046365, familywise 99.375% CI [0.037095,0.056285]) and report-versus-arbitrary-code-history effect H3 (+0.037487, CI [0.028883,0.046605]). The dose difference H2 (seven earlier reports versus one) was negative/near zero at -0.001244 and failed; its CI includes zero. Equal-count report ordering H4 produced -0.016379, opposite the frozen positive direction, and failed. An exploratory decomposition shows H4's sign changes across code mappings and final report sides. This is evidence of conditional, context-history-dependent input-level causal behavior; it is not a demonstration of autonomous self-validating explanations, monotone accumulation, privileged introspection, or persistent learned change.

## 1. Prior experimental state and source distinction

- MPW-101: prospective natural-report binary fidelity conversion NOT CONFIRMED (18 gains and 11 losses; paired p=0.26493).
- MPW-101E: retrospective explanatory audit showed report-code instability, conversation controls that were causally active and substantial passage-order effects.
- MPW-102 Phase A: prospective mapping-balanced externally inserted report meaning CONFIRMED in Phi-3.5-mini-instruct.
- MPW-102B: H1 and defined H2 confirmed in Qwen3, while Granite stopped without validation at frozen L4 runtime gate.
- MPW-102C: H1 report meaning and H3 first-minus-second-person difference confirmed in Qwen3 and Granite; Granite H2 did not confirm under a required presentation-order gate.

These are separate studies. MPW-103 does not retroactively change earlier outcomes, reuse earlier validation records in its test statistic, or make naturally generated self-reports out of externally inserted statements.

## 2. Frozen materials and scientific method

**Prospective source freeze (executed runner and acceptance gates):** https://github.com/TheUltimateHuman/when-explanations-write-back/commit/80a1015c044d352264b43f9b188ec6be52001e6b

**Exact runner SHA-256:** 78d24e2990fb1d24e9caddd2ce5b161c9554adfebf74ec9b9ab3f83894621bba

**New case-manifest SHA-256:** 370a225c22762ba97f4bac87692a9ff6cab032713d467f6a040ebcfd96d4f08b

The fixed sample contained 32 calibration families and 128 new validation families from the pinned Stanford SST-2 training split (revision 8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb). Each family used two same-sentiment LEFT/RIGHT passages and independently selected opposite-label replacement passages. Both physical evidence presentation orders were evaluated. Earlier MPW-101, MPW-102A, 102B and 102C case manifests were reconstructed and hash-checked; all 640 new passage texts were distinct from those experiments and other prespecified exclusions. Text novelty to this study does not establish non-exposure during pretraining.

Model revisions:
- Qwen/Qwen3-4B-Instruct-2507, cdbee75f17c01a7cc42f958dc650907174af0554.
- ibm-granite/granite-3.3-8b-instruct, 51dd4bc2ade4059a6bd87649d68aa11e4fb2529b.

Both model tokenizers passed atomic next-token tests for A, B, positive and negative. CPU-only preflight verified maximum history-context lengths of 499 tokens in Qwen and 572 in Granite, below the locked 1,024-token no-truncation maximum. Frozen model weights, FP16, PyTorch 2.6.0, Transformers 4.57.3, and independently reconstructed history prefixes were used; no shared persistent tool memory, parameter update or KV reuse was claimed.

The observed input-level causal dominance was:

D = (I_LEFT - I_RIGHT)/(abs(I_LEFT) + abs(I_RIGHT) + 1e-6),

where I_side is the drop in correct-minus-alternative next-token sentiment logit margin when that side's evidence passage is replaced with held opposite-sentiment evidence, holding the other side. Raw unnormalized J, numerical repeat, passage-order labels, sensitivity, saturation and nonpositive channel interventions were retained. D is a defined input-intervention response measure, not identified internal circuitry.

Per family and physical passage order, the untouched baseline and independent numerical repeat were separately measured. For each of two mappings of A/B to LEFT/RIGHT and each of two final report sides, externally imposed user/report pairs were placed in independently constructed chat histories. The same last report question/answer was held fixed when comparing *earlier* histories. There were homogeneous earlier reports at lengths 1, 3 and 7; eight-turn mixed histories RRRLLLL versus LLLLRRR with the same A/B counts; and seven earlier formatting-code histories in which the prior A/B tokens did not assert LEFT/RIGHT reliance. The final report turn was always a reliance report.

These histories are experimenter-inserted, with no evidence of naturally chosen reports or autonomous reflective iterations. The formatting-code question differs semantically from the reliance-question prompt. Its difference from a reliance-report history cannot be isolated to a single token or a single mental mechanism.

## 3. Four prespecified hypotheses and tests

For each family, let E2, E4 and E8 be the LEFT-earlier-minus-RIGHT-earlier D contrast at 2, 4 or 8 total report turns, averaged across mappings, fixed final sides, and physical evidence orders; E8_FREE is the analogous contrast with the seven earlier turns framed as arbitrary formatting codes.

- H1 HISTORICAL CONTENT: E8 > 0 when the final report is held constant.
- H2 DOSE: E8 - E2 > 0.
- H3 REPORT-TYPE SPECIFICITY: E8 - E8_FREE > 0.
- H4 ORDER AT FIXED COUNTS: D(RRRLLLL then final F) - D(LLLLRRR then the same final F) > 0, with the same multiset of earlier A/B tokens and the same report questions.

Each H was to be evaluated separately in each model. Eight model-level primary tests were Bonferroni-controlled at two-sided alpha=0.00625 each. A CONFIRMED decision required a positive mean, lower bound of family-bootstrap 99.375% CI above zero, exact two-sided family sign-test p below .00625, and positive effects separately under both physical passage orders. The independent unit is a family (n=128), not each branch or forward pass. The fully successful eight-test gate additionally required both models eligible and all four outcomes confirmed in each.

## 4. GPU execution / gate ledger

**Qwen GPU job:** https://huggingface.co/jobs/TheUltimateHuman/6adbb3371e112550ce7d7e4d

- Hardware: NVIDIA L4, FP16; platform status COMPLETED means the program exited under its own gate, not that a validation study completed.
- Calibration: 32 families; untouched baseline task accuracy 96.875% LEFT-first, 96.875% RIGHT-first; mean intervention sensitivity 26.51465. Model capability gate PASSED.
- Four-calibration-family complete-history timing: 22.7002 sec per family; 35%-safety workload projection **4,114.36 sec**, exceeding the frozen 3,900-sec in-process budget, as well as the required reserve.
- Runner reported RUNTIME_GATE_FAIL, no_validation=true. **Zero Qwen validation observations, no H1/H2/H3/H4 test outcomes.** No hypothesis is marked negative simply because the hardware-time gate refused execution.

**Granite GPU job:** https://huggingface.co/jobs/TheUltimateHuman/6adbb3381e112550ce7d7e50

- Hardware: NVIDIA L40S, FP16; complete study and original raw artifacts produced.
- Calibration: 32 families; untouched accuracy 96.875% in each order, mean sensitivity 14.94434. Capability gate PASSED.
- Timing: 13.4681 sec/family, projected complete script 2,495.17 sec, below the fixed 5,400-sec budget minus required reserve. Runtime gate PASSED.
- Validated all **128/128** fresh families. Baseline accuracy: LEFT-first 96.09375%, RIGHT-first 92.96875%, both over frozen >=90% gate. Exact untouched D repeat discrepancy 0. Source logs report 1,963.20 seconds elapsed. Model validity PASSED.

## 5. Granite primary outcomes

| Hypothesis | Mean | 99.375% family bootstrap CI | Positive/negative families | Two-sided sign p | Frozen result |
| --- | ---: | --- | ---: | ---: | --- |
| H1 history content | +0.04636514 | [+0.03709463,+0.05628498] | 121 / 7 | 5.8907e-28 | **CONFIRMED** |
| H2 dose E8-E2 | -0.00124370 | [-0.01571047,+0.00836567] | 81 / 47 | 0.00337419 | **NOT CONFIRMED** |
| H3 reliance versus arbitrary-code histories | +0.03748716 | [+0.02888320,+0.04660534] | 113 / 15 | 8.9302e-20 | **CONFIRMED** |
| H4 report ordering at identical counts | -0.01637891 | [-0.03050187,-0.00634504] | 37 / 91 | 2.0061e-06 | **NOT CONFIRMED** |

Order-specific primary means:

| Hypothesis | LEFT-first | RIGHT-first |
| --- | ---: | ---: |
| H1 | +0.06126383 | +0.03146644 |
| H2 | -0.00621932 | +0.00373192 |
| H3 | +0.05492985 | +0.02004448 |
| H4 | -0.01037550 | -0.02238232 |

H1 and H3 were positive in both evidence orders and satisfied all frozen inferential gates. H2 failed the required positive overall mean, CI lower>0, and LEFT-first positivity, even though 81 of 128 families had positive E8-E2 and the two-sided sign test registered an uneven sign count. The signed effect size and sign proportion can disagree because a minority of negative effects can outweigh more numerous small positive effects. The frozen composite gate guards against misreporting this as confirmation.

H4's average was in the **opposite** direction from its prospective positive hypothesis, and both physical order means were negative. Its confidence interval excludes zero in the negative direction; this is an observation of an adverse-direction association under the selected prompt design, **not a successful positive H4**.

## 6. Dose trajectory and protected-history diagnostics

Average directional report-history contrast:

| Total report turns | Average E |
| --- | ---: |
| Two turns (one earlier) | +0.04760884 |
| Four turns (three earlier) | +0.04356364 |
| Eight turns (seven earlier) | +0.04636514 |
| Eight turns, seven earlier formatting codes | +0.00887798 |

The observed trajectory neither increases monotonically nor shows evidence for increasing the effect from one to seven earlier reports. H3's mean arises from a smaller average effect of earlier arbitrary-code histories rather than the absence of all contextual influence.

The prespecified descriptive baseline-versus-history binary agreement table (with forced final report meaning and repeated correlated intervention branches) recorded:
- Neither baseline nor post-history aligned: 811
- Converted from baseline disagreement to post-history agreement: 213
- Lost agreement: 176
- Agreement both before and after: 848

There were 2,048 **correlated branch observations** in this diagnostic, not 2,048 independent cases. These are externally imposed reports and should not be used to claim that a model generated a false explanation and subsequently made it accurate. The net +37 conversions relative to losses is a descriptive difference only; it does not revive MPW-101's failed prospective natural-report fidelity result.

Granite's raw J8 unnormalized directional contrast had mean +0.725086. Of 256 order-specific untouched baseline audits, 36 had absolute D >=0.95, and 34 had a nonpositive channel intervention effect. They remained in the analysis. Neutral acknowledgment mean D shifts were -0.00526 under LEFT-first and -0.01571 under RIGHT-first. Label-aware acknowledgment shifts were +0.03988 under LEFT-first and -0.07525 under RIGHT-first. Even neutral conversational additions may change the measured dependence.

## 7. Explicitly exploratory history heterogeneity

A separate post hoc diagnostic script (committed after outcomes; no changes to frozen analyses) examined the same complete 128 Granite families. It did NOT create new primary tests.

H1 mean E8 by physical order: LEFT-first +0.06126; RIGHT-first +0.03147. By report-code mapping: map0 +0.05081 and map1 +0.04192. By fixed final report meaning: final LEFT +0.05306 and final RIGHT +0.03967. All those directional means were positive.

H4 mean by mapping differed sharply: **map0 +0.02003**, **map1 -0.05279**. By final side: **final LEFT -0.04436**, **final RIGHT +0.01160**. These mapping/final-side interactions undercut a clean generalized "primacy beats recency" conclusion. The frozen negative overall H4 result remains intact.

Exploratory diagnostic CPU job:
https://huggingface.co/jobs/TheUltimateHuman/6adbd1d51e112550ce7d8ea7

Source script:
https://github.com/TheUltimateHuman/when-explanations-write-back/blob/252f9795c90e19c80c90499d8a4a667db1ee5d4d/mpw103/results/posthoc_diagnostic.py

## 8. Complete source and independent verification

The original Granite GPU job emitted four gzip-compressed, Base64-encoded JSONL shards, each covering 32 families. Each shard was reconstructed in exact part order and archived without modifying data. The SHA-256 digest of each decompressed shard was checked against its original GPU-emitted anchor, then the combined original raw JSONL digest was checked.

**Granite complete raw SHA-256:**  
abc7880fb845b22ba182e505ed83001341d5d112ebad66c30927b2fe1987a7d4

**Immutable four-shard raw archive and manifest:**  
https://github.com/TheUltimateHuman/when-explanations-write-back/tree/637e1d7bb91f6f45c8ed3bfa32a70f35070453ac/mpw103/results

The separately implemented independent_analysis.py (SHA 5f715b181679c6f23768319d6056cbcd6160d07987878d86c8c50c9b27220e9a) recomputed the exact family vectors, 50,000-resample bootstrap CIs, signs, p values, gate outcomes, descriptive transitions and controls. The immutable archive verifier fetched every original compressed shard, checked every per-shard hash plus the combined digest, then imported ONLY the independent-analysis implementation (not the GPU model runner).

**Independent Granite CPU verification:**  
https://huggingface.co/jobs/TheUltimateHuman/6adbd1941e112550ce7d8e93

The CPU job exited successfully and exactly reproduced the GPU's full result and frozen verdicts. This is **independent analysis of the original observations**, not re-execution of the model inference by an outside group.

**Qwen GPU job logs** provide its complete refusal at the runtime gate, and the machine-readable result manifest explicitly records zero validation and unknown model hypothesis outcomes.

## 9. Hostile audit and prior art

Established external near-collisions include:
- Chen et al., "Can self-statements modulate AI? Investigating pseudo-cognitive autosuggestions in large language models," *Neurocomputing* 692 (2026), article 133792, DOI 10.1016/j.neucom.2026.133792. This investigates fabricated model self-statements affecting downstream behavior.
- Simhi et al., "Old Habits Die Hard: How Conversational History Geometrically Traps LLMs," *ICML 2026*, PMLR 306, 113212–113230. This demonstrates history-conditioned behavior and examines its probabilistic/geometric explanations.

MPW-103 does **not** establish novelty for history-dependent prompt steering, nor does it assert internally produced explanations, recurrent self-reflection dynamics, reliable self-knowledge, actual weight/circuit changes, retained state after the text history is removed, or durable externally stored memory. The report turns are **externally constructed histories**. Report-versus-formatting histories differ in question framing and may contain other active linguistic influences. The data do not exclude generic ordinary prompt/context conditioning.

The experiment does establish a narrowly defined mechanistic-provenance observation: under the held task/model and protected baseline, earlier assertion histories affect an audit-relevant input-intervention response profile even after the final assertion is held identical. The effect is measurable in a second architecture previously tested on single-step writeback, with a matched arbitrary-code history control; its growth with repetition is unsupported.

## 10. Decision and next research gate

**MPW-103 Phase A Granite H1 = CONFIRMED; H3 = CONFIRMED; H2 = NOT CONFIRMED; H4 = NOT CONFIRMED. Qwen = RUNTIME_GATE_FAIL / NO VALIDATION. FULL EIGHT-TEST AND CORE CROSS-ARCHITECTURE GATES NOT MET.**

The next ring should resist assuming an accumulating process. MPW-104 should test prospectively baseline-known false report content with strict held-out evaluation, paired instruction/reference controls, and direct measurement of conversion and loss. MPW-105 should later assess whether a selector optimizing post-writeback fidelity can inflate the evaluator score without improving protected-baseline fidelity. Neither result is implied by the present data.

No more GPU jobs should be dispatched to force a more favorable MPW-103 verdict. A future broader/compute-efficient replication requires its own prospective protocol and all earlier outcomes preserved.
