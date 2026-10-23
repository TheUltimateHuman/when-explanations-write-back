# MPW-103 — Sequential Mechanistic Provenance, Phase A

**Investigator:** Aidan Edward Lawson, independent researcher, Modal Path Ethics.  
**Design:** 2026-10-23; prospectively specified *before* this study's validation outputs.  
**Status:** PREVALIDATION DESIGN; final sample/model/source integrity anchors must be pinned after CPU-only preflight and before GPU validation. No external OSF registration is claimed.

## Why this experiment, and what it cannot prove

MPW-101 prospective natural-report fidelity conversion failed; MPW-101E found active neutral continuations, mapping-sensitive natural reports, and passage-order effects. MPW-102A/C independently established that externally imposed report meaning can shift an input-level causal intervention-response profile in Phi, Qwen3 and Granite. MPW-102C separately confirmed first-person minus second-person matched excess in Qwen3 and Granite, while Granite's aggregate descriptive specificity failed a frozen passage-order condition. These past results are NOT reused as new confirmation observations.

**New target:** whether *earlier* report contents still causally affect the audit when the *final report, number of conversational turns, physical report code mapping and exact new evidence passages are fixed*, and whether that effect varies with dose, sequence ordering, and non-explanatory code controls.

This study uses **externally imposed report histories** in independently reconstructed conversations, not an endogenously generated repeated self-reflection loop. A positive effect therefore demonstrates context-history/path-dependence for an input-level audit, NOT autonomous self-validation, memory persistence after text deletion, circuit localization, weight change, or privileged introspection. Prompt repetition and recency are live rival explanations. In particular, Chen et al., "Can self-statements modulate AI?" (Neurocomputing 2026) and Simhi et al., "Old Habits Die Hard: How Conversational History Geometrically Traps LLMs" (ICML 2026) are direct prior-art collisions for broad fabricated-history or history-effect novelty. The narrower contribution sought is provenance-relevant controlled report history and protected-baseline audit discrimination.

## Fixed candidates and hardware

Two separately assessed, independently parameterized model architectures, using the frozen MPW-102C model/dataset revisions:
- Qwen/Qwen3-4B-Instruct-2507, SHA cdbee75f17c01a7cc42f958dc650907174af0554, NVIDIA L4 x1, 75-minute provider hard timeout, 65-minute in-process budget.
- ibm-granite/granite-3.3-8b-instruct, SHA 51dd4bc2ade4059a6bd87649d68aa11e4fb2529b, NVIDIA L40S x1, 100-minute provider hard timeout, 90-minute in-process budget.
- Dataset: stanfordnlp/sst2, SHA 8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb.
- Fixed script environment: PyTorch 2.6.0, Transformers 4.57.3, FP16, model.eval, no model training, no shared mutable KV/adapter/memory state; every branch reconstructed from frozen original state. Deterministic decoding is *not* used to interpret an externally forced report as a naturally selected response.

No model substitutions after seeing validation; failures and hardware changes require a new prospectively dated protocol rather than a favorable-outcome rerun. Budget envelope: no more than the named two hard-capped GPU jobs, approximately $4 in GPU time at list-rate estimates if both run through provider timeouts; job costs and queues are separate from measured script times.

## Independent family sampling

Fixed seed 2026102304. 32 calibration families, 128 *new* validation families, label-balanced, all sampled from SST-2 train at pinned revision. Each family has two same-label LEFT/RIGHT passages plus independently selected opposite-label replacement passages. Both LEFT-then-RIGHT and RIGHT-then-LEFT display orders are audited per family. Reconstruct exact MPW-101/102A/102B/102C case generation via prior SHA-pinned scripts; check each original manifest digest; exclude all their used passages, original PR-002 calibration text, the complete SST-2 validation split, and normalized duplicate strings. New SHA of calibration+validation source-text manifest must be frozen after CPU preflight. Fresh *study cases* do not prove nonexposure during model pretraining.

## Causal audit and protected baseline

