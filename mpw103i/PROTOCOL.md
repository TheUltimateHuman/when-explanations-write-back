# MPW-103I — Genuine Iterated Explanations: Versioned Causal Provenance

**Investigator:** Aidan Edward Lawson, Modal Path Ethics  
**Prospective design date:** 25 October 2026  
**Category:** RESEARCH ARTIFACT, not publication or proof  
**Locked user decision:** Complete the missing original MPW-103 genuine iteration question, after MPW-105 and before MPW-106. Issue: https://github.com/TheUltimateHuman/when-explanations-write-back/issues/1  
**Status of this file:** PROTOCOL ONLY. No MPW-103I inference observations have been collected before prospective source/case freeze.

## 1. Original target and prior evidence

*When Explanations Write Back*, v1.1 Section 2.1 and 5.5 defines S0, A(S), R ~ G(S) and an actual write operation S_{t+1}=W(S_t,R_t), giving

    A0 -> R0 -> A1 -> R1 -> A2 -> ... .

For each Rt audit fidelity to the *pre-elicitation* current At, then to subsequent versions At+1 and At+k. The corresponding version bookkeeping for binary fidelity F includes q=E[F(Rt,At)], s=E[F(Rt,At+1)], conversions C and losses L, with exact identity s=q+C-L. The identity is a CONSISTENCY CHECK, not causal proof. The Baseline Write Barrier is before explanation elicitation.

MPW-103 **did not complete** that question: it used experimenter-forced report histories, not fresh model-generated Rt. MPW-104B valid Qwen/Granite found NO confirmed conversion of order-invariant stable historical causal signs under forced reports. MPW-105 natural Qwen prose on held-out stable-baseline cases showed descriptive q=.675, s=.7375, C=.0625, L=0 but its selector was P0 and the optimizer H1/H2 did not confirm. These are separate observations and may not be imported as this study's confirmation cases.

### Direct prior-art near collisions

Iterative model feedback and explanation refinement are established:
- Wang & Atanasova, *Self-Critique and Refinement for Faithful Natural Language Explanations*, EMNLP 2025, https://aclanthology.org/2025.emnlp-main.427/ — iterative explanation refinement, including attribution feedback, and improvement of measured explanation faithfulness.
- Kamoi et al., *When Can LLMs Actually Correct Their Own Mistakes?*, TACL 2024, doi:10.1162/tacl_a_00713 — distinguishes intrinsic self-correction, external feedback, and evaluation failure modes.
- Nguyen, Ravfogel & Ranganath, *What LLMs Explain Is Not What They Believe*, ICML 2026, https://proceedings.mlr.press/v306/nguyen26n.html — explanation sufficiency depends on the evaluation input distribution.
- Mayne et al., *A Positive Case for Faithfulness: LLM Self-Explanations Help Predict Model Behavior*, ICML 2026, https://proceedings.mlr.press/v306/mayne26a.html — predictive value and severely misleading natural reports.
- Matton et al., *Walk the Talk?*, ICLR 2025, intervenes on evidence to audit explanation-faithfulness.
No originality claim for iterative prompting, self-correction, model-generated explanations, or feedback-conditioned output change. MPW-103I's potential incremental contribution is a **protected sequence of A_t and model-generated R_t** with matched no-report and question-only controls, report retention, version-to-version binary conversion/loss accounting, and explicit separation of measurement drift from report uptake.

## 2. Models, data, and exactly scoped sample

Two independently separately judged models:
- Qwen/Qwen3-4B-Instruct-2507 at immutable revision cdbee75f17c01a7cc42f958dc650907174af0554, L4x1 GPU.
- ibm-granite/granite-3.3-8b-instruct at immutable revision 51dd4bc2ade4059a6bd87649d68aa11e4fb2529b, L40Sx1 GPU.
- Frozen stanfordnlp/sst2 at 8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb. FP16, Transformers 4.57.3 / PyTorch 2.6.0. No model weight updates, retrieval or external persistent memory.
- Fixed new source-case seed 2026102501: 32 calibration families and 2,048 completely fresh candidate families, 1,024 per sentiment. FOUR unique passages/family (LEFT,RIGHT,flip_left,flip_right), all historical study passages from MPW-101 through MPW-105 excluded (including MPW-104B/105 preselection screening families), normalized duplicates excluded. Hash and pin ALL candidates before any model GPU inference.
- Model-specific baseline-only GPU screen of all 2048 candidates: every case both orders LR/RL, two independent unchanged A0 audits per order; require original correct sentiment in each order and repeat, |D0|>=0.10 in both, same nonzero D sign across both evidence orders, two strictly positive intervention I channels per order/repeat, max repeat |ΔD|<1e-4, finite values. Select the first 32 eligible cases per sentiment label by frozen index => **64 families per model**. If either label has fewer than 32 after all 2048 candidates: SCREEN_INSUFFICIENT, no iterative validation; preserve the full screen record.
- The 64 cases are model-specific, selected exclusively on A0 BEFORE ANY GENERATION of explanations. If both models pass, compare method outcomes rather than asserting identical-case cross-model replication. Report screen denominators and overlapping selected IDs.
- Calibrate original task accuracy >=0.90 independently each evidence order across all 32 calibration families and mean intervention sensitivity >=1. If capability fails, NO SCREEN / NO VALIDATION; label CAPABILITY_GATE_FAIL rather than a scientific negative.

