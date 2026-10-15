# MPW-102 Phase A — Source-Bound Results Report

**STATUS: PENDING RAW RECORDS AND INDEPENDENT VERIFICATION.** This template is not evidence. Do not supply favorable numbers from MPW-101, MPW-101E, or calibration as a proxy for MPW-102 validation.

## Exact research object

The effect of forcibly inserted report meaning on later LEFT/RIGHT input-level logit-margin intervention dependence, averaged per independent natural-language paired-sentiment family across 3 independently encoded report token pairs, 2 code-to-side mappings, and 2 passage presentation orders. This cannot directly establish introspective self-readout, fixed-weight neural circuit localization, or universal semantic manipulation.

## Provenance audit

| Requirement | Required evidence | Outcome |
|---|---|---|
| Frozen Git commit | `817a15118286553bb1758d8f4d47803ae06a9147` | Confirm source SHA after execution |
| Frozen source SHA256 | `36f2125299ac918db044359e9e8ebebe4c1e5b20029ec19e48a3cfe2f7e39118` | Verify in job log |
| Family manifest | `90ac38a668c6fa03ebdd1a37f294dc7280b24533b5d5caacbd8ed034f54549c5` | Verify in job log |
| Model / dataset revisions | Exact pinned hashes in protocol | Verify |
| Aborted first preflight | `AMENDMENT-001.md` and job log | Preserve |
| Preflight passed | job `6ad0321f5ccb47ba0f7a30e9` | PASS |
| Calibration accuracy / sensitivity | >=90% / >=1.0 | PASS (0.921875 / 53.9143) |
| Data count / completeness | 256 rows, exactly four complete compressed shards | Pending |
| Raw row digest | Match provider SHA | Pending |
| Independent recomputation | Separate script from full raw records | Pending |
| Runtime / cost | L4, 90m server/70m internal, approximate cap $1.20 GPU | Pending actual runtime |

## Primary result

**Verdict:** UNKNOWN until independent recomputation.

Record N; mean per-family mapping-balanced report-meaning effect; 95% bootstrap CI; counts of positive, negative and zero families; two-sided exact sign-test p; three carrier means and two order means. Validate that each frozen gate holds. Gate failures cannot be rescued by secondary contrasts.

## Required controls

Record both code-pair controls for every carrier, the neutral and label-aware acknowledgments, calibration/test accuracy separately by order, logit-margin sensitivity, negative interventional effects, D saturation, the raw-J effect, and untouched numerical repeats. Interrogate whether effects reduce to shared recency/format/position rather than report semantics. Do not assume any placeholder is neutral.

## Cross-family checks

Check error distributions, outliers, mapped code inversion behavior, order interactions, and robustness to limiting extreme D values. These are post hoc unless prespecified as secondary. No subgroup-based primary rescue.

## Novelty and career boundary

The study does not discover that context changes model behavior. Even a positive result establishes robustness of a specific intervention-response quantity across the measured carrier and display-order manipulations, in one model and task. A second architecture and ecological tasks remain required before stronger generality. A null result is publishable as a clean limit to a predecessor claim, provided the data and exact counterfactual design are preserved.
