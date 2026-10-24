# MPW-104B — The False Explanation Under Order-Stable Protected Baselines

**Technical closeout: October 24, 2026**  
**Investigator:** Aidan Edward Lawson, Independent Researcher, Modal Path Ethics  
**Evidence category:** RESEARCH ARTIFACT  
**Final disposition:** **BOTH ARCHITECTURES VALID; ALL SIX FROZEN HYPOTHESES NOT CONFIRMED.** The primary joint false-to-apparently-true conversion target was NOT CONFIRMED in either model. A stable historical causal preference did not show the robust four-cell conversion found under the weaker order-conditional Phase A design.

## Abstract

MPW-104 Phase A found a strong, preregistered order-conditional false-report conversion result in Qwen3, with a subsequent hostile audit revealing that positive results disproportionately arose in evidence-presentation-order-unstable baselines. MPW-104B was prospectively designed to test that limitation, screening a fresh 2,048-case corpus for original input-causal dependence that was task-correct, stable in causal sign under reversal of physical presentation order, numerically repeatable, and positive in both causal intervention channels. Crucially, **selection was performed and archived using untouched baselines only**, and an independently written CPU analysis reproduced the selection **before** any false-report treatment job was launched.

Two models, Qwen3-4B-Instruct-2507 and Granite-3.3-8B-Instruct, screened all 2,048 fresh candidates each. Qwen retained 173 eligible cases (87 class 0 / 86 class 1); Granite retained 736 (426 class 0 / 310 class 1). Both prospectively selected the first 40 eligible cases per sentiment class by candidate index, producing 80 stable-baseline families per model, with 12 overlapping selected indices. Both subsequently completed the frozen 17-arm false/true explanation and sham treatments on those fixed selections. Every selected family retained the original causal dominance sign across stage-1/2 jobs with zero observed measurement drift and zero repeat discrepancy.

Every one of six model-level primary tests failed the prospectively defined confirmation gate. Qwen's false REPORT minus formatting sham contrast H1 was −0.004968; its strict four-way joint conversion H2 was exactly 0/80 under both treatment and sham, and its first-person false declaration versus matched reference H3 was +0.069229 with familywise CI lower above zero but two-sided sign-test p=.01832, above the required .00833. Granite H1 was +0.041087 with familywise CI spanning zero and sign p=.05666; H2 crossed in 2/80 after report versus 0/80 sham, p=.5; H3 was +0.020145 and not confirmed. No model suffered an invalidity gate failure.

These results fail to confirm the stronger claim that an experimenter-supplied false explanation can consistently induce conversion of a **presentation-order-invariant, known historical input-causal preference**. They do not establish a general impossibility of report-conditioned changes, and cannot be promoted to proof that the order instability *caused* the earlier Phase A positives; the Phase B population is deliberately screen-conditioned and different, and the new cases are fresh.

## 1. Origin, question and prospectivity

MPW-101's natural-report fidelity conversion was NOT CONFIRMED. MPW-102A, 102B (Qwen), 102C (Qwen and Granite), and MPW-103 (Granite, plus post-result amended Qwen completion) established operationally scoped report-meaning and history-conditioned shifts. MPW-104 Phase A Qwen met its original H1/H2/H3 for false-report uptake, sign crossing and first-person descriptive framing, but physical evidence reversal changed the sign of its untouched causal preference in **85/128 cases**. An explicitly post hoc split revealed that positive H1/H2 effects concentrated in those sign-inconsistent cases. Phase A's positive *order-conditional* results remain true to that frozen experimental definition. Granite's original Phase A study was INVALID on the right-first task accuracy gate.

MPW-104B was committed before any MPW-104B GPU screening or treatment output. Its prospective target was a stronger, independently screened *order-invariant* baseline, selected without exposure to treatment effects, and a four-way sign crossing criterion that must hold across both evidence orders and both A/B code mappings. Its model panel, candidate sample, selection rule, 80-case treatment size and test gates were fixed in advance.