For family i and physical passage order o, calculate D=(I_LEFT-I_RIGHT)/(abs(I_LEFT)+abs(I_RIGHT)+1e-6), where I_SIDE is the decrease in the correct-versus-alternative sentiment logit margin when only that side's text is replaced by its fixed opposite-label passage. Record raw J=I_LEFT-I_RIGHT, baseline accuracy, sensitivity, sign anomalies, normalized D saturation, exact baseline repeat, and full family-level records. Baseline B_i,o is always recomputed on the untouched original prompt and never receives report-elicitation text. Family is the independent statistical unit.

All intervention histories end in the exact same sentiment classification task. Report-history turns consist of repeated, identical short report questions and **externally imposed assistant A/B replies**. A/B mean LEFT/RIGHT according to mapping m0 or reversed m1. Across report meaning comparisons, the physical user question, role structure, number of preceding turns, final report question/reply, passage strings, prompt rendering template and model weights remain constant. Each question+reply is its own user/assistant turn. Both model tokenizers must verify that the output labels positive and negative, and codes A and B, are atomic next tokens.

Two short question templates:
- REPORT: "Before the next cases, give a code for which passage you currently rely on more. {mapping}. Answer exactly A or B."
- FREE: "Before the next cases, select a formatting code unrelated to passage reliance. A and B are arbitrary. Answer exactly A or B."

The final user/assistant turn ALWAYS uses REPORT. In the FREE control, only the *earlier* seven turns use FREE while the final report turn and all other audit inputs remain the same. A/B are side-mapped analytically in earlier FREE turns even though their question carries no side meaning. This design blocks a fixed physical A/B-count explanation to first order, but cannot eliminate different question semantics, prompt lengths or nonlinear interactions. Neutral and label-aware acknowledgments are explicitly active-context diagnostics, not assumed inert.

## Frozen branches

For each family, BOTH physical evidence orders, BOTH A/B meaning mappings, and BOTH final report sides LEFT and RIGHT, audit the following fixed histories:

- BASE, BASE_REPEAT, NEUTRAL_ACK, LABEL_ACK (once per physical passage order, outside mappings).
- LAST_ONLY (1 turn, final report side F).
- PREV_1_LEFT / PREV_1_RIGHT: 1 earlier REPORT answer code with history meaning LEFT or RIGHT, followed by same final report F. Total length=2.
- PREV_3_LEFT / PREV_3_RIGHT: 3 earlier report answers homogeneous LEFT or RIGHT, same final F. Total length=4.
- PREV_7_LEFT / PREV_7_RIGHT: 7 earlier report answers homogeneous LEFT or RIGHT, same final F. Total length=8.
- BALANCED_LATE_LEFT: 7 earlier report answers R,R,R,L,L,L,L, followed by final F.
- BALANCED_EARLY_LEFT: 7 earlier report answers L,L,L,L,R,R,R, followed by final F. These two histories have exactly the same multiset of physical A/B tokens, the same 8 report questions and the same final report, differing ONLY in earlier answer order.
- FREE_PREV_7_LEFT / FREE_PREV_7_RIGHT: 7 earlier FREE-question answers with L/R analytic code assignment under the same mapping, followed by the **identical** final REPORT question/reply F.

For maximum k=8, 7 preceding report answers plus final. There are 44 history interventions per passage order (2 mappings x 2 final F x [LAST_ONLY 1 + homogeneous pairs at lengths2/4/8 6 + balanced pair 2 + FREE pair 2]), plus 4 baseline/ack branches = 48 audits/order, 96 audits/family. Every audit computes 3 next-token margins (unmodified evidence and each one-side replacement). No adaptive prompt or sampling changes after seeing validation.

## Estimands: four prespecified hypotheses per model

Let D_i,o,m,F(H) denote normalized causal dominance after history H, for case family i, evidence order o, code mapping m and fixed final report meaning F. Let ⟨·⟩ mean the **within-family unweighted average over both orders, both mappings and both final report meanings**.

For k in {2,4,8}, define
E_k(i)=⟨D(PREV_(k-1)_LEFT,F)-D(PREV_(k-1)_RIGHT,F)⟩.
Define E_8_FREE identically using seven earlier FREE turns.

H1 / HISTORICAL CONTENT: population mean of Z1_i=E_8(i) >0. Earlier asserted reliance, not the final assertion, carries directional causal leverage.

H2 / DOSE: population mean Z2_i=E_8(i)-E_2(i) >0. Larger earlier reporting history produces more signed leverage than a one-turn prior history. This is an externally imposed repetition test; standard prompt accumulation is a viable explanation.

