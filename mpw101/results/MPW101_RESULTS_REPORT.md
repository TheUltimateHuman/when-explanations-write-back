# MPW-101 — Prospective Natural-Report Fidelity-Transition Replication

**Investigator:** Aidan Edward Lawson · Independent Researcher, Modal Path Ethics  
**Execution:** 14 October 2026 CDT / 15 October 2026 UTC  
**Status:** COMPLETED; **PRIMARY NOT CONFIRMED**  
**Research parent:** *When Explanations Write Back: Mechanistic Provenance for Language Models*, v1.1 (October 2026)

## 1. Executive ruling

MPW-101 completed an unmodified, prospective 256-family primary analysis after the publicly timestamped protocol and sampling commitment were frozen. Phi-3.5-mini-instruct met calibration and validation competency gates. Natural-report fidelity increased from **133/256 (51.95%)** against the pre-elicitation mechanism to **140/256 (54.69%)** after the question and naturally selected report were inserted, a net **+7/256 = +0.02734**. Eighteen family reports changed from unfaithful to faithful, while eleven changed from faithful to unfaithful.

This failed the locked primary rule:

- Paired exact two-sided McNemar test: **p = 0.2649308965**.
- 95% paired-family percentile bootstrap CI for net change: **[-0.01171875, 0.06640625]**.
- The lower CI endpoint is negative, and p exceeds 0.05.

**Verdict: PRIMARY NOT CONFIRMED.** This is an interpretable failed confirmation attempt. Neither a successful job nor a favorable secondary analysis can change it.

## 2. Provenance and preregistration status

The prospective source files were committed to a public Git branch *before MPW-101 validation data were generated*. No OSF preregistration was filed; the Git history is the timestamped research commitment, not an OSF badge.

- Frozen source commit: `2e650115db72b72ee5a03ae759326b7db1a19c20`.
- Frozen runner SHA-256: `2f099745a19aea2241ec2821ac5e4632206ff6068ab93759e2a6ca40cac476d9`.
- CPU preflight: `https://huggingface.co/jobs/TheUltimateHuman/6ad01fb4c66288145224914c`, completed before GPU validation.
- GPU experiment: `https://huggingface.co/jobs/TheUltimateHuman/6ad0205b5ccb47ba0f7a2a2f`, status COMPLETED.
- Model revision: `microsoft/Phi-3.5-mini-instruct` @ `2fe192450127e6a83f7441aef6e3ca586c338b77`.
- Dataset revision: `stanfordnlp/sst2` @ `8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb`.
- Python 3.12.12, Torch 2.6.0+cu124, Transformers 4.49.0, CUDA 12.4, NVIDIA L4.
- Sampling seed 2026101501; bootstrap seed 520261015.
- Manifest SHA-256: `9559ac6421cb4c5498009b25831766bbdbd5a3fa563083ce9eecfaadde6dda3f`.
- Validation-record SHA-256: `35a86479177dd7089878e66e0d23d7ba8bc95ee3ba32c8320c4eec1517e50885`.

The runner enforced the preflight manifest hash and verified pinned revisions before audit. The 288 families consisted of 32 calibration and 256 validation families with 1,152 unique passages. Passages came from the **SST-2 training split**, excluding the entire SST-2 validation split and the reconstructed original PR-002 calibration text; the pool was free of within-run passage duplicates. This differs from the original PR-002 validation-split design. This is a *fresh-to-the-study* sample, not a claim of immunity to model-pretraining contamination.

## 3. Calibration and execution

| Measure | Outcome |
| --- | ---: |
| Calibration families | 32 |
| Calibration accuracy | 93.75% — PASS |
| Calibration mean intervention sensitivity | 58.13623 — PASS |
| Validation families | 256 |
| Validation same-sentiment accuracy | 96.875% — PASS |
| Mean validation intervention sensitivity | 58.74695 |
| Maximum repeated-baseline numerical discrepancy | 0 |
| Full script runtime | 351.11 seconds |
| GPU hardware | NVIDIA L4 |

An eight-hour GPU timeout enforced the agreed $10 overall credit ceiling; the job completed in about six minutes of script runtime. The provider's listed L4 rate was $0.80/hour; a runtime-based computation is not an account billing receipt.

## 4. Primary 2 × 2 table

| Fidelity to pre-elicitation target | Fidelity after question + natural report | Count |
| --- | --- | ---: |
| Unfaithful | Unfaithful | 105 |
| Unfaithful | Faithful (conversion) | 18 |
| Faithful | Unfaithful (loss) | 11 |
| Faithful | Faithful | 122 |

Baseline fidelity: `q = 133/256 = 0.51953125`.  
Post-writeback fidelity: `s = 140/256 = 0.546875`.  
Conversion mass: `C = 18/256 = 0.0703125`.  
Fidelity-loss mass: `L = 11/256 = 0.04296875`.  
`tau = C − L = 0.02734375`; and `s = q + C − L` exactly.

The predeclared primary definition counted report agreement only when `report_sign * D > 0`, with ties unfaithful. The treatment compares the untouched baseline against **question plus answer writeback**. It does not separately identify a pure answer-token effect, and does not establish privileged introspection or localized neural-circuit rewriting.

