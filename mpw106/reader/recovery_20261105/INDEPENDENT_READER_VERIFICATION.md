# MPW-106 independent reader verification

Verified 2026-11-05. No new model/provider jobs, reruns, spending, commits, comments, or other external writes. GitHub and Hugging Face were read only. Local CPU reanalysis used the exact frozen scientific analyzer with its pinned NumPy 2.1.3 and SciPy 1.15.3 dependencies.

## Scientific findings

The recovered Qwen reader passes the frozen record-validity checks. H1 is **CONFIRMED under the frozen decision rule** in this independent local replay. H2 and H3 are **INDETERMINATE_CAPABILITY**, not confirmed and not null findings: the originally unfaithful parseable cohort has 15 cases, below the prospectively frozen minimum of 16. The six-test Bonferroni threshold was retained despite Granite's invalidity and H2/H3 ineligibility.

H1, persistent-report steering, uses all 64 selected source families, including three unparseable reports assigned zero contribution. Each family contributes the average across LR/RL physical orders of report-side-signed D(LIVE) minus D(NEUTRAL).

- Mean: **0.12461084020151117**.
- Frozen familywise 99.1667% percentile bootstrap CI: **[0.012197469051895051, 0.24350580311765138]**.
- Descriptive 95% CI: [0.04137474073571733, 0.21232175987787164].
- Exact two-sided sign-test p: **0.0002642786618272985**, below 0.05/6.
- Family signs: 45 positive, 16 negative, 3 zero.
- LR mean: **0.0936223367307423**; RL mean: **0.15559934367227998**. Both strictly positive.
- 50,000 family-bootstrap replicates, frozen seed 520261107.

The statistic, sign counts, exact combinatorial binomial p, and percentile interpolation were independently reconstructed without invoking the analyzer's statistical helpers and agreed. The initial replay with newer installed numerical libraries gave the same values, then the final replay used the pinned versions above.

This establishes a narrow external-retrieval result: for this selected Qwen cohort, retrieving the exact earlier model-authored explanatory text from durable Git storage in a separate fresh GPU process shifts the input-intervention source-dominance score toward the report's stated side more than retrieving the fixed neutral note. It does not establish an internally stored memory, changed weights, autonomous writing, privileged introspection, pure semantic causation, or spontaneous self-correction. D is a normalized intervention contrast, not a classification probability or percentage accuracy.

## Fidelity accounting and controls

Historical native-report fidelity q = 46/64 = 0.71875. There are 61 parseable reports: 46 LEFT, 15 RIGHT, and 3 unparseable. Source true-side counts are 38 LEFT and 26 RIGHT. Labels remain exactly 32 negative and 32 positive, as selected before treatment.

For every arm, post-retrieval native-report fidelity s is also 46/64. The equal aggregate rate does not imply no change: LIVE has two conversions and two losses that cancel.

| Arm | 00 | 01 (conversion) | 10 (loss) | 11 | C | L | LR/RL sign disagreements |
|---|---:|---:|---:|---:|---:|---:|---:|
| CLEAN | 18 | 0 | 0 | 46 | 0 | 0 | 0 |
| NEUTRAL | 18 | 0 | 0 | 46 | 0 | 0 | 1 |
| LIVE | 16 | 2 | 2 | 44 | 0.03125 | 0.03125 | 4 |
| CORRECTED | 18 | 0 | 0 | 46 | 0 | 0 | 1 |
| DELETED | 18 | 0 | 0 | 46 | 0 | 0 | 0 |
| MISSING | 18 | 0 | 0 | 46 | 0 | 0 | 0 |
| EXPLICIT_STALE | 16 | 2 | 2 | 44 | 0.03125 | 0.03125 | 4 |

The table classifies the original report against protected A0 and later two-order fidelity. The 18 initially nonfaithful include three unparseable reports, whereas the eligible-for-H2/H3 candidate cohort contains only 15 parseable false reports. The identity s=q+C-L holds exactly and is accounting, not causal evidence.

Descriptively, false-report conversions in LIVE occurred at case indices 51 and 195. Initially faithful reports lost two-order fidelity at indices 586 and 621. Among the 15 false parseable reports, LIVE fidelity is 2/15, NEUTRAL 0/15, and CORRECTED 0/15. These counts do not rescue the ineligible H2/H3 hypotheses, and no additional confirmatory test was performed on them.