- [Prospective protocol and selection rule](https://github.com/TheUltimateHuman/when-explanations-write-back/blob/8822587b6d0026338e4b20cd5c75ae0a0299d39a/mpw104b/PROTOCOL.md)
- [Frozen pre-GPU source and case manifest](https://github.com/TheUltimateHuman/when-explanations-write-back/blob/f23419671acd425a60cd66f1c8cd173d652ba033/mpw104b/FREEZE.md)
- Executed GPU runner SHA-256: d6f102401b4f74e543df7b4339becb5c9aa8b5bfdf2d7830a8b04b8e042d1b49.
- Independently written screening and treatment analysis SHA-256: 845e49791d8a2a8bf93ca0546bf24aa1490698688c77e589d157af2f52dc68e9.
- New candidate/calibration canonical source SHA-256: 86eee90fa35e92b82a653e74e473fa1cffae5cee5681ed2a88bcedd4f9682cae.
- Original data revision: stanfordnlp/sst2 at 8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb.
- Qwen/Qwen3-4B-Instruct-2507 SHA: cdbee75f17c01a7cc42f958dc650907174af0554.
- ibm-granite/granite-3.3-8b-instruct SHA: 51dd4bc2ade4059a6bd87649d68aa11e4fb2529b.

The source uses frozen models, FP16, no weight updates, no shared mutable KV state and no silent truncation. Stage-1 and Stage-2 jobs run separately. No external OSF preregistration is asserted.

## 2. Candidate population and strict baseline-only screen

The exact source sample contains 64 calibration cases and 2,048 candidate families, 1,024 per sentiment class; each family contains 4 distinct passages (two original same-sentiment LEFT/RIGHT and two independently chosen opposite-sentiment replacements). All 8,448 new passage strings are unique and disjoint from 6,216 historical normalized text keys (recovering MPW-101 through MPW-104A and original PR-002 calibration exclusions). Candidate sampling seed is 2026102402.

For each candidate and model, prior to any report treatment the untouched original and independent repeat causal audit were performed in both physical evidence orders LR and RL. The causal measure was D=(I_LEFT−I_RIGHT)/(|I_LEFT|+|I_RIGHT|+1e−6), where I_side is the reduction in constrained correct-versus-alternative sentiment answer margin when only one corresponding passage was counterfactually replaced. Positive D means LEFT exerted greater causal influence under this defined method.

The prospectively frozen screen required, under both physical orders: (i) correct untreated sentiment answer on both audit repeats; (ii) same nonzero D sign across LR and RL; (iii) |D|>=.10 each order; (iv) positive I_LEFT and I_RIGHT on both repeats, (v) exact original-repeat |ΔD|<1e−4, and (vi) finite audit values. Eligible cases were selected as **the first 40 in each sentiment class sorted by immutable candidate index**. All candidate rows and rejection reasons were archived. No model-specific treatment outcome could influence selection or create substitutions.

| Screen outcome | Qwen3 | Granite |
| --- | ---: | ---: |
| Calibrated task accuracy LR | 96.875% | 98.4375% |
| Calibrated task accuracy RL | 95.3125% | 90.625% |
| Calibrated input sensitivity | 28.95044 | 17.62457 |
| Total candidate families | 2,048 | 2,048 |
| Eligible class 0 | 87 | 426 |
| Eligible class 1 | 86 | 310 |
| Eligible total | **173 (8.45%)** | **736 (35.94%)** |
| Frozen selected cases | 40+40=80 | 40+40=80 |

Screening rejection reasons are multi-label and their counts are NOT disjoint. The independent screen archive reanalysis found, among others:
- Qwen: 1,408 cases with original causal sign disagreement between orders; 123 incorrect LR, 132 incorrect RL; 336 with nonpositive LR channel(s), 669 with nonpositive RL channel(s); 307 below |D| threshold LR, 136 below threshold RL.
- Granite: 476 order-sign disagreements; 156 incorrect LR, 193 incorrect RL; 304 and 321 with nonpositive channel(s) LR/RL; 380 and 416 below |D| threshold LR/RL.

The selected index sets overlapped on **12 of 80** families, so empirical cross-architecture comparisons are comparisons of a screen procedure on model-specific stable cohorts, not 80 identical inputs per model.

### Immutable baseline-only screen and independent selection verification

The Qwen GPU screening job [6adc36a3046eb82b1ecda4bb](https://huggingface.co/jobs/TheUltimateHuman/6adc36a3046eb82b1ecda4bb) and Granite [6adc36a5046eb82b1ecda4bd](https://huggingface.co/jobs/TheUltimateHuman/6adc36a5046eb82b1ecda4bd) BOTH completed all 2,048 original baseline-only records.

Their **4,096 original candidate rows** were preserved in 16 gzip/Base64 JSONL shards (8 shards of 256 per model) along with their original GPU raw SHA-256 anchors. Every source record was verified by independently written CPU script without importing GPU source. The independent CPU verifier recovered all shards and recomputed the frozen selection algorithm, matching every selected index and every baseline record with the GPU-emitted selection JSON. These CPU jobs completed **before** the first treatment execution was launched.

- Immutable original screen/selection Git commit: **1d4842a8db8af239505d09a89c91e56b03cbd5c4**.
- [Original complete screen records and manifest](https://github.com/TheUltimateHuman/when-explanations-write-back/tree/1d4842a8db8af239505d09a89c91e56b03cbd5c4/mpw104b/screen)
- [Qwen frozen selected 80 families](https://github.com/TheUltimateHuman/when-explanations-write-back/blob/1d4842a8db8af239505d09a89c91e56b03cbd5c4/mpw104b/selection/qwen3.json); original selection SHA 7727a4b8a520bb843825fd7aee8643ee814ab009043365a4cd4d8caa580bb7c8.
- [Granite frozen selected 80 families](https://github.com/TheUltimateHuman/when-explanations-write-back/blob/1d4842a8db8af239505d09a89c91e56b03cbd5c4/mpw104b/selection/granite.json); original selection SHA 7a9dfc6ecb70810d196722661eb285f6b632cc63432180b412931609a7b15c08.
- Independent Qwen screen-verification job: https://huggingface.co/jobs/TheUltimateHuman/6adce53a1e112550ce7e1df3.
- Independent Granite screen-verification job: https://huggingface.co/jobs/TheUltimateHuman/6adce53b046eb82b1ecde29b.

**Screening only** occurred in these jobs. No false report, neutral-acknowledgment test or other treatment was applied to select an apparently easy cohort.

## 3. Separate locked treatment experiment

After each selected 80-family cohort was frozen and independently verified, the two treatment jobs loaded that exact immutable screening commit and reconstituted each selected case by its candidate index and original case SHA, preserving the **screen-defined TRUE/FALSE side**. They did not reorient TRUE/FALSE using a fresh measurement. Each treatment separately remeasured untouched original and repeated baselines under both physical orders, applying the stringent predeclared cross-job consistency gates: no wrong task answers in selected cases, no sign changes, no within-job baseline numeric deviation >=1e−4, and no screen-to-treatment baseline D drift >=1e−4.

Both treatment jobs then evaluated all 17 predeclared conditions from MPW-104 Phase A for each order: baseline, repeat, neutral continuation, A/B reverse-mapped TRUE/FALSE reliance reports, TRUE/FALSE arbitrary-code shams, free-text TRUE/FALSE declarations, person-matched TRUE/FALSE references, and TRUE/FALSE imperatives. Each branch used the same original passages and the same independent opposite-sentiment replacements. Three model outputs were scored for each branch to recompute I_LEFT and I_RIGHT.

**Qwen original treatment:** https://huggingface.co/jobs/TheUltimateHuman/6adce55a1e112550ce7e1e1b  
**Granite original treatment:** https://huggingface.co/jobs/TheUltimateHuman/6adce55c046eb82b1ecde2a9

Both passed stage-2 calibration, immutable source and selection hashes, and real provider runtime feasibility without assistant-invented internal caps. Both completed exactly **80/80** selected families with complete finite arms.

| Stage-2 validity | Qwen3 | Granite |
| --- | ---: | ---: |
| Wrong original task answers across selected families/orders | 0 | 0 |
| Protected baseline sign flips relative to screening | 0 | 0 |
| Max untreated baseline repeat | 0 | 0 |
| Max screen-to-treatment D difference | 0 | 0 |
| Complete families | 80/80 | 80/80 |
| Verdict | **VALID** | **VALID** |

These are model-execution results and do not constitute validation of explanation truth outside the experimental intervention-response measurement.

## 4. Six frozen model-level hypotheses

Let s_i be +1 if the screen-defined FALSE side was LEFT and −1 if FALSE was RIGHT. Q_i(T)=s_i D_i(T), positive when the measured influence after treatment favors the originally false assertion. Effects are averaged within family across LR/RL and m0/m1, with each of the 80 selected *families* as the independent statistical unit.

H1 STABLE_FALSE_REPORT_UPTAKE: mean of Q(REPORT_FALSE)−Q(FREE_FALSE) >0, with separate positive effects under both orders AND both code mappings.

H2 JOINT_CONVERSION_EXCESS: report-side conversion R_i=1 only if Q(REPORT_FALSE)>0 in **all 4** LR/RL×m0/m1 combinations. Sham S_i is defined the same way for the arbitrary-code FREE_FALSE arm. Family effect is R_i−S_i in {−1,0,+1}. This is specifically designed to reject a sign crossing seen only with a favorable evidence order or one native A/B mapping.

H3 PERSON-MATCHED_FALSE_DECLARATION: mean across LR/RL of Q(SELF_DECLARATIVE_FALSE)−Q(SELF_REFERENCE_FALSE)>0.

For each model and hypothesis the prospectively required confirmation gates were: positive family mean, 50,000-family-resample bootstrap two-sided **99.1667%** interval lower endpoint >0, exact two-sided family sign p<.0083333 under Bonferroni six-test correction, and H1/H3 positive physical-order and H1 mapping means. All three hypotheses had to survive model validity above. Weights were not retrained, no outcome-based family deletion was permitted, and no post hoc thresholds were substituted.

## 5. Full primary outcome table

| Hypothesis | Qwen3 mean | Qwen3 99.1667% interval | Qwen verdict | Granite mean | Granite 99.1667% interval | Granite verdict |
| --- | ---: | --- | --- | ---: | --- | --- |
| H1 report uptake over sham | **−0.00496827** | [−0.04317465,+0.03518919] | **NOT CONFIRMED** | +0.04108652 | [−0.00994044,+0.09316189] | **NOT CONFIRMED** |
| H2 joint conversion excess | **0.00000000** | [0,0] | **NOT CONFIRMED** | +0.02500000 | [0,+0.075] | **NOT CONFIRMED** |
| H3 false declaration over matched reference | +0.06922895 | [+0.02593669,+0.11651647] | **NOT CONFIRMED** | +0.02014464 | [−0.03481021,+0.07109037] | **NOT CONFIRMED** |

### Individual family signs and exact tests

- **Qwen H1:** 34 positive, 46 negative, 0 tied; sign p=.218518. LR mean −.0590430 and RL +.0491065; code mapping0 −.0033532, mapping1 −.0065833. Point estimate negative, CI includes zero; also violates mandatory physical order and mapping positivity.
- **Qwen H2:** 0 positive, 0 negative, 80 ties; sign p=1. **0/80** report families and **0/80** sham families met all four joint crossing conditions.
- **Qwen H3:** 51 positive, 29 negative, 0 tied; sign p=.018316, which FAILS Bonferroni alpha .008333 despite positive mean and positive adjusted bootstrap interval. LR +.0845221, RL +.0539358. Keeping the sign-test gate yields NOT CONFIRMED, not a post hoc success.
- **Granite H1:** 49 positive, 31 negative; sign p=.056664, adjusted CI includes zero, despite mean +.0410865 and positive mapping and physical-order averages.
- **Granite H2:** 2 positive, 0 negative, 78 ties; sign p=.5, adjusted lower CI equals zero. **2/80** report families jointly crossed; **0/80** sham families jointly crossed.
- **Granite H3:** 47 positive, 33 negative; sign p=.145635, adjusted CI includes zero, LR −.0313723 and RL +.0716616, so it also fails physical-order positivity.

The family-level unit and all 80 original selected cases were used throughout; raw treatment components were never treated as independent observations for significance.

## 6. Partial crossings and control diagnostics

The stricter joint H2 requirement rules out counting an isolated sign crossing as stable causal alignment.

| Number of 4 cells crossing | Qwen false report | Qwen sham | Granite false report | Granite sham |
| --- | ---: | ---: | ---: | ---: |
| 0 of 4 | 77 | 78 | 67 | 68 |
| 1 of 4 | 1 | 0 | 4 | 3 |
| 2 of 4 | 2 | 2 | 6 | 9 |
| 3 of 4 | 0 | 0 | 1 | 0 |
| **4 of 4** | **0** | **0** | **2** | **0** |

The secondary imperative-minus-reference effect was +.64235 in Qwen and +.33414 in Granite, larger than the corresponding declarative-minus-reference H3 means. Those are active ordinary language steering effects, but they do not rescue the false-report-as-explanation hypothesis. Neutral continuation was not inert: its directional mean was −.07447 in Qwen and +.04037 in Granite. Both models had zero nonpositive selected baseline intervention channels, which was enforced by screening. Qwen had 9 saturated selected order-specific baselines and Granite 2; both were retained.

The report FALSE-minus-TRUE code contrast was +.05476 in Qwen and +.08317 in Granite; unnormalized raw J report-vs-sham contrast −2.93755 in Qwen and +1.39546 in Granite. These are descriptive and not substitutes for the three primary false-report comparisons.

## 7. Hostile-audit interpretation of Phase A versus Phase B

**Phase A positive record is preserved.** It confirmed a comparatively broad, order-CONDITIONAL report-induced shift and binary conversion, with 85/128 Qwen cases changing original causal sign when physical evidence order was reversed. Its false-side assignment was made separately within each order, a legitimate feature of its frozen protocol but a weaker measure of initial historical causal organization.

**Phase B used a DIFFERENT and prospectively stronger population:** 80 genuinely stable original-baseline cases selected per model without any report exposure, independently reverified before treatment, with one frozen TRUE/FALSE assignment for both presentation orders. Model-specific selection altered case distribution (Qwen only 8.45% eligible in the original pool), and Phase B's H2 requires all four subsequent report conditions to cross sign simultaneously, unlike Phase A's order-conditional per-cell and mean excess calculation. Thus the Phase B failure cannot *logically prove* that physical-order instability alone caused Phase A's positive result; the test conditions differ in multiple declared respects. It does establish that the specifically stronger invariant-historical-conversion claim FAILED confirmation under the selected, cleanly held experimental implementation.

The Qwen contrast is especially telling: its overall order-conditional H1 in Phase A was +.21498 and binary excess H2 +.26442, while the stable-cohort H1 in Phase B was −.00497 and jointly confirmed crossings were zero. Granite was INVALID in Phase A; in Phase B it was VALID and still failed H1/H2/H3. No broad claim of self-validation survives these stringent tests.

Pre-existing work on positional evidence biases and fabricated model self-statements prevents labeling this as a fundamentally novel effect. Phase B's value is a **negative controlled falsification attempt** with protected, screening-stable causal provenance and a reproducible pre/post test. See [Phase B prior-art audit](https://github.com/TheUltimateHuman/when-explanations-write-back/blob/42f3e91bf2a56c9d9e68bd14851a20aec39aec11/mpw104b/PRIOR_ART.md).

## 8. Raw artifacts and independent replication

All results below were recorded as separate original GPU jobs and original GPU-tagged compressed record chunks, then archived unchanged. The computer-assisted analysis verifier re-read the immutable GitHub raw data; it did not rerun the neural inference.

**Complete 4,096 candidate baseline-screen family records, 16 raw shards, two selections and manifest:**  
https://github.com/TheUltimateHuman/when-explanations-write-back/tree/1d4842a8db8af239505d09a89c91e56b03cbd5c4/mpw104b

Screen original concatenated SHA-256:
- Qwen: 8ca51d4ce010f6e2b5443c00af0c8bef87d1fc9b293a3f2c9f6bfc343cde47fe.
- Granite: 99b7965f913b800213cd7cbe4842760eb49c934ba20d49c17136e6cafcd49ff3.

Screen selection hashes:
- Qwen: 7727a4b8a520bb843825fd7aee8643ee814ab009043365a4cd4d8caa580bb7c8.
- Granite: 7a9dfc6ecb70810d196722661eb285f6b632cc63432180b412931609a7b15c08.

Screen CPU independent job verifiers:
- https://huggingface.co/jobs/TheUltimateHuman/6adce53a1e112550ce7e1df3
- https://huggingface.co/jobs/TheUltimateHuman/6adce53b046eb82b1ecde29b

**Original full 160 treatment-family raw records (8 shards), screen source anchor and machine manifest:**  
https://github.com/TheUltimateHuman/when-explanations-write-back/tree/77e5ff91a417b7bf5dc5a925f925e51f1a8e24ae/mpw104b/results

Original treatment raw SHA-256:
- Qwen: 419ec164ac41fe1108f3ba58c670ab1856b46744e3764b6994c314d1dd61074f.
- Granite: c22eb79cecb7a5977503674a559d568a2ceada06f73dba893d12ff94b3c9fd95.

Separate CPU verifiers downloaded and integrity-checked all four treatment shards per model, retrieved the immutably committed original screening baseline truths, imported ONLY the independently implemented analysis (written before screening), and exactly reproduced every H1/H2/H3 mean, adjusted interval, sign test, order/mapping mean, validity check, partial crossing count and final verdict.

- Qwen CPU treatment verifier: https://huggingface.co/jobs/TheUltimateHuman/6adce8681e112550ce7e1fc5
- Granite CPU treatment verifier: https://huggingface.co/jobs/TheUltimateHuman/6adce8691e112550ce7e1fcd

This is independent statistical *recomputation* of original model-output measurements, not independent external-laboratory model inference. Integrity verification is byte exact with pinned model/data/source/selection.

## 9. Final scientific disposition and next decision

**EXACT:** The two 2,048-case baseline-only screening studies completed, with independent source-hash verification and no report treatment leakage. The immutable first-40-per-class selections, 80 per model, were frozen and independently reconstructed BEFORE the treatment GPU runs. Both treatment runs were COMPLETE and VALID with zero screen-to-treatment drift, zero baseline-repeat differences and zero sign reversals. The six frozen tests and independent CPU recomputation all report NOT_CONFIRMED.

**NEGATIVE:** Neither architecture passed H1, H2 or H3 in the stricter stable-baseline population. In the most demanding joint H2, Qwen showed no all-four-cell crossing and Granite two all-four-cell crossings but not a statistically established excess over sham. Thus the intended evidence for conversion of a stable historical causal organization was **NOT CONFIRMED**.

**UNKNOWN / unresolved:** Whether naturally selected false model-authored explanations can redirect a stable underlying mechanism under other tasks, whether richer or longer external report histories matter, whether controlled alternation of evidence order could create differences, or whether training/memory changes could produce durable apparent self-validation. The current experiments do not establish that explanations are intrinsically unable to change future behavior. Conversely, no demonstrated *stable, order-invariant mechanistic self-validation* justifies proceeding as if it exists.

**Recommendation:** Retain MPW-104A and B side by side, with Phase B as the principal hostile-audit narrowing. MPW-105 may proceed **only if reframed as an adversarial evaluator audit**: can a report selector drive up measured post-writeback scores through prompt, positional and intervention-apparatus effects without improving protected historical fidelity? It must not assume stable false-to-true conversion was confirmed. Further MPW-104C targeted replication is optional but not necessary to document the clean negative Phase B outcome.

**Final MPW-104B ruling: VALID BOTH MODELS. H1/H2/H3 NOT CONFIRMED IN BOTH. CORE JOINT STABLE-CONVERSION GATE NOT MET. FULL SIX-TEST GATE NOT MET.**
