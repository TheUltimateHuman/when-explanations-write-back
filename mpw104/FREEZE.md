# MPW-104 Prospective Prevalidation Freeze

Study: The False Explanation — Protected-Baseline Conversion.
Date: October 23, 2026 (CDT).
Status: SOURCE AND SAMPLE FROZEN BEFORE GPU INFERENCE. No MPW-104 validation outcomes available.

## Frozen identities
- Protocol: mpw104/PROTOCOL.md, initial commit dac5166ce07cae787861b31d239391a4807c4af6.
- Executing runner: mpw104/scripts/mpw104.py, last source update commit 874ba1448ff04a459a214ac0dc16562b92b80565.
- Runner exact SHA-256: d8866d46dcb4bc6f5e2289108c22c434add56c423e63f1731c929aed86d6d1e1.
- Source prevalidation SHA before inserting case hash: bd51bb22cee3d2e347598ad45becea48e3bedc2081a9edb21df6307b030a2164.
- Independent analysis SHA-256: 797effb9607a1fdc26b20971b8fbbb85c0f79f2e591ab0e979696a9736e7bcfd.
- Archive verifier SHA-256: b3131fbe22385506e72e342ffb6782d12f5ec38dfbd3998d519e227c795d58d6.
- 32 calibration + 128 fresh validation case manifest SHA-256: f80ccf2b2901acdc7d8fbd7ad8df3edcc297a14b97fb5b2e7a26da0576d3a97d.
- 640 new distinct passage strings; 5576 historical text keys excluded. MPW-101, 102A/B/C, 103 sample manifests regenerated and checked.
- Dataset stanfordnlp/sst2 revision 8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb.
- Qwen model Qwen/Qwen3-4B-Instruct-2507 revision cdbee75f17c01a7cc42f958dc650907174af0554.
- Granite model ibm-granite/granite-3.3-8b-instruct revision 51dd4bc2ade4059a6bd87649d68aa11e4fb2529b.

## CPU-only prevalidation evidence
- HF sample/tokenizer/context preflight job 6adc118d046eb82b1ecd975d: PASSED, no inference. Both A/B and positive/negative candidates atomic.
- Qwen max rendered context 281 tokens; Granite 358; frozen hard context maximum 1024.
- Synthetic independent-analysis positive, negative, and low-eligibility tests: HF job 6adc11a1046eb82b1ecd9761 PASSED. Synthetic data are not empirical results.
- Source/hash audits: jobs 6adc1240046eb82b1ecd9786 and 6adc12711e112550ce7dba27 PASSED.

## Frozen inference design
Each family receives protected untreated A0 and exact independent repeat under both physical passage orders. False/true side is selected from the protected original A0 before any report insertions. All 17 treatment arms per order, both A/B meaning mappings, three input-causal intervention margins per arm, raw J, and complete baseline diagnostics are retained.

Three hypotheses per model, six Bonferroni controlled tests at alpha .00833333333. H1 directional movement toward previously false evidence reliance after externally imposed false report versus arbitrary-code sham, all 128 families. H2 actual false-to-apparent-true sign crossing excess over sham among baseline-known cases, with predeclared minimum eligible families and orders. H3 false first-person description versus person-matched reference, all 128 families. Family-bootstrap 50,000 draws, 99.1667% percentile CI, exact family sign-test, and separate positive means for both physical orders.

Model validity: untouched task accuracy >=.90 in EACH order; maximum untouched repeat difference in D less than .0001 for ALL 128 families; all 17 arms complete and finite. Capability calibration 32 families, >=.90 per physical order and sensitivity >=1. H2 INDETERMINATE_CAPABILITY if fewer than 64 known baseline families or 40/order. No threshold changes after outcomes.

## Runtime-policy fix
L4 Qwen and L40S Granite, each with an actual 90-minute provider hard timeout, 120 seconds archival reserve only. The timing probe prints observed and 35% padded forecasts but does NOT impose the arbitrary 3900-second internal gate. Only unpadded physical infeasibility against actual provider hard timeout may cause RESOURCE_REPLAN. Maximum list-rate hardware exposure ~US$3.90; not a billing receipt.

This is an experiment on externally imposed report text and subsequent input-causal response profiles, not on spontaneously generated model explanations, privileged introspection, learned parameters, persistent memory or optimizer-mediated evaluator corruption. No external OSF registration.
