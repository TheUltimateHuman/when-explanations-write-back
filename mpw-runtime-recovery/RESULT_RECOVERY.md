# MPW Runtime Amendment — Recovery Checklist

**Records at start:** original MPW-102B Granite and MPW-103 Qwen jobs failed only the internally imposed timing forecast gate. Both original jobs remain untouched. Two completion jobs were submitted after the post-result correction was documented and their one-line source changes were independently hash-verified.

## Jobs
- MPW-102B Granite L4 completion: https://huggingface.co/jobs/TheUltimateHuman/6adbd71c046eb82b1ecd7858
- MPW-103 Qwen L4 completion: https://huggingface.co/jobs/TheUltimateHuman/6adbd71e046eb82b1ecd785a

Source freeze: bd9c54d9911581ca077d7f85d7122c681fd04871
MPW-102B amended SHA-256: f2d7f6d4a34ae3ebdebb44e6b6fe01856e814e00dfee089b807f20ec04cb4dfe
MPW-103 amended SHA-256: 153336fc9d93edafe1fad4d40d37d9f9cab101aa2aeda9c3c5d766e35dfd3cd4

## What must be recovered

Inspect each job (provider COMPLETED is insufficient); retrieve complete logs. Expected MPW-102B Granite tags: MPW102B_PREVALIDATION, MPW102B_CALIBRATION, MPW102B_TIMING, MPW102B_VALIDATION_START, MPW102B_SHARD_B64, MPW102B_SHARD, MPW102B_PRIMARY_RESULT, MPW102B_END. Four shards of 48 family records = 192. The identical model/data/case manifest must match the original frozen MPW-102B study at 5604b42d0264c5ddf228a649e3847ab392b57116d89aaf3c0b625407583928ce.

Expected MPW-103 Qwen tags: MPW103_PREVALIDATION, MPW103_CALIBRATION, MPW103_TIMING, MPW103_VALIDATION_START, MPW103_RECORD_B64, MPW103_SHARD, MPW103_PRIMARY_RESULT, MPW103_END. Four shards of 32 families =128. Case manifest must match 370a225c22762ba97f4bac87692a9ff6cab032713d467f6a040ebcfd96d4f08b.

For each:
1. Recover all base64/gzip shard chunks in order by their emitted internal part index, **not** provider log ordering.
2. Verify each decompressed shard SHA-256 against the actual emitted anchor. Verify the concatenated raw JSONL SHA against the job's MPW102B_END or MPW103_END raw_sha256. Check exact record count and distinct family identifiers.
3. Store all original compressed raw chunks unmodified on a new Git commit in this branch under mpw-runtime-recovery/results/ and create a machine-readable results manifest including original and amended job references.
4. Recompute MPW-102B family-level H1 and H2 with the *existing* mpw102b/scripts/independent_analysis.py from the source freeze; recompute MPW-103 family-level H1-H4 with the *existing* mpw103/scripts/independent_analysis.py from source freeze. These were authored before the current amendment and must not be revised to fit results.
5. Publish every primary verdict, negative and invalidity outcome, capability/timing and numerical gates, provider billed cost if available, and the constant-only source code diff.
6. Always identify outcomes as POST-RESULT TIME-GATE AMENDMENT. They are retrospective completions on the original untested model/case cohorts, not untouched original pre-registered confirmations.

If hardware still queues, record SCHEDULING, not a GPU outcome. If a new runtime fail occurs, do not silently introduce further modifications or reruns. Keep all hashes and logs.

## Standing safeguard
No future artificial private 65-minute limit or 35%-padded veto when the unpadded forecast fits a provider window. Use mpw-runtime-recovery/scripts/runtime_policy.py and its regression tests before any new freeze. Budget decisions are distinct from the research hypothesis's acceptance conditions.
