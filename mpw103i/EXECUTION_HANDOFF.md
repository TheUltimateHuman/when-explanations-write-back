# MPW-103I — Genuine Iteration Execution and Reproducibility Handoff

**Status at creation:** GPU SCREEN jobs submitted; iteration treatments not yet submitted; no MPW-103I validation observations or primary hypothesis outcomes exist at this point. **Category:** RESEARCH ARTIFACT.

## Frozen source and exactly two baseline-only jobs

- Scientific protocol + candidate source freeze at immutable Git commit **f0a12228e223a0a41948935dc3b1ef75f73574c4**.
- Frozen screen executable SHA256 **4f89a4d759b82cd74ec21465239e48c2558df9f359f5cdff2bf5b4a208e9a04f**, stage tag MPW103I.
- Frozen native eight-cycle/controls runner SHA256 **6fc0467425777a8c5e7ae7c32878a53c886a6f808306f734a4e58badf3763206**.
- Frozen independent baseline selection SHA256 **92f275c4373b404cfe8e742ff39cf938d0360eccafc21d9dc7daf1a443ca0274**.
- Frozen independent eight-cycle analysis SHA256 **bec4c408964163e96ccd9bb92b6c05326979828e31f0b55b6b885c6acfeeb4e7**.
- Frozen screen verifying program SHA256 **df1826d7abdc48664438154ac06108df52480b6699f3c22ca39364c489c8f1da**.
- Frozen eight-cycle results verifying program SHA256 **eed1238a3147de80834ac2073595b0ad393c9ce6acede8ac2480388483783b40**.
- Fresh candidate-bank SHA256 **00cf578b03d0aeabc08b0226c5d84702695e9aa3f5b3264392b31d914526c20a**: 32 calibrated + 2048 candidates, 1024 per sentiment, 8320 new distinct evidence texts, 27208 historical text keys excluded from MPW-101 through MPW-105.
- Qwen/GPU L4 baseline-only screen: https://huggingface.co/jobs/TheUltimateHuman/6ade9c09046eb82b1ece9553
- Granite/GPU L40S baseline-only screen: https://huggingface.co/jobs/TheUltimateHuman/6ade9c0b046eb82b1ece9555
- Both hard provider timeouts 120 minutes and 120 sec archival reserve, with no separate invented 65-minute cap.

## Stage 1: required raw screen recovery and immutable selection BEFORE any generated report

1. Check original job status and MPW103I_END; provider COMPLETED is not enough. Capability needs calibration >=90% LR and RL; sensitivity>=1. SCREEN_COMPLETED requires 2048/2048 original family records. If calibration or provider feasibility fails, record CAPABILITY_GATE_FAIL or RESOURCE_REPLAN respectively and zero iterative validation.
2. Retrieve full GPU logs and locate MPW103I_SOURCE, MPW103I_CALIBRATION, MPW103I_SCREEN_TIMING, MPW103I_SCREEN_PROGRESS, MPW103I_SCREEN_B64, MPW103I_SCREEN_SHARD, MPW103I_SELECTION_CHUNK, MPW103I_SCREEN_SELECTED and MPW103I_END. SCREEN_SHARD raw_sha256 is the digest anchor (check actual raw field).
3. Reconstruct all **8 × 256-family gzip/Base64 shards per model** by grouping SCREEN_B64 messages on original decompressed SHA-256, sorted by chunk part; preserve exact encoded data. Check each decompressed SHA against corresponding SCREEN_SHARD and concatenated full JSONL SHA against MPW103I_END. Save unchanged Base64 to mpw103i/screen/MODEL_shard01..08.jsonl.gz.b64.
4. Reconstruct exact original **MPW103I_SELECTION_CHUNK** text by ascending part, compare selection_sha256 with MPW103I_SCREEN_SELECTED selected_manifest_sha256; parse. Save as mpw103i/selection/MODEL.json. It must contain 64 selected, 32 per sentiment, original order-stable A0 profiles and frozen historical TRUE/FALSE sides.
5. On a new results branch created from prospective freeze, save mpw103i/screen/SCREEN_MANIFEST.json with original model/data/source/case SHA, original GPU job ID, 8 raw SHA anchors, total original raw SHA and original selection JSON SHA; commit to immutable Git SHA.
6. Run mpw103i/scripts/verify_screen.py <IMMUTABLE_SCREEN_COMMIT> <MODEL> as an independent CPU job. It re-reads all original shards and recreates the screen selection without GPU runner import. It must reproduce all 64 selected indices, baseline profiles and source truth. Do not dispatch any generated-iteration GPU job before this passes. If fewer than 32 eligible per class, SCREEN_INSUFFICIENT and no treatment.