DELETED and MISSING have identical model-visible text, prefix hashes, and entire audit profiles for all 64 cases. LIVE and EXPLICIT_STALE likewise match exactly. DELETED does not numerically restore CLEAN: mean absolute D displacement is 0.11896058717639713, consistent with a no-record wrapper effect. Deletion means active lookup removal only; original LIVE Git history remains deliberately readable.

Mean absolute D displacement from CLEAN is 0 for CLEAN, 0.2032329241 NEUTRAL, 0.2993241189 LIVE, 0.2566782024 CORRECTED, 0.1189605872 DELETED/MISSING, and 0.2993241189 EXPLICIT_STALE. Full D/J signed and absolute diagnostics and task accuracies are in independent_audit_details.json. LIVE task accuracy is 62/64 LR and 64/64 RL, so a steering result must not be described as a general performance improvement.

## Provenance and checks performed

- Re-decoded all four writer and four reader original Base64/gzip shards; verified all eight compressed and raw SHA-256 values, sixteen records per shard, complete concatenated byte equality, and whole digests against recovered provider terminals. Reader digest: **33280f6b99dd6355a1b8aa287ab7a9bb6bda94819d8e314aa7e55baf23cb9df8**. Writer digest: **a0ae9a72fb188bf3b96f3e7e4e27895452b24c0c5c158efd467458b7a6dd84de**.
- Retrieved the immutable screen selection at 63b8e7fd4385408e724ad81e7e8fcd51b6fc043a and all four state files from their original immutable commits. Independently checked each returned Git blob SHA-1, raw SHA-256, state kind/model/bank, and canonical NEUTRAL→LIVE→CORRECTED→DELETED parent hash chain.
- Verified all 64 unique reader indices and order exactly match the screen selection; all 64 reader report texts/hashes match the original writer records; all 256 snapshot entries match the exact protocol neutral, original live, external-correction, or deleted content.
- All 128 clean baseline cells match their historical screen profile exactly, not merely within the 1e-4 tolerance; clean repeats also match exactly. Frozen analyzer validates task correctness, positive intervention channels, source sign, both-order availability, report parser/hash, all seven arms, retrieval text, and control integrity.
- Independently checked all 896 arm×order profiles: J equals I_left minus I_right; sensitivity equals the sum of absolute channels; D equals J/(sensitivity+1e-6), exactly. All recorded read snapshot references match the declared original snapshots.
- Independently reran fail-closed memory-contract tests for wrong case hash, wrong existing case ID, wrong bank, wrong model, presenting stale LIVE as DELETED, bad schema, unsupported kind, and altered content. All rejected with their expected errors. Explicit missing and deleted reads return NO_RECORD; explicit old LIVE remains readable.
- Retrieved the exact analyzer source from immutable Git and checked SHA-256 **a3b3141a134d5d30b16798bedd0f6d6e43ee216408aeb0659303f65e6c1f29b0**, identical to FREEZE.md. Verified the predeclared all-64 contribution, minimum-16 eligibility, alpha .05/6, bootstrap seed/count, sign-test and both-order decision rules against PROTOCOL.md and FREEZE.md.
- Fresh Hugging Face inspection confirms amended Qwen reader 6aea62010e0338d1bb7f7617 finished with provider COMPLETED at 2026-11-03T22:55:47.244Z. Its executed source URL uses immutable commit f997a656155af182f32ffd3ac7845a6b9d3b5883. That source is byte-identical to the later owning-head copy, Git blob 53a77bcc1f26fe94bc56d8c560bee4c63b8ff6af. The original log source SHA matches **ce0a1c7a93ac142152b6114949c4bdbd0e9e8166ab4f451cb8ad7e83252fab09**. It records the expected model revision, case-bank hash, all snapshot refs, no available writer history, and final snapshot hash.

## Scope limits and remaining formal gate

