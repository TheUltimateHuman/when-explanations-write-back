# MPW-101 — Prospective Fidelity-Transition Replication

**Status:** DRAFT / NOT PREREGISTERED / NOT EXECUTED  
**Prepared:** 2026-10-14 (America/Chicago)  
**Target execution:** Thursday, 2026-10-15  
**Research program:** The Self-Validating Explanation: Sequential Mechanistic Provenance in Language Models  
**Investigator / publication identity:** Aidan Edward Lawson — Independent Researcher, Modal Path Ethics

## 0. Authoritative predecessor and corrective scope

Source: *When Explanations Write Back: Mechanistic Provenance for Language Models*, v1.1 (October 2026), notably Sections 2–4, 7, Appendix F and Appendix H. Reuse the publicly frozen PR-002 protocol and exact executed script as a starting point. Do **not** modify, overwrite, or relabel the archived PR-002 outcomes.

The prior PR-002 Phi-3.5-mini-instruct study obtained a positive preregistered mapping-balanced report-meaning contrast (96 held-out families), but its *binary natural-report fidelity transition* analysis was post hoc: baseline faithful 52/96; post-writeback faithful 60/96; unfaithful-to-faithful 11/96; faithful-to-unfaithful 3/96. The prospective hypothesis here concerns this binary transition. For the 11 versus 3 discordant cases, a two-sided exact McNemar/binomial test yields p=0.057373, not p<0.05. This limitation must remain visible.

MPW-101 is **not** a test for consciousness, deception, privileged introspection, circuit localization, universal model behavior, or long-horizon self-amplification.

## 1. Scientific question

Does the *naturally selected* report of causal feature dependence prospectively increase its agreement with the later audited dependence profile relative to an untouched, historical baseline, when the report is returned to the same fixed-weight model?

Notation:
- A0: audit-relevant intervention-response profile in the untouched pre-question state.
- Q: explanation-elicitation prompt delivered on a separate branch.
- R: natural report chosen from exactly A/B according to that branch's next-token logits.
- A1(R): audited profile after the same question and chosen report are written back.
- D(A): signed LEFT-versus-RIGHT causal dominance statistic exactly as in PR-002.
- r: +1 for report meaning LEFT, -1 for RIGHT.
- F(R,A): 1 if r × D(A) > 0, otherwise 0; exact ties count as 0.

Define F0=F(R,A0) and F1=F(R,A1(R)). Define conversion C=P(F0=0,F1=1), fidelity loss L=P(F0=1,F1=0), and tau=P(F1=1)-P(F0=1)=C-L.

The identity s=q+C-L is algebraic and not an experimental discovery; MPW-101 estimates the terms prospectively.

## 2. Frozen hypotheses (proposed; freeze before execution)

**Primary H1:** tau > 0 for the specified model/task/interface distribution. **Primary null:** tau <= 0. Use a *two-sided* exact conditional McNemar test for paired discordant counts, and require tau > 0, p < 0.05, and a family-bootstrap percentile 95% confidence interval with lower endpoint > 0. If any required gate fails, the primary result is NOT CONFIRMED.

The sign-only definition is chosen to directly replicate the originally exploratory criterion, *not* because it is known to be optimal. Predeclare near-zero sensitivity analyses with thresholds δ∈{0.02, 0.05, 0.10}: Fδ=1 if r × D > δ, else 0. Report all three whether favorable or not; if the effect disappears with modest thresholds, mark it FRAGILE and do not claim a robust conversion effect even if primary H1 passes.

**Secondary (not sufficient to rescue the primary):** (a) continuous natural alignment r(D1-D0), (b) comparison with counterfactual opposite-meaning report branch using fixed Q, (c) mapping-balanced re-encoding of the same semantic report across A/B token meanings, (d) content-free A/B carrier contrast, (e) question-control / elicitation-only contrasts only when the exact intervening carrier is disclosed, (f) raw causal margin J=I_LEFT-I_RIGHT and intervention sensitivity, and (g) polarity/order strata.

The natural report is selected *once* on the randomized assigned question mapping for the family. The same semantic report can be re-encoded on a mirrored carrier branch for sensitivity analysis; selecting a different semantic report on the mirror branch is a different treatment and must not silently replace the original selection.

## 3. Model, data and sample

**Primary model:** Phi-3.5-mini-instruct, exact model revision pinned in the execution manifest; the previous executed revision was `2fe192450127e6a83f7441aef6e3ca586c338b77` (verify it remains downloadable and appropriate). Freeze the exact revision; do not silently use `main`.

**Task:** the PR-002 redundant sentiment procedure, direct `positive`/`negative` outputs, independently manipulable LEFT and RIGHT movie-review passages, held-out opposite-sentiment replacements, intervention-response logit margins. No localized-circuit claim.

**Validation N:** 256 fresh families; family is the independent sampling/analysis unit. Equal numbers of positive and negative target families. This is a prospective extension of PR-002, not a rerun of the original 96 cases. Use a predeclared fresh family seed (`2026101501`, proposed) and a completely disjoint source-text manifest. Construct from the *SST-2 training split* if adequate validation-split inventory is unavailable; exclude every earlier PR-002 calibration family and every new calibration family. Because training-split examples may have influenced general-purpose pretrained models, disclose the split choice and do not call this a contamination-free test of semantic generalization. The older 96 were SST-2 validation-derived; the source split change is a limitation.