## Stage 2: only after selection independently frozen

Execute ORIGINAL frozen code from:
https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/f0a12228e223a0a41948935dc3b1ef75f73574c4/mpw103i/scripts/mpw103i_iterate.py

Arguments: execute --model qwen3 --screen-commit <verified_screen_immutable_commit>, and separately execute --model granite --screen-commit <same_verified_screen_immutable_commit>. Same Qwen L4, Granite L40S, true hard provider timeout 120 min/job.

Runner regenerates/validates original case bank and exactly one screen-selected cohort, remeasures its A0 twice under both physical orders and checks maximum cross-job A0 drift <1e−4, original task answer correctness, screen-original causal sign preservation, positive causal I channels, and no unbounded input truncation. Reject original source drift rather than redefining FALSE or dropping cases.

For each original selected case, independently start six histories at common S0: native MODEL-GENERATED prose report with eight successive actual R0..R7 fed back into future state; ELICIT_ACK identical question with no report uptake; NEUTRAL_ACK; model-generated ARBITRARY_CODE; externally FORCED_FALSE; and ordinary DIRECTIVE. Every arm repeatedly generates the model's own task answer before asking for/forcing the next user/assistant turn. Store all exact generated raw report text, token IDs, state SHA256, current native answer, answer scores, and original screen historical truth. Native branch audits A0..A8 after every generated report. ELICIT_ACK and other controls audit 0,1,2,4,8. Every native report has same-history local elicitation+acknowledgment counterfactual, with input-causal audits to separate elicitation from content uptake.

Primary N=64 families/model, H1 native first-step drift over same-question ack, H2 first report fidelity to native successor over local ack successor, H3 additional step 1→8 native drift versus repeated elicitation+ack. Three tests/model, six Bonferroni-controlled tests alpha=.05/6, 50k family bootstrap, exact signs, order-specific gates. Parseable native report rate >=80% across 8*64 reports or INSTRUMENT_FAILURE. Capture q_t,s_t,C_t,L_t 2x2 transitions at every iteration, report flips, causal sign oscillation, return-to-original and plateau diagnostics without retrospective hypothesis promotion.

## Stage 3: complete original model data and independent verification

GPU log MPW103I_ITERATION_B64/MPW103I_ITERATION_SHARD groups: four original compressed 16-family chunks/model, total 64 unique cases. Reassemble, validate all original SHAs and MPW103I_END combined raw sha. Save raw chunks unchanged to mpw103i/results/MODEL_shard01..04.jsonl.gz.b64 and a machine manifest referencing independently verified screen commit, model source SHA, model/dataset pins and primary gates. Commit immutably.

Run mpw103i/scripts/verify_iteration.py <IMMUTABLE_RESULTS_COMMIT> <MODEL> in a separate CPU job. It checks every original raw shard and combined SHA, exact frozen screen truth and case hashes, then imports **ONLY** independent_analysis.py to reconstruct all 64 eight-step state/version ledgers and H1/H2/H3. Require CPU/GPU result agreement before confirming a positive. Preserve invalid, nonconfirmed, instrument failure and provider error outcomes.

No auto-retry charged GPU jobs to chase favorable science. No work is represented as completed simply because provider shows a completed job. Original MPW-103I user decision stays open until native iteration results pass the complete two-stage archive audit.

## Novelty caution
The native report loop is genuine model-generated conversational history, while the prompts are authored by investigator; the model's weights are not changed. Wang & Atanasova EMNLP 2025, Mayne et al. ICML 2026 and explanation-faithfulness literature already investigate self-explanation and iterative refinement. Only the versioned historical versus local and later causal intervention-response profiles and independent results can support a narrow MPW-103I advance.
