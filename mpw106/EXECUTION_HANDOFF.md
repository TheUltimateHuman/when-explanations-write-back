# MPW-106 — Durable Memory Causal-Provenance Execution Handoff

**Research classification:** RESEARCH ARTIFACT. **Current status when written:** prospective protocol and implementations authored, synthetic positive/null/source-tamper/blind-selection tests passed, fresh source-case CPU preflight still running. NO MPW-106 GPU results; NO source-content memory store has yet been written.

## Provenance and original target

The canonical original *When Explanations Write Back* v1.1, §§2.1–2.5 and Appendix B.2–B.3, requires a **carrier-aware Baseline Write Barrier**. MPW-106 tests an actual durable Git external memory carried from one model GPU process into another, with a protected historical A0 and the same report under later retrieved A_R.

This is NOT an internally persistent weight/mind and deletion from the active Git read path is not cryptographic removal of old Git history. MemGPT, LoCoMo, MemSecBench and MemForm provide direct near prior-art collisions for memory itself.

## Frozen stage design

[MPW-106 prospective protocol](PROTOCOL.md) originally committed 2026-11-01 on branch mpw106-20261101-prevalidation (initial protocol commit b84d4e0ab37108aa4ee021e89b6ad8b396c691a9). Its H1–H3 and validity gates are frozen before the GPU treatment.

Fresh case preflight: HF CPU job https://huggingface.co/jobs/TheUltimateHuman/6ae821bfc78863f9c6301405. It recreates all MPW-101 through MPW-105 and MPW-103I historical samples, excludes texts, and prints NEW case-bank SHA. The executable screen has EXPECTED_CANDIDATE_MANIFEST placeholder until that hash is pinned in a commit. **Do not launch screening with an unpinned placeholder.**

Implemented research files:
- mpw106/scripts/mpw106_screen.py (untreated-only original A0 and 2048-case selection, 32 eligible per sentiment).
- mpw106/scripts/independent_screen.py and verify_screen.py (CPU SHA/source replay).
- mpw106/scripts/mpw106_writer.py (different GPU original A0 repeat and genuinely model-generated task answer + one-sentence report; no memory commit inside GPU).
- mpw106/scripts/independent_writer.py and verify_writer.py (separate CPU raw report/source check).
- mpw106/scripts/build_store.py (CPU conversion of independently verified writer raw records to N→L→C→D persistent versions).
- mpw106/scripts/memory_contract.py and verify_store.py (pure, SHA-bound external-memory read/active-delete and correction provenance).
- mpw106/scripts/mpw106_reader.py (DIFFERENT GPU process; reads Git snapshot commits, never writer transcript, audits clean/neutral/live/corrected/deleted/missing/explicit-old-live).
- mpw106/scripts/independent_analysis.py and verify_reader.py (source-independent q/s/C/L and frozen H1/H2/H3).

Synthetic tests (NO science inference):
- https://huggingface.co/jobs/TheUltimateHuman/6ae823f00e0338d1bb7dcbb4 — positive, null, tampered record/binding rejection, PASS.
- https://huggingface.co/jobs/TheUltimateHuman/6ae8245dc78863f9c63014a6 — independent first-32-per-label synthetic screen, PASS.
- https://huggingface.co/jobs/TheUltimateHuman/6ae82500c78863f9c63014e0 — independently check native writer original text, repeat and wrong-case negative fixtures, PASS.
- https://huggingface.co/jobs/TheUltimateHuman/6ae823f30e0338d1bb7dcbb6 — initial source AST/hash audit, PASS. The final manifest pins require a NEW final byte audit before GPU.

## Stage 0: complete preflight, pin and freeze

1. Read original MPW106_SOURCE, MPW106_PREFLIGHT_MODEL, MPW106_PREFLIGHT_COMPLETE from the CPU job logs. Require complete fresh 32+2048 families, pinned SST-2 dataset, exclusion digest and atomic output tokens.
2. Update the screen EXPECTED_CANDIDATE_MANIFEST with exact new SHA, then run independent final AST/SHA audit on the exact executable.
3. Pin writer and reader SCREEN_URL and SCREEN_SHA to that exact immutable, candidate-pinned screen source. Pin their CASE_MANIFEST / EXPECTED_CASE_BANK values; pin reader CONTRACT_URL/CONTRACT_SHA to the frozen memory_contract.py content. No scientific gate modifications.
4. Commit mpw106/FREEZE.md with all final literal SHA, case-bank hash, model revisions, study size, hypotheses and TRUE hard provider timeout. No GPU jobs before it.

## Stage 1: baseline-only GPU screen