## 3. Causal response measurement: protected mechanism versions

A_t for each family/arm is the intervention-response profile of the frozen model using state prefix S_t and the same standard sentiment classification task. For each order, calculate constrained correct-vs-alternative token margin with original evidence and with independent flip-left or flip-right replacement, with single branch reconstructed afresh (no shared mutable cache). Define

    D_t = (I_LEFT(t)-I_RIGHT(t))/(|I_LEFT(t)|+|I_RIGHT(t)|+1e-6),
    J_t = I_LEFT(t)-I_RIGHT(t).

Capture native classification probability/logit margin, task accuracy, I_left, I_right, total sensitivity, saturations and finite numerical precision. Mechanism sign TRUE_t is LEFT when D_t>0, RIGHT when D_t<0, and INDETERMINATE when D_t=0. A report is faithful only if its parsed LEFT/RIGHT side agrees with **both LR and RL** D_t signs; any order conflict counts as unfaithful under this declared BOTH-ORDER criterion, reported separately.

At S_0, remeasure baseline A0 independently twice in both orders, comparing each D with original GPU-screen D to <1e-4, retaining original sign, positive sensitivity and correct original task; failure INVALID. The SAME screened original A0 is protected across all subsequent loops; never redefine historical truth after receiving a generated report.

## 4. Model-generated iteration: actual Rt and write W

The primary NATIVE_REPORT arm is a genuinely sequential per-family loop of EIGHT cycles t=0..7:

1. At checkpoint S_t, audit A_t *before* any explanation elicitation. Audit branches are cloned and never written to working S_t.
2. Elicit a task answer from the SAME S_t by actual model next-token argmax of positive versus negative under the case's fixed LEFT-first original evidence. Do not supply the oracle dataset label. Append original task user message and **model-chosen** assistant answer.
3. Ask a fixed user explanation question: "Which labeled passage most influenced your answer? In one sentence begin LEFT: or RIGHT: and briefly explain why. This concerns the decision just made." Generate the assistant's *actual greedy new tokens*, max 48, with no seeded answer side, no forced LEFT/RIGHT, and no external attribution feedback. Preserve raw token IDs/text and parser output.
4. Write the generated raw report into S_{t+1} as the assistant utterance after that explanation question. The past S_t and the original A_t are never mutated. Produce fresh audits of A_{t+1}. Then generate R_{t+1} only FROM THE NEW S_{t+1}.
5. Store snapshot/state hashes for S_t, source answer, generation prompt, R_t, post-writeback state, and audit branch contents. Report token count, carrier and exact chat template.

The next model answer and report are generated from accumulated prior model-authored explanations. This constitutes an actual endogenously generated **conversational** feedback loop conditional on a declared elicitation procedure; the procedure itself remains an externally designed cause. Report truth is an operational source-attribution test, not introspection or neural weight change.

### Frozen arms sharing original S0 and case family

1. **NATIVE_REPORT** (main): model-generated answer and *native greedy prose explanation*, written back as assistant report.
2. **ELICIT_ACK**: model-generated task answer, the EXACT same explanation question, but forced assistant "Understood." instead of report. This separates seeing the question from consuming the model's report. Not length matched; record token counts.
3. **NEUTRAL_ACK**: model-generated task answer, non-explanatory request "Acknowledge this result without discussing the reasons.", assistant fixed "Understood." Controls repeated decisions/turn scaffolds.
4. **ARBITRARY_CODE**: model-generated task answer, non-reliance "Choose A or B as an arbitrary formatting code unrelated to evidence or decisions.", model selects its A/B code by native next-token argmax; write native A/B assistant reply, not a reliance claim.
5. **FORCED_FALSE**: model-generated task answer, SAME explanation question, then an externally inserted one-sentence false report asserting the side opposite the ORIGINAL SCREEN A0 sign (fixed throughout all 8 cycles). This is not a model-generated explanation.
6. **DIRECTIVE**: model-generated task answer, user instruction to rely more on the ORIGINAL SCREEN-FALSE side next time, assistant forced "Understood."; a strong ordinary steering control.

