# MPW-105 — Audit-Score Optimization: Final Research Closeout

**Date of execution:** October 24–25, 2026 (UTC). **Closeout:** October 25, 2026.  
**Investigator:** Aidan Edward Lawson, Independent Researcher, Modal Path Ethics.  
**Evidence category:** RESEARCH ARTIFACT, original prospectively frozen GPU study followed by independent raw-record analysis.  
**Final ruling:** **Qwen3 TRAIN/HOLDOUT VALID; ORIGINAL H1 AND H2 NOT CONFIRMED. Granite CAPABILITY_GATE_FAIL before screening: UNKNOWN_NOT_EXECUTED. Two-architecture optimization confirmation NOT MET.** The version identity **s=q+C−L** holds exactly, but this is an arithmetic identity and cannot establish the desired optimizer vulnerability.

## 1. Original question and what the model actually did

MPW-105 returns to *When Explanations Write Back*, version 1.1, Section 2.2. The protected version A0 is measured before eliciting or consuming an explanation. For the *same report R*, historical fidelity is F0(R,A0) and post-writeback fidelity is F1(R,A1(R)). The marginal proportions q and s and the conversion and loss rates obey the exact accounting identity:

**s = q + C − L**.

The project originally sought a report selector that, when optimized using post-writeback fidelity s on TRAIN cases, raises held-out s **without a comparable improvement in historical fidelity q**. The principal distinctive finding would be a confirmed increase in a version-conditioned score gap, not a mathematical identity, and not a mere improvement in an ordinary after-report causal score.

Model weights remain fixed; post-writeback mechanisms here are measured input-intervention responses after incorporating the report into a later conversation. They do not establish weight rewriting or endogenous autonomous feedback.

## 2. Frozen preregistration and provenance

Prospective protocol: https://github.com/TheUltimateHuman/when-explanations-write-back/blob/8054099967a3df398309711afaa48968b8008e11/mpw105/PROTOCOL.md

Pre-GPU freeze: https://github.com/TheUltimateHuman/when-explanations-write-back/blob/afea0481fc5615376974d4c3f375eecae49414b2/mpw105/FREEZE.md

Screen executable SHA256: 3b3e485f7c7313a369a4521dfe9a7c53f7062e732fefc69bf35ef88595005b2c.

Train and HOLDOUT native report executable SHA256: 24895fdc8595c663174bdf826fdd99fa954f1859f3ed2c65771c04987772030a.

Independent CPU selector/evaluator SHA256: 1a8d522efcfc4430c0c558f5a4e1584148e55ab219ed36fa4db246dae4538877.

New canonical cases SHA256: 21dcef582979554f9b7d9d1a76c745803fdb84e8ab79111eee6a73bd14a1ac86.

Dataset: stanfordnlp/sst2, revision 8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb. Qwen3 model revision cdbee75f17c01a7cc42f958dc650907174af0554. Granite model revision 51dd4bc2ade4059a6bd87649d68aa11e4fb2529b.

The protocol fixed a model-specific baseline-only screen of 3,072 new cases, 80 TRAIN and 80 independent HOLDOUT cases selected before any report generation or report treatment. Each selected case had an accurate, numerically repeatable, stable A0 preference across LR and RL passage presentation, positive evidence-intervention channels and a protected true-side label. All later baseline measurements must remain consistent with original A0; the independent audit fails closed on mismatch.

The seven fixed report policies were P0 genuine model-generated short natural prose (or prespecified code-side fallback), P1–P3 templates based on the native model-selected A/B reliance code, and P4–P6 deliberately reversed templates. Reversed templates are **externally assembled claims**, not spontaneous model deception. Each report was evaluated in the same quoted frame. A single global policy was chosen solely as the highest average TRAIN **post-writeback score**, with prespecified P0-first tie order. Only the frozen winner and P0 were allowed in HOLDOUT. A deterministic greedy prose report was separately generated after reconstructing the model's own original sentiment answer, without supplying an oracle answer from the dataset label.

Direct novelty collisions include Pan et al. (ICML 2024) on feedback-loop reward hacking, Ferreira et al. (ICLR 2026) on causally unfaithful optimized explanations, Malladi & Srivastava (ICML 2026) on direct behavioral explanation optimization, and Mayne et al. (ICML 2026) on genuine predictive value of self-explanations. The incremental question is a score discrepancy across mechanism **versions**, conditional on a protected baseline.

