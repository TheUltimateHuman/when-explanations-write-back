# MPW-104B — The False Explanation Under Order-Stable Protected Baselines

**Investigator:** Aidan Edward Lawson, Independent Researcher, Modal Path Ethics.
**Date of design:** 2026-10-23; this file is a prospective design document, not an external OSF preregistration.
**Evidence status at design:** MPW-104 Phase A is archived, including its positive order-conditional Qwen results and the POST HOC finding that those positives concentrate in 85/128 families whose untreated causal-dominance sign changes when LEFT/RIGHT evidence presentation order changes. There are **NO** MPW-104B treatment outcomes at time of this document.

## Hostile problem and why Phase B exists

MPW-104 Phase A Qwen met its predeclared H1/H2/H3, but only 43/128 families maintained the same initial causal-dominance sign when the physical evidence order was reversed. Among 32 order-consistent baseline-known Qwen families only 2 had a positive binary conversion advantage; 30 were ties. Only 9 families were simultaneously order-consistent and baseline-known in both physical orders. The phase A claim is an order-conditional causal-response result. It does not establish that a false explanation of a *stable* existing mechanism becomes self-validating.

MPW-104B prospectively screens a large FRESH text-disjoint cohort using **untreated baselines only**, and *fixes* a study population of order-invariant, repeatable, label-correct, causally sensitive cases BEFORE administering the false report. The screen-selected target is a **conditional subpopulation**, not a random sample of all model decisions. Model-specific selection is unavoidable for a model-internal causal measure; Qwen and Granite selected families are not assumed to be identical and will not be pooled as a paired cross-model sample.

Its decisive question: does a false forced report cause **both** physically opposite evidence layouts, under **both** A/B code-meaning reversals, to switch their later causal-dominance sign to the formerly false side more frequently than an arbitrary-code sham? This is a stronger test than Phase A's per-order binary conversion.

## Previously frozen sources and candidate model panel

- Qwen/Qwen3-4B-Instruct-2507, model SHA cdbee75f17c01a7cc42f958dc650907174af0554.
- ibm-granite/granite-3.3-8b-instruct, SHA 51dd4bc2ade4059a6bd87649d68aa11e4fb2529b.
- Dataset stanfordnlp/sst2 revision 8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb.
- Source ancestors: MPW-104 Phase A runner from immutable commit c94d1299e8862686bb728880c3f36a1527e7b7c0, exact SHA d8866d46dcb4bc6f5e2289108c22c434add56c423e63f1731c929aed86d6d1e1. Original MPW-101 through MPW-104 Phase A sample manifests and texts must be exactly reconstructed and excluded.
- Fixed candidate selection seed **2026102402**. Exactly **64 calibration families and 2,048 screening candidate families**, label-balanced (1,024 candidates per sentiment) with four unique passages each; all 8,448 candidate/calibration passage strings must be distinct from previous study samples and from each other. The count of 2,048 was fixed from the historically observed Qwen doubly-known/stable rate of ~7%, allowing an expected ~140 eligible cases before label/accuracy constraints; no Phase B outcomes were seen to choose this count.
- Models use FP16, pinned transformers 4.57.3, torch 2.6.0, frozen weights, native single-token positive/negative and A/B response codes, no shared mutable KV across branches and no truncation.
- Qwen NVIDIA L4x1, Granite NVIDIA L40Sx1; one GPU screening job and one GPU treatment job per model, separate immutable source/job identities, <=75 minute actual provider hard timeout each. Total worst-case hardware time at indicative $0.80 L4 and $1.80 L40S hourly rates is ~$6.50 across four fully exhausted 75m windows, and is **not** actual billing. Do not add an assistant-invented lower runtime cap. Forecast padding is WARN ONLY; only unpadded measured physical infeasibility relative to the provider cutoff/writeout reserve can prevent validation, labeled RESOURCE_REPLAN, never a hypothesis null. No result-dependent hardware switch.

## Stage 0: CPU-only preflight and candidate source freeze

Regenerate old manifest hash anchors, sample exactly 64 + 2,048 families using the seed above, and freeze their canonical JSON source manifest SHA in Git **before any MPW-104B GPU forward pass**. Check 4 unique passages per family, no overlaps, both label classes balanced, both native model tokenizers atomic. Preflight the original classification prompt and forced response branches under a 1,024-token maximum with no silent truncation. 64 calibration families are reserved for model capability and runtime pilots; NO calibration or screening families are reused as prior work.