1. The frozen analyzer's local scientific replay has passed, but **verify_reader.py has not been run against an immutable reader-results archive commit**. The inspected owning head 10da1059a53b74046a7baec9f0d2937a1340a8a0 contains no mpw106/reader archive. The last administrative/provenance step is to archive the already-finished original shards with a manifest, then run that unchanged verifier on the resulting immutable commit. No model rerun is needed.
2. The original recovered files named independent_analysis.py and verify_reader.py each had one extra trailing blank line relative to Git. Their semantics match, but their byte hashes do not. This audit left those files untouched and used exact Git bytes saved as analysis_source.py and verifier_source.py. Do not publish the recovered-copy hash as the frozen source hash.
3. This review did not reconstruct the entire prior-study corpus or rerun the full 2,048-family screen. It independently checked against the immutable original selection and preserved earlier screen/writer/store verification as provenance. Do not imply that the upstream data-generation/model-inference processes were newly replicated.
4. Successful reader calibration is enforced in the executed source before proceeding, but the reader source does not emit the successful numeric calibration scores or archive the calibration profiles. This review can verify the enforced gate and completed execution, not independently recover those numeric reader calibration statistics. The writer's recovered log separately reports calibration accuracy 0.9375 in each order, native parse rate 0.9375 and sensitivity 27.45654296875.
5. Recorded prefix hashes are checked for expected control equality and length by the frozen analyzer; this review did not reconstruct every original base prompt from all ancestral task sources and independently rehash each whole prefix. Model-visible retrieval text and exact executed retrieval construction were inspected.
6. LIVE and NEUTRAL differ in wording, report-side distribution and length (recovered pre-reader audit: median LIVE 236.5 characters, NEUTRAL 113). CORRECTED is explicitly external-oracle content with different authority/wording. Those are interpretive confounds, not grounds to rewrite the frozen test after outcomes.
7. Granite's original writer is **INVALID_BASELINE_DRIFT in 125/128 cells**, with no created memory or reader result. It is a validity failure, not a scientific null or failed replication. The original Qwen reader's case_sha256 KeyError is a preserved implementation failure before treatment; the amended reader is the completed scientific dataset.
8. The protocol is a prospective repository research artifact, expressly not an external preregistration. This audit does not validate novelty claims or earlier/later MPW stages.

## Reproducible local deliverables

- independent_local_result_pinned.json: complete frozen-analyzer scientific output.
- independent_audit_details.json: extra integrity checks, independent statistical replay, source URLs/hashes and D/J diagnostics.
- audit_local.py: local reproduction script. Run with NumPy 2.1.3 and SciPy 1.15.3.
- verification_inputs.json: exact connector-retrieved immutable inputs and Git blob anchors.
- analysis_source.py and verifier_source.py: exact frozen Git source bytes.
- reader_logs_verified.json and reader_inspect_verified.json: newly read provider source/terminal and operational metadata.
- Original qwen_reader_shard01..04.jsonl.gz.b64 and qwen_reader_records.jsonl remain unchanged.

## Primary evidence links

- Protocol: https://github.com/TheUltimateHuman/when-explanations-write-back/blob/10da1059a53b74046a7baec9f0d2937a1340a8a0/mpw106/PROTOCOL.md
- Freeze: https://github.com/TheUltimateHuman/when-explanations-write-back/blob/10da1059a53b74046a7baec9f0d2937a1340a8a0/mpw106/FREEZE.md
- Original selection: https://github.com/TheUltimateHuman/when-explanations-write-back/blob/63b8e7fd4385408e724ad81e7e8fcd51b6fc043a/mpw106/selection/qwen3.json
- Frozen analysis: https://github.com/TheUltimateHuman/when-explanations-write-back/blob/10da1059a53b74046a7baec9f0d2937a1340a8a0/mpw106/scripts/independent_analysis.py
- Reader job: https://huggingface.co/jobs/TheUltimateHuman/6aea62010e0338d1bb7f7617
- Executed reader source: https://github.com/TheUltimateHuman/when-explanations-write-back/blob/f997a656155af182f32ffd3ac7845a6b9d3b5883/mpw106/amendments/mpw106_reader_20261103_lookupfix.py
- Pre-reader eligibility: https://github.com/TheUltimateHuman/when-explanations-write-back/blob/10da1059a53b74046a7baec9f0d2937a1340a8a0/mpw106/store/PRE_READER_CAPABILITY_GATE.md