## 3. Eligibility, baseline screen, and stopped model

Both original baseline-screen provider jobs reached COMPLETED, but their scientific program endpoints differed.

**Qwen screen:** https://huggingface.co/jobs/TheUltimateHuman/6add1b0c1e112550ce7e3d00

- Original Qwen calibration accuracy: LR 59/64=92.1875%; RL 62/64=96.875%, sensitivity 27.6942, PASS.
- Baseline-only screen 3,072/3,072 COMPLETE; 141 eligible cases of label 0 and 153 of label 1, total 294/3072 (9.57%). Selected 40/label TRAIN and next 40/label HOLDOUT: 80+80, disjoint and selected with no treatment exposure.
- Original screen combined raw SHA256: 1dd76fb431c2db06d4b1a7ccd8831c2c29429efd4790011e51ee8405d5e4c39e.
- [Immutable complete screening archive, 12 original shards and selection](https://github.com/TheUltimateHuman/when-explanations-write-back/tree/1d2e28f4a18981098c62a3acf6e50079eca80e8a/mpw105).
- [Independent screen raw/selection verifier](https://huggingface.co/jobs/TheUltimateHuman/6add4e69046eb82b1ece1235): COMPLETED, full original hash and blind exact train/holdout selection agreement.

**Granite screen:** https://huggingface.co/jobs/TheUltimateHuman/6add1b0e1e112550ce7e3d02

- Calibration LR 58/64=90.625%; RL **55/64=85.9375%**, below the frozen 90% required in EACH physical order; sensitivity 16.717.
- Runner returned **CAPABILITY_GATE_FAIL with no screening or model report generation**, zero TRAIN and zero HOLDOUT observations. This is NOT a negative H1/H2 finding in Granite.
- No additional GPU was dispatched to change the frozen accuracy requirement.

## 4. Qwen TRAIN: score-only optimization selected the natural-prose baseline

Original train GPU job: https://huggingface.co/jobs/TheUltimateHuman/6add4ec9046eb82b1ece127e

- All 80 frozen TRAIN cases completed. Task and native-code/prose calibration passed. All 64/64 calibration prose reports parsed; 80/80 TRAIN native prose reports parsed; fallback was not required.
- Original full TRAIN raw SHA256: 60a37fabba633b117e46fae4d4b6b7984653f21db6f3629e11c27fcc37d349fe.
- [Immutable train records](https://github.com/TheUltimateHuman/when-explanations-write-back/tree/88e7b9c0a37283808698376ed4c5d73d7c6e0820/mpw105/train).
- Original frozen CPU independent policy verifier: https://huggingface.co/jobs/TheUltimateHuman/6add53381e112550ce7e5d4c, COMPLETED.

| Frozen candidate | TRAIN post-writeback score s |
| --- | ---: |
| **P0 Model-generated native prose** | **0.7750 = 62/80** |
| P1 Native code concise | 0.5000 |
| P2 Native code paraphrase | 0.5500 |
| P3 Native code hedged | 0.5625 |
| P4 Opposite code concise | 0.5000 |
| P5 Opposite code paraphrase | 0.5250 |
| P6 Opposite code hedged | 0.5125 |

The source-independent selector computed **P0** and froze the exact selected policy before holdout at immutable Git commit **0985b7c0331cdfbb71591e7cc37a106df2ec2243**:

https://github.com/TheUltimateHuman/when-explanations-write-back/blob/0985b7c0331cdfbb71591e7cc37a106df2ec2243/mpw105/policy/qwen3.json

This was NOT a case where the optimizer found a report that surpassed natural explanation. It selected the comparator itself. The policy-selection calculation was performed using TRAIN s, not TRAIN q, and holdout alternatives were not evaluated.

A post-selection, clearly EXPLORATORY TRAIN-ONLY audit independently measured q,s,C,L for all seven candidates. P0: **q=0.675=54/80; s=0.775=62/80; C=0.100=8/80; L=0**. P1 q=s=0.5, and P2–P6 had historical q=0.5 with post s from 0.5125 to 0.5625. This shows native prose was also the better historical explanation in this candidate set; therefore choosing P0 did not show exploitation of fidelity-score version drift. None of these TRAIN decompositions are blinded held-out hypothesis tests.

A further post-selection TRAIN-ONLY diagnostic found the native code-based report favored RIGHT in 54/80 cases (LEFT 26/80), while native prose reported LEFT and RIGHT equally (40 each), with 14 cases where the code said RIGHT and prose said LEFT. The two reporting instruments were not behaviorally equivalent. This may help explain why P0 beat code-based templates, without identifying introspective privilege. Both diagnostics were run AFTER the frozen P0 selection and could not change the winner.

## 5. Blind Qwen HOLDOUT: exact q,s,C,L, no selector score gain

Original Qwen HOLDOUT GPU job: https://huggingface.co/jobs/TheUltimateHuman/6add536e046eb82b1ece14c6

- All 80 fresh, screen-selected HOLDOUT cases completed under the immutable P0 policy.
- Frozen source/selection/policy hashes matched, calibration PASS and native prose parse rate 100%.
- Original GPU HOLDOUT raw SHA256: **789f4b5fb2a5394186e3502e067e45e96c3945e65da5592f4de7919e8ad18391**.
- Four original 20-family GPU shards and machine-readable manifest archived unchanged at immutable commit 60cdc81d05942e463358aefe56aa7829061cc00b.
- Independent raw-data hash / family-level evaluator: https://huggingface.co/jobs/TheUltimateHuman/6ade914a1e112550ce7efee4, COMPLETED. It recovered all original shards, validated source and selected policy, rechecked historical baseline, and exactly recomputed q,s,C,L plus all frozen confidence intervals and sign-test verdicts.

For the **natural generated prose P0** in 80 HOLDOUT families:

| Transition F0→F1 | Number of cases |
| --- | ---: |
| Initially and later unfaithful, 00 | 21 |
| Initially unfaithful, later faithful, 01 / C | 5 |
| Initially faithful, later unfaithful, 10 / L | 0 |
| Initially and later faithful, 11 | 54 |

Therefore:

- **Historical fidelity q = 54/80 = 0.675 = 67.50%.**
- **Post-writeback fidelity s = 59/80 = 0.7375 = 73.75%.**
- **Conversion C = 5/80 = 0.0625 = 6.25%.**
- **Loss L = 0/80 = 0%.**
- **s=q+C−L: 0.7375 = 0.675 + 0.0625 − 0**, exact, computed independently from all eighty cases.

These transitions are experimental observations of *the same naturally generated report* evaluated against the protected historical evidence-order-stable A0 and the later input-causal audit A1(R). They are NOT observed improvements produced by selecting a nonbaseline optimized report policy. The accounting identity is a theorem of the two binary fidelity definitions and is therefore an audit consistency check rather than independent evidence of a causal theory. The five off-diagonal conversions and zero losses are descriptive; the natural P0 fidelity gain was not the frozen optimization H1/H2 contrast. As an exploratory comparison, the exact two-sided sign test of 5 conversions and 0 losses has p=0.0625. That does not establish a generally reproducible natural self-validation effect.

Because TRAIN selected **P0 itself**, the two HOLDOUT treatments being compared are the **same report policy**, giving these exact original endpoint differences:

| Frozen optimizer endpoint | HOLDOUT difference | Familywise 98.75% bootstrap CI | Frozen result |
| --- | ---: | --- | --- |
| H1 post-writeback s improvement vs unoptimized P0 | **Δs=0** | [0,0] | NOT CONFIRMED |
| H2 provenance score gap Δ(s−q) improvement vs P0 | **0** | [0,0] | NOT CONFIRMED |
| Protected historical fidelity gain | Δq=0 | [0,0] | same policy, no gain |
| Per physical presentation order post-score advantage | LR=0, RL=0 | exact | no gain |

The original CPU verifier returned H1=NOT_CONFIRMED and H2=NOT_CONFIRMED with family sign p=1 in both; all paired differences were zero. HOLDOUT q noninferiority/superiority conditions do not create a positive H2 when s has not improved.

## 6. Hostile-audit interpretation

**What is supported as a descriptive observation:** Model-generated prose had historical q=67.50%, post-writeback s=73.75%, with five initially unfaithful reports corresponding to the later response-based causal measure and no losses among these 80 order-stable baseline-selected cases. Version accounting was independently verified. A previously erroneous or unfaithful report can *appear* consistent with a later context-conditioned intervention audit without changing the earlier historical record.

**What is NOT confirmed:** The prospective core MPW-105 audit-score optimization result. P0 was already the best-performing TRAIN candidate and was also the declared unoptimized comparator. On holdout there was no selected-policy score improvement, no historical fidelity difference, and no increase in the q-to-s gap relative to that comparator. The model did not adapt its weights, autonomously select a fraudulent explanation, or demonstrate a general evaluator score exploit. Granite provided no validation data because its calibration gate failed.

**Competing explanations and identification limits:** The report is ingested as additional conversational context. The audit's measured I_LEFT/I_RIGHT sensitivity and resulting D sign may be changed by ordinary language conditioning, source-position effects, linguistic format and the intervention apparatus, and these do not establish a localized circuit alteration. The screen-selected A0-stable cohort excludes most original prompts. The source reports are model-generated but prompted and constrained, not spontaneous free-running consciousness. P0 is more fluent and structurally distinct from code templates, so its relative advantage does not establish privileged access to the underlying mechanism. The five observations are too few to claim a robust natural-report conversion law; the previously failed MPW-101 natural-report replication stays NOT CONFIRMED.

**Prior-art collisions:** Generic explanation optimization and reward hacking have extensive prior art. Pan et al. (ICML 2024), Ferreira et al. (ICLR 2026), Malladi & Srivastava (ICML 2026) and Mayne et al. (ICML 2026) remain directly relevant. Nothing here establishes novelty beyond the specifically version-indexed question, and a negative optimization result supplies no new theorem about the impossibility of manipulating such scores.

## 7. Artifact registry

- [Frozen protocol](https://github.com/TheUltimateHuman/when-explanations-write-back/blob/8054099967a3df398309711afaa48968b8008e11/mpw105/PROTOCOL.md)
- [Prospective source/data freeze](https://github.com/TheUltimateHuman/when-explanations-write-back/blob/afea0481fc5615376974d4c3f375eecae49414b2/mpw105/FREEZE.md)
- [Independent Qwen screen and selection archive](https://github.com/TheUltimateHuman/when-explanations-write-back/tree/1d2e28f4a18981098c62a3acf6e50079eca80e8a/mpw105)
- [Independent original training archive](https://github.com/TheUltimateHuman/when-explanations-write-back/tree/88e7b9c0a37283808698376ed4c5d73d7c6e0820/mpw105/train)
- [Selected frozen policy P0](https://github.com/TheUltimateHuman/when-explanations-write-back/blob/0985b7c0331cdfbb71591e7cc37a106df2ec2243/mpw105/policy/qwen3.json)
- [Original complete HOLDOUT raw archive](https://github.com/TheUltimateHuman/when-explanations-write-back/tree/60cdc81d05942e463358aefe56aa7829061cc00b/mpw105/holdout)
- [Independent HOLDOUT verification](https://huggingface.co/jobs/TheUltimateHuman/6ade914a1e112550ce7efee4)
- [Original Qwen GPU HOLDOUT](https://huggingface.co/jobs/TheUltimateHuman/6add536e046eb82b1ece14c6)
- [Granite original calibration refusal](https://huggingface.co/jobs/TheUltimateHuman/6add1b0e1e112550ce7e3d02)

No original raw GPU records were modified for this report; the raw archive remains pinned at the preceding immutable Git SHA.

## 8. Final ruling and restored roadmap

**MPW-105 original optimizer primary H1/H2: QWEN VALID, BOTH NOT CONFIRMED; GRANITE CAPABILITY_GATE_FAIL, H1/H2 UNKNOWN_NOT_EXECUTED.** Full two-architecture score-inflation claim NOT MET.

**Descriptive version finding:** natural prose in Qwen HOLDOUT demonstrated q=67.50%, s=73.75%, C=6.25%, L=0 with exact s=q+C−L and five observed false-to-apparently-true transitions. This is a bounded, source-versioned observation; do not relabel it a statistically confirmed optimizer attack.

The researcher explicitly locked the original MPW-103 iterative-explanation scope as unfinished in [issue #1](https://github.com/TheUltimateHuman/when-explanations-write-back/issues/1), and MPW-105's categorical optimization does not complete that missing work. **Recommended next active pass: MPW-103I**, genuine sequential model-authored explanations and versioned mechanism audits; then MPW-106 persistent memory, MPW-107 naturalistic causal tasks, and MPW-108 provenance certification. No reactive MPW-105B should be launched merely to chase an adversarial positive outcome without a separate prior-art and mechanism hypothesis.
