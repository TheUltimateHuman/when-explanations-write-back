# MPW-102B — Cross-Architecture, Person-Framed Writeback and Steering Specificity
Aidan Edward Lawson — Independent Researcher, Modal Path Ethics

**Protocol design date:** 2026-10-23. **Status:** PREVALIDATION DEVELOPMENT — *no MPW-102B calibration or validation outcomes exist at protocol creation*. The protocol becomes frozen only after a separately committed CPU-only sampling/tokenizer preflight, recorded fixed model revisions and sample SHA, and a final immutable Git commit. Preflight repairs must be dated and occur before any GPU validation.

## Evidence boundary
MPW-101 failed the natural-report binary conversion primary gate (18 conversions vs 11 losses, paired p=.26493). MPW-101E exposed report-option bias and passage-order / context sensitivity. MPW-102 Phase A confirmed a controlled, mapping-balanced *externally inserted* report-meaning effect in Phi-3.5-mini-instruct, not natural-report introspection. MPW-102B pursues model transport and separates multiple linguistic frames; it neither reinterprets that prior failure nor claims pure semantic or introspective causality.

## Predeclared independent model panel
1. Qwen/Qwen3-4B-Instruct-2507 (Qwen3, approximately 4B parameters)
2. ibm-granite/granite-3.3-8b-instruct (Granite 3.3, approximately 8B parameters)

Use model-specific immutable revision SHAs recorded by CPU preflight before validation. Model identifiers, family sizes, and analysis must not be changed in response to validation outcomes. Distinct tokenizers, architecture and chat templates make these genuinely different from Phi but do not establish population generality. Each model is screened on the same fresh cases; report independent model-specific results and the conjunctive cross-architecture gate. GPU = Hugging Face L4 24 GB, FP16, model.eval(), use_cache=False, pinned dependencies, independent prefix reconstruction.

## Fresh case construction
SST-2 train split at exact dataset revision 8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb. Reconstruct original MPW-101/102 case sampling from their SHA-pinned scripts, verify both historical manifest hashes, and exclude all four evidence strings from both samples and PR-002 calibration, as well as all SST-2 validation rows and case-insensitive duplicates. Fixed seed 2026102302. 32 calibration and 192 validation families, balanced sentiment; each has two same-sentiment passages and two disjoint opposite-sentiment replacements. Display both LEFT-first and RIGHT-first for each family. Sampling output and exclusions are hashed, published and checked at GPU runtime. Training-split text disjointness from previous study cases does not imply exclusion from pretraining.

## Treatment and potential-outcome audit
Same base prompt and causal intervention definitions from MPW-102. For each case, both evidence display orders, and each treatment:
D = (I_LEFT - I_RIGHT) / (abs(I_LEFT) + abs(I_RIGHT) + 1e-6)
I_side = loss in correct-versus-alternative next-token logit margin upon counterfactually replacing that side's review with independently held opposite-sentiment text. Record raw J = I_LEFT-I_RIGHT and total sensitivity; audit accuracy separately.

Baseline, exact repeated baseline, neutral acknowledgement, label-aware acknowledgement, and original AB coded response condition (both A/B mapping reversals, both externally inserted LEFT/RIGHT code responses) are mandatory.

Seven matched full-language treatment frames will be used. All are put in the same user-to-assistant message slot and followed by the **same assistant acknowledgment** 'Understood.' to avoid conflating grammatical person with message-role. A fixed attribution preamble identifies the model as the referent of 'I', 'you', and 'the assistant'. These are externally inserted quotations, **not natural self-reports**.

For side L vs R, the statements are:
- SELF_DECLARATIVE: "I currently rely more on LEFT than RIGHT."
- YOU_DECLARATIVE: "You currently rely more on LEFT than RIGHT."
- THIRD_DECLARATIVE: "The assistant currently relies more on LEFT than RIGHT."
- YOU_QUESTION: "Do you currently rely more on LEFT than RIGHT?"
- YOU_PRESCRIPTIVE: "You should rely more on LEFT than RIGHT in the next case."
- DIRECTIVE: "For the next case, rely more on LEFT than RIGHT."
- SIDE_REFERENCE: "The next case contains evidence labeled LEFT."

