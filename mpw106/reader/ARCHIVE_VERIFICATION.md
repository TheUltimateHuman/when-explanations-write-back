# MPW-106 archive-based verification — 2026-11-06

## Result

**PASS.** The unchanged frozen `mpw106/scripts/verify_reader.py` ran successfully against immutable original reader archive [d209d440ef09e75be3d2c076a0ba533f71eb3e8f](https://github.com/TheUltimateHuman/when-explanations-write-back/commit/d209d440ef09e75be3d2c076a0ba533f71eb3e8f), returned `MPW106_READER_INDEPENDENT_VERIFIED`, exit code 0, and `valid: true`. The archive gate identified by the November 5 recovery audit is now complete.

- Qwen H1: **CONFIRMED under the frozen decision rule**. Mean report-signed LIVE-minus-NEUTRAL normalized source-dominance contrast 0.12461084020151117; familywise 99.1667% bootstrap CI [0.012197469051895051, 0.24350580311765138]; exact two-sided sign p=0.0002642786618272985. Family signs 45 positive, 16 negative, 3 zero. Both order means positive (LR 0.0936223367307423, RL 0.15559934367227998).
- Qwen H2 and H3: **INDETERMINATE_CAPABILITY**, because 15 originally false parseable reports fall below the frozen minimum 16. These are not null results.
- Granite: **INVALID_BASELINE_DRIFT** in original writer; no memory or reader results. Not a scientific null or replication.

## What this establishes

For this fixed Qwen cohort, retrieving prior model-authored explanations from external Git memory in a separate fresh model process steered the input-intervention source-dominance measure toward the explanation's stated side more than a neutral note. This is a narrow external-retrieval result, not internally stored memory, changed weights, privileged introspection, autonomous memory writing, pure semantic causation, or spontaneous correction. LIVE/NEUTRAL length and wording differ, so the result does not isolate explanatory semantics. The normalized contrast is not a probability or percentage accuracy improvement.

Aggregate native-report fidelity remains 46/64 in every arm; LIVE has two conversions and two losses. DELETED equals explicit MISSING, and LIVE equals EXPLICIT_STALE, in the frozen checks. Active lookup deletion does not erase old Git history and does not numerically restore CLEAN. Correction is externally authored oracle content, not self-repair.

## Verification and provenance

The exact original four compressed shards were archived without regeneration. Their compressed and raw SHA-256 checks, whole reader digest, unchanged independent-analysis hash, historical selection and four-snapshot revision chain all pass the original archive verifier. Combined reader SHA-256: `33280f6b99dd6355a1b8aa287ab7a9bb6bda94819d8e314aa7e55baf23cb9df8`.

The verifier was downloaded from the immutable archive commit and byte-compared to the exact frozen Git source, SHA-256 `654694594f2fcad00c9d5a4a7c417783492c8442c8c018d2ebbeebe2d66885c0`. Analysis SHA-256 remains `a3b3141a134d5d30b16798bedd0f6d6e43ee216408aeb0659303f65e6c1f29b0`. NumPy 2.1.3 and SciPy 1.15.3 were used. The unmodified verifier fetched its inputs over HTTPS from the immutable Git archive and historical commits, not from substituted local fixtures. Exact output and execution metadata are in `verification_20261106/`.

No GPU inference, model rerun, provider job or new experimental spending was initiated. No source, hypothesis, cohort or decision threshold was changed. This is an independent archive reanalysis of existing inference, not a new model replication. The original pre-treatment lookup failure and separate four-site execution amendment remain preserved. The dated recovery audit remains unchanged and its calibration/prefix-reconstruction and interpretation limitations still apply.

## Reproduce

Download `mpw106/scripts/verify_reader.py` from the archive commit and run:

```sh
uv run verify_reader.py d209d440ef09e75be3d2c076a0ba533f71eb3e8f qwen3
```

The script's inline dependency pins specify NumPy 2.1.3 and SciPy 1.15.3. This report is a follow-on commit; the immutable input archive it verifies is identified above.