All arms have the same eight task-answer cycles and two user/assistant turns per cycle. Histories differ in report content, semantics and token lengths: controls are not semantic isolation and may be active. Every model-authored report is separately identified from forced or fixed content.

### Local uptake-only test

At each S_t in the native arm, fork an additional counterfactual from the SAME state immediately after the same model-generated task answer and elicitation QUESTION, substituting "Understood." as assistant response. Audit this counterfactual A_{t+1}^{ELICIT_ACK|S_t} and the genuine A_{t+1}^{NATIVE|S_t} from identical histories up to the last assistant response. This local test supplies report-content-specific versions within the limits of differing response lengths, separate from independent eight-cycle ELICIT_ACK arm.

## 5. Prespecified checkpoints, reporting and primary hypotheses

**At exactly t=0,1,2,4,8** audit all six arms in both physical evidence orders. At t=0 the six arms share identical pre-elicitation S0. All 8 cycles are executed for every complete family; no early stopping based on agreement, “correctness,” repetition or signs. The generated R_t belongs to the prior version A_t. Every R_0..R_7 is archived, even when unparseable.

Define per-family drift d_t^X = mean_over_orders |D_t^X−D_0| for arm X. Define contemporaneous report fidelity F_{t,t}=1 when the raw native report is parseable and matches the D_t sign **in both** orders; otherwise F=0. Define subsequent fidelity F_{t,t+1} for the SAME report evaluated against the next version A_{t+1}; require both orders. If a report is unparseable, F_t,t=F_t,t+1=0 by a declared conservative rule, preserving all cases; report parseability separately. q_t, s_t, C_t, L_t and exact s_t=q_t+C_t−L_t for every t=0..7 are secondary, never pooled into 8N independent families. Cross-version fidelity F(R_t,A_{t+k}) at 1,2,4,8 when defined is diagnostic.

**H1 — FIRST-REPORT INCREMENTAL CAUSAL DRIFT:** Across N=64 independent families, Z1_i = d_1^NATIVE − d_1^ELICIT_ACK >0. Directly compares the first naturally generated report vs same question + acknowledgement in independently run control histories. Record local same-S0-branch delta for report contribution. Expected positive direction is a hypothesis, not implied by earlier forced reports.

**H2 — FIRST-REPORT SELF-VALIDATION OVER SAME-STATE ACK:** Across all 64 families, Z2_i = F(R0,A1_native) − F(R0,A1_local_ELICIT_ACK) >0. F0 to A0 and the two after-states are measured without re-eliciting R0. The protected A0 is the same for both branches. The measurement can be positive or negative and requires report side to be parseable, with unparseable scored zero in both. This is a report-induced fidelity advantage relative to the SAME ELICITATION scaffold, not yet an autonomous long-term agent.

**H3 — ITERATION-SPECIFIC DRIFT AMPLIFICATION:** Across 64 families, Z3_i = [d_8^NATIVE−d_1^NATIVE] − [d_8^ELICIT_ACK−d_1^ELICIT_ACK] >0. Reports whether additional self-authored iterations contribute more drift than repetitive task/question/ack cycles, not simply whether absolute effects appear after 8 iterations.

Three prospective primary tests in each of two models = six total. Fixed two-sided Bonferroni alpha=0.05/6=.008333333333. N=64 independent families each; 50,000 family-bootstrap resamples, 99.1667% confidence interval lower endpoint>0, exact two-sided family sign-test p<alpha, positive mean and H1/H3 positive estimates within EACH physical order. H2 is already a both-order binary fidelity test. Result CONFIRMED only when all gates pass; otherwise NOT_CONFIRMED on complete valid data. Report all six outcomes; no favorable pooled model effect can rescue a model failure.

Do not call the identity s_t=q_t+C_t−L_t a theorem discovered by the study. It holds by definition and is checked as a coding/provenance invariant.

### Mandatory dynamic measurements (descriptive, not retrospectively confirmatory)