The RIGHT treatment swaps LEFT/RIGHT throughout each statement. The last is a side-word/label control rather than a reliance assertion. Questions and prescriptive/imperative forms are not counted as explanatory assertions. The preamble and forms are author-defined experimental instruments; grammatical variation alters more than one token, so side contrasts and matched controls cannot prove pure token-independent semantics. Prompt-length and surface effects remain potential residual explanations.

## Two separately evaluated primary hypotheses (four model-level tests)

H1 / TRANSPORT_AB: for each model, Z1_i is the mean LEFT-versus-RIGHT *AB-coded answer-writeback* D contrast across both display orders and both meaning mappings. The source question and A/B meaning reversal are inherited verbatim from frozen MPW-102. This is replication of a specific AB-coded stratum, **not** the full three-carrier original.

H2 / EXPLANATORY_SPECIFICITY: let E_i(style) be the LEFT-minus-RIGHT D contrast averaged across both display orders under that worded treatment. Z2_i = mean(E_i(SELF_DECLARATIVE), E_i(YOU_DECLARATIVE), E_i(THIRD_DECLARATIVE)) - E_i(SIDE_REFERENCE). This difference-in-differences requires explanation-typed statements to have a greater directional influence than a matched mention of the evidence-side label. It **does not** establish privileged introspection or an effect that cannot be supplied by ordinary prompting.

Each model's H1 and H2 is a distinct family-level null; 4 model-level tests share a conservative Bonferroni familywise rule: bootstrap 98.75% two-sided percentile CI lower>0, two-sided exact family sign-test p<0.0125, positive mean, with 50,000 resamples per model/hypothesis using fixed seed 520261023 and independence at the **family**, never prompt or forward-pass, level. H1 also requires positive means within both passage orders. H2 additionally requires positive E_i population means for EACH of the three descriptive statements and both orders. The joint FULL_PASS requires *both* models eligible and all four model-level tests to pass. Report independent H1 / H2 verdicts even when FULL_PASS fails. Model/calibration failure cannot be replaced after seeing results.

## Eligibility / invalidity
Before seeing validation: 32 calibration families; accuracy >=0.90 overall and individually by passage order; mean total intervention sensitivity >=1. All output label and AB report code candidates must be exactly one next-token id per tokenizer. Failed tokenization or capability yields corresponding NOT_ELIGIBLE, no confirmatory validation for that model. Frozen model revisions, dataset revision, parent-source hashes, case manifest, CUDA availability and runtime ceiling are mandatory.
Validation: 192 complete families per eligible model, baseline accuracy >=0.90 by each order, maximum untouched duplicated D discrepancy <1e-4, all 2-order audits present, no hidden outcome exclusions, nonfinite statistics INVALID.

## Mandatory secondary / negatives
Report E for all seven frames, relative to SIDE_REFERENCE; display-order asymmetry, raw J, numeric floor, saturation, negative causal interventions, free-text acknowledgment effects, and all A/B carrier/token effects. YOU_QUESTION and YOU_PRESCRIPTIVE MUST be reported independently rather than pooled into second-person explanation. Comparisons to imperative and prescriptive frames are diagnostics; weaker, equal or stronger effects of commands remain allowed and reduce any interpretation of explanatory specificity. The whole task remains constructed paired SST-2 sentiment classification.

## Budget and release
Two model jobs separately on Hugging Face L4 with <=75-minute platform timeout each and <=65-minute in-script limit. A prevalidation timing probe using calibration-only cases must imply total workload with 35% safety factor fits <=62 minutes, otherwise NO-PROCEED. Estimated ceiling at $0.80/L4-hour is $2 for GPU if both reach hard timeout; billing may differ. No speculative extra models or reruns for a favorable result. Release source freeze, failed preflights, calibration, all row-level records, per-shard SHA and combined SHA, independent CPU reanalysis, exact provider job IDs, model/dataset revisions and outcome verbatim. If incomplete, report INDETERMINATE and do not publish a journal claim.

**Execution authorization:** user requested proceed to MPW-102B, including second-person treatments, 2026-10-23. The research program and the previous run are independent; no additional budget is presumed beyond the conservative cap above.