## 5. Prespecified secondary thresholds — no rescue

| Alignment threshold δ | Conversions | Losses | Net fidelity change | Exact two-sided p |
| ---: | ---: | ---: | ---: | ---: |
| 0 (primary) | 18 | 11 | +0.02734 | 0.26493 |
| 0.02 | 20 | 9 | +0.04297 | 0.06143 |
| 0.05 | 24 | 8 | +0.06250 | 0.00700 |
| 0.10 | 23 | 7 | +0.06250 | 0.00522 |

The 0.05 and 0.10 secondary diagnostics exhibit stronger positive changes than the zero-threshold criterion. Their confidence intervals from the preregistered script are respectively `[0.01953125, 0.10546875]` and `[0.0234375, 0.10546875]`.

This threshold dependence is a finding worth investigating, not a substitute for the failed primary test. These contrasts may reflect shifts in *strength* of alignment that do not translate into robust sign conversion at zero, as well as threshold geometry, carrier/context interactions, or other causes. Identifying the mechanism requires a new frozen experiment.

## 6. Supporting causal-dependence results

The separately specified counterfactual report-meaning statistic remained positive on fresh families, matching the qualitative earlier PR-002 observation:

| Secondary quantity | Observed mean | Additional descriptive finding |
| --- | ---: | --- |
| Meaning-balanced report contrast | +0.030218 | Positive in 225/256 families |
| Mapping M1 | +0.031984 | Positive in 199/256 |
| Reversed mapping M2 | +0.028452 | Positive in 178/256 |
| Content-free A-minus-B carrier control | +0.033213 | Nonzero, substantial carrier effect |
| Continuous natural-report alignment shift | +0.063407 | Positive in 155/256 |

The mapping-specific contrasts agreed in sign within 131/256 families (51.17%). These are population-level patterns, not deterministic per-family rules. The content-free perturbation is of comparable order to the meaning-balanced mean, so single-carrier inference is unsafe. Mapping reversal cancels a stable additive token effect, while other token-by-context interactions remain possible.

Natural reports named LEFT in only 45/256 families (17.58%), indicating substantial asymmetry in report selection. These quantities are supporting or exploratory; none was allowed to replace the primary conversion endpoint.

### Post hoc metric pressure checks

For the meaning-balanced counterfactual contrast:

- Restricting to families with positive LEFT and RIGHT intervention effects in all four meaning branches: **n=188**, mean **+0.03763**, 172 positive.
- Restricting to unsaturated families (`|D| < 0.95` in all four meaning branches): **n=177**, mean **+0.03948**, 163 positive.
- Unnormalized causal-margin counterpart: mean **+1.61493**, positive in 232/256 families (one exact-zero case).
- Baseline families with a negative intervention effect on at least one side: 51/256.
- Baseline dominance saturation `|D| >= 0.95`: 59/256; selected-report state: 73/256.

These were calculated **after** collecting the 256 records and are *post hoc* robustness checks, not registered evidence of a new primary claim.

## 7. Independent recomputation

A separate analysis reconstructed all 256 rows from the retained Hugging Face logs and recomputed the 2×2 table, exact paired-test p, threshold counts, continuous effects, and diagnostic strata. The independent exact test matched the runner to full displayed precision. A separate 100,000-resample bootstrap using a different pseudorandom generator yielded 95% CI `[-0.01171875, 0.0703125]`, with the same failed primary verdict.

An independent UTF-8 SHA-256 implementation hashed the newline-joined log records and obtained the **exact** job-record digest:

`35a86479177dd7089878e66e0d23d7ba8bc95ee3ba32c8320c4eec1517e50885`.

All 256 family records are archived on the prospective study branch as four 64-family JSONL segments, in order:

- `results/families_part01.jsonl`
- `results/families_part02.jsonl`
- `results/families_part03.jsonl`
- `results/families_part04.jsonl`

Concatenate them in ascending filename order with no extra separators and compute SHA-256. The hash must match the value above. The old PR-002 source and observations were not modified.

## 8. Scientific conclusion and next experiment

**The tested binary natural-report fidelity-conversion hypothesis was not confirmed in a fresh 256-family prospective Phi sample.** More demanding alignment thresholds and a counterfactually balanced report-meaning statistic nevertheless remained positive as secondary evidence. Those results support continued investigation of *graded alignment*, report-meaning versus physical carrier interactions, and the distinction between elicitation effects and answer writeback.

The appropriate next pass is **MPW-102: Multi-Carrier Causal Attribution and Graded Fidelity**, with the new primary target frozen prospectively. It should include multiple independent carrier alphabets, matched elicitation-only and content-free branches, calibrated continuous-effect measurements, natural report selection that does not import an artificial question bias, and at least one independent model family. The present dataset may inform design and power assumptions but must never serve as its confirmatory set.

This record does **not** establish long-term accumulation, iterative self-validation, mechanistic rewiring of hidden neural circuits, model introspective privilege, or universal failure of post-writeback audits. It supplies an audited negative primary result and a set of bounded follow-up hypotheses.
