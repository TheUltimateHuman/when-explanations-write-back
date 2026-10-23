# MPW-103 — Execution and Recovery Handoff

**Status when authored:** Frozen GPU jobs accepted, no validation outcomes yet.  
**Study:** Sequential Mechanistic Provenance, Phase A — externally imposed report histories.

## Jobs and frozen source

- Qwen3 L4 GPU job [6adbb3371e112550ce7d7e4d](https://huggingface.co/jobs/TheUltimateHuman/6adbb3371e112550ce7d7e4d).
- Granite L40S GPU job [6adbb3381e112550ce7d7e50](https://huggingface.co/jobs/TheUltimateHuman/6adbb3381e112550ce7d7e50).
- Both run mpw103/scripts/mpw103.py from immutable Git commit **80a1015c044d352264b43f9b188ec6be52001e6b**.
- Executed source bytes SHA-256 **78d24e2990fb1d24e9caddd2ce5b161c9554adfebf74ec9b9ab3f83894621bba**.
- Fresh 32+128 family manifest **370a225c22762ba97f4bac87692a9ff6cab032713d467f6a040ebcfd96d4f08b**.
- Model SHAs: Qwen cdbee75f17c01a7cc42f958dc650907174af0554, Granite 51dd4bc2ade4059a6bd87649d68aa11e4fb2529b.
- Data SHA 8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb.

## What to inspect in order

1. Inspect GPU job current status. A provider stage of COMPLETED is NOT by itself evidence of completing the scientific study.
2. Retrieve the **complete** plain logs for each job, not truncated tail entries; classify MPW103_PREVALIDATION, MPW103_HARDWARE, MPW103_CALIBRATION, MPW103_TIMING, MPW103_VALIDATION_START, MPW103_PROGRESS, MPW103_RECORD_B64, MPW103_SHARD, MPW103_PRIMARY_RESULT, and MPW103_END.
3. If an outcome fails at capability, token, context, runtime or data integrity gate, record its exact error and zero validation; **no attempts to rescue with outcome-dependent changes**.
4. For any valid completed run, require exactly four original _SHARD anchors (part=0..3, 32 families per shard) and all associated ordered 10,000-character Base64 component messages for the same raw SHA.
5. Concatenate chunk payloads by ascending internal part index within each block (do not trust generic log order). Preserve exact Base64 gzip bytes as separate files named mpw103/results/<model>_shard01.jsonl.gz.b64 through shard04.
6. Verify gzip-decompressed shard SHA-256 against the runner's _SHARD record and that concatenated raw JSONL bytes match the _END raw_sha256. N=128 and indices must cover the exact frozen validation families 32..159.
7. Preserve raw shards in a new Git branch created from this prevalidation branch, along with a RESULTS_MANIFEST.json that anchors original job ID, model revision, source SHA, case manifest, per-shard SHA, combined raw SHA, independent-analysis source SHA and n.
8. The independent analysis source is mpw103/scripts/independent_analysis.py. The full verifier mpw103/scripts/verify_archive.py takes an immutable Git commit and model name. Run CPU verification against exact committed archive. It must check all 4 shards and rederive family H1–H4 and all validity gates from raw observations without importing the original model inference runner.
9. Report eight model-level hypothesis outcomes and both conjunctive gates (H1+H3 cross-model, all eight tests). Preserve failures, nulls, invalidity, saturation, active neutral controls, mapping/order/final-report heterogeneity, and descriptive baseline-versus-post-history fidelity transitions.

## Confirmation must retain narrow scope

Even all eight positives only support a sequential *externally imposed* report-history effect and controls, not an endogenous repeated explanation, protected long-term memory, independent feature-circuit localization or autonomous self-validation. Prior art on fabricated self-statement histories and conversational history effects must be included. MPW-104/105 must explicitly test false-report uptake and evaluator score manipulation.

## Prior-art reminders
- Chen et al., "Can self-statements modulate AI? investigating pseudo-cognitive autosuggestions in large language models", Neurocomputing 2026, DOI 10.1016/j.neucom.2026.133792.
- Simhi et al., "Old Habits Die Hard: How Conversational History Geometrically Traps LLMs", ICML 2026, PMLR 306.

## Budget and status
Qwen L4 75m platform timeout, Granite L40S 100m platform timeout. Frozen study's list-rate hard ceiling approximately $4 GPU combined, actual billing distinct. Both may queue. Do not claim validation outcomes until recovered.
