# MPW-105 — Execution Handoff and Non-Leakage Gates

**Classification:** RESEARCH ARTIFACT, prospective MPW-105. **At handoff creation:** baseline-only screen GPU jobs submitted; no report-generation or optimization jobs launched, and no scientific MPW-105 outcomes known.

## Two original baseline-only jobs
- Qwen3-4B-Instruct L4: https://huggingface.co/jobs/TheUltimateHuman/6add1b0c1e112550ce7e3d00
- Granite-3.3-8B-Instruct L40S: https://huggingface.co/jobs/TheUltimateHuman/6add1b0e1e112550ce7e3d02
- Both ran frozen screen source Git SHA afea0481fc5615376974d4c3f375eecae49414b2, executable SHA-256 3b3e485f7c7313a369a4521dfe9a7c53f7062e732fefc69bf35ef88595005b2c.
- 64 calibration plus 3,072 baseline-only candidate families, balanced 1,536 each label; candidate sample SHA-256 21dcef582979554f9b7d9d1a76c745803fdb84e8ab79111eee6a73bd14a1ac86.
- Each GPU job has 75-minute actual provider timeout with 120-second archival reserve; forecast padding cannot veto a physically executable study.

## Strict stage order

### Screen → independent archive → fixed train/holdout selection
1. Inspect both Hugging Face screening logs. A provider COMPLETED stage is not sufficient: locate MPW105_END with SCREEN_COMPLETED, 3072 candidates and 160 selected train+holdout cases. If capability or actual provider/resource gate fails, record it and do not assume success.
2. Recover every MPW105_SCREEN_B64 and MPW105_SCREEN_SHARD group: 12 gzip/Base64 JSONL shards of **256** families each, with GPU-emitted decompressed SHA-256 anchors. MPW105_SELECTION_CHUNK carries the complete selected-manifest JSON, keyed by exact selection_sha256, with parts in numeric order. Check original MPW105_SCREEN_SELECTED summary and MPW105_END raw_sha256.
3. Archive unchanged original Base64 gzip shards to mpw105/screen/MODEL_shard01..12.jsonl.gz.b64 plus model selected JSON mpw105/selection/MODEL.json. Make mpw105/screen/SCREEN_MANIFEST.json holding model/source/data pins, job ID, 12 raw shard SHAs, combined raw SHA, selection SHA and independent_screen.py SHA. **Commit to a new Git branch**; remember exact resulting immutable SHA.
4. Run frozen mpw105/scripts/verify_screen.py on that immutable SHA for BOTH models. It downloads all raw shards, checks original GPU hashes and separately reproduces the fixed eligibility filter and 40/40 TRAIN plus 40/40 HOLDOUT split by sentiment WITHOUT importing the GPU runner.
5. Require selected_n=160, train_n=80 and holdout_n=80, full case disjointness and independent CPU verification. If insufficient, record SCREEN_INSUFFICIENT and do NOT generate reports/train.

### Score-only TRAIN: never touch holdout before choosing winner
6. Train source has ALREADY been authored, syntactically checked and source-locked before GPU screen: mpw105/scripts/mpw105_optimize.py from Git commit afea0481fc5615376974d4c3f375eecae49414b2, SHA-256 24895fdc8595c663174bdf826fdd99fa954f1859f3ed2c65771c04987772030a.
7. Only after both model selections are archived and CPU-verified, submit a *separate* GPU job per eligible model with arguments: train --model MODEL --screen-commit IMMUTABLE_SCREEN_RESULTS_SHA; Qwen L4x1, Granite L40Sx1, provider timeout 75m.
8. Train stage reconstitutes original 80 model-specific TRAIN cases; remeasures protected A0; elicits true model-produced constrained code and raw explanatory prose after its own task answer; reports parse/fallback; evaluates all **P0..P6** candidate reports and controls. It must pass original baseline task/numerical gates and natural-prose calibration >=80% before TRAIN. TRAIN reports/controls are not heldout validation.
9. Recover MPW105_TRAIN_B64 and MPW105_TRAIN_SHARD original raw shards (4×20 cases/model). Archive exact bytes and GPU SHA anchors in mpw105/train/ and machine-readable TRAIN_MANIFEST.json. Run mpw105/scripts/verify_train.py on the immutable Git commit. It imports separately written independent_selector.py and computes the **globally highest mean TRAIN F1=s**. The training selector receives no F0/q values for policy choice.
10. Save CPU-verified exact policy JSON as mpw105/policy/MODEL.json in a NEW immutable Git commit, preserving train raw/policy source SHA and selected report policy P0..P6. The CPU policy hash is computed before any holdout GPU run. If P0 wins, the eventual primary Δs=0 by definition.

### Blind HOLDOUT → independent versioned q/s/C/L decision
11. Submit a NEW GPU job per model with arguments: holdout --model MODEL --screen-commit IMMUTABLE_SCREEN_SHA --policy-commit IMMUTABLE_POLICY_SHA; same frozen source/hardware/75m actual limit. HOLDOUT evaluates ONLY comparator P0 and learned policy, plus predeclared neutral/sham/imperative/oracle diagnostic controls. Never scan alternate candidate policies or select winners on heldout families.
12. Recover exact MPW105_HOLDOUT_B64/SHARD (4×20 cases/model), raw hashes and report text, store in mpw105/holdout/ plus HOLDOUT_MANIFEST.json. Independent CPU verify_holdout.py rereads original screen historical A0 and frozen policy and computes q,s,C,L, the 2x2 transitions, 50k family-bootstrap intervals, exact signs and all frozen H1/H2 gates.
13. H1 requires positive heldout Δs with adjusted bootstrap lower>0, sign p<.0125 and positive both-order diagnostic gain. H2 additionally requires positive adjusted lower on Δ(s−q), sign p<.0125, one-sided 98.75% upper Δq<=.05 and H1. Historical q improvement or nonsignificant q alone NEVER establishes evaluator gaming. Negative/indeterminate/invalidity preserved.

## Original substantive and prior-art boundaries
- MPW-101 natural reports did NOT pass primary conversion. MPW-104B stronger stable-baseline false-report conversion tests were valid and NOT CONFIRMED in both architectures. Neither result is silently overwritten by optimized policy outcomes.
- User decision: MPW-103I genuine iterative generated explanations remains an explicitly open requirement in https://github.com/TheUltimateHuman/when-explanations-write-back/issues/1; optimizing candidate reports here does not complete it.
- Pan et al. 2024 already study in-context reward hacking, Ferreira et al. 2026 reward-hacked explanations, Malladi & Srivastava 2026 optimize behavioral explanation faithfulness. No generic novelty claim about reward hacking/optimization is permitted. Incremental target is A0-versus-A1 versioned fidelity transfer.
- These tests include deliberately reversed *externally assembled* candidate reports, plus genuinely model-generated prose (with parse/fallback disclosure). Do not call every candidate an endogenous self-explanation. No model weights or durable memory are updated.

No new paid jobs should be repeated solely for desired positive results. Original sampled cases, protocol, source hashes and family-level statistical gates are permanent.
