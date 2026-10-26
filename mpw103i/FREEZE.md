# MPW-103I — Prospective Source, Source-Case and Hypothesis Freeze

**Investigator:** Aidan Edward Lawson · Modal Path Ethics.
**Freeze date:** October 25–26, 2026 (local/UTC).
**State at commit:** All CPU-only sampling, source/hash audits and synthetic null/positive/invalid tests completed. **No GPU MPW-103I screening or genuine iterative explanation has been measured before this commit.**

## Historical and scientific scope
This specifically completes the original MPW-103 iteration question preserved in [issue #1](https://github.com/TheUltimateHuman/when-explanations-write-back/issues/1), distinct from the previous MPW-103 experiment with experimenter-forced report histories. Its executed chain will be actual model-generated R0..R7 consumed by the model before the subsequent R1..R7 are generated.

The original source manuscript *When Explanations Write Back*, v1.1 Section 2.1 and 5.5 defines S0, A_t, generated R_t, writeback W, and version-indexed audits. The identity s_t=q_t+C_t-L_t is an audit checksum rather than independently established causal evidence.

## Immutable design
[Prospective protocol](PROTOCOL.md): first commit 47e26cf4da4c5ce354d38cf2babf52bd7bd7ea53.

- Baseline-only GPU screening executable mpw103i/scripts/mpw103i_screen.py, byte SHA-256 **4f89a4d759b82cd74ec21465239e48c2558df9f359f5cdff2bf5b4a208e9a04f**, content Git commit 613a165b21fd7d4e589108ffe3fe198ca52cd8c4.
- Eight-cycle model-generated explanation/causal audit executable mpw103i/scripts/mpw103i_iterate.py, SHA-256 **6fc0467425777a8c5e7ae7c32878a53c886a6f808306f734a4e58badf3763206**.
- Independently authored screening analysis mpw103i/scripts/independent_screen.py SHA-256 **92f275c4373b404cfe8e742ff39cf938d0360eccafc21d9dc7daf1a443ca0274**.
- Independent genuine iteration statistical / provenance analyzer mpw103i/scripts/independent_analysis.py SHA-256 **bec4c408964163e96ccd9bb92b6c05326979828e31f0b55b6b885c6acfeeb4e7**.
- Blind raw screen SHA verifier mpw103i/scripts/verify_screen.py SHA-256 **df1826d7abdc48664438154ac06108df52480b6699f3c22ca39364c489c8f1da**.
- Blind raw 8-cycle versioned report verifier mpw103i/scripts/verify_iteration.py SHA-256 **eed1238a3147de80834ac2073595b0ad393c9ce6acede8ac2480388483783b40**.

## Frozen candidate bank and model/data versions
- Canonical fresh 32-calibration plus 2048-candidate bank **SHA-256 00cf578b03d0aeabc08b0226c5d84702695e9aa3f5b3264392b31d914526c20a**.
- Seed 2026102501; 1024 candidates per sentiment; 8320 DISTINCT new evidence texts; 27208 normalized historical text keys excluded. Every original MPW-101/102A/102B/102C/103/104A/104B/105 cohort was regenerated and hash checked before sample freeze.
- Dataset stanfordnlp/sst2 SHA 8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb.
- Qwen/Qwen3-4B-Instruct-2507 SHA cdbee75f17c01a7cc42f958dc650907174af0554, NVIDIA L4 GPU.
- ibm-granite/granite-3.3-8b-instruct SHA 51dd4bc2ade4059a6bd87649d68aa11e4fb2529b, NVIDIA L40S GPU.

## Verified before first GPU
- [CPU historical manifest reconstruction and token preflight](https://huggingface.co/jobs/TheUltimateHuman/6ade9761046eb82b1ece92ec) **COMPLETED_NO_MODEL_INFERENCE**. Source bank SHA above; both native output-label pairs and A/B codes atomic; max observed baseline prompt Qwen 179 tokens, Granite 249; declared hard input cap 4096, runtime has no silent truncation.
- Source screening final AST and SHA: [6ade9b721e112550ce7f05aa](https://huggingface.co/jobs/TheUltimateHuman/6ade9b721e112550ce7f05aa).
- All six source AST and hash audit [6ade9ba4046eb82b1ece950f](https://huggingface.co/jobs/TheUltimateHuman/6ade9ba4046eb82b1ece950f) **PASS**.
- Blind 2048-case screening positive/incomplete synthetic test: [6ade99df046eb82b1ece9417](https://huggingface.co/jobs/TheUltimateHuman/6ade99df046eb82b1ece9417) **PASS** (screen executable was subsequently metadata-cleaned and SHA-pinned, selection procedure unchanged).
- Independent genuine 64-family eight-cycle synthetic POSITIVE, NULL and INVALID test: [6ade9ba5046eb82b1ece9513](https://huggingface.co/jobs/TheUltimateHuman/6ade9ba5046eb82b1ece9513) **PASS**. Synthetic outcomes have NO scientific meaning.

## Strict execution ordering
1. Execute **baseline-only** 2048-case screening for each eligible model, never generating a report; select exactly FIRST 32 eligible families per class on frozen A0 sign accuracy/sensitivity/repeat/presentation-invariance.
2. Recover ALL 2048 original untreated GPU records and select 64 in immutable Git results; CPU independently recompute exact selected cases/hashes. Do NOT submit genuine iteration before this gate.
3. From the frozen selected 64 cases, run genuine eight-cycle NATIVE_REPORT plus 5 declared independently rooted control histories. Generate native task answers and model-generated report prose from current S_t; append generated R_t in a new assistant turn before generating R_t+1.
4. Audit true A0, A1, A2, A4, A8 (and NATIVE all intermediate t) under both physical evidence orders, plus local elicitation+acknowledgment counterfactuals at each NATIVE step. Fail INVALID if original baseline changes numerically or source sign before treatment; never reorient old true side.
5. The three frozen tests per model: first native report effect vs same-question ack H1; first self-validation relative SAME S0 elicitation+ack H2; incremental 1→8 drift beyond elicitation+ack H3. SIX model-level tests Bonferroni .05/6 with family/bootstrap/sign/physical-order checks. Fidelity q_t,s_t,C_t,L_t for all t, report-side changes, mechanism sign oscillation/reversion/plateau are mandatory, but secondary.
6. Archive original 64 eight-cycle raw families in 4×16 gzip/Base64 SHA-anchored shards plus complete state/report provenance and independent CPU replay before any confirmation.
7. **No invented 65-minute runtime gate.** Each GPU screen and iteration job uses its true 120-minute provider timeout; four-case measured physical feasibility, 35% padding warning only and 120-second archival reserve. Provider cost figures are estimates, not final bills.

Scientific limits: no proof of introspection or weight rewriting, only frozen model context versions; elicitation and token length can be active causal channels. EMNLP 2025 explanation self-critique prior art and 2026 explanation sufficiency/simulatability work prevent generic novelty claims. True result statuses must distinguish confirmed, null, invalid, unexecuted or resource constrained.