Submit one job per eligible model using frozen screen script:
- Qwen L4x1, Granite L40Sx1, provider hard timeout 90m/job.
- source args: screen --model qwen3 / screen --model granite.
- require calibration >=.90 both orders + sensitivity>=1; if failure record CAPABILITY_GATE_FAIL with NO candidate/hypothesis results.
- screen 2048/2048 original A0 families; select exactly 32/class by predeclared order-invariant source sign, original task answer, channel positivity and numerical repeat.
- log tags: MPW106_SOURCE, _HARDWARE, _CALIBRATION, _SCREEN_TIMING, _SCREEN_B64, _SCREEN_SHARD, _SELECTION_CHUNK, _SCREEN_SELECTED, _END.
- Recover 8 gzip/Base64 shards/model of 256 families and original GPU selection JSON assembled from chunks; verify each decompressed SHA and concatenated whole raw SHA. Save to mpw106/screen/MODEL_shard01..08.jsonl.gz.b64, mpw106/selection/MODEL.json, mpw106/screen/SCREEN_MANIFEST.json and commit immutable results.
- CPU verify_screen.py <immutable_results_git_sha> <model> must pass BEFORE writer.

## Stage 2: native report WRITER

Fresh GPU job with frozen mpw106_writer.py:
 write --model MODEL --screen-commit IMMUTABLE_SCREEN_GIT_SHA.
- First audit original protected A0 twice vs screen. Any drift, wrong task or bad side => INVALID, no stored memory; no reassigning original A0.
- Calibrate natural model prose parse >=80% on 32 source calibration cases. Then generate exactly 64 model-selected sentiment answers and greedy <=48 token native reports, with every raw text/token ID/hash, original case and source side.
- 4 original 16-family B64/GZIP raw shards with tags MPW106_WRITER_B64 and WRITER_SHARD, original end SHA. Preserve original GPU bytes; create mpw106/writer/WRITER_MANIFEST.json referencing immutable source/screen and four raw hashes. CPU verify_writer.py must pass first.
- If ANY report raw is entirely empty, record INSTRUMENT_FAILURE rather than pretending an ACTIVE store has content.

## Stage 3: actual Git persistent memory N→L→C→D

Run frozen CPU build_store.py with writer archive SHA/model after independent writer verification. It independently downloads original writer GPU shards and prints four STATE_CHUNK groups (NEUTRAL, LIVE, CORRECTED, DELETED). Combine by sha/part, JSON-parse each and confirm output STATE SHA. These are external persistent records, NOT model logits and not a synthetic chat prefix.

Create mpw106/store/state.json with NEUTRAL JSON, commit N. UPDATE the SAME PATH content to LIVE, commit L. UPDATE to CORRECTED, commit C. UPDATE to DELETED/tombstone, commit D. Every read is pinned to original complete 40-char Git commit; do NOT overwrite only at branch HEAD without retaining immutable version refs. Record all four refs in manifest and CPU verify_store.py.

- Neutral content is an ordinary non-reliance note.
- Live content is EXACT generated model report text and source raw SHA.
- Correction uses frozen original TRUE side but is labeled EXTERNAL_AUDITOR_CORRECTION; no model spontaneous repair claim.
- D active text is null, status DELETED. Earlier Git commits still retain LIVE and C, so not cryptographically erased.
- Independent store verification checks parent digest chain, all 64 case SHA bindings, wrong key, tamper and revision mismatch blocks, no silent fallback from D, and EXPLICIT_STALE old L still intentionally accessible.
- Any invalidity => NO GPU reader, regardless of plausible narrative.

## Stage 4: new GPU READER and scientific inference

Run separately frozen mpw106_reader.py:
 read --model MODEL --screen-commit <IMMUTABLE_SCREEN_COMMIT> --neutral-commit <N> --live-commit <L> --corrected-commit <C> --deleted-commit <D>.
One newly loaded model with NO writer conversation, code cache or KV transferred; true hard provider timeout 90m.
- Fresh clean A0 original and repeat across both LR/RL, strict original source screen drift <1e−4 and task/channel validity.
- READ only model-visible per-key record from each Git snapshot. Seven conditions CLEAN, NEUTRAL, LIVE, CORRECTED, DELETED, MISSING, EXPLICIT_STALE; D and MISSING exact same wrapper, LIVE and EXPLICIT_STALE same old L content. All raw I_LEFT/I_RIGHT/D/J/accuracy/returned content hashes and messages retained.
- 4 gzip/Base64 original GPU 16-family shards, full SHA and machine manifest. CPU verify_reader.py re-reads all ORIGINAL raw SHA, original selection and N/L/C/D versions and independently recomputes H1 signed report-specific steering over neutral, H2 false natural report conversion over neutral (min16 original false cases), H3 external correction effect (min16). N=64 families, six-model Bonferroni .05/6, 50k family bootstrap and exact family sign checks plus both-order conditions. q,s,C,L checked exactly.
- Publication statuses: CONFIRMED / NOT_CONFIRMED / INVALID / INDETERMINATE_CAPABILITY / CAPABILITY_GATE_FAIL / SCREEN_INSUFFICIENT / INSTRUMENT_FAILURE / RESOURCE_REPLAN / UNKNOWN_NOT_EXECUTED.

No GPU re-runs to chase positive results. Distinguish external retrieval effect from intrinsic model persistence, correction instruction effect from model self-repair, and ACTIVE tombstone from complete archival deletion.

**Tracking issue:** https://github.com/TheUltimateHuman/when-explanations-write-back/issues/2