**Calibration N:** 32 new families, text-disjoint from the 256 validation families. Capability gate before validation: at least 90% same-sentiment baseline accuracy and mean total intervention sensitivity at least 1.0. Prespecified required tokens (positive, negative, A, B) must be single-token next-token candidates. Do not inspect validation outcomes to adjust the family generator, prompts, decoding, thresholds, or sample count.

**Validation gate:** baseline same-sentiment accuracy >=0.90. If this fails, report INVALID FOR PRIMARY INTERPRETATION; preserve complete outputs and do not report the test as a null writeback result. A calibration failure similarly yields CAPABILITY-GATE FAILURE.

**Power planning:** Conditional on reproducing original post hoc rates C≈11/96 and L≈3/96, N=256 has estimated two-sided exact-test power about 94%; approximately 71% for the δ=0.02 sensitivity counts (10 versus 4). These are highly optimistic because they come from exploratory data; report as planning assumptions, not evidence of a guaranteed result. Do not alter N after examining validation effects.

## 4. Branches for each family

Fork from identical untouched pre-elicitation state and preserve:
1. A0: untouched baseline audit, repeated independently as numerical-floor control.
2. Q: explanatory-question branch to select natural A/B report R by deterministic next-token argmax; record raw logits and the randomized mapping.
3. Q+R: same question plus naturally selected report; audit A1(R).
4. Q+R': same question plus counterfactual opposite-meaning report on a matched branch.
5. Q+R re-encoded under reversed A/B semantics; assess sensitivity to token identity (account for changed question text).
6. Matched content-free formatting question with A and B branches; report nonzero carrier effects.

Report prompting is itself an intervention. A question-only branch with an artificial placeholder is not assumed causally neutral; if implemented, characterize the placeholder as a treatment and avoid claiming it isolates a pure question effect.

## 5. Analysis and multiplicity

Compute F0 and F1 before aggregation, and the full 2×2 table (00, 01, 10, 11). Derive q, s, C, L and tau from the same family rows. Verify the decomposition exactly. Compute two-sided exact McNemar/binomial p from 01 versus 10. Use 100,000 bootstrap resamples over *families*, fixed bootstrap seed proposed `520261015`, for a percentile 95% CI on tau. Show raw counts and effect sizes alongside p. Do not treat the multiple within-family audit forward passes as independent observations.

Use the primary rule only once. Secondary threshold, meaning-reversal, carrier, norm-vs-raw, and subgroup analyses are diagnostic and do not substitute for primary success. Preserve outcomes where mapping-specific signs disagree or interventions have negative sensitivity. If numerical-floor repeats show meaningful nondeterminism, disclose it and rerun the designated same-input check; never silently discard families.

## 6. Reproducibility and governance of the run

Before validation:
- [ ] Independent hostile read of protocol and analysis script.
- [ ] Pin dataset revision, model revision, transformers/torch versions, hardware, precision, and inference settings.
- [ ] Freeze code, sampling manifest, seeds, threshold definitions, gates, output schema, and cost/timeout controls.
- [ ] Publish or embargo a timestamped preregistration (OSF Registries is suitable) and record Git commit/hash.
- [ ] Perform calibration without inspecting validation scores; if gate fails, stop.

For each job, retain: complete exact submitted script; full per-family records with report and audit data; raw stdout/stderr; container and dependency versions; timestamps; Hugging Face job ID; actual hardware; model/dataset revisions; runtime; cost if provided; SHA-256 manifests and independently recomputed summary.

Release an independent *MPW-101* record without rewriting original PR-002. Separate SOURCE RECORD, PREREGISTERED RESULT, EXPLORATORY DIAGNOSTIC, and INFERENCE.

## 7. Execution budget / stop policy (PROPOSED, not user-authorized spend)

Current Hugging Face Jobs list shows no running jobs. L4 is currently listed at $0.80/hour, A10G small at $1.00/hour. Begin with a short calibration/timing job on L4 if hardware permits. Estimate full cost from actual measured families/hour; set an explicit job timeout and spending ceiling *before* launch. Suggest an initial $10 research-job cap, subject to approval, not a claim that the full run will cost $10. Verify account billing access and OAuth session at execution time. Do not launch a paid job from this draft.

## 8. Failure and narrow results

- Calibration fails: CAPABILITY-GATE FAILURE. No confirmatory primary inference.
- Validation accuracy fails: INVALID FOR PRIMARY INTERPRETATION. Full outcomes archived.
- Primary tau<=0 or exact p>=0.05 or bootstrap lower<=0: PRIMARY NOT CONFIRMED (with measured estimate and uncertainty).
- Primary passes but δ=0.02 or stronger thresholds reverse/null: PRIMARY SIGN RESULT / THRESHOLD FRAGILITY. No strong general claim.
- Effect tracks arbitrary tokens, order, or general instructions as well as alleged report semantics: REDUCE TO PROMPT/ CARRIER SENSITIVITY; retain measured result and narrow interpretations.
- Good primary Phi result but no independent model replication: SINGLE-MODEL PROSPECTIVE RESULT; not a cross-architecture generalization.

## 9. Next paper gate

MPW-101 on its own is not sufficient for a broad follow-up paper. Only after prospective confirmation plus strengthened carrier and cross-architecture tests should the series evaluate iterative dynamics (MPW-103) and audit-reward optimization (MPW-105). The candidate Paper II contribution is an *evidence-backed divergence of historical and post-writeback fidelity* and a practical provenance-preserving evaluation, NOT novelty of ordinary self-conditioning.
