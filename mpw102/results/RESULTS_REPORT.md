# MPW-102 — Final Results and Reproducibility Record

**Aidan Edward Lawson · Independent Researcher, Modal Path Ethics**

**Study:** Multi-Carrier, Order-Paired Mechanistic Provenance (Phase A, Phi-3.5-mini-instruct).
**Execution:** October 14–15, 2026 (local/UTC).
**Archival recovery:** October 22, 2026.
**Verdict: PRIMARY CONFIRMED — SINGLE-ARCHITECTURE / SCOPED TASK ONLY.**

## Prospective causal claim

Externally inserting a report that asserts LEFT rather than RIGHT evidence reliance changes the subsequent *input-intervention response profile* in the claimed direction, averaged over three response-code pairs, reversed code-meaning mappings, and both physical passage orders. The randomized family—not one intervention branch—is the statistical unit. Protocol, dataset/model pins and all primary gates were frozen before validation in commit [817a15118286553bb1758d8f4d47803ae06a9147](https://github.com/TheUltimateHuman/when-explanations-write-back/commit/817a15118286553bb1758d8f4d47803ae06a9147). There is **no OSF registration**.

## Primary results

| Measure | Verified result |
| --- | ---: |
| New validation families | 256 |
| Overall same-sentiment baseline accuracy | 92.7734% |
| LR passage-order accuracy | 91.40625% |
| RL passage-order accuracy | 94.140625% |
| Mean report-meaning D contrast | +0.02711761 |
| 95% bootstrap CI (50,000 family resamples) | [0.02403376, 0.03029471] |
| Positive / negative families | 243 / 13 |
| Two-sided exact sign-test p | 4.3583932e-56 |
| Numerical repeat discrepancy | 0 |
| Raw unnormalized J contrast (supporting) | +1.49858 |

All three prespecified carrier means were positive: AB +0.02578, XY +0.02620, KM +0.02937. Both prespecified passage-order means were positive: LR +0.03260, RL +0.02164. The preregistered-in-Git primary gates were all met.

A prior CPU-only preflight found numeric response codes 1 and 2 were non-atomic tokens. A dated prevalidation amendment replaced those with K/M and a new CPU preflight passed. That failed preflight remains in the provenance ledger.

## Active controls and caveats

Neutral and label-aware acknowledgments also caused material, order-sensitive shifts. Content-free code effects were heterogeneous across carrier/order cells. These are real causal inputs, so a near-zero grand average does not make any particular placeholder inert. Reversing response-code meanings defeats a stable additive carrier-token main effect as a complete explanation, but does not eliminate all nonlinear interactions among code, mapping instructions, and context.

Near-saturation was present in 102 of 512 order-specific baseline audits (absolute D >= 0.95); 85 of 512 baseline audits had a nonpositive intervention effect for at least one channel. None was excluded after observing outcomes.

## Raw data and independent replication of the analysis

Original GPU job: [6ad0329e5ccb47ba0f7a3139](https://huggingface.co/jobs/TheUltimateHuman/6ad0329e5ccb47ba0f7a3139).

All 256 family records were preserved in four compressed 64-family shards, with SHA-256 per shard and for the concatenated raw JSONL:

6b7164146f594392db8d1545892bcc0f3ecccf79f0c7d2585c7cc3e55a523469

Immutable independently verified archive: [commit 005673b5517e706be737d4283b7d24ebd7092d01](https://github.com/TheUltimateHuman/when-explanations-write-back/tree/005673b5517e706be737d4283b7d24ebd7092d01/mpw102/results).

Independent CPU verifier: [6adae7b1925af0e27d4facf7](https://huggingface.co/jobs/TheUltimateHuman/6adae7b1925af0e27d4facf7). It recovered and validated all four raw shards and their combined raw digest, checked the independent analysis source, and reproduced every primary statistic and verdict. It did not import the model runner.

Reproduce with the archived verify_from_archive.py and independent_analysis.py, run with uv and give the frozen archive commit ID as argument.

## Explicit boundaries

The earlier natural-report experiment MPW-101 was **PRIMARY NOT CONFIRMED** (18 conversions, 11 losses, paired p=0.26493). MPW-102's positive forced-report contrast neither contradicts that outcome nor rescues it.

This is one model on experimentally constructed redundant SST-2 sentiment inputs sampled disjointly from earlier study cases. Study-text disjointness does not establish pretraining non-exposure. No distinct-architecture confirmation, privileged introspective readout, localized neural-circuit rewriting, model-parameter change, persistence after deletion, or iteration-induced self-validation has been established. Ordinary language-conditioned steering remains a possible mechanism.

**Research decision:** PRIMARY CONFIRMED / ARCHIVE VERIFIED, confined to this operational contrast. Next: a new prospective distinct-model replication and sharper elicitation-versus-response and explanatory-versus-imperative controls.
