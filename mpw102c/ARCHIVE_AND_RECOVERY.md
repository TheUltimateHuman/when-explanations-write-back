# MPW-102C — Raw Artifact Recovery and Release Contract

The GPU job runner was prospectively frozen at Git commit b02449a43edbdc4332d893d69a269f954e3d1e42.

## Original job identities
- Granite L40S: https://huggingface.co/jobs/TheUltimateHuman/6adb93921e112550ce7d6a2e
- Qwen3 L4: https://huggingface.co/jobs/TheUltimateHuman/6adb939b046eb82b1ecd5a01

Each job is allowed to enter the validation phase only after its own 32-family calibration and 4-family complete-treatment runtime gates pass. In particular, a Hugging Face status of COMPLETED can reflect a clean gate refusal with no validation, as happened in MPW-102B Granite.

## Conditional artifact recovery, without changing the run
- Capture complete job logs. Look for MPW102C_PREVALIDATION, _CALIBRATION, _TIMING, _VALIDATION_START, _PROGRESS, _SHARD_B64, _SHARD, _PRIMARY_RESULT, and _END.
- Only use _SHARD_B64 blocks if the corresponding _SHARD SHA and n=40 are present. Exactly four 40-family shards must reconstruct the original 160-family JSONL. Their combined hash must equal the raw_sha256 emitted in _END.
- If a model stops at a gate, archive logs including its prevalidation metadata, calibration and timing and record no validation. Do not synthesize missing records.
- Do not cherry-pick families, carrier mappings, presentation orders, models or hypotheses. Preserve full 10-treatment counterfactual branches for each successful model and negative controls.
- Archive raw shards and RESULTS_MANIFEST.json at a new immutable Git commit without changing source.
- Run the independently implemented mpw102c/scripts/independent_analysis.py on the full raw JSONL (it does not import the model runner). Or run the separately prepared verify_from_archive.py with an immutable result commit and model name. The independent SHA check, model calibration status and all three statistical gates must pass before any success claim.
- Record every model H1/H2/H3 result and the two-model conjunctive gate. For person-specific comparisons, report the planned H3 separately; any further contrasts are explicitly exploratory.

## Primary reproducibility pins
- MPW-102C case SHA-256: 55435add76c33a0a6eafedb1e4044902025ed4c1a41d37df9d8514f6372a5ff1
- Runner SHA-256: a6951dfa98ca00ddf02e50bf09798b09d38ff3845cfaff3583ce3948f0ec8b6a
- Qwen model revision: cdbee75f17c01a7cc42f958dc650907174af0554
- Granite model revision: 51dd4bc2ade4059a6bd87649d68aa11e4fb2529b
- Data revision: 8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb
- 160 held-out families (32..191), both physical orders, 50,000 family bootstrap resamples.
- Six prospectively defined model-level hypothesis gates with familywise alpha .05/6.

No outcome should be called confirmed based solely on job runner logs without reanalysis from complete hash-verified raw observations.