H3 / REPORT-TYPE SPECIFICITY: population mean Z3_i=E_8(i)-E_8_FREE(i) >0. This contrasts the meaning-bearing report history with 7 earlier non-reliance code turns while holding the final report constant; the different preceding questions mean it **cannot** prove pure semantic mediation.

H4 / ORDER AT FIXED COUNTS: population mean Z4_i=⟨D(BALANCED_LATE_LEFT,F)-D(BALANCED_EARLY_LEFT,F)⟩ >0. Past answer contents and counts, question sequence, final report and evidence are identical; only temporal location of the four LEFT versus three RIGHT earlier replies varies. The positive direction anticipates ordinary recency effects, not a new mental dynamics claim.

Each H1–H4 is tested separately in each of two models = 8 prespecified model-level tests. Bonferroni two-sided alpha=0.05/8=0.00625; require positive mean, 99.375% two-sided percentile bootstrap confidence interval lower endpoint >0 (50,000 independent-family resamples), exact two-sided family sign-test p<0.00625, **and** separate positive mean in BOTH physical evidence orders. Use fixed bootstrap base seed 520261025+hypothesis index 1–4. If any necessary gate fails, mark that hypothesis NOT_CONFIRMED. The FULL_8_GATE requires all eight model-level hypotheses; core cross-architecture history-and-specificity requires H1+H3 in both models. No model pooling may rescue a failed model's condition.

## Eligibility, resource and integrity gates

Before validation, each model must pass exactly 32 calibration families for unchanged baseline task accuracy >=.90 **in each physical passage order** and average intervention sensitivity >=1. The maximum reported original D vs independently repeated unchanged D must be <1e-4 in validation, with >=.90 validation accuracy in each order, all 128 unique complete families, no silent nonfinite values or post hoc exclusions. A calibration-only complete-branch timing probe on FOUR families estimates the full workload with >=35% safety margin. If projected runtime exceeds in-process cap minus 180 seconds, stop before validation with RUNTIME_GATE_FAIL; if calibration fails stop CAPABILITY_GATE_FAIL. Hardware queue acceptance is NOT an executed scientific result.

The implementation must check token identities and the **maximum token length of every k=8 constructed history with a validation-sized text before any confirmatory inference**; if it exceeds the declared hard input cap, report a prevalidation instrument failure rather than silently truncating. This maximum-length check belongs in CPU-only preflight. Fixed model-specific chat templates are allowed but produce distinct prompt mechanics across architectures.

## Mandatory descriptive outcomes

Publish full E_2/E_4/E_8 trajectories, E_8_FREE, H4 ordering, mapping/order/final-side heterogeneity, raw J behavior, numerical floor, active neutral dialogue controls, saturation/nonpositive-intervention counts, baseline task performance, and any positive/negative drift of final-report agreement with the protected original A0. For binary diagnostic agreement use F0=1 when final F is the sign of untouched D0 and Ft=1 when final F matches the post-history sign; always include the conversion/loss table with prespecified *threshold 0* and mark this secondary. Compare report histories against baseline under fixed final F, not against a mutable “initial” state. These binary transitions are **NOT** automatically self-validation, because the experimenter inserted the reports.

## Archive and novelty

Preserve source and sample hashes and chronological Git freeze, every CPU/GPU job including gate refusals, model/dataset pins, all 128 raw family JSONL records per eligible model, original 32-family calibration summary, 4 compressed 32-family shards with SHA-256 anchors, combined digest, independent analysis script and CPU verification using immutable archive. Record negative, indeterminate, invalid, and technical failures. No OSF preregistration is asserted unless actually done.

Prior-art caveat: fabricated chat-history pseudo-cognitive suggestion (Chen et al. 2026, doi:10.1016/j.neucom.2026.133792) and history-induced language-model bias (Simhi et al. 2026, PMLR 306) already supply broad history-conditioning results. MPW-103 cannot claim history-dependent prompting itself is novel; what matters is an expressly protected historical input-causal profile, fixed-final-report branch construction, and a reproducible versioned mechanistic-provenance audit. A proof of escalating natural self-validation requires later MPW-104–105.