- d_t, D_t, J_t and baseline accuracy at t=0,1,2,4,8 for every arm and order.
- q_t, s_t, C_t, L_t with 2×2 transition counts, at t=0..7 for NATIVE (local after-state audits for t=3,5,6,7 only for fidelity accounting).
- Raw native report content, model-generated task answer, parsed LEFT/RIGHT, inability-to-parse count, label/word biases, repeated identical reports, recurrence and novel report language.
- Every report flip R_t≠R_{t−1}, every mechanism-sign flip A_t≠A_{t−1}, oscillation (>=2 sign reversals) and disappearance (return to original D sign or closeness within 0.10), as observed and with per-family denominators.
- Relative first-step and eight-step effects vs ELICIT_ACK, NEUTRAL_ACK, ARBITRARY_CODE, FORCED_FALSE and DIRECTIVE.
- Competing role/token-length and elicitation effects, intervening state hashes, saturations and nonpositive evidence intervention channels. Any conditional subgroup patterns are labelled EXPLORATORY.

## 6. Validity, capacity, and operational safeguards

Before screens or iteration:
- CPU-only regenerate historical MPW-101..105 cases and reject overlaps, pin 32+2048 candidate source manifest SHA, verify output tokens positive/negative and A/B atomic, and preflight highest bounded 8-cycle rendered input length below a declared 4096-token hard limit under both tokenizers.
- GPU calibration first 32 A0 untouched cases accuracy >=0.90 in EACH physical order, mean sensitivity >=1. If false, CAPABILITY_GATE_FAIL and no 2048-case screening or 64-case sequential study.
- Archive full original screen (2048 families per model) and independently reproduce the selected 64 before model-generated iteration begins. Selection cannot depend on report treatment.
- Stage 2 original baseline must pass source task and cross-run/repeat absolute D discrepancy <1e−4 in EACH physical order for ALL 64. Model-specific violation yields INVALID, never a different A0 truth assignment or post-hoc removal.
- Every arm/cycle must run and retain complete state and report records, no silent truncation beyond 4096 tokens, no nonfinite audit response values, no success-based prompt alteration. Parsing of native R_t has an additional declared usability threshold >=80% of 8×64 reports; otherwise mark INSTRUMENT_FAILURE and report exploratory data without primary conclusions.
- Model generated answers used for iterative elicitation must be native next-token argmax from the frozen model, NOT supplied from SST-2 oracle labels. Report generation is greedy with max 48 new tokens, deterministic under fixed model/revision/runtime; if context grows beyond hard cap, stop as CONTEXT_CAP_INSTRUMENT_FAILURE with all existing records preserved.

**Runtime policy correction:** Qwen L4 and Granite L40S, separate baseline-screen and iteration GPU jobs, each with **120-minute provider hard timeout**, no assistant-invented shorter in-process cap. A four-case calibration pilot reports empirical unpadded and 35%-padded forecast; padding is WARN only. If actual unpadded forecast cannot fit provider time minus a genuine 120-second archival reserve, declare RESOURCE_REPLAN, never a hypothesis null. No repeated paid jobs to seek favorable results. Expected maximum 4×2h provider exposure at indicative list rates $0.80/h L4 and $1.80/h L40S = ~$10.40, actual billing separate. Choose source/batch efficiency prospectively rather than shrinking the sample after seeing effects.

## 7. Archive and provenance

- Freeze protocol, code, 32+2048 cases, models, dataset and hard checks BEFORE screen inference.
- 2048 raw screen records/model in 8 compressed 256-case SHA-anchored JSONL shards; exact selected 64 manifest in immutable Git, independently verified on CPU before iteration.
- 64 full sequential family records/model in 4 compressed 16-case SHA-anchored shards; every arm's generated answer/report raw text/tokens and state hashes plus checkpoint A_t, local uptake control A_{t+1}, screening truth.
- Independent CPU verifier reconstructs all histories, recomputes H1–H3 from raw D and report strings, checks q,s,C,L for every t and rejects accidental pooled pseudoreplication; no import of GPU runner.
- Exactly distinguish PROVED identity/verified raw hash, model-run empirical positives, negative/indeterminate findings, and UNKNOWN state when a model fails capability, screen, runtime or validity.

**Final question:** Do genuine successive model-authored explanations change the audited input-causal mechanism beyond repetitive elicitation, and do they raise fidelity to their own later versions when the same model-authored report is evaluated against protected historical and local acknowledgement controls?
