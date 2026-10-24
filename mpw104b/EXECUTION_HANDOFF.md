# MPW-104B — Two-Stage Order-Stable Screen Execution Handoff

**Classification:** RESEARCH ARTIFACT / PROSPECTIVE MPW-104B.
**Status at original handoff:** SCREEN GPUs submitted. NO FALSE-REPORT TREATMENTS SUBMITTED or results observed. Model-specific selection is frozen at SOURCE/ALGORITHM level, but outcome-dependent *selected indices* do not yet exist.

## Immutable source and screen jobs
- Git source/protocol freeze: **f23419671acd425a60cd66f1c8cd173d652ba033**.
- Final executing GPU runner SHA-256: **d6f102401b4f74e543df7b4339becb5c9aa8b5bfdf2d7830a8b04b8e042d1b49**.
- Independent analyzer SHA-256 **845e49791d8a2a8bf93ca0546bf24aa1490698688c77e589d157af2f52dc68e9**.
- Screen verifier SHA **0ef866b3923dcfbfaddea72cd31b6efd913eccaa4a0f4201acfdae2363c1d4bc**; treatment verifier SHA **790fe2a10033aacd86b0a48e62b30cbf5ac42a1698d5a201d3ed7034e15e7a38**.
- Frozen source sample SHA: **86eee90fa35e92b82a653e74e473fa1cffae5cee5681ed2a88bcedd4f9682cae**.
- 64 calibration cases, 2,048 screening cases (1,024 each sentiment), 8,448 new unique texts, 6,216 historical exclusions.
- **Qwen screening L4**: https://huggingface.co/jobs/TheUltimateHuman/6adc36a3046eb82b1ecda4bb
- **Granite screening L40S**: https://huggingface.co/jobs/TheUltimateHuman/6adc36a5046eb82b1ecda4bd
- Provider timeouts 75 min each. No artificial independent 65-minute cap, 35%-padded forecast is information only; real provider feasibility may cause RESOURCE_REPLAN.

## Stage 1 recovery: do before any Stage 2
1. Inspect both job statuses and full provider logs. Identify tagged lines MPW104B_SOURCE, _HARDWARE, _CALIBRATION, _SCREEN_TIMING, _SCREEN_PROGRESS, _SCREEN_B64, _SCREEN_SHARD, _SELECTION_CHUNK, _SCREEN_SELECTED and _END. Provider COMPLETED may represent a cap/ability error: verify MPW104B_END scientific status explicitly.
2. Each fully screened model must have exactly **2,048** baseline-only family records from eight compressed shards of **256** families, tagged MPW104B_SCREEN_B64 and MPW104B_SCREEN_SHARD. Each compressed shard is encoded as multiple chunk pieces keyed by its RAW sha256 with a 0-based part and total, not necessarily by apparent output ordering.
3. Reconstruct original Base64 gzip data per shard, order pieces by part; preserve exact bytes as Git paths mpw104b/screen/{model}_shard01.jsonl.gz.b64 through shard08. Check every decompressed shard SHA and the combined 2,048-record canonical JSONL SHA against MPW104B_END.
4. Selection data are emitted as **MPW104B_SELECTION_CHUNK** (up to 9,000 chars each) with model, selection_sha256, part and total. Join these textual JSON chunks, parse the full model-specific selection manifest and verify SHA against MPW104B_SCREEN_SELECTED. The manifest has source_candidate_sha256, first 40 eligible indices per sentiment, and complete per-order baseline records. Output location mpw104b/selection/{model}.json.
5. Create mpw104b/screen/SCREEN_MANIFEST.json with case SHA, original original GPU job ID, original GPU raw SHA, eight per-shard raw SHA, original selection JSON SHA, freeze SHA and independent analyzer SHA. Commit screen raw shards + selection files + manifest to a NEW result branch to produce an immutable Git commit.
6. Run mpw104b/scripts/verify_screen.py <IMMUTABLE_GIT_SHA> <model> on CPU for each model. It independently recovers all raw 2,048 records, reproduces the screen filter without importing GPU source, and must reproduce the selection manifest exactly. Do not dispatch treatment unless verifier COMPLETED and reports **selected_n=80, 40 per sentiment class**. If fewer, SCREEN_INSUFFICIENT (not a negative scientific result).
7. Record attrition to label/accuracy, intervention sensitivity, numerical-repeat precision and physical-order sign consistency, including numbers of *eligible* families not selected; never optimize which eligible cases are chosen based on future treatment effect.

## Stage 2 treatment, ONLY after screen archived + verified
Use original frozen script:

- URI: https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/f23419671acd425a60cd66f1c8cd173d652ba033/mpw104b/scripts/mpw104b.py
- Qwen arguments: validate --model qwen3 --selection-commit <IMMUTABLE_SCREEN_RESULT_GIT_SHA>
- Granite arguments: validate --model granite --selection-commit <IMMUTABLE_SCREEN_RESULT_GIT_SHA>
- Qwen hardware l4x1; Granite l40sx1; provider hard timeout 75m each.
- The model regenerates original full 2,048 candidates from frozen sample/dataset and selects **only the previously verified 80** whose indices and sha256 match the immutable screen files. TRUE/FALSE orientation must not be changed if remeasurement differs.
- Treatment has the exact Phase A 17 arm names per physical order, both A/B mappings. Missing branches, screen-to-treatment baseline drift >=1e-4, within-job D-repeat >=1e-4, sign changes relative to screen, misclassification or nonfinite observations require INVALID. Neither screen nor treatment may drop families to gain favorable significance.
- H1: directional false report vs formatting sham on 80 selected stable cases. H2: both presentation orders × both code mappings ALL cross toward initially FALSE after report vs sham. H3: first-person declaration vs matched reference. Bonferroni 6 model tests, family bootstrap 50k and exact sign p. All negative/invalid/indeterminate outcomes preserved.
- Final treatment raw archive: mpw104b/results/{model}_shard01..04.jsonl.gz.b64 (20 families each), plus RESULTS_MANIFEST.json pointing to screen selection immutable commit. Verify with mpw104b/scripts/verify_treatment.py <RESULTS_GIT_SHA> <model> on CPU BEFORE issuing success claims.

## Prior art and interpretive boundaries
- [Phase B protocol](PROTOCOL.md) and [Phase B cited prior art](PRIOR_ART.md) explain direct collisions with the study of positional attention, counterfactual explanation faithfulness and self-report predictive value.
- Valid results still reflect **externally imposed**, model-specific screen-selected false report text. No endogenous model explanation, persistent memory, privileged introspection, weights changed or self-certifying estimator follows.
- Phase A order-conditional positive Qwen H1/H2/H3 are not upgraded; Phase A Granite remains INVALID. Phase B separately tests the stronger screen-defined stable baseline.
