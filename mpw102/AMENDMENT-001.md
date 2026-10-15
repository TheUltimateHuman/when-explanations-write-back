# MPW-102 protocol amendment 001 — pre-validation tokenization failure

**Date:** 2026-10-14 CDT, before any GPU validation output.  
**Source of amendment:** CPU-only preflight job `6ad030965ccb47ba0f7a3089`.  
**Original source commit:** `75917ce719a25eaf1d571fc8123174fffd5adcf5`.

The first source-frozen preflight generated the 32 + 256 family manifest successfully, excluding all prior MPW-101 case passages, and reported full source-text disjointness. The independent third carrier pair **`1`/`2`** failed its **atomic next-token requirement** under the pinned Phi tokenizer:

- `1`: `[29871, 29896]` (two tokens)
- `2`: `[29871, 29906]` (two tokens)

The job raised `CARRIER_TOKEN_PREFLIGHT_FAILED` and terminated without loading inference model or collecting validation data. The original intended estimand requires isolated next-token logit candidates, so it would be invalid to proceed with the numeric carrier.

**Amendment:** Replace the third carrier pair `1`/`2` with **`K`/`M`**. Leave unchanged: N=256 validation, N=32 calibration, model, dataset, source-text independence rule, sampling seed, two passage orders, both report-code mappings, family-level statistic, bootstrap seed and size, inferential gates, negative controls and runtime limits. Because code-pair names are part of the family manifest, rerun CPU-only sample and tokenizer preflight, then pin the new manifest SHA in a new Git commit before any GPU validation.

This is a **pre-validation instrumentation repair**, not a successful confirmation, modification to validation data, or deletion of a failed experimental result. If K/M or another code fails the atomicity test, the gate fails again. Any further code changes must be dated and justified before GPU validation. No favorable outcome is available for tuning.