## Stage 1: baseline-only GPU screening with complete provenance

Per model on all 2,048 candidate families, BEFORE ANY treatment conditions, independently calculate the untreated D0 and untouched D0_REPEAT under both physical orders LR and RL (two repeats x 2 orders, each with original evidence and two opposite-label single-side replacements). D=(I_LEFT-I_RIGHT)/(abs(I_LEFT)+abs(I_RIGHT)+1e-6); I_SIDE is the reduction in correct-vs-alternative logit margin when replacing exactly the respective evidence passage. Record all 2,048 baseline records including accuracy, I_LEFT, I_RIGHT, D, J, sensitivitiy, repeat, case ID, original source hash, each physical order and every screen rejection reason. No forced reliance reports, arbitrary codes or explanatory treatment prefix may be measured in this screen job. The separate 64 calibration families must pass >=90% original task accuracy in BOTH physical orders and mean causal sensitivity >=1. If not, STOP CAPABILITY_GATE_FAIL without treatment.

Before seeing any screening output, we fix the exact eligibility rule:
1. Untreated baseline correctly classifies the sentiment in BOTH LR and RL orders.
2. The sign of the first D0 is the same, nonzero, under LR and RL: TRUE side therefore has ONE fixed meaning across physical orders.
3. abs(D0) >= 0.10 in BOTH physical orders.
4. BOTH intervention channels are strictly positive in BOTH baseline runs under EACH order.
5. abs(D0-D0_REPEAT) < 0.0001 in BOTH orders.
6. Every audit value is finite.

Choose the **first 40 eligible** model-specific families for sentiment label 0 and first 40 for label 1 in ascending immutable candidate index, for exactly **80 validation families per model**. Do NOT rank by |D|, treatment response, ease of sign reversal, or significance. No replacements are allowed after treatment outcomes. If either label has fewer than 40 eligible across all 2,048 candidates, record SCREEN_INSUFFICIENT and NO_TREATMENT (not a scientific negative), retaining the entire original screen archive; a new separate prospective study would be required to increase candidates. Report all screening denominators, attrition reasons, and any model-specific overlap of selected case identities.

The screen job must print its original canonical record SHA anchors and deterministic selected index list and a hash of the selected full case+screen baseline manifest. Archive full baseline screen records and selection manifest in an IMMUTABLE Git results commit and run a *separately implemented* CPU verifier before either model's Stage 2 starts. The immutable selection Git commit, selected 80 case IDs and per-order baseline scores are input to Stage 2. No selection after seeing any false-report treatment outcomes.

## Stage 2: post-selection treatment run with a PROTECTED original baseline

On the previously selected 80 families, repeat the untouched baseline independently twice under both physical orders, preserving original SCREEN-selected TRUE and FALSE side and exact case IDs. **Never redefine FALSE** to match a newer measurement or better-looking outcome. Report screen-to-treatment baseline drift and sign reversals. Frozen validity gate: all 80 selected families remain correct on the original sentiment task in BOTH physical orders, both new baseline repeats have abs(D difference)<1e-4, and the first treatment-run baseline differs from the screen's first baseline by <1e-4 per family/order. This stringent cross-job consistency may fail; preserve INVALID rather than removing any family. The true side originally screened must retain its original sign in both treatment-run orders; otherwise INVALID. Stage 2 all 80 families and all arms must complete, and every value finite. These conditions differ from general-population baseline accuracy gates because the *prescreened valid task cases* are the prospective target population; screening attrition and population-level calibration must be reported separately.

Every family receives the exact 17 arms from MPW-104 Phase A, in the same role positions and native A/B mapping reversals, and independent corrected-vs-alternative logit audits. The arms: BASE and BASE_REPEAT, NEUTRAL_ACK, REPORT_FALSE_m0/m1, REPORT_TRUE_m0/m1, FREE_FALSE_m0/m1, FREE_TRUE_m0/m1, SELF_DECLARATIVE_FALSE/TRUE, SELF_REFERENCE_FALSE/TRUE, DIRECTIVE_FALSE/TRUE. Fixed assistant acknowledgment for quoted and directive sentences. False/true refers to SCREEN D0, not the model's claimed natural report. Equal original/replacement passages across treatment branches.

## Primary hypotheses and acceptance criteria (six model-level tests)

