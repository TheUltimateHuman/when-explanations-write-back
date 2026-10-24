# MPW-104 — GPU Execution and Raw-Data Recovery Handoff

**Study:** The False Explanation, prospective Phase A. Category: RESEARCH ARTIFACT. Prevalidation lock and exact source at Git commit c94d1299e8862686bb728880c3f36a1527e7b7c0.
**At handoff creation:** both GPU jobs submitted, scientific outcomes UNKNOWN until complete raw records are verified.

## Original GPU jobs
- Qwen3-4B-Instruct (L4): https://huggingface.co/jobs/TheUltimateHuman/6adc12a1046eb82b1ecd97a7
- Granite-3.3-8B-Instruct (L40S): https://huggingface.co/jobs/TheUltimateHuman/6adc12a31e112550ce7dba2d
- Both use exactly mpw104/scripts/mpw104.py from commit c94d1299e8862686bb728880c3f36a1527e7b7c0, 90m provider hard timeout, no separate 65m runtime veto.
- Executing source SHA-256: d8866d46dcb4bc6f5e2289108c22c434add56c423e63f1731c929aed86d6d1e1.
- Independent analysis code SHA-256: 797effb9607a1fdc26b20971b8fbbb85c0f79f2e591ab0e979696a9736e7bcfd.
- Independent archival verifier SHA-256: b3131fbe22385506e72e342ffb6782d12f5ec38dfbd3998d519e227c795d58d6.
- Fresh sample manifest SHA-256: f80ccf2b2901acdc7d8fbd7ad8df3edcc297a14b97fb5b2e7a26da0576d3a97d.

## How to close out
1. Inspect both Hugging Face job IDs. Provider status COMPLETED may indicate an early scientific or resource gate exit; locate MPW104_END and MPW104_VALIDATION_START explicitly.
2. Obtain **complete logs** using the Hugging Face jobs connector (avoid truncated tails). Extract events MPW104_PREVALIDATION, _HARDWARE, _CALIBRATION, _TIMING, _VALIDATION_START, _PROGRESS, _RECORD_B64, _SHARD, _PRIMARY_RESULT, _END.
3. No validation or fewer than 128 families is NOT a negative primary. Report CAPABILITY_GATE_FAIL or RESOURCE_REPLAN or TIMEOUT separately, with original data/logs.
4. For each complete valid run, recover the **four original 32-family compressed raw shards**, joining all MPW104_RECORD_B64 components by internal part number, grouped by original SHA. Check each decompressed shard SHA-256 against the matching MPW104_SHARD record (n=32, range 0–31,32–63,64–95,96–127) and the concatenated raw JSONL SHA against MPW104_END raw_sha256. Verify indices 32..159 and exactly 17 conditions per physical order; no hidden family exclusion.
5. Commit the untouched original compressed Base64 shard bytes to mpw104/results/{model}_shard01.jsonl.gz.b64 through shard04 plus RESULTS_MANIFEST.json including frozen sample/model/source/revisions, original job ID, per-shard raw SHAs, combined raw SHA, independent analysis code SHA.
6. Run mpw104/scripts/verify_archive.py <immutable_results_git_commit> <model> as a separate CPU job. It downloads all four immutable original shards, verifies SHA anchors and imports only mpw104/scripts/independent_analysis.py to recompute H1/H2/H3; not the GPU runner. Require exact replication of all model-level estimates, CIs, sign p-values and invalidity verdicts before claiming success.
7. **Never suppress an INVALID result**. MPW-102B Granite was invalid for accuracy/numerical repeat under earlier frozen gates; MPW-104 also has accuracy >=.90 separately LR/RL and max repeat D delta <1e-4 across all validation cases. A positive raw effect on an invalid model cannot rescue it. H2 can be INDETERMINATE_CAPABILITY for too few baseline-known cases.
8. Declare all outcomes and known near prior-art collisions. A forced false report coming to agree with later causal dependence is a writeback result, not proof of the model's spontaneous self-validation, introspection or persistent weight change.

## Frozen 104 endpoints and control hierarchy
- H1 directional false REPORT minus false arbitrary-code sham, all 128 families.
- H2 strict-baseline-known false-sign crossing report minus sham, >=64 eligible families and >=40 each physical order.
- H3 free-text false self-declarative minus false self-reference, all 128.
- Six family-level model tests total, Bonferroni .05/6; lower 99.1667% family-bootstrap CI>0, exact family sign-test p<.0083333, positive both physical orders.
- True report, true formatting-code, false/true imperative and matched natural-language references are diagnostic controls and are never promoted post hoc to confirmations.

## Resource policy
No arbitrary assistant-chosen 3,900-second cutoff. The 35%-padded throughput forecast is informational. If the unpadded forecast does not fit the real 90m provider timeout less the 120sec archival reserve, report RESOURCE_REPLAN and preserve calibration. No extra paid retry to seek a desirable result.