For each selected family i, TRUE_i and FALSE_i are inherited from screen and remain fixed across LR/RL. Let s_i = +1 if FALSE_i is LEFT else -1, so Q(T)=s_i D(T) measures alignment toward the initially false side. All family-level stats use the average across physical orders and mappings WITHIN a family. The model/case family is the independent statistical unit (N=80 per model).

H1 — STABLE_FALSE_REPORT_UPTAKE: mean_i mean_(order,m)[Q(REPORT_FALSE_m)-Q(FREE_FALSE_m)] >0. Requires positive mean under EACH physical presentation order and each A/B mapping as additional consistency gates. This tests directional uptake beyond code/formatting.

H2 — JOINT_CONVERSION_EXCESS: define R_i = 1 only if Q(REPORT_FALSE_m)>0 in *all FOUR* combinations LR/RL × m0/m1. Define S_i analogously for FREE_FALSE sham. Each family contributes Z2_i=R_i-S_i in {-1,0,+1}. Primary mean(Z2)>0 tests excess truly presentation-order- AND mapping-stable later crossings relative to sham, all 80 screened families. Report complete 2x2 table, raw R and S crossing rates, and how many partial (one-, two-, three-of-four) crossings occurred. A single order-specific crossing is insufficient to count.

H3 — PERSON-MATCHED_FALSE_DECLARATION: mean_i mean_order[Q(SELF_DECLARATIVE_FALSE)-Q(SELF_REFERENCE_FALSE)]>0. Require positive mean in BOTH physical orders. This is an explanatory-framing prompt contrast, not pure semantic or introspective identification.

Each H is tested separately in BOTH model architectures: six tests with frozen two-sided Bonferroni alpha=0.05/6=0.008333333333; 50,000 bootstrap family resamples for 99.1666667% two-sided percentile CI lower>0 (deterministic numpy seed 520261027 plus fixed H index 1–3), exact two-sided family sign-test p<.0083333333 excluding zero ties, and positive point estimate. The six-test FULL_GATE requires all six valid individual confirmations. The central cross-model stable false-conversion gate requires H2 confirmed in both. An eligible subset that fails to cross is genuine negative/NOT_CONFIRMED and must stay published. If no eligible cohort of 80 can be screened, the corresponding model H tests are UNKNOWN_NOT_EXECUTED, not negative.

## Controls, exploratory records, and hostile-audit constraints

In every model retain descriptive false-v-true report asymmetry, true-v-false sham, active neutral acknowledgment, imperative-vs-reference effect, baseline sign/drift and numeric floor, raw J effects, saturation/negative-channel effect, by-order and by-mapping H1, partial crossing configurations, selection ratio, class balance, 64-calibration ability, and overlap of selected cases between models. Raw original screen and treatment records must be archived, hash checked and independently reanalyzed.

Selection conditions explicitly enrich stable/accurate/sensitive cases; success in such a conditional sample cannot be generalized to all prompts. Selection at an extreme threshold can produce regression-to-mean across independent audits; preserving a frozen original screen baseline and two independent treatment-run repeats plus sham controls helps test, but does not rule out every apparatus effect. The code-mapping question and sham differ pragmatically, and historical natural self-report honesty was NOT established in MPW-101. A reported false statement becoming post-writeback compatible does not change the historical A0, weights, or the fact of its initial falseness. Also, Qwen and Granite may select different subsets, so separate model-level successes do not establish identical-case cross-model replication.

Existing history-conditioning and self-suggestion prior art (Chen et al. 2026; Simhi et al. 2026) and explanation-faithfulness intervention studies preclude novelty claims based on prompting effects alone. This study does not test model-generated false explanations, durable memory, explanation selectors or optimized self-validation scores. Those require separate later protocols.

## Integrity and release
Model/source/dataset/candidate SHA pins, complete 2,048-screen raw records per model (eight compressed 256-family shards), exact selected-80 frozen manifest/indices, 80 treatment family records per model (four compressed 20-family shards), six frozen model hypothesis verdicts and negatives must be archived under immutable commits. The separate CPU screening verifier must check original shard hashes and selection consistency; independent treatment verifier must check raw treatment SHA and recompute all 3 hypothesis vectors WITHOUT importing the GPU runner. Every timeout/resource refusal and invalid run must be recorded. **No further assistant-invented runtime gate.**
